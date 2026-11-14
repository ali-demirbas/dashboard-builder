"""`cohort`: cohort matrix with right-censored cells marked missing.

references/data-quality-gate.md §3 "Right-censored cohort cells": a cell whose
offset lies beyond the cohort's age at the export date has not been observed,
even when the export fills it with 0 or a blank. It is treated as missing,
never averaged or summed as 0. The immature-cohort WARNING (§Severity rules)
governs the horizon: rates per horizon are computed over mature cohorts only,
weighted by cohort size.

Age is measured from the cohort's LAST acquisition day (the youngest member),
so a weekly cohort is mature for D7 only when its last day is 7 days old.
Cohort labels may be dates, YYYY-MM months or ISO weeks (2026-W40, read as
that week's Monday); a column with no readable cohort date is an error.

Value kind (--value-kind auto): a % sign means percentages; every value
<= 1 means proportions; whole numbers with a cohort size column mean
retained counts. Auto refuses — and asks for --value-kind — when the values
are not whole numbers (42.5 could be a percent or an average) or when every
value is <= 100 while every cohort is larger than 100 (40 of 1,000 users
and 40% read the same). A wrong guess here silently changes every rate.
"""
import calendar
import datetime as _dt
import os
import re
import statistics

from . import checks, tabular

_OFFSET = re.compile(r"(?:^|[^a-z])(d|day|days|gun|w|week|weeks|wk|hafta|m|month|months|mo|ay)[\s_-]*(\d+)(?![0-9])")
_UNIT = {"d": "day", "day": "day", "days": "day", "gun": "day",
         "w": "week", "week": "week", "weeks": "week", "wk": "week", "hafta": "week",
         "m": "month", "month": "month", "months": "month", "mo": "month", "ay": "month"}


def parse_offset(label, default_unit="day"):
    s = checks._fold(str(label)).strip()
    if re.fullmatch(r"\d+", s):
        return default_unit, int(s)
    m = _OFFSET.search(s)
    if not m:
        return None
    return _UNIT[m.group(1)], int(m.group(2))


def add_months(d, k):
    y, m = divmod(d.month - 1 + k, 12)
    y += d.year
    m += 1
    return _dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def horizon_date(last_day, unit, k):
    if unit == "day":
        return last_day + _dt.timedelta(days=k)
    if unit == "week":
        return last_day + _dt.timedelta(days=7 * k)
    return add_months(last_day, k)


def _span(dates):
    ds = sorted(set(dates))
    if len(ds) < 2:
        return "day"
    gaps = [(b - a).days for a, b in zip(ds, ds[1:])]
    g = statistics.median(gaps)
    if 27 <= g <= 32:
        return "month"
    if g == 7:
        return "week"
    return "day"


def _last_day(d, span):
    if span == "week":
        return d + _dt.timedelta(days=6)
    if span == "month":
        return _dt.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
    return d


