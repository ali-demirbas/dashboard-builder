"""Calc trace: one JSON record per computed figure, and its renderer.

Record shape (one JSON object per line, appended to the trace file):

    {"id", "label", "value", "unit", "formula",
     "inputs": [{"file", "sheet", "column", "filter", "aggregation", "value"}],
     "method", "citation", "script", "version"}

No timestamp is written, so the same inputs always produce the same trace.
``file`` holds the basename only, never a local path. Values are stored at
full precision; ``render`` rounds for presentation only.
"""
import hashlib
import html
import json
import math
import os
import re

from . import SCRIPT, VERSION

CITATIONS = {
    "wilson1927": "Wilson, E. B. (1927). Probable inference, the law of succession, and statistical "
                  "inference. Journal of the American Statistical Association, 22(158), 209-212.",
    "newcombe1998": "Newcombe, R. G. (1998). Interval estimation for the difference between independent "
                    "proportions: comparison of eleven methods. Statistics in Medicine, 17(8), 873-890 "
                    "(method 10, hybrid score).",
    "fisher1935": "Fisher, R. A. (1935). The Design of Experiments. Oliver & Boyd (exact test on a 2x2 table).",
    "welch1947": "Welch, B. L. (1947). The generalization of 'Student's' problem when several different "
                 "population variances are involved. Biometrika, 34(1-2), 28-35.",
    "holm1979": "Holm, S. (1979). A simple sequentially rejective multiple test procedure. Scandinavian "
                "Journal of Statistics, 6(2), 65-70.",
    "fabijan2019": "Fabijan, A., Gupchup, J., Gupta, S., Omhover, J., Qin, W., Vermeer, L., Dmitriev, P. (2019). "
                   "Diagnosing Sample Ratio Mismatch in Online Controlled Experiments: A Taxonomy and Rules "
                   "of Thumb for Practitioners. KDD '19. doi:10.1145/3292500.3330722.",
    "pearson1900": "Pearson, K. (1900). On the criterion that a given system of deviations from the probable "
                   "... Philosophical Magazine, 50(302), 157-175.",
    "kitagawa1955": "Kitagawa, E. M. (1955). Components of a difference between two rates. Journal of the "
                    "American Statistical Association, 50(272), 1168-1194.",
    "playbook-sufficiency": "references/analysis-playbook.md §Statistical sufficiency.",
    "dqg-locale": "references/data-quality-gate.md §1 Structure and grain, §3 Validity (locale).",
    "dqg-period": "references/data-quality-gate.md §2 Completeness (covered period).",
    "dqg-cohort": "references/data-quality-gate.md §3 Right-censored cohort cells.",
    "dqg-anomaly": "references/data-quality-gate.md §5 Distributional (rolling-sigma scan with 7-day trend "
                   "window, 14-day test window, 3 sigma; same-weekday baseline over 4 prior weekdays).",
    "dqg-join": "references/data-quality-gate.md §1 Join Safety Gate.",
    "contribution": "Additive contribution of each segment to a total's change (delta and share of total "
                    "delta); references/analysis-playbook.md §Time-series analysis (concentration risk).",
    "arithmetic": "Direct arithmetic on supplied values.",
    "aggregate": "Plain aggregation of the supplied rows (sum, count, mean, min, max, ratio of sums), totals "
                 "rows excluded; references/data-quality-gate.md §1.",
}


def make_id(cmd, label, formula, inputs):
    blob = json.dumps([cmd, label, formula, inputs], sort_keys=True, ensure_ascii=False)
    return "%s:%s" % (cmd, hashlib.sha1(blob.encode("utf-8")).hexdigest()[:10])


def record(cmd, label, value, unit, formula, inputs, method, citation, note=None):
    inputs = [dict({"file": None, "sheet": None, "column": None, "filter": None,
                    "aggregation": None, "value": None}, **i) for i in inputs]
    if note:
        for i in inputs:
            if i.get("file"):
                i["note"] = note
    return {"id": make_id(cmd, label, formula, inputs), "label": label, "value": value,
            "unit": unit, "formula": formula, "inputs": inputs, "method": method,
            "citation": citation, "script": SCRIPT, "version": VERSION}


class TraceError(ValueError):
    """A trace file that cannot be rendered; reported as a JSON error."""


