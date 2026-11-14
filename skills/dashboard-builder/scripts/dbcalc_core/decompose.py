"""`decompose`: rate/mix decomposition of a blended rate change.

Method: Kitagawa, E. M. (1955). Components of a difference between two rates.
Journal of the American Statistical Association, 50(272), 1168-1194.
Citation key ``kitagawa1955``.

Blended rate R = sum_i c_i r_i, with c_i = den_i / sum(den) (segment share)
and r_i = num_i / den_i (segment rate). For base period 0 and compare period 1:

  symmetric (Kitagawa) split, the default — two terms, no residual:
    rate effect = sum_i (r1_i - r0_i) * (c0_i + c1_i) / 2
    mix effect  = sum_i (c1_i - c0_i) * (r0_i + r1_i) / 2
    rate + mix  = R1 - R0 exactly

  three-term split, base-weighted (also reported):
    rate effect = sum_i c0_i (r1_i - r0_i)
    mix effect  = sum_i (c1_i - c0_i) r0_i
    interaction = sum_i (c1_i - c0_i)(r1_i - r0_i)

Per-segment terms. The rate term (r1_i - r0_i)(c0_i + c1_i)/2 has the
intuitive sign. The raw Kitagawa mix term (c1_i - c0_i)(r0_i + r1_i)/2 does
not: it is positive for every segment that gained share, whatever its rate,
because it measures the share shift against a zero rate. Since the share
changes sum to zero, sum_i (c1_i - c0_i) * k = 0 for any constant k, so the
mix term can be centered on the average blended rate Rbar = (R0 + R1)/2
without changing the total:

    mix contribution_i = (c1_i - c0_i) * ((r0_i + r1_i)/2 - Rbar)

Its sign follows the segment's rate relative to the blend: share moving
into an above-blend segment (or out of a below-blend one) raises the blend.
The per-segment mix contributions sum exactly to the Kitagawa mix effect.
Both are reported (``mix_effect`` raw, ``mix_contribution`` centered); read
the total mix effect, and use the centered terms to say which segments'
share shift drove it. The centering is an algebraic identity on Kitagawa's
split, not a different method.

A segment present in only one period has an undefined rate in the other; its
missing rate is set equal to its observed rate, so its whole contribution is
mix (stated in the output). Simpson's-paradox flag: every segment observed in
both periods moved one way and the blended rate moved the other.
"""
import math
import os
import re

from . import checks, tabular

_RANGE = re.compile(r"^\s*(\S+)\s*\.\.\s*(\S+)\s*$")
_MONTH = re.compile(r"^\d{4}-\d{2}$")


def period_mask(typed, col, spec):
    """Rows belonging to a period spec: 'START..END' (inclusive dates),
    'YYYY-MM' (a month, on a date column), or an exact value."""
    m = _RANGE.match(spec)
    texts = typed.texts(col)
    if m:
        a, b = tabular.parse_date(m.group(1), "iso"), tabular.parse_date(m.group(2), "iso")
        if not a or not b:
            raise tabular.InputError("period range must be YYYY-MM-DD..YYYY-MM-DD")
        ds = typed.dates(col)
        return [d is not None and a <= d <= b for d in ds], {"first": a.isoformat(), "last": b.isoformat()}
    if _MONTH.match(spec.strip()):
        try:
            ds = typed.dates(col, record=False)
        except tabular.InputError:
            ds = None
        if ds is not None and any(ds):
            y, mo = map(int, spec.strip().split("-"))
            mask = [d is not None and d.year == y and d.month == mo for d in ds]
            if any(mask):
                typed.dates(col)  # a date column after all: count its unreadable cells as dropped
                sel = sorted(d for d, k in zip(ds, mask) if k)
                if typed.order_for(col) == "month":
                    return mask, {"first": spec.strip(), "last": spec.strip()}
                return mask, {"first": sel[0].isoformat(), "last": sel[-1].isoformat()}
    mask = [t == spec.strip() for t in texts]
    return mask, None


