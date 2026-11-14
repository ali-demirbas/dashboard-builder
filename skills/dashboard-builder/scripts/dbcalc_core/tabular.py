"""Reading CSV/XLSX files and parsing locale-dependent numbers and dates.

Implements the locale checks of references/data-quality-gate.md §3
("Locale of the file itself") and analysis-playbook.md §Ingestion
(decimal comma, delimiter, day-month order, non-UTF-8 fallback, header not on
row 1, hidden sheets). Nothing is guessed silently: every convention that
could not be settled from the data is reported as "ambiguous".
"""
import csv
import datetime as _dt
import functools
import io
import json
import os
import re
import sys
import zipfile

csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))

NULL_TOKENS = {"", "na", "n/a", "#n/a", "null", "none", "nan", "-", "--", "—", "–"}
_CURRENCY = "₺$€£¥"
_CUR_CODES = re.compile(r"^(?:TRY|TL|USD|EUR|GBP)\s*|\s*(?:TRY|TL|USD|EUR|GBP)$", re.I)
_NUM_SHAPE = re.compile(r"^[+-]?(?:\d[\d.,]*|[.,]\d+)$")
_SPACES = re.compile(r"[\s   ']")

_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T]\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$")
_YMD_SLASH = re.compile(r"^(\d{4})[/.](\d{1,2})[/.](\d{1,2})$")
_AB_YEAR = re.compile(r"^(\d{1,2})([./-])(\d{1,2})\2(\d{4})(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?$")
_YM = re.compile(r"^(\d{4})-(\d{2})$")
_COMPACT = re.compile(r"^(20\d{2})(\d{2})(\d{2})$")
_ISOWEEK = re.compile(r"^(\d{4})-?W(\d{1,2})(?:-?([1-7]))?$", re.I)


class InputError(Exception):
    """A file or argument problem reported to the caller as JSON, not a traceback."""


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


class Table:
    def __init__(self, name, headers, rows, meta):
        self.name = name          # sheet name for xlsx, None for csv
        self.headers = headers    # list[str]
        self.rows = rows          # list[list[raw]]; raw is str, int, float, datetime or None
        self.meta = meta          # dict: delimiter, encoding, header_row, ...
        self.lines = list(range(1, len(rows) + 1))  # source locator per row (see _finish)

    def locator(self):
        """What ``lines`` counts: 'line' (CSV file line), 'sheet_row' (XLSX
        worksheet row) or 'record' (JSON record number)."""
        return self.meta.get("locator", "line")

    def col(self, name):
        try:
            return self.headers.index(name)
        except ValueError:
            raise InputError("column not found: %r (columns: %s)" % (name, ", ".join(self.headers)))


