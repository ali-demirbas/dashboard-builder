"""`drivers`: contribution analysis of an additive total's change.

For each dimension, each value's change (compare - base) and its share of the
total change; ranked by absolute contribution (ties by value, ascending);
positive and negative contributors reported separately; the smallest set of
same-direction contributors whose cumulative share reaches 50% (cum_stop);
one drill level into the top contributor by the next dimension; and "no
single driver" when no value explains at least min_share (default 25%) of
the change. A single value carrying >= 50% is flagged as concentration
(references/analysis-playbook.md §Time-series analysis, concentration risk),
unless the members moved against each other so much that the net change is
small next to the gross movement: when sum_i |delta_i| > 3 x |delta_total|
(OFFSETTING_RATIO, a working convention, unverified, directional only) the
dimension is labeled "offsetting moves" instead, because a share of a small
net change says little about concentration. A zero total change has no
shares: "Not meaningful — zero total change".

Per-period subtotal rows ("Paid total", "All devices", "Toplam", or rows
equal to the sum of the other rows of their period) are excluded with a
warning (checks.segment_exclusions); --exclude-rows names more labels.

Only additive metrics decompose this way. A ratio (CVR, CTR, ROAS, CPA, AOV,
any average or percentage) does not: its change is a rate effect plus a mix
effect, so a ratio metric is sent to ``decompose`` (Kitagawa 1955) instead.
Citation key ``contribution``.
"""
import math
import os

from . import checks, tabular
from .decompose import BLANK, OUTCOME_NOTE, decompose, exclusion_report, period_mask

OFFSETTING_RATIO = 3.0
ZERO_CHANGE = "Not meaningful — zero total change"

RATIO_TOKENS = {"rate", "ratio", "cvr", "ctr", "ctor", "roas", "roi", "cpa", "cac", "cpc", "cpm", "cpi",
                "aov", "arpu", "arpa", "arppu", "avg", "average", "mean", "pct", "percent", "share",
                "oran", "orani", "ortalama", "yuzde", "per"}


def is_ratio_name(h):
    return "%" in h or bool(set(checks.header_tokens(h)) & RATIO_TOKENS)


def _analyse(rows, dim_vals, metric, delta_total, min_share, cum_stop):
    """rows: iterable of (dim value, period 0/1, metric value)."""
    agg = {}
    for v, p, x in rows:
        a = agg.setdefault(v, [0.0, 0.0])
        a[p] += x
    items = []
    for v, (b, c) in agg.items():
        d = c - b
        items.append({"value": v, "base": b, "compare": c, "delta": d,
                      "share_of_total_change": (d / delta_total) if delta_total else None})
    items.sort(key=lambda r: (-abs(r["delta"]), str(r["value"])))
    for k, r in enumerate(items, 1):
        r["rank"] = k
    sign = 1 if delta_total > 0 else (-1 if delta_total < 0 else 0)
    same = [r for r in items if sign and r["delta"] * sign > 0]
    opp = [r for r in items if sign and r["delta"] * sign < 0]
    cum, explain = 0.0, []
    for r in same:
        if cum >= cum_stop:
            break
        cum += r["share_of_total_change"]
        explain.append(r["value"])
    top_share = same[0]["share_of_total_change"] if same else None
    gross = math.fsum(abs(r["delta"]) for r in items)
    ratio = (gross / abs(delta_total)) if delta_total else None
    offsetting = ratio is not None and ratio > OFFSETTING_RATIO
    res = {
        "ranked": items,
        "positive_contributors": [r["value"] for r in items if r["delta"] > 0],
        "negative_contributors": [r["value"] for r in items if r["delta"] < 0],
        "same_direction_as_total": [r["value"] for r in same],
        "offsetting": [r["value"] for r in opp],
        "cumulative_stop": {"threshold": cum_stop, "values": explain,
                            "cumulative_share": cum if explain else None,
                            "reached": bool(explain) and cum >= cum_stop},
        "top_contributor": same[0]["value"] if same else None,
        "top_share": top_share,
        "no_single_driver": bool(delta_total) and ((top_share is None) or top_share < min_share),
        "gross_movement": gross,
        "gross_over_net": ratio,
        "offsetting_moves": offsetting,
        "concentrated": (not offsetting) and top_share is not None and top_share >= 0.5,
    }
    if not delta_total:
        res["note"] = ZERO_CHANGE
    elif offsetting:
        res["note"] = ("offsetting moves: members moved in opposite directions; the gross movement is %.1fx "
                       "the net change (above %.0fx), so shares of the net change are not read as "
                       "concentration" % (ratio, OFFSETTING_RATIO))
    return res


def _verdict(b):
    if b.get("note") == ZERO_CHANGE:
        return ZERO_CHANGE
    if b["offsetting_moves"]:
        return ("offsetting moves: gross movement %.1fx the net change; no concentration read"
                % b["gross_over_net"])
    if b["no_single_driver"]:
        return "no single driver"
    if b["concentrated"]:
        return "concentrated: %s carries %.0f%% of the change" % (b["top_contributor"], 100 * b["top_share"])
    return "top driver: %s (%.0f%% of the change)" % (b["top_contributor"], 100 * b["top_share"])