def append(path, records):
    """Append records, skipping any whose exact line is already in the file
    (re-running the same command, e.g. profile twice, adds nothing)."""
    if not path or not records:
        return 0
    seen = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            seen = {ln.strip() for ln in fh if ln.strip()}
    n = 0
    with open(path, "a", encoding="utf-8") as fh:
        for r in records:
            line = json.dumps(r, ensure_ascii=False, sort_keys=True)
            if line in seen:
                continue
            seen.add(line)
            fh.write(line + "\n")
            n += 1
    return n


_SCALAR = (str, int, float, bool, type(None))


def _valid_value(v):
    if isinstance(v, _SCALAR):
        return True
    return isinstance(v, list) and all(isinstance(x, _SCALAR) for x in v)


def read(path):
    """Read and validate a trace file. A hand-written row needs at least
    ``id`` and ``label``; ``value`` must be a number, string, boolean, null
    or a list of those."""
    if os.path.isdir(path):
        raise TraceError("%s is a directory, not a trace file" % os.path.basename(path.rstrip("/")))
    if not os.path.exists(path):
        raise TraceError("trace file not found: %s" % os.path.basename(path))
    out = {}
    order = []
    problems = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                problems.append("line %d: not valid JSON" % n)
                continue
            if not isinstance(r, dict):
                problems.append("line %d: a trace row is a JSON object" % n)
                continue
            miss = [k for k in ("id", "label") if not r.get(k)]
            if miss:
                problems.append("line %d: missing %s (a hand-written row needs at least "
                                "{\"id\": \"hand:<slug>\", \"label\": ..., \"value\": ...})"
                                % (n, " and ".join(miss)))
                continue
            if not _valid_value(r.get("value")):
                problems.append("line %d: value must be a number, string, boolean, null or a list of "
                                "those, not %s" % (n, type(r.get("value")).__name__))
                continue
            if r.get("inputs") is not None and not (isinstance(r["inputs"], list)
                                                    and all(isinstance(i, dict) for i in r["inputs"])):
                problems.append("line %d: inputs must be a list of objects" % n)
                continue
            if r["id"] not in out:
                order.append(r["id"])
            out[r["id"]] = r  # last write wins for a re-computed figure
    if problems:
        raise TraceError("%s cannot be rendered: %s" % (os.path.basename(path), "; ".join(problems[:10])))
    return [out[i] for i in order]


def _sig_decimals(x, sig=3, floor=1, cap=8):
    """Decimals that show at least ``sig`` significant digits, never fewer
    than ``floor``: a nonzero value never renders as 0.0 or 0.00."""
    if x == 0 or not math.isfinite(x):
        return floor
    mag = int(math.floor(math.log10(abs(x))))
    return max(floor, min(cap, sig - 1 - mag))


def _group(int_part, sep):
    return "{:,}".format(int_part).replace(",", sep)


def _num(x, dec, lang):
    s = ("%." + str(dec) + "f") % abs(x)
    whole, _, frac = s.partition(".")
    tsep, dsep = (".", ",") if lang == "tr" else (",", ".")
    out = _group(int(whole), tsep) + ((dsep + frac) if frac else "")
    return ("-" if x < 0 and float(s) != 0 else "") + out


TEXT = {
    "en": {"title": "How each number was computed",
           "head": ("#", "Figure", "Value", "Unit", "Formula", "Inputs", "Method"),
           "cited": "Methods cited", "yes": "yes", "no": "no", "pp": "pp",
           "footer": "Computed by %s %s; values rounded for display only."},
    "tr": {"title": "Her rakam nasıl hesaplandı",
           "head": ("#", "Rakam", "Değer", "Birim", "Formül", "Girdiler", "Yöntem"),
           "cited": "Kaynak gösterilen yöntemler", "yes": "Evet", "no": "Hayır", "pp": "puan",
           "footer": "%s %s ile hesaplandı; değerler yalnızca gösterim için yuvarlandı."},
}