def _days(info, typed, col, mask):
    try:
        if typed.order_for(col) == "month":
            return None
        ds = typed.dates(col, record=False)
    except tabular.InputError:
        return None
    sel = {d for d, k in zip(ds, mask) if k and d}
    return len(sel) if sel else None


BLANK = "(blank)"
OUTCOME_NOTE = ("an exact arithmetic split, not an estimate: rate, mix and contribution effects take the outcome "
                "of the change they split (NOT APPLICABLE on full-population data, the sample's outcome on a "
                "sample) and get no test of their own (analysis-playbook.md §Statistical sufficiency)")


def exclusion_report(tbl, excluded, label_cols, kept_blank, what):
    """Rows left out, with reasons, and the warnings that say so (labels
    scrubbed; identifier columns never reach here)."""
    rows = [{"row": i + 1, tbl.locator(): tbl.lines[i], "reason": r} for i, r in sorted(excluded.items())]
    warns = []
    by = {}
    for i, r in sorted(excluded.items()):
        lab = " / ".join((v[i] or BLANK) for v in label_cols.values())
        by.setdefault(r, []).append(lab)
    text = {"total_label": "labeled as a total",
            "equals_sum_of_other_rows": "equal to the sum of all other rows",
            "period_subtotal": "equal to the sum of the other rows in the same period (per-period subtotal)",
            "excluded_by_flag": "named by --exclude-rows"}
    for r, labs in by.items():
        names = sorted(set(labs))
        warns.append("excluded %d row(s) %s: %s" % (len(labs), text.get(r, r),
                                                    ", ".join(checks.scrub(n, 40) for n in names[:8])))
    if kept_blank:
        warns.append("%d row(s) with a blank %s kept as their own %r segment (not a sum of the other rows)"
                     % (kept_blank, what, BLANK))
    return rows, warns


