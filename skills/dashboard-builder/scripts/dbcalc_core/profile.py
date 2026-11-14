"""`profile`: structure, locale, grain, totals rows, period echo, PII flags.

Implements the mechanical part of references/data-quality-gate.md §1
(totals/subtotal rows first, grain test over 2-3 candidate keys, multi-sheet
workbooks incl. hidden sheets), §2 (covered period: first/last date actually
present), §3 (locale: delimiter, decimal mark over the full column, day/month
order) and §Handling PII (identifier-like columns reported by count and type,
never by value), plus analysis-playbook.md §Ingestion (header not on row 1,
duplicate headers, non-UTF-8 fallback).
"""
import math
import datetime as _dt
import itertools
import os

from . import checks, tabular

MAX_KEY_COLS = 8
MAX_KEY_SIZE = 3
LOW_CARD = 30


LARGE_FILE_BYTES = 20 * 1024 * 1024


def _col_profile(tbl, typed, i, h, hidden=False):
    raw = [r[i] for r in tbl.rows]
    nonnull = [v for v in raw if not tabular.is_null(v)]
    n_null = len(raw) - len(nonnull)
    info = {"name": h, "nulls": n_null,
            "null_rate": (n_null / len(raw)) if raw else None}
    typable = [v for v in nonnull if not (isinstance(v, str) and checks.TOTAL_LABEL.match(v))]
    order, kinds = tabular.date_order(typable)
    date_hits = sum(kinds.values()) if kinds else 0
    conv, ev = tabular.decimal_convention(nonnull)
    num_hits = sum(ev[k] for k in ("comma", "dot", "ambiguous", "none", "native"))
    pct = any(tabular.has_percent(v) for v in nonnull)
    if typable and date_hits >= 0.95 * len(typable) and date_hits >= num_hits:
        info["type"] = "month" if order == "month" else "date"
        info["date_order"] = order
    elif nonnull and num_hits >= 0.95 * len(nonnull):
        info["decimal"] = conv
        if conv in ("comma", "dot", "conflict"):
            dec = "comma" if conv == "comma" else "dot"
        else:
            dec = typed.decimal_for(h) if conv == "ambiguous" else "dot"
        vals = [tabular.parse_number(v, dec) for v in nonnull]
        vals = [v for v in vals if v is not None]
        info["type"] = "percent" if pct else (
            "integer" if vals and all(float(v).is_integer() for v in vals) else "decimal")
        info["numeric_parse_failures"] = len(nonnull) - len(vals)
        info["_values"] = [tabular.parse_number(v, dec) for v in raw]
    else:
        info["type"] = "text" if nonnull else "empty"
    strs = [v for v in nonnull if isinstance(v, str)]
    pats, rows = checks.value_patterns(strs)
    reason_h = checks.identifier_reason_from_header(h)
    reasons = []
    if reason_h:
        reasons.append("header")
    for k in ("email", "phone", "uuid"):
        if pats[k] and pats[k] >= max(1, 0.5 * len(strs)):
            reasons.append("values:" + k)
    info["identifier_like"] = bool(reasons)
    if reasons:
        info["identifier_reasons"] = reasons
    info["pattern_counts"] = {k: v for k, v in pats.items() if v}
    distinct = len({str(v).strip() for v in nonnull})
    info["distinct"] = distinct
    if info["type"] == "text" and not info["identifier_like"] and distinct <= LOW_CARD:
        vals = sorted({str(v).strip() for v in nonnull})
        if hidden:
            info["values_withheld"] = {"count": len(vals), "reason": "hidden sheet: values never printed"}
        else:
            short = [v for v in vals if checks.looks_categorical(v)]
            if short:
                info["values"] = [checks.scrub(v) for v in short]
            if len(short) < len(vals):
                info["values_withheld"] = {"count": len(vals) - len(short),
                                           "reason": "long or sentence-like free text is not printed"}
    elif info["type"] == "text" and not info["identifier_like"]:
        info["values_withheld"] = {"count": distinct, "reason": "more than %d distinct values" % LOW_CARD}
    return info


def _date_summary(typed, h, order):
    try:
        ds = typed.dates(h)
    except tabular.InputError as e:
        return {"column": h, "order": order, "period": None, "note": str(e),
                "readings": _both_readings(typed, h)}
    present = sorted({d for d in ds if d is not None})
    if not present:
        return {"column": h, "order": order, "period": None}
    fmt = (lambda d: d.isoformat()[:7]) if order == "month" else (lambda d: d.isoformat())
    out = {"column": h, "order": order,
           "period": {"first": fmt(present[0]), "last": fmt(present[-1])},
           "distinct_dates": len(present)}
    if order != "month":
        span = (present[-1] - present[0]).days + 1
        missing = []
        if len(present) >= 2:
            have = set(present)
            d = present[0]
            while d <= present[-1]:
                if d not in have:
                    missing.append(d.isoformat())
                d += _dt.timedelta(days=1)
        out["span_days"] = span
        out["missing_dates_in_span"] = len(missing)
        out["missing_dates_sample"] = missing[:10]
        weekdays = sorted({d.weekday() for d in present})
        out["weekdays_present"] = len(weekdays)
    return out