def cohort(path, cohort_col, export_date, value_col=None, age_col=None, wide=False,
           size_col=None, value_kind="auto", cohort_span="auto", sheet=None,
           decimal="auto", date_order="auto"):
    tbl = tabular.load(path, sheet)
    typed = tabular.Typed(tbl, decimal, date_order)
    exp = tabular.parse_date(export_date, "iso")
    if exp is None:
        raise tabular.InputError("--export-date must be YYYY-MM-DD")
    cdates = typed.dates(cohort_col)
    labels = typed.texts(cohort_col)
    sizes = typed.numbers(size_col) if size_col else [None] * len(tbl.rows)
    # cells: list of (row index, horizon (unit, k), raw value)
    cells = []
    horizons = []
    if wide:
        skip = {cohort_col, size_col}
        for h in tbl.headers:
            if h in skip:
                continue
            off = parse_offset(h)
            if off is None:
                continue
            horizons.append((off, h))
        if not horizons:
            raise tabular.InputError("--wide: no offset columns found (expected headers like D1, D7, W1, M1)")
        horizons.sort()
        for off, h in horizons:
            vals = typed.numbers(h)
            i = tbl.col(h)
            for r, v in enumerate(vals):
                cells.append((r, off, v, tbl.rows[r][i]))
    else:
        if not (age_col and value_col):
            raise tabular.InputError("long format needs --age-col and --value-col (or use --wide)")
        ages = typed.texts(age_col)
        vals = typed.numbers(value_col)
        i = tbl.col(value_col)
        seen = set()
        for r, (a, v) in enumerate(zip(ages, vals)):
            off = parse_offset(a) if a is not None else None
            if off is None:
                continue
            seen.add(off)
            cells.append((r, off, v, tbl.rows[r][i]))
        horizons = [(o, "%s%d" % (o[0][0].upper(), o[1])) for o in sorted(seen)]
    span = cohort_span if cohort_span != "auto" else _span([d for d in cdates if d])
    # value kind
    raw_vals = [raw for _, _, _, raw in cells]
    nums = [v for _, _, v, _ in cells if v is not None]
    kind_rule = value_kind
    if not any(d is not None for d in cdates):
        raise tabular.InputError("no cohort date could be read in column %r (expected dates such as "
                                 "2026-10-01, months such as 2026-10, or ISO weeks such as 2026-W40)"
                                 % cohort_col)
    if value_kind == "auto":
        szs = [x for x in sizes if x is not None]
        if any(tabular.has_percent(x) for x in raw_vals):
            value_kind, kind_rule = "rate_percent", "auto: % sign present"
        elif nums and max(nums) <= 1.0:
            value_kind, kind_rule = "rate", "auto: every value <= 1"
        elif not size_col:
            raise tabular.InputError("value kind not settled: pass --value-kind count|rate|rate_percent")
        elif any(not float(v).is_integer() for v in nums):
            raise tabular.InputError("value kind not settled: values are not whole numbers (percentages "
                                     "without a % sign, or counts?); pass --value-kind rate_percent|count|rate")
        elif nums and szs and max(nums) <= 100 and min(szs) > 100:
            raise tabular.InputError("value kind not settled: every value is <= 100 while every cohort has "
                                     "more than 100 members, so the values read as counts and as "
                                     "percentages alike; pass --value-kind count|rate_percent")
        else:
            value_kind, kind_rule = "count", "auto: whole numbers with a cohort size column"
    # per cohort
    cohorts = {}
    order = []
    for r, d in enumerate(cdates):
        if d is None:
            continue
        key = labels[r]
        if key not in cohorts:
            order.append(key)
            last = _last_day(d, span)
            cohorts[key] = {"cohort": key, "cohort_start": d.isoformat(), "cohort_last_day": last.isoformat(),
                            "age_days_at_export": (exp - last).days, "size": sizes[r], "cells": {}, "_last": last}
        elif sizes[r] is not None and cohorts[key]["size"] is None:
            cohorts[key]["size"] = sizes[r]
    hlabel = {off: name for off, name in horizons}
    stats_cells = {"observed": 0, "censored": 0, "censored_zero_filled": 0, "censored_blank": 0,
                   "censored_nonzero": 0}
    for r, off, v, raw in cells:
        key = labels[r]
        if key not in cohorts:
            continue
        c = cohorts[key]
        hd = horizon_date(c["_last"], off[0], off[1])
        observed = hd <= exp
        if value_kind == "rate_percent" and v is not None:
            v = v / 100.0
        if observed:
            stats_cells["observed"] += 1
            status = "observed" if v is not None else "observed_blank"
            c["cells"][hlabel[off]] = {"value": v, "status": status}
        else:
            stats_cells["censored"] += 1
            if v is None:
                stats_cells["censored_blank"] += 1
            elif v == 0:
                stats_cells["censored_zero_filled"] += 1
            else:
                stats_cells["censored_nonzero"] += 1
            c["cells"][hlabel[off]] = {"value": None, "status": "censored", "file_value_was": (
                "blank" if v is None else ("zero" if v == 0 else "nonzero"))}
    # per-horizon mature rates
    per_h = []
    for off, name in horizons:
        num = den = 0.0
        naive_num = naive_den = 0.0
        mature = immature = 0
        rates = []
        for key in order:
            c = cohorts[key]
            cell = c["cells"].get(name)
            if cell is None:
                continue
            size = c["size"]
            if cell["status"] == "censored":
                immature += 1
                if cell["file_value_was"] == "zero" and size:
                    naive_den += size
                continue
            v = cell["value"]
            if v is None:
                continue
            mature += 1
            if size:
                retained = v if value_kind == "count" else v * size
                num += retained
                den += size
                naive_num += retained
                naive_den += size
            elif value_kind != "count":
                rates.append(v)
        rec = {"horizon": name, "unit": off[0], "offset": off[1], "mature_cohorts": mature,
               "immature_cohorts": immature}
        if den > 0:
            rec.update({"weighted_rate": num / den, "retained": num, "cohort_size_sum": den,
                        "method": "size-weighted over mature cohorts"})
            if naive_den > den:
                rec["naive_rate_if_censored_read_as_zero"] = naive_num / naive_den
        elif rates:
            rec.update({"weighted_rate": statistics.fmean(rates),
                        "method": "unweighted mean of mature cohort rates (no cohort size column)"})
        else:
            rec.update({"weighted_rate": None,
                        "note": "Not available — no mature cohort for this horizon"
                        if mature == 0 else "Not available — no cohort size to weight counts"})
        per_h.append(rec)
    out_cohorts = []
    for key in order:
        c = dict(cohorts[key])
        c.pop("_last")
        out_cohorts.append(c)
    warnings = []
    if stats_cells["censored_nonzero"]:
        warnings.append("%d cell(s) beyond the cohort's age carry a nonzero value — check the export date"
                        % stats_cells["censored_nonzero"])
    if stats_cells["censored_zero_filled"]:
        warnings.append("%d unobserved cell(s) were exported as 0; treated as missing, not as churn"
                        % stats_cells["censored_zero_filled"])
    if not out_cohorts:
        raise tabular.InputError("no cohort rows could be built from column %r" % cohort_col)
    dw, dnote = typed.dropped([cohort_col] + ([value_col] if value_col else [h for _, h in horizons]))
    warnings += dw
    return {"command": "cohort", "file": os.path.basename(path), "sheet": tbl.name, "dropped_note": dnote,
            "export_date": exp.isoformat(), "cohort_span": span, "value_kind": value_kind,
            "value_kind_rule": kind_rule, "rule": "cell observed iff cohort_last_day + offset <= export_date",
            "cells": stats_cells, "horizons": per_h, "cohorts": out_cohorts,
            "warnings": warnings + typed.warnings}