def _decode(raw):
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16"), "utf-16"
    for enc in ("utf-8-sig", "cp1254", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


def _pick_delimiter(text):
    lines = [ln for ln in text[:200000].splitlines() if ln.strip()][:50]
    best, best_score = ",", -1
    for cand in (",", ";", "\t", "|"):
        try:
            counts = [len(r) for r in csv.reader(io.StringIO("\n".join(lines)), delimiter=cand)]
        except csv.Error:
            continue
        if not counts or max(counts) < 2:
            continue
        mode = max(sorted(set(counts)), key=counts.count)
        score = counts.count(mode) * 100 + mode
        if score > best_score:
            best, best_score = cand, score
    return best


def _header_index(rows):
    """First row that looks like a header: >=2 non-empty cells, all text, and
    at least 60% as wide as the widest of the first 20 rows."""
    width = max((sum(1 for c in r if _blank(c) is False) for r in rows[:20]), default=0)
    for i, r in enumerate(rows[:20]):
        filled = [c for c in r if not _blank(c)]
        if len(filled) >= max(2, 0.6 * width) and all(isinstance(c, str) for c in filled):
            if not all(_NUM_SHAPE.match(_SPACES.sub("", c)) for c in filled):
                return i
    return 0


def _blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def _dedupe_headers(hs):
    out, seen = [], {}
    for i, h in enumerate(hs):
        h = ("" if h is None else str(h)).strip() or "column_%d" % (i + 1)
        if h in seen:
            seen[h] += 1
            h = "%s__%d" % (h, seen[h])
        else:
            seen[h] = 1
        out.append(h)
    return out


def _finish(name, grid, meta, lines=None):
    """grid: list of rows; lines: the source locator of each grid row (file
    line for CSV, worksheet row for XLSX, record number for JSON)."""
    if lines is None:
        lines = list(range(1, len(grid) + 1))
    while grid and all(_blank(c) for c in grid[-1]):
        grid.pop()
        lines.pop()
    if not grid:
        raise InputError("no rows found")
    hi = _header_index(grid)
    raw_headers = grid[hi]
    meta["header_row"] = hi + 1
    meta["header_line"] = lines[hi]
    stripped = [str(x).strip() for x in raw_headers if x is not None]
    meta["duplicate_header_names"] = sorted({h for h in stripped if stripped.count(h) > 1})
    headers = _dedupe_headers(raw_headers)
    width = len(headers)
    rows, row_lines = [], []
    blank_rows = 0
    for r, ln in zip(grid[hi + 1:], lines[hi + 1:]):
        if all(_blank(c) for c in r):
            blank_rows += 1
            continue
        r = list(r[:width]) + [None] * (width - len(r))
        rows.append(r)
        row_lines.append(ln)
    meta["blank_rows_skipped"] = blank_rows
    t = Table(name, headers, rows, meta)
    t.lines = row_lines
    return t


_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _sniff(path):
    with open(path, "rb") as fh:
        head = fh.read(8)
    if head.startswith(b"\xd0\xcf\x11\xe0"):
        return "ole"
    if head.startswith(b"PK\x03\x04"):
        return "zip"
    return "text"


def load_csv(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    text, enc = _decode(raw)
    del raw
    meta = {"format": "csv", "encoding": enc, "warnings": []}
    nul = text.count("\x00")
    if nul:
        if nul > max(10, len(text) // 20):
            raise InputError("%s does not look like a delimited text file (it is full of NUL bytes: "
                             "binary, or UTF-16 without a byte-order mark)" % os.path.basename(path))
        text = text.replace("\x00", "")
        meta["warnings"].append("%d NUL byte(s) removed from the file" % nul)
    sample = text[:65536]
    if sample and len(_CTRL.findall(sample)) > max(5, len(sample) // 100):
        raise InputError("%s does not look like a delimited text file (binary content)"
                         % os.path.basename(path))
    if "\r" in text and "\n" not in text:
        text = text.replace("\r", "\n")  # classic Mac (CR-only) line endings
        meta["line_endings"] = "CR"
    delim = _pick_delimiter(text)
    meta["delimiter"] = delim
    grid, lines = [], []
    cache = {}
    rd = csv.reader(io.StringIO(text, newline=""), delimiter=delim)
    prev = 0
    for rec in rd:
        # intern repeated values (dimension labels, dates) to keep memory near the file size
        grid.append([cache.setdefault(c, c) if len(c) < 64 else c for c in rec])
        lines.append(prev + 1)
        prev = rd.line_num
        if len(cache) > 200000:
            cache.clear()
    del text
    return _finish(None, grid, meta, lines)


def load_json(path):
    """A list of flat objects, or {"rows": [...]} / {"data": [...]} holding
    one; .jsonl / .ndjson: one object per line. Nested values are kept as
    JSON text."""
    base = os.path.basename(path)
    with open(path, encoding="utf-8-sig") as fh:
        raw = fh.read()
    recs = None
    if os.path.splitext(path)[1].lower() in (".jsonl", ".ndjson"):
        recs = []
        for n, line in enumerate(raw.splitlines(), 1):
            if line.strip():
                try:
                    recs.append(json.loads(line))
                except ValueError:
                    raise InputError("%s line %d is not valid JSON" % (base, n))
    else:
        try:
            doc = json.loads(raw)
        except ValueError as e:
            raise InputError("%s is not valid JSON (%s)" % (base, e))
        if isinstance(doc, dict):
            for k in ("rows", "data", "records", "items"):
                if isinstance(doc.get(k), list):
                    recs = doc[k]
                    break
        elif isinstance(doc, list):
            recs = doc
    if recs is None or not all(isinstance(r, dict) for r in recs):
        raise InputError("unsupported JSON shape in %s: expected a list of flat objects, or "
                         "{\"rows\": [...]} holding one" % base)
    headers = []
    seen = set()
    for r in recs:
        for k in r:
            if k not in seen:
                seen.add(k)
                headers.append(k)

    def cell(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False, sort_keys=True)
        return v

    grid = [list(headers)] + [[cell(r.get(h)) for h in headers] for r in recs]
    lines = [0] + list(range(1, len(recs) + 1))
    return _finish(None, grid, {"format": "json", "encoding": "utf-8", "locator": "record"}, lines)


def _openpyxl():
    try:
        import openpyxl  # noqa: F401
        return openpyxl
    except ImportError:
        raise InputError("reading .xlsx needs the optional openpyxl package "
                         "(pip install openpyxl), or export the sheet to CSV")


HIDDEN_ROWS_MAX_BYTES = 10 * 1024 * 1024


def open_workbook(path):
    """Open read-only (streaming) with cached values. A file whose content is
    an .xlsx but whose extension is not (.csv, .xls) is opened by content."""
    op = _openpyxl()
    try:
        with open(path, "rb") as fh:
            data = io.BytesIO(fh.read())
        return op.load_workbook(data, read_only=True, data_only=True)
    except zipfile.BadZipFile:
        raise InputError("%s is not a valid .xlsx workbook (not a zip archive)" % os.path.basename(path))
    except KeyError as e:
        raise InputError("%s is a zip archive but not an .xlsx workbook (%s missing)"
                         % (os.path.basename(path), e))


def xlsx_sheets(path, wb=None):
    """Every sheet including hidden ones: name, state, rows, hidden rows.
    Hidden-row counts need the full (non-streaming) reader, so they are read
    only for files up to 10 MB and reported as null above that."""
    wb = wb or open_workbook(path)
    hidden = {}
    if os.path.getsize(path) <= HIDDEN_ROWS_MAX_BYTES:
        op = _openpyxl()
        with open(path, "rb") as fh:
            full = op.load_workbook(io.BytesIO(fh.read()), data_only=True)
        hidden = {ws.title: sum(1 for _, d in ws.row_dimensions.items() if d.hidden) for ws in full.worksheets}
    out = []
    for ws in wb.worksheets:
        nonempty = 0
        max_row = 0
        for r in ws.iter_rows(values_only=True):
            max_row += 1
            if any(not _blank(c) for c in r):
                nonempty += 1
        out.append({"sheet": ws.title, "state": ws.sheet_state,
                    "max_row": max_row, "nonempty_rows": nonempty,
                    "hidden_rows": hidden.get(ws.title)})
    return out


def load_xlsx(path, sheet=None, wb=None):
    wb = wb or open_workbook(path)
    names = wb.sheetnames
    if sheet is None:
        sheet = names[0]
    if sheet not in names:
        raise InputError("sheet not found: %r (sheets: %s)" % (sheet, ", ".join(names)))
    ws = wb[sheet]
    grid = [list(r) for r in ws.iter_rows(min_row=1, values_only=True)]
    meta = {"format": "xlsx", "sheet_state": ws.sheet_state, "locator": "sheet_row", "warnings": []}
    return _finish(sheet, grid, meta, list(range(1, len(grid) + 1)))


def is_xlsx(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        return True
    return os.path.isfile(path) and _sniff(path) == "zip" and _is_xlsx_zip(path)


def _is_xlsx_zip(path):
    try:
        with zipfile.ZipFile(path) as z:
            return "xl/workbook.xml" in z.namelist()
    except (zipfile.BadZipFile, OSError):
        return False


def check_path(path):
    base = os.path.basename(path.rstrip("/")) or path
    if os.path.isdir(path):
        raise InputError("%s is a directory, not a file" % base)
    if not os.path.exists(path):
        raise InputError("file not found: %s" % base)
    ext = os.path.splitext(path)[1].lower()
    kind = _sniff(path)
    if kind == "ole":
        raise InputError("%s is a legacy Excel .xls (or other OLE) file, which is not supported: "
                         "save it as .xlsx or CSV" % base)
    if ext in (".xls",) and not (kind == "zip" and _is_xlsx_zip(path)):
        raise InputError("%s: legacy .xls is not supported; save it as .xlsx or CSV" % base)
    if ext in (".pdf", ".zip", ".parquet", ".docx", ".pptx") or (kind == "zip" and not _is_xlsx_zip(path)):
        raise InputError("%s: unsupported file type for dbcalc (CSV, TSV, XLSX or JSON)" % base)


def disguised_warning(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".xlsx", ".xlsm"):
        return ("%s is an .xlsx workbook saved with a %s extension; read as .xlsx"
                % (os.path.basename(path), ext or "missing"))
    return None


def load(path, sheet=None):
    check_path(path)
    ext = os.path.splitext(path)[1].lower()
    if is_xlsx(path):
        t = load_xlsx(path, sheet)
        w = disguised_warning(path)
        if w:
            t.meta["warnings"].append(w)
        return t
    if ext in (".json", ".jsonl", ".ndjson"):
        return load_json(path)
    return load_csv(path)


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------


_PCT_LEAD = re.compile(r"^([+-]?)\s*%\s*")


def has_percent(raw):
    """True for '12%', '12 %', '%12,5' (Turkish form) and '% 12,5'."""
    if not isinstance(raw, str):
        return False
    s = raw.strip()
    return s.endswith("%") or bool(_PCT_LEAD.match(s))


def _strip_number(s):
    s = s.strip()
    pct = False
    m = _PCT_LEAD.match(s)
    if m:
        pct, s = True, m.group(1) + s[m.end():]
    if s.endswith("%"):
        pct, s = True, s[:-1]
    s = s.strip()
    s = s.strip(_CURRENCY).strip()
    s = _CUR_CODES.sub("", s).strip()
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg, s = True, s[1:-1]
    s = _SPACES.sub("", s)
    if s.startswith("-"):
        neg, s = (not neg), s[1:]
    elif s.startswith("+"):
        s = s[1:]
    return s, neg, pct


def number_evidence(raw):
    if isinstance(raw, str):
        return _number_evidence_str(raw)
    return "native" if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None


@functools.lru_cache(maxsize=65536)
def _number_evidence_str(raw):
    """Which decimal mark a single raw value implies: 'comma', 'dot', 'ambiguous'
    (one separator followed by exactly 3 digits), 'none' (no separator), or
    None when the value is not number-shaped."""
    if not isinstance(raw, str):
        return "native" if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None
    s, _, _ = _strip_number(raw)
    if not s or not _NUM_SHAPE.match(s):
        return None
    has_c, has_d = "," in s, "." in s
    if has_c and has_d:
        return "comma" if s.rfind(",") > s.rfind(".") else "dot"
    for sep, single, multi in ((",", "comma", "dot"), (".", "dot", "comma")):
        if (has_c if sep == "," else has_d):
            if s.count(sep) > 1:
                return multi
            whole = s[:s.rfind(sep)]
            # a leading 0 group (0,125 / 0.125) is never a thousands group
            if len(s) - s.rfind(sep) - 1 == 3 and whole and whole.strip("0"):
                return "ambiguous"
            return single
    return "none"


def decimal_convention(values):
    """Settle the decimal mark over the FULL column (not a sample)."""
    ev = {"comma": 0, "dot": 0, "ambiguous": 0, "none": 0, "native": 0}
    for v in values:
        e = number_evidence(v)
        if e:
            ev[e] += 1
    if ev["comma"] and ev["dot"]:
        conv = "conflict"
    elif ev["comma"]:
        conv = "comma"
    elif ev["dot"]:
        conv = "dot"
    elif ev["ambiguous"]:
        conv = "ambiguous"
    elif ev["native"]:
        conv = "native"
    else:
        conv = "none"
    return conv, ev


def parse_number(raw, decimal="dot"):
    """Parse a raw cell into a float, or None if it is not a number.
    ``decimal`` is 'dot' or 'comma'. Percent signs are stripped; the caller
    decides the rate representation (data-quality-gate.md §3)."""
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, str):
        return None
    if raw.strip().lower() in NULL_TOKENS:
        return None
    s, neg, _ = _strip_number(raw)
    if not s or not _NUM_SHAPE.match(s):
        return None
    if decimal == "comma":
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def is_null(raw):
    return raw is None or (isinstance(raw, str) and raw.strip().lower() in NULL_TOKENS)


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------


def date_shape(raw):
    if isinstance(raw, str):
        return _date_shape_str(raw)
    return _date_shape(raw)


@functools.lru_cache(maxsize=65536)
def _date_shape_str(raw):
    return _date_shape(raw)


def _date_shape(raw):
    """Classify one raw value: ('iso'|'ymd'|'ab'|'month'|'compact'|'native', parts) or None."""
    if isinstance(raw, _dt.datetime):
        return "native", raw.date()
    if isinstance(raw, _dt.date):
        return "native", raw
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    m = _ISO.match(s)
    if m:
        return "iso", (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _YMD_SLASH.match(s)
    if m:
        return "ymd", (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _AB_YEAR.match(s)
    if m:
        return "ab", (int(m.group(1)), int(m.group(3)), int(m.group(4)), m.group(2))
    m = _YM.match(s)
    if m:
        return "month", (int(m.group(1)), int(m.group(2)))
    m = _COMPACT.match(s)
    if m:
        return "compact", (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _ISOWEEK.match(s)
    if m:
        return "isoweek", (int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))
    return None


def date_order(values):
    """Day/month order for a column of a.b.yyyy dates. Any first part > 12
    settles day-first, any second part > 12 settles month-first; neither is
    'ambiguous' (data-quality-gate.md §3). ISO and native dates are 'iso'."""
    kinds = {}
    max_a = max_b = 0
    seps = set()
    for v in values:
        sh = date_shape(v)
        if not sh:
            continue
        kinds[sh[0]] = kinds.get(sh[0], 0) + 1
        if sh[0] == "ab":
            a, b, _, sep = sh[1]
            max_a, max_b = max(max_a, a), max(max_b, b)
            seps.add(sep)
    if not kinds:
        return None, kinds
    if "ab" in kinds:
        if max_a > 12 and max_b > 12:
            order = "conflict"
        elif max_a > 12:
            order = "dmy"
        elif max_b > 12:
            order = "mdy"
        else:
            order = "ambiguous"
    elif set(kinds) == {"month"}:
        order = "month"
    else:
        order = "iso"
    return order, kinds


def parse_date(raw, order="iso"):
    """Parse one value into datetime.date (a yyyy-mm month becomes its 1st)."""
    sh = date_shape(raw)
    if not sh:
        return None
    kind, p = sh
    try:
        if kind == "native":
            return p
        if kind in ("iso", "ymd", "compact"):
            return _dt.date(p[0], p[1], p[2])
        if kind == "month":
            return _dt.date(p[0], p[1], 1)
        if kind == "isoweek":
            return _dt.date.fromisocalendar(p[0], p[1], p[2])  # ISO 8601 week, Monday first
        if kind == "ab":
            a, b, y, _ = p
            if order == "dmy":
                return _dt.date(y, b, a)
            if order == "mdy":
                return _dt.date(y, a, b)
            return None  # ambiguous: refuse to guess
    except ValueError:
        return None
    return None


# ---------------------------------------------------------------------------
# Typed column access shared by the analysis subcommands
# ---------------------------------------------------------------------------


class Typed:
    """A table plus resolved per-column decimal and date conventions.

    ``decimal`` / ``date_order`` override detection ('auto' detects). An
    ambiguous date order with 'auto' raises InputError when a date column is
    actually used, rather than picking one reading.
    """

    def __init__(self, table, decimal="auto", date_order_opt="auto"):
        self.t = table
        self.decimal_opt = decimal
        self.date_opt = date_order_opt
        self.warnings = list(table.meta.get("warnings") or [])
        self.unparsed = {}   # (column, "number"|"date") -> non-empty cells that did not parse
        self._dec = {}
        self._dord = {}
        file_ev = {"comma": 0, "dot": 0}
        for i, h in enumerate(table.headers):
            conv, ev = decimal_convention([r[i] for r in table.rows])
            self._dec[h] = conv
            file_ev["comma"] += ev["comma"]
            file_ev["dot"] += ev["dot"]
        if file_ev["comma"] and not file_ev["dot"]:
            self.file_decimal = "comma"
        elif file_ev["dot"] and not file_ev["comma"]:
            self.file_decimal = "dot"
        elif file_ev["dot"] and file_ev["comma"]:
            self.file_decimal = "conflict"
        else:
            self.file_decimal = "undetermined"

    def decimal_for(self, col):
        if self.decimal_opt in ("dot", "comma"):
            return self.decimal_opt
        conv = self._dec.get(col, "none")
        if conv in ("dot", "comma"):
            return conv
        if conv == "ambiguous":
            if self.file_decimal in ("dot", "comma"):
                return self.file_decimal
            w = ("column %r: every value has one separator followed by 3 digits; decimal "
                 "mark not settled by the data, read as thousands separator (pass --decimal "
                 "to override)" % col)
            if w not in self.warnings:
                self.warnings.append(w)
            return "comma" if self.t.meta.get("delimiter") == ";" else "dot"
        if conv == "conflict":
            raise InputError("column %r mixes decimal conventions; pass --decimal dot|comma" % col)
        return "dot"

    def order_for(self, col):
        if col in self._dord:
            return self._dord[col]
        i = self.t.col(col)
        order, _ = date_order([r[i] for r in self.t.rows])
        if order in ("ambiguous", "conflict"):
            if self.date_opt in ("dmy", "mdy"):
                order = self.date_opt
            else:
                raise InputError("column %r: day/month order is %s (no value above 12 settles it); "
                                 "pass --date-order dmy|mdy" % (col, order))
        self._dord[col] = order
        return order

    def numbers(self, col):
        i = self.t.col(col)
        dec = self.decimal_for(col)
        out = [parse_number(r[i], dec) for r in self.t.rows]
        self.unparsed[(col, "number")] = sum(1 for v, r in zip(out, self.t.rows)
                                             if v is None and not is_null(r[i]))
        return out

    def dates(self, col, record=True):
        """``record=False`` for an opportunistic read (is this a date column?)
        that must not count unreadable cells as dropped rows."""
        i = self.t.col(col)
        order = self.order_for(col)
        out = [parse_date(r[i], order) for r in self.t.rows]
        if record:
            self.unparsed[(col, "date")] = sum(1 for v, r in zip(out, self.t.rows)
                                               if v is None and not is_null(r[i]))
        return out

    def kind(self, col):
        """'date', 'number', 'text' or 'empty' by the 95% rule profile uses."""
        i = self.t.col(col)
        vals = [r[i] for r in self.t.rows if not is_null(r[i])]
        if not vals:
            return "empty"
        if sum(1 for v in vals if date_shape(v)) >= 0.95 * len(vals):
            return "date"
        if sum(1 for v in vals if number_evidence(v)) >= 0.95 * len(vals):
            return "number"
        return "text"

    def dropped(self, cols=None):
        """Non-empty cells that could not be read, per column: the rows they
        sit on were left out of the computation. Returns (warnings, note)."""
        warns, bits = [], []
        for (col, what), n in sorted(self.unparsed.items()):
            if n and (cols is None or col in cols):
                warns.append("column %r: %d non-empty cell(s) could not be read as a %s; "
                             "those rows were left out" % (col, n, what))
                bits.append("%d unreadable %s cell(s) in %s left out" % (n, what, col))
        return warns, ("; ".join(bits) or None)

    def texts(self, col):
        i = self.t.col(col)
        out = []
        for r in self.t.rows:
            v = r[i]
            if v is None:
                out.append(None)
            elif isinstance(v, (_dt.datetime, _dt.date)):
                out.append(v.isoformat()[:10])
            elif isinstance(v, float) and v.is_integer():
                out.append(str(int(v)))
            else:
                out.append(str(v).strip())
        return out