def decompose(path, segment_col, num_col, den_col, period_col, base, compare, sheet=None,
              decimal="auto", date_order="auto", exclude_labels=None):
    tbl = tabular.load(path, sheet)
    typed = tabular.Typed(tbl, decimal, date_order)
    seg = typed.texts(segment_col)
    checks.guard_dimension(segment_col, seg, "--segment-col")
    num = typed.numbers(num_col)
    den = typed.numbers(den_col)
    label_cols = {segment_col: seg}
    excl, kept_blank = checks.segment_exclusions(label_cols, {num_col: num, den_col: den},
                                                 typed.texts(period_col), exclude_labels)
    excluded_rows, excl_warns = exclusion_report(tbl, excl, label_cols, kept_blank, segment_col)
    m0, p0 = period_mask(typed, period_col, base)
    m1, p1 = period_mask(typed, period_col, compare)
    if not any(m0) or not any(m1):
        raise tabular.InputError("no rows matched --base or --compare in column %r" % period_col)
    agg = {}
    for i in range(len(tbl.rows)):
        if i in excl or (num[i] is None and den[i] is None):
            continue
        s_i = seg[i] if seg[i] not in (None, "") else BLANK
        for p, mask in ((0, m0), (1, m1)):
            if mask[i]:
                a = agg.setdefault(s_i, [[0.0, 0.0], [0.0, 0.0]])
                a[p][0] += num[i] or 0.0
                a[p][1] += den[i] or 0.0
    D0 = math.fsum(a[0][1] for a in agg.values())
    D1 = math.fsum(a[1][1] for a in agg.values())
    N0 = math.fsum(a[0][0] for a in agg.values())
    N1 = math.fsum(a[1][0] for a in agg.values())
    if D0 == 0 or D1 == 0:
        raise tabular.InputError("Not meaningful — zero %s in one period" % den_col)
    R0, R1 = N0 / D0, N1 / D1
    Rbar = (R0 + R1) / 2
    segs = []
    notes = []
    rate_s = mix_s = rate_b = mix_b = inter = 0.0
    up = down = flat = 0
    for s in sorted(agg):
        (n0, d0), (n1, d1) = agg[s]
        c0, c1 = d0 / D0, d1 / D1
        r0 = n0 / d0 if d0 else None
        r1 = n1 / d1 if d1 else None
        if r0 is None and r1 is None:
            notes.append("segment with zero %s in both periods skipped" % den_col)
            continue
        both = r0 is not None and r1 is not None
        if r0 is None:
            r0 = r1
            notes.append("a segment absent in the base period: its base rate set to its compare rate (pure mix)")
        if r1 is None:
            r1 = r0
            notes.append("a segment absent in the compare period: its compare rate set to its base rate (pure mix)")
        re_ = (r1 - r0) * (c0 + c1) / 2
        me_ = (c1 - c0) * (r0 + r1) / 2
        rate_s += re_
        mix_s += me_
        rate_b += c0 * (r1 - r0)
        mix_b += (c1 - c0) * r0
        inter += (c1 - c0) * (r1 - r0)
        if both:
            if r1 > r0:
                up += 1
            elif r1 < r0:
                down += 1
            else:
                flat += 1
        segs.append({"segment": checks.scrub(s), "base": {"num": n0, "den": d0, "rate": n0 / d0 if d0 else None,
                                                          "share": c0},
                     "compare": {"num": n1, "den": d1, "rate": n1 / d1 if d1 else None, "share": c1},
                     "rate_effect": re_, "mix_effect": me_,
                     "mix_contribution": (c1 - c0) * ((r0 + r1) / 2 - Rbar),
                     "observed_both_periods": both})
    dR = R1 - R0
    simpson = (up > 0 and down == 0 and flat == 0 and dR < 0) or (down > 0 and up == 0 and flat == 0 and dR > 0)
    out = {
        "command": "decompose", "file": os.path.basename(path), "sheet": tbl.name,
        "segment_col": segment_col, "num": num_col, "den": den_col,
        "base": {"spec": base, "period": p0, "days": _days(p0, typed, period_col, m0), "num": N0, "den": D0, "rate": R0},
        "compare": {"spec": compare, "period": p1, "days": _days(p1, typed, period_col, m1), "num": N1, "den": D1,
                    "rate": R1},
        "blended_change": dR,
        "method": "kitagawa1955 symmetric two-factor split (rate + mix, no residual)",
        "rate_effect": rate_s, "mix_effect": mix_s,
        "three_term_base_weighted": {"rate_effect": rate_b, "mix_effect": mix_b, "interaction": inter},
        "check_sum_equals_change": abs(rate_s + mix_s - dR) < 1e-12,
        "segment_terms_note": ("per segment: rate_effect = (r1 - r0)(c0 + c1)/2 (sign = the segment's own rate "
                               "move); mix_effect = raw Kitagawa term (c1 - c0)(r0 + r1)/2, positive for any "
                               "segment that gained share, so do not read its sign; mix_contribution = "
                               "(c1 - c0)((r0 + r1)/2 - (R0 + R1)/2), sign follows the segment's rate relative "
                               "to the blend and the terms sum exactly to mix_effect. Interpret the total mix "
                               "effect; use mix_contribution to say which share shifts drove it."),
        "outcome_note": OUTCOME_NOTE,
        "segments": segs,
        "segments_up": up, "segments_down": down, "segments_flat": flat,
        "simpsons_paradox": simpson,
        "excluded_totals_rows": [r["row"] for r in excluded_rows],
        "excluded_rows": excluded_rows,
        "notes": sorted(set(notes)),
        "warnings": typed.warnings + excl_warns,
    }
    dw, dnote = typed.dropped([num_col, den_col, period_col])
    out["warnings"] += dw
    out["dropped_note"] = dnote
    if out["base"]["days"] and out["compare"]["days"] and out["base"]["days"] != out["compare"]["days"]:
        out["warnings"].append("unequal period lengths: base %d days vs compare %d days"
                               % (out["base"]["days"], out["compare"]["days"]))
    return out

