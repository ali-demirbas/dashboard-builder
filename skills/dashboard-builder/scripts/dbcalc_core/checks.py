"""Row- and column-level detectors shared by the subcommands.

- Totals/subtotal rows: references/data-quality-gate.md §1 (first check,
  before the grain test and before any aggregation).
- Identifier-like columns and PII/credential patterns:
  data-quality-gate.md §Handling PII. Detectors return counts and row
  numbers only, never the matched values.
- Instruction-like text in cells: data-quality-gate.md §Untrusted input.
"""
import re
import unicodedata

TOTAL_LABEL = re.compile(
    r"^\s*(grand\s*total|total|totals|sub\s*-?\s*total|overall|all\s+campaigns|all\s+channels|"
    r"sum|toplam|genel\s+toplam|ara\s+toplam|tümü|hepsi)\s*[:.]?\s*$", re.I)
BUCKET_LABEL = re.compile(r"^\s*(\(other\)|other|others|diğer|\(not set\))\s*$", re.I)

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w])(?:\+\d{1,3}[\s.-]?)?(?:\(?0?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?![\w])")
UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
CREDENTIAL = re.compile(
    r"(sk_live_[0-9A-Za-z]{8,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[abposr]-[0-9A-Za-z-]{10,}|"
    r"Bearer\s+[A-Za-z0-9\-_.=]{20,}|api[_-]?key\s*[:=]\s*\S{8,}|AIza[0-9A-Za-z\-_]{30,}|"
    r"(?:postgres|mysql|mongodb)(?:\+srv)?://\S+:\S+@)", re.I)
# Matched against the folded text (see _fold: Turkish dotted/dotless i and
# diacritics removed, casefolded), so the Turkish phrases are written folded.
INSTRUCTION = re.compile(
    r"\b(ignore|disregard|forget|override|skip)\s+(all\s+|any\s+|the\s+|your\s+|of\s+|everything\s+|anything\s+)*"
    r"(previous|prior|above|earlier|preceding|former|system)\b"
    r"|\b(ignore|disregard|forget)\s+(all\s+|any\s+|your\s+|these\s+|the\s+)*(instructions|rules|prompts?)\b"
    r"|\bsystem\s+(message|prompt|instruction)s?\b"
    r"|\byou\s+are\s+(now|no\s+longer|an?\s+(ai|assistant|chatbot|language\s+model|llm)|"
    r"the\s+(assistant|system|model))\b"
    r"|\bact\s+as\s+(an?\s+|the\s+)?(ai|assistant|system|admin)"
    r"|\b(always|now)\s+(output|report|answer|respond|reply|say)\b"
    r"|\b(report|output|state|show|write|say)\s+(\S+\s+){1,3}as\s+[$\u20ac\u00a3\u20ba]?\d"
    r"|\bnew\s+instructions?\s*:"
    r"|\b(onceki|yukaridaki|eski)\s+(tum\s+)?(talimat|komut|yonerge|mesaj)\w*"
    r"|\b(talimat|komut|yonerge)\w*\s+(\w+\s+){0,3}(yok\s+say|unut|gormezden\s+gel|dikkate\s+alma)\w*"
    r"|\b(yok\s+say|gormezden\s+gel)\w*\s+(\w+\s+){0,2}(talimat|komut|yonerge)\w*"
    r"|\bsistem\s+(mesaji|istemi|talimati)\b"
    r"|\bsen\s+artik\b"
    r"|\b(her\s+zaman|daima)\s+(\S+\s+){0,3}(yaz|soyle|raporla|goster)\b", re.I)


def is_instruction_like(text):
    """Instruction-like text in a data cell (data-quality-gate.md §Untrusted
    input). Matched on folded text so Turkish casing and diacritics do not
    hide a phrase. Deliberately broad: a false positive only withholds a
    label from printing."""
    return isinstance(text, str) and bool(INSTRUCTION.search(_fold(text[:MAX_SCAN])))

_ID_TOKENS = {
    "email", "mail", "eposta", "phone", "telephone", "tel", "gsm", "msisdn", "mobile", "cep", "telefon",
    "surname", "soyad", "soyadi", "isim", "firstname", "lastname", "fullname", "customer", "musteri",
    "user", "userid", "uid", "deviceid", "idfa", "idfv", "gaid", "adid", "aaid", "advertising",
    "transaction", "txn", "txid", "ip", "address", "adres", "tckn", "ssn", "iban", "token", "apikey",
    "secret", "password", "sifre", "member", "contact", "lead", "visitor", "client", "subscriber",
}
_ID_SUFFIX = {"id", "no", "nr", "number", "num", "numarasi", "code", "kodu", "ref"}
_ID_PREFIX = {"device", "cihaz", "order", "siparis", "invoice", "fatura", "payment", "odeme", "account", "hesap", "session"}
_DIM_TOKENS = {"campaign", "kampanya", "channel", "kanal", "product", "urun", "ad", "adset", "adgroup",
               "creative", "page", "event", "segment", "source", "medium", "platform", "country",
               "template", "sheet", "list", "group", "count", "total", "sayisi", "adet", "rate"}


_NAME_JOINED = {"adsoyad", "adisoyadi", "adsoyadi", "isimsoyisim", "isimsoyad", "fullname", "namesurname",
                "firstname", "lastname", "givenname", "familyname", "surname", "soyad", "soyadi", "soyisim",
                "musteriadi", "musteriadisoyadi", "musteriismi", "customername", "clientname", "contactname",
                "username", "kullaniciadi", "uyeadi", "personname", "kisiadi"}
_STRONG_ID = {"email", "mail", "eposta", "phone", "telephone", "tel", "gsm", "msisdn", "telefon", "tckn",
              "ssn", "iban", "password", "sifre", "apikey", "idfa", "idfv", "gaid", "aaid"}
_METRIC_SUFFIX = {"count", "sayisi", "adet", "total", "number", "num", "new", "active", "returning", "rate",
                  "sends", "sent", "opens", "open", "clicks", "click", "delivered", "bounces", "bounce",
                  "unsubscribes", "orani", "share", "pct"}


def _fold(s):
    s = s.replace("İ", "I").replace("ı", "i")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


def header_tokens(h):
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", h)
    return [t for t in re.split(r"[^a-z0-9]+", _fold(s)) if t]


def identifier_reason_from_header(h):
    toks = header_tokens(h)
    joined = "".join(toks)
    if not toks:
        return None
    # joined person-name forms first ("Ad Soyad", "ad_soyad", "full name",
    # "müşteri adı"): their parts ("ad", "name") also read as dimension tokens
    for i in range(len(toks)):
        for j in range(i + 1, min(len(toks), i + 3) + 1):
            if "".join(toks[i:j]) in _NAME_JOINED and not (set(toks[j:]) & _METRIC_SUFFIX):
                return "header"
    metricish = set(toks) & (_METRIC_SUFFIX - {"number", "num"})
    for i in range(len(toks)):
        for j in range(i + 2, min(len(toks), i + 2) + 1):
            if "".join(toks[i:j]) in _STRONG_ID:  # "e-posta", "e_mail"
                return None if metricish else "header"
    if set(toks) & _STRONG_ID:
        return None if metricish else "header"
    if set(toks) & _DIM_TOKENS and not (set(toks) & {"email", "mail", "eposta", "phone", "tel", "gsm"}):
        return None
    if joined in ("id", "name", "ad", "adsoyad", "namesurname"):
        return "header"
    if set(toks) & _ID_PREFIX and set(toks) & _ID_SUFFIX:
        return "header"
    hit = set(toks) & _ID_TOKENS
    if hit:
        # counts of customers/users/orders are metrics, not identifiers
        if set(toks) & {"count", "sayisi", "adet", "total", "number", "num", "new", "active", "returning"} \
                and not (hit & {"email", "mail", "phone", "token", "password"}):
            return None
        if toks[-1] in ("count", "s") or joined.endswith("count"):
            return None
        return "header"
    if "name" in toks:
        return "header"
    return None


MAX_SCAN = 4096
_PLAIN_NUMBER = re.compile(r"\s*[-+]?[\d.,]+\s*")


def value_patterns(values):
    """Counts of PII/credential/instruction patterns over raw string values.
    ``rows`` holds 0-based positions in ``values`` of instruction-like cells."""
    c = {"email": 0, "phone": 0, "uuid": 0, "credential": 0, "instruction_like": 0}
    rows = {"instruction_like": []}
    memo = {}
    for i, v in enumerate(values):
        if not isinstance(v, str) or not v.strip():
            continue
        if v in memo:  # repeated labels: same verdict, counted again
            hit = memo[v]
            for k in hit:
                c[k] += 1
            if "instruction_like" in hit:
                rows["instruction_like"].append(i)
            continue
        if _PLAIN_NUMBER.fullmatch(v) and v.strip()[0] not in "+0":
            continue
        before = dict(c)
        key = v
        v = v[:MAX_SCAN]  # the patterns are linear per start position; a 200k-char cell would be quadratic
        if EMAIL.search(v):
            c["email"] += 1
        if PHONE.search(v) and not re.fullmatch(r"[\d.,\s]+", v.strip()):
            c["phone"] += 1
        elif re.fullmatch(r"\+?0?\d{10,13}", v.strip()) and v.strip()[0] in "+0":
            c["phone"] += 1
        if UUID.search(v):
            c["uuid"] += 1
        if CREDENTIAL.search(v):
            c["credential"] += 1
        if is_instruction_like(v):
            c["instruction_like"] += 1
            rows["instruction_like"].append(i)
        if len(memo) < 100000:
            memo[key] = [k for k in c if c[k] != before[k]]
    return c, rows


def scrub(text, limit=80):
    """Text safe to print: PII and credentials redacted, instruction-like text withheld."""
    text = text[: max(limit * 4, 256)]
    if is_instruction_like(text):
        return "[instruction-like text withheld]"
    text = EMAIL.sub("[redacted:email]", text)
    text = CREDENTIAL.sub("[redacted:credential]", text)
    text = UUID.sub("[redacted:id]", text)
    text = PHONE.sub("[redacted:phone]", text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def total_rows(label_cols, numeric_cols, group_col=None):
    """Detect totals/subtotal rows.

    label_cols: {name: [str|None per row]} — dimension/label columns.
    numeric_cols: {name: [float|None per row]}.
    group_col: optional list of group keys (e.g. the date) for subtotal-per-group.
    Returns a sorted list of {row, reason, column} with 1-based data row numbers.
    """
    n = len(next(iter(numeric_cols.values()))) if numeric_cols else (
        len(next(iter(label_cols.values()))) if label_cols else 0)
    found = {}
    for name, vals in label_cols.items():
        for i, v in enumerate(vals):
            if v and TOTAL_LABEL.match(v):
                found.setdefault(i, {"row": i + 1, "reason": "total_label", "column": name})
    # blank dimension values with populated metrics, when other rows have them
    if label_cols and numeric_cols:
        populated_dims = [i for i in range(n) if any(vals[i] for vals in label_cols.values())]
        if len(populated_dims) >= max(2, n // 2):
            for i in range(n):
                if i in found:
                    continue
                if not any(vals[i] for vals in label_cols.values()) and any(
                        vals[i] not in (None, 0.0) for vals in numeric_cols.values()):
                    found[i] = {"row": i + 1, "reason": "blank_dimensions_with_metrics", "column": None}
    # rows equal to the sum of all other rows (whole file), then per group
    cols = [v for v in numeric_cols.values()]

    need = 2 if len(cols) >= 2 else 1

    def sum_rows(idx, label):
        if len(idx) < (3 if need == 2 else 4) or not cols:
            return
        sums = [sum(c[i] or 0.0 for i in idx if i not in found) for c in cols]
        for i in idx:
            if i in found:
                continue
            checked = 0
            ok = True
            for c, s in zip(cols, sums):
                v = c[i]
                if v is None or v == 0:
                    continue
                checked += 1
                other = s - v
                if abs(v - other) > max(0.05, 1e-4 * abs(other)):
                    ok = False
                    break
            if ok and checked >= need:
                found[i] = {"row": i + 1, "reason": label, "column": None}
                return  # one aggregate row per scope

    sum_rows(list(range(n)), "equals_sum_of_other_rows")
    if group_col is not None:
        groups = {}
        for i, g in enumerate(group_col):
            if g is not None:
                groups.setdefault(g, []).append(i)
        for g in sorted(groups, key=str):
            sum_rows(groups[g], "equals_sum_of_other_rows_in_group")
    return [found[i] for i in sorted(found)]


def bucket_rows(label_cols):
    out = []
    for name, vals in label_cols.items():
        for i, v in enumerate(vals):
            if v and BUCKET_LABEL.match(v):
                out.append({"row": i + 1, "column": name})
    return out


def looks_categorical(v, max_len=40, max_words=5):
    """A short label (campaign, channel, device) safe to print as a sample
    value. Long or sentence-like free text is never printed: it can carry
    personal data or instructions the patterns above do not know."""
    v = v.strip()
    if len(v) > max_len or len(v.split()) > max_words:
        return False
    if re.search(r"[.!?;:]\s+\S", v) or "\n" in v:
        return False
    return not is_instruction_like(v)


def guard_dimension(name, texts, what="dimension"):
    """Refuse to group by (and so print values of) an identifier-like column:
    by its header, or when most values are e-mails, phone numbers or UUIDs
    (data-quality-gate.md §Handling PII)."""
    from .tabular import InputError
    if identifier_reason_from_header(name):
        raise InputError("%s %r looks like an identifier column (by its header); this command runs on "
                         "aggregate dimensions only and would print its values" % (what, name))
    strs = [t for t in texts if t]
    if strs:
        pats, _ = value_patterns(strs)
        for k in ("email", "phone", "uuid"):
            if pats[k] >= max(1, 0.5 * len(strs)):
                raise InputError("%s %r holds %s values in most rows; this command runs on aggregate "
                                 "dimensions only and would print them" % (what, name, k))


AGG_HINT = re.compile(r"(^|[^a-z0-9])(grand\s*total|sub\s*-?\s*total|totals?|all|overall|sum|toplam|"
                      r"tumu|hepsi|genel|butun|tum)([^a-z0-9]|$)")


def segment_exclusions(label_cols, numeric_cols, period_keys, exclude_labels=None):
    """Rows to leave out of a per-segment computation (drivers, decompose).

    - TOTAL_LABEL rows and whole-file "equals the sum of the other rows" rows
      (``total_rows``);
    - per-period subtotals: a row equal to the sum of the other rows of its
      period (every numeric column, nonzero ones checked). Accepted when its
      label reads like an aggregate ("Paid total", "All devices", "Toplam"),
      when two or more numeric columns match, or when the same label is the
      sum in every period it appears in (two or more periods) — a single
      coincidence on one column (300 = 100 + 200) is not enough;
    - labels named by the caller (``--exclude-rows``).

    A row with blank dimensions that is NOT a sum stays in as its own
    "(blank)" segment (kpi-framework.md §8: an (other)/(not set) bucket stays
    in). Returns (excluded: {row index: reason}, kept_blank_rows: int).
    """
    n = len(next(iter(numeric_cols.values()))) if numeric_cols else 0
    excluded = {}
    for t in total_rows(label_cols, numeric_cols):
        if t["reason"] != "blank_dimensions_with_metrics":
            excluded[t["row"] - 1] = t["reason"]
    wanted = {_fold(x).strip() for x in (exclude_labels or []) if x and x.strip()}
    if wanted:
        for vals in label_cols.values():
            for i, v in enumerate(vals):
                if v and _fold(v).strip() in wanted:
                    excluded.setdefault(i, "excluded_by_flag")
    cols = list(numeric_cols.values())
    groups = {}
    for i, g in enumerate(period_keys):
        if g is not None:
            groups.setdefault(g, []).append(i)

    def label_of(i):
        return " / ".join((v[i] or "(blank)") for v in label_cols.values())

    hits = {}      # label -> periods where the row is the sum of the others
    appear = {}    # label -> periods where it appears
    strong = set()
    for g, idx in groups.items():
        live = [i for i in idx if i not in excluded]
        for i in live:
            appear.setdefault(label_of(i), set()).add(g)
        if len(live) < 3:
            continue
        sums = [sum(c[i] or 0.0 for i in live) for c in cols]
        for i in live:
            checked, ok = 0, True
            for c, tot in zip(cols, sums):
                v = c[i]
                if v is None or v == 0:
                    continue
                checked += 1
                if abs(v - (tot - v)) > max(0.05, 1e-4 * abs(tot - v)):
                    ok = False
                    break
            if ok and checked:
                hits.setdefault(label_of(i), set()).add(g)
                if checked >= 2:
                    strong.add((label_of(i), g))
    for g, idx in groups.items():
        for i in idx:
            if i in excluded:
                continue
            lab = label_of(i)
            if g not in hits.get(lab, ()):
                continue
            hint = bool(AGG_HINT.search(_fold(lab))) or lab.replace("(blank)", "").strip(" /") == ""
            consistent = len(appear.get(lab, ())) >= 2 and hits[lab] == appear[lab]
            if hint or consistent or (lab, g) in strong:
                excluded[i] = "period_subtotal"
    kept_blank = sum(1 for i in range(n) if i not in excluded
                     and not any(v[i] for v in label_cols.values()))
    return excluded, kept_blank