def fmt_value(v, unit=None, digits=4, lang="en"):
    """Display form. Label tokens and other strings pass through unchanged
    (they stay in English in every language); None is "Not meaningful"."""
    t = TEXT[lang]
    if v is None:
        return "Not meaningful"
    if isinstance(v, bool):
        return t["yes"] if v else t["no"]
    if isinstance(v, str):
        return v
    if isinstance(v, (list, tuple)):
        return "[" + "; ".join(fmt_value(x, None, digits, lang) for x in v) + "]"
    if not isinstance(v, (int, float)) or not math.isfinite(v):
        return "Not meaningful"
    if unit in ("pp",):
        x = v * 100
        s = _num(x, _sig_decimals(x), lang)
        sign = "+" if x > 0 else ""
        return "%s%s %s" % (sign, s, t["pp"])
    if unit in ("share", "rate", "proportion"):
        x = v * 100
        s = _num(x, _sig_decimals(x), lang)
        return ("%" + s) if lang == "tr" else (s + "%")
    if float(v).is_integer() and abs(v) < 1e15:
        return _num(float(v), 0, lang)
    if abs(v) >= 1000:
        return _num(v, 2, lang)
    if v == 0:
        return "0"
    mag = int(math.floor(math.log10(abs(v))))
    dec = max(0, digits - 1 - mag)
    return _num(v, min(dec, 8), lang)


def _inputs_text(inputs, lang="en"):
    parts = []
    for i in inputs:
        src = i.get("file") or ""
        if i.get("sheet"):
            src += "[%s]" % i["sheet"]
        bits = [b for b in (src, i.get("column"), i.get("filter"), i.get("aggregation")) if b]
        txt = " · ".join(str(b) for b in bits)
        if i.get("value") is not None:
            txt += (" = " if txt else "") + fmt_value(i["value"], None, 4, lang)
        if i.get("note"):
            txt += " (%s)" % i["note"]
        if txt:
            parts.append(txt)
    return "; ".join(parts)


TITLE = TEXT["en"]["title"]


def anchor(rid):
    """HTML id of a trace row: calc-<command>-<hash> (the record id with ':'
    replaced by '-'), so a footnote marker can link to #calc-<...>."""
    return "calc-" + re.sub(r"[^A-Za-z0-9_-]", "-", str(rid))


def render(records, fmt="md", lang="en"):
    if lang not in TEXT:
        raise ValueError("lang must be en or tr")
    t = TEXT[lang]
    rows = []
    cites = []
    for n, r in enumerate(records, 1):
        c = r.get("citation")
        if c and c not in cites:
            cites.append(c)
        rows.append((r["id"], (str(n), str(r["label"]), fmt_value(r.get("value"), r.get("unit"), 4, lang),
                               str(r.get("unit") or ""), str(r.get("formula") or ""),
                               _inputs_text(r.get("inputs") or [], lang),
                               "%s [%s]" % (r.get("method") or "", c) if c else str(r.get("method") or ""))))
    head = t["head"]
    footer = t["footer"] % (SCRIPT, VERSION)
    if fmt == "md":
        def cell(s):
            return s.replace("|", "\\|").replace("\n", " ")
        lines = ["## " + t["title"], "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        lines += ["| " + " | ".join(cell(x) for x in row) + " |" for _, row in rows]
        if cites:
            lines += ["", "**%s**" % t["cited"], ""]
            lines += ["- [%s] %s" % (c, CITATIONS.get(c, c)) for c in cites]
        lines += ["", "_%s_" % footer]
        return "\n".join(lines) + "\n"
    if fmt == "html":
        e = html.escape
        out = ['<section class="calc-trace" aria-labelledby="calc-trace-title"%s>'
               % (' lang="tr"' if lang == "tr" else ""),
               '<h2 id="calc-trace-title">%s</h2>' % e(t["title"]),
               '<table><thead><tr>' + "".join("<th scope=\"col\">%s</th>" % e(h) for h in head)
               + "</tr></thead><tbody>"]
        for rid, row in rows:
            out.append('<tr id="%s">' % e(anchor(rid)) + "".join("<td>%s</td>" % e(x) for x in row) + "</tr>")
        out.append("</tbody></table>")
        if cites:
            out.append("<h3>%s</h3><ul>" % e(t["cited"]))
            out += ["<li>[%s] %s</li>" % (e(c), e(CITATIONS.get(c, c))) for c in cites]
            out.append("</ul>")
        out.append("<p><small>%s</small></p>" % e(footer))
        out.append("</section>")
        return "\n".join(out) + "\n"
    raise ValueError("format must be md or html")
