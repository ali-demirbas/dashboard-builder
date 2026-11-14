"""`aggregate`: plain KPI values (sum, count, mean, min, max, ratio of sums).

The figures a KPI card shows: total revenue in October, orders by channel,
CVR as sum(orders) / sum(sessions). Each one goes through the same
totals-row exclusion as the analysis commands (references/data-quality-gate.md
§1: totals and subtotal rows are found before any aggregation), so a
"Total" or per-day subtotal row is never summed with the rows it totals,
and every output value gets a trace record.

A ratio is always a ratio of sums, never a mean of row-level ratios
(kpi-framework.md: a blended rate weights each row by its denominator).
Citation key ``aggregate``.
"""
import os
import statistics

from . import checks, tabular
from .decompose import exclusion_report, period_mask

AGGS = ("sum", "count", "mean", "min", "max", "ratio")


def parse_filters(specs):
    out = []
    for s in specs or []:
        if "=" not in s:
            raise tabular.InputError("--filter needs COLUMN=VALUE, got %r" % s)
        col, val = s.split("=", 1)
        out.append((col.strip(), val.strip()))
    return out


def aggregate(path, metrics, agg="sum", den=None, group_by=None, filters=None, period_col=None,
              period=None, sheet=None, decimal="auto", date_order="auto", exclude_labels=None):
    if agg not in AGGS:
        raise tabular.InputError("--agg must be one of %s" % ", ".join(AGGS))
    if agg == "ratio" and not den:
        raise tabular.InputError("--agg ratio needs --den (the ratio is sum(metric) / sum(den))")
    if agg != "count" and not metrics:
        raise tabular.InputError("--metric is required for --agg %s" % agg)
    if bool(period_col) != bool(period):
        raise tabular.InputError("--period-col and --period go together")
    tbl = tabular.load(path, sheet)
    typed = tabular.Typed(tbl, decimal, date_order)
    n = len(tbl.rows)
    for c in list(metrics) + ([den] if den else []):
        tbl.col(c)
    groups = [None] * n
    if group_by:
        groups = typed.texts(group_by)
        checks.guard_dimension(group_by, groups, "--group-by")
    flt = parse_filters(filters)
    keep = [True] * n
    for col, val in flt:
        texts = typed.texts(col)
        keep = [k and (t is not None and t == val) for k, t in zip(keep, texts)]
    per = None
    if period_col:
        mask, per = period_mask(typed, period_col, period)
        keep = [k and m for k, m in zip(keep, mask)]
    nums = {m: typed.numbers(m) for m in metrics}
    if den:
        nums[den] = typed.numbers(den)
    # totals rows: every text column is a label column, the date column (if any) the group
    kinds = {h: typed.kind(h) for h in tbl.headers}
    label_cols = {h: typed.texts(h) for h in tbl.headers if kinds[h] == "text"
                  and not checks.identifier_reason_from_header(h)}
    date_cols = [h for h in tbl.headers if kinds[h] == "date"]
    # the "period" a subtotal sums over: the period column, else the first date
    # column, else each low-cardinality text column in turn (month labels, P0/P1)
    keys = [period_col] if period_col else (date_cols[:1] or
                                            [h for h in label_cols if len(set(label_cols[h])) <= n / 2])
    excl, kept_blank = {}, 0
    if nums and label_cols:
        for k in keys or [None]:
            lc = {h: v for h, v in label_cols.items() if h != k} or label_cols
            pk = typed.texts(k) if k else [None] * n
            e, kb = checks.segment_exclusions(lc, nums, pk, exclude_labels)
            for i, why in e.items():
                excl.setdefault(i, why)
            kept_blank = max(kept_blank, kb)
    excluded_rows, excl_warns = exclusion_report(tbl, excl, label_cols, kept_blank, "label")
    if not label_cols:
        excl_warns = []
    rows = [i for i in range(n) if keep[i] and i not in excl]
    if not rows:
        raise tabular.InputError("no rows left after the filters and period selection")
    gnames = sorted({groups[i] for i in rows}, key=lambda g: "" if g is None else g) if group_by else []
    targets = [(False, None, rows)] + [(True, g, [i for i in rows if groups[i] == g]) for g in gnames]
    results = []
    for m in (metrics or [None]):
        for is_group, g, idx in targets:
            label = None if not is_group else (checks.scrub(g) if g not in (None, "") else "(blank)")
            rec = {"metric": m, "group": label, "scope": "group" if is_group else "all rows"}
            if agg == "count":
                vals = [i for i in idx if m is None or nums[m][i] is not None]
                rec.update({"value": len(vals), "rows": len(idx)})
            elif agg == "ratio":
                num_sum = sum(nums[m][i] for i in idx if nums[m][i] is not None)
                den_sum = sum(nums[den][i] for i in idx if nums[den][i] is not None)
                rec.update({"value": (num_sum / den_sum) if den_sum else None, "num_sum": num_sum,
                            "den_sum": den_sum, "rows": len(idx)})
                if not den_sum:
                    rec["note"] = "Not meaningful — zero %s" % den
            else:
                vals = [nums[m][i] for i in idx if nums[m][i] is not None]
                fn = {"sum": sum, "min": min, "max": max, "mean": statistics.fmean}[agg]
                rec.update({"value": fn(vals) if vals else (0.0 if agg == "sum" else None),
                            "rows": len(idx), "values_used": len(vals)})
            results.append(rec)
    dw, dnote = typed.dropped(list(metrics) + ([den] if den else []) + ([period_col] if period_col else []))
    return {"command": "aggregate", "file": os.path.basename(path), "sheet": tbl.name, "agg": agg,
            "metrics": list(metrics), "den": den, "group_by": group_by,
            "filters": ["%s = %s" % f for f in flt],
            "period": {"column": period_col, "spec": period, "range": per} if period_col else None,
            "rows_used": len(rows), "results": results,
            "excluded_totals_rows": [r["row"] for r in excluded_rows], "excluded_rows": excluded_rows,
            "dropped_note": dnote, "warnings": typed.warnings + excl_warns + dw}