def _both_readings(typed, h):
    i = typed.t.col(h)
    res = {}
    for order in ("dmy", "mdy"):
        ds = sorted({d for d in (tabular.parse_date(r[i], order) for r in typed.t.rows) if d})
        res[order] = {"first": ds[0].isoformat(), "last": ds[-1].isoformat()} if ds else None
    return res


def _grain(tbl, typed, cols, excluded):
    cand = []
    for c in cols:
        if c["type"] in ("date", "month"):
            cand.append((0, c["distinct"], c["name"]))
    for c in cols:
        if c["type"] == "text" and (c["distinct"] < len(tbl.rows) or c["identifier_like"]):
            cand.append((1, c["distinct"], c["name"]))
        elif c["type"] == "text" and c["distinct"] == len(tbl.rows):
            cand.append((2, c["distinct"], c["name"]))
    for c in cols:
        if c["type"] == "integer":
            toks = set(checks.header_tokens(c["name"]))
            if toks & {"id", "no", "week", "month", "year", "day", "offset", "cohort", "hafta", "ay", "gun"}:
                cand.append((3, c["distinct"], c["name"]))
    cand = [name for _, _, name in sorted(cand)][:MAX_KEY_COLS]
    keep = [k for k in range(len(tbl.rows)) if k not in excluded]
    texts = {c: typed.texts(c) for c in cand}
    types = {c["name"]: c for c in cols}
    tested, holding = [], []
    for size in range(1, MAX_KEY_SIZE + 1):
        for combo in itertools.combinations(cand, size):
            if any(set(h) <= set(combo) for h in holding):
                continue
            seen = {}
            null_keys = 0
            for k in keep:
                key = tuple(texts[c][k] for c in combo)
                if any(v in (None, "") for v in key):
                    null_keys += 1
                    continue
                seen[key] = seen.get(key, 0) + 1
            dup_groups = sum(1 for v in seen.values() if v > 1)
            dup_rows = sum(v for v in seen.values() if v > 1)
            rec = {"key": list(combo), "unique": dup_groups == 0 and null_keys == 0,
                   "duplicate_groups": dup_groups, "rows_in_duplicate_groups": dup_rows,
                   "null_keys": null_keys}
            if size == 1 and dup_groups and types[combo[0]]["type"] in ("date", "month"):
                rec["duplicated_values"] = sorted(k[0] for k, v in seen.items() if v > 1)[:20]
            tested.append(rec)
            if rec["unique"]:
                holding.append(combo)
    return {"candidate_columns": cand, "tested": tested,
            "holding": [list(h) for h in holding],
            "note": "keys tested on rows excluding detected totals rows"}