def drivers(path, metric_col, period_col, base, compare, dims, sheet=None, min_share=0.25,
            cum_stop=0.5, den_col=None, force_additive=False, decimal="auto", date_order="auto",
            exclude_labels=None):
    if den_col or (is_ratio_name(metric_col) and not force_additive):
        if not den_col:
            return {"command": "drivers", "delegated": False, "metric": metric_col,
                    "error": ("%r looks like a ratio (rate/average/percentage); a ratio's change does not "
                              "split additively by segment. Use `decompose --num <numerator> --den "
                              "<denominator>` (Kitagawa rate/mix), or pass --den here, or --force-additive "
                              "if the column is in fact an additive total." % metric_col)}
        return {"command": "drivers", "delegated": True, "delegated_to": "decompose", "outcome_note": OUTCOME_NOTE,
                "reason": "ratio metric %s / %s: per-segment change is a rate effect plus a mix effect, "
                          "not an additive contribution" % (metric_col, den_col),
                "results": [decompose(path, d, metric_col, den_col, period_col, base, compare, sheet,
                                      decimal, date_order, exclude_labels) for d in dims]}
    tbl = tabular.load(path, sheet)
    typed = tabular.Typed(tbl, decimal, date_order)
    dvals = {}
    for d in dims:
        dvals[d] = typed.texts(d)
        checks.guard_dimension(d, dvals[d], "dimension")
    metric = typed.numbers(metric_col)
    excl, kept_blank = checks.segment_exclusions(dvals, {metric_col: metric}, typed.texts(period_col),
                                                 exclude_labels)
    excluded_rows, excl_warns = exclusion_report(tbl, excl, dvals, kept_blank, "dimension value")
    m0, p0 = period_mask(typed, period_col, base)
    m1, p1 = period_mask(typed, period_col, compare)
    if not any(m0) or not any(m1):
        raise tabular.InputError("no rows matched --base or --compare in column %r" % period_col)
    idx = [i for i in range(len(tbl.rows)) if i not in excl and metric[i] is not None]
    T0 = math.fsum(metric[i] for i in idx if m0[i])
    T1 = math.fsum(metric[i] for i in idx if m1[i])
    dT = T1 - T0

    def rows_for(dim, filt=None):
        for i in idx:
            if filt and dvals[filt[0]][i] != filt[1]:
                continue
            v = dvals[dim][i]
            v = BLANK if v in (None, "") else v
            if m0[i]:
                yield v, 0, metric[i]
            if m1[i]:
                yield v, 1, metric[i]

    per_dim = []
    for d in dims:
        res = _analyse(rows_for(d), None, metric_col, dT, min_share, cum_stop)
        res["dimension"] = d
        per_dim.append(res)
    drill = None
    if len(dims) >= 2 and per_dim[0]["top_contributor"] is not None:
        top = per_dim[0]["top_contributor"]
        top_delta = next(r["delta"] for r in per_dim[0]["ranked"] if r["value"] == top)
        drill = _analyse(rows_for(dims[1], (dims[0], top)), None, metric_col, top_delta, min_share, cum_stop)
        drill.update({"within": {"dimension": dims[0], "value": top, "delta": top_delta},
                      "by": dims[1], "shares_are_of": "the top contributor's change"})
        for r in drill["ranked"]:
            r["share_of_total_change_overall"] = (r["delta"] / dT) if dT else None
    # scrub printed labels
    for block in per_dim + ([drill] if drill else []):
        for r in block["ranked"]:
            r["value"] = checks.scrub(str(r["value"]))
        for k in ("positive_contributors", "negative_contributors", "same_direction_as_total", "offsetting"):
            block[k] = [checks.scrub(str(v)) for v in block[k]]
        block["cumulative_stop"]["values"] = [checks.scrub(str(v)) for v in block["cumulative_stop"]["values"]]
        if block["top_contributor"] is not None:
            block["top_contributor"] = checks.scrub(str(block["top_contributor"]))
    if drill:
        drill["within"]["value"] = checks.scrub(str(drill["within"]["value"]))
    out = {"command": "drivers", "file": os.path.basename(path), "sheet": tbl.name, "metric": metric_col,
           "base": {"spec": base, "period": p0, "total": T0},
           "compare": {"spec": compare, "period": p1, "total": T1},
           "total_change": dT, "relative_change": (dT / T0) if T0 else None,
           "min_share": min_share, "outcome_note": OUTCOME_NOTE, "dimensions": per_dim, "drill": drill,
           "summary": [{"dimension": b["dimension"], "verdict": _verdict(b)} for b in per_dim],
           "excluded_totals_rows": [r["row"] for r in excluded_rows], "excluded_rows": excluded_rows,
           "warnings": typed.warnings + excl_warns}
    dw, dnote = typed.dropped([metric_col, period_col])
    out["warnings"] += dw
    out["dropped_note"] = dnote
    return out