def profile_table(tbl, hidden=False):
    typed = tabular.Typed(tbl)
    cols = [_col_profile(tbl, typed, i, h, hidden) for i, h in enumerate(tbl.headers)]
    label_cols = {c["name"]: typed.texts(c["name"]) for c in cols
                  if c["type"] == "text" and not c["identifier_like"]}
    measure_cols = {c["name"]: c["_values"] for c in cols
                    if c.get("_values") is not None and not c["identifier_like"]
                    and "id" not in checks.header_tokens(c["name"])}
    date_cols = [c for c in cols if c["type"] in ("date", "month")]
    group = None
    if date_cols:
        try:
            group = typed.dates(date_cols[0]["name"])
        except tabular.InputError:
            group = typed.texts(date_cols[0]["name"])
    dim_cols = dict(label_cols)
    for c in date_cols:
        dim_cols[c["name"]] = typed.texts(c["name"])
    totals = checks.total_rows(dim_cols, measure_cols, group)
    excluded = {t["row"] - 1 for t in totals}
    for t in totals:
        t[tbl.locator()] = tbl.lines[t["row"] - 1]
    for t in totals:
        if t["reason"] == "total_label":
            i = t["row"] - 1
            comp = []
            for name, vals in measure_cols.items():
                v = vals[i]
                if v is None:
                    continue
                s = math.fsum(x or 0.0 for k, x in enumerate(vals) if k not in excluded)
                comp.append({"column": name, "stated": v, "sum_of_rows": s,
                             "matches": abs(v - s) <= max(0.05, 1e-4 * abs(s))})
            t["stated_vs_rows"] = comp
    # measure sums excluding totals rows (for cross-sheet comparison)
    sums = {name: math.fsum(v or 0.0 for k, v in enumerate(vals) if k not in excluded)
            for name, vals in measure_cols.items()}
    for c in cols:
        vals = c.get("_values")
        if vals is not None and not c["identifier_like"]:
            vv = [v for k, v in enumerate(vals) if v is not None and k not in excluded]
            if vv:
                c["min"], c["max"], c["sum_excl_totals"] = min(vv), max(vv), math.fsum(vv)
    exact_dups = 0
    seen = {}
    for r in tbl.rows:
        key = tuple("" if v is None else str(v) for v in r)
        seen[key] = seen.get(key, 0) + 1
    exact_dups = sum(v - 1 for v in seen.values() if v > 1)
    instr = []
    cred = []
    pii_other = []
    for c in cols:
        pc = c["pattern_counts"]
        if pc.get("instruction_like"):
            i = tbl.headers.index(c["name"])
            where = [tbl.lines[k] for k, r in enumerate(tbl.rows) if checks.is_instruction_like(r[i])]
            instr.append({"column": c["name"], "cells": pc["instruction_like"],
                          ("lines" if tbl.locator() == "line" else tbl.locator() + "s"): where[:20]})
        if pc.get("credential"):
            cred.append({"column": c["name"], "cells": pc["credential"]})
        if not c["identifier_like"] and (pc.get("email") or pc.get("phone")):
            pii_other.append({"column": c["name"], "email_cells": pc.get("email", 0),
                              "phone_cells": pc.get("phone", 0)})
    for c in cols:
        c.pop("_values", None)
        if c["identifier_like"]:
            for k in ("min", "max", "sum_excl_totals", "values"):
                c.pop(k, None)
    out = {
        "sheet": tbl.name,
        "header_row": tbl.meta.get("header_row"),
        "header_" + tbl.locator(): tbl.meta.get("header_line"),
        "row_locator": {"line": "line numbers are lines of the source file (1 = first line)",
                        "sheet_row": "sheet_row numbers are worksheet row numbers",
                        "record": "record numbers count JSON records from 1"}[tbl.locator()],
        "duplicate_header_names": tbl.meta.get("duplicate_header_names") or [],
        "rows": len(tbl.rows),
        "columns": cols,
        "decimal_convention": typed.file_decimal,
        "date_columns": [_date_summary(typed, c["name"], c["date_order"]) for c in date_cols],
        "totals_rows": totals,
        "aggregate_bucket_rows": checks.bucket_rows(label_cols),
        "grain": _grain(tbl, typed, cols, excluded),
        "exact_duplicate_rows": exact_dups,
        "identifier_columns": [{"column": c["name"], "type": c["type"], "nonnull": len(tbl.rows) - c["nulls"],
                                "distinct": c["distinct"], "reasons": c["identifier_reasons"]}
                               for c in cols if c["identifier_like"]],
        "pii_in_other_columns": pii_other,
        "instruction_like_cells": instr,
        "credential_like_cells": cred,
        "measure_sums_excl_totals": sums,
        "warnings": typed.warnings,
    }
    return out


def _size_note(path):
    size = os.path.getsize(path)
    if size >= LARGE_FILE_BYTES:
        return ("large file (%.0f MB): profile holds every row in memory and tests key combinations "
                "over all of them, so it takes noticeably longer; profile one sheet (--sheet) or a "
                "column subset if it is slow" % (size / 1048576.0))
    return None


def profile(path, sheet=None):
    base = os.path.basename(path)
    tabular.check_path(path)
    note = _size_note(path)
    if tabular.is_xlsx(path):
        wb = tabular.open_workbook(path)
        sheets = tabular.xlsx_sheets(path, wb)
        if sheet is not None and sheet not in [s["sheet"] for s in sheets]:
            raise tabular.InputError("sheet not found: %r (sheets: %s)"
                                     % (sheet, ", ".join(s["sheet"] for s in sheets)))
        names = [s["sheet"] for s in sheets] if sheet is None else [sheet]
        tables = []
        for nm in names:
            st = next((s for s in sheets if s["sheet"] == nm), None)
            if st and st["nonempty_rows"] == 0:
                continue
            try:
                tables.append(profile_table(tabular.load_xlsx(path, nm, wb),
                                            hidden=bool(st and st["state"] != "visible")))
            except tabular.InputError as e:
                tables.append({"sheet": nm, "error": str(e)})
        cross = _cross_sheet(tables)
        out = {"command": "profile", "file": base, "format": "xlsx", "sheets": sheets,
               "tables": tables, "cross_sheet_sums": cross}
        w = tabular.disguised_warning(path)
        if w:
            out["warnings"] = [w]
    else:
        tbl = tabular.load(path)
        t = profile_table(tbl)
        out = {"command": "profile", "file": base, "format": tbl.meta["format"],
               "encoding": tbl.meta.get("encoding"), "delimiter": tbl.meta.get("delimiter"),
               "blank_rows_skipped": tbl.meta["blank_rows_skipped"], "tables": [t]}
    if note:
        out["large_file_note"] = note
    return out


def _cross_sheet(tables):
    by = {}
    for t in tables:
        for name, s in (t.get("measure_sums_excl_totals") or {}).items():
            by.setdefault(checks._fold(name).strip(), []).append((t["sheet"], name, s))
    out = []
    for key in sorted(by):
        items = by[key]
        if len(items) < 2:
            continue
        vals = [s for _, _, s in items]
        mx = max(abs(v) for v in vals)
        match = max(vals) - min(vals) <= max(0.05, 1e-6 * mx)
        out.append({"column": items[0][1],
                    "sums": [{"sheet": sh, "sum_excl_totals": s} for sh, _, s in items],
                    "match": match, "max_difference": max(vals) - min(vals)})
    return out
