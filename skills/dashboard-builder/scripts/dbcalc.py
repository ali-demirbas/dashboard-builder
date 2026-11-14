#!/usr/bin/env python3
"""dbcalc — the dashboard-builder computation layer.

Every subcommand prints one JSON document to stdout. With ``--trace PATH``
it also appends one trace record per computed figure to PATH (JSON lines);
``trace render PATH --format md|html`` turns that file into a
"How each number was computed" table. See scripts/README.md.

Standard library only; .xlsx input needs the optional openpyxl package.
"""
import argparse
import csv
import json
import math
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dbcalc_core import VERSION  # noqa: E402
from dbcalc_core import aggregate as m_aggregate  # noqa: E402
from dbcalc_core import anomaly as m_anomaly  # noqa: E402
from dbcalc_core import cohort as m_cohort  # noqa: E402
from dbcalc_core import decompose as m_decompose  # noqa: E402
from dbcalc_core import drivers as m_drivers  # noqa: E402
from dbcalc_core import joins as m_joins  # noqa: E402
from dbcalc_core import profile as m_profile  # noqa: E402
from dbcalc_core import stats as m_stats  # noqa: E402
from dbcalc_core import tabular  # noqa: E402
from dbcalc_core import trace as m_trace  # noqa: E402

R = m_trace.record


def _clean(o):
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


def _floats(s, what="value"):
    out = []
    for x in s.replace(";", ",").split(","):
        if x.strip():
            try:
                out.append(float(x))
            except ValueError:
                raise tabular.InputError("%s %r is not a number" % (what, x.strip()))
    return out


def _counts(s):
    vals = _floats(s, "count")
    for v in vals:
        if v < 0 or not float(v).is_integer():
            raise tabular.InputError("counts must be non-negative whole numbers (units per arm), got %r" % v)
    return [int(v) for v in vals]


def _confidence(c):
    if not 0 < c < 1:
        raise tabular.InputError("--confidence must lie strictly between 0 and 1 (0.95 = 95%%), got %s" % c)


def _structure(a):
    if a.material is not None and a.structure is None:
        raise tabular.InputError("--material needs --structure: independent (two groups, e.g. A/B arms) or "
                                 "single-series (a SAMPLED series read before/after, UNTESTED unless its trend "
                                 "gate cleared). A before/after rate over every unit in the period (all "
                                 "sessions, the full population) has no sampling question: classify it with "
                                 "`stats classify --not-applicable` and read the move against the series' own "
                                 "variation; an interval from this command is then a sampling-noise floor only "
                                 "(analysis-playbook.md §Statistical sufficiency, Step 1)")
    return a.structure or "independent"


def _inputs(args, names, values):
    if getattr(args, "inputs_json", None):
        try:
            given = json.loads(args.inputs_json)
        except ValueError:
            raise tabular.InputError("--inputs-json is not valid JSON")
        if not isinstance(given, list) or not all(isinstance(g, dict) for g in given):
            raise tabular.InputError("--inputs-json must be a JSON list of objects")
        if len(given) == len(values):
            return [dict(g, value=v) for g, v in zip(given, values)]
        return given
    return [{"column": n, "value": v} for n, v in zip(names, values)]


def _lab(a, default):
    """Trace label prefix: --label when given, else a default naming the metric."""
    return a.label or default


def _labels_arg(a):
    out = []
    for x in getattr(a, "exclude_rows", None) or []:
        out += [y.strip() for y in x.split(",") if y.strip()]
    return out


# ---------------------------------------------------------------------------
# command implementations: each returns (result, trace_records)
# ---------------------------------------------------------------------------


def c_profile(a):
    res = m_profile.profile(a.file, a.sheet)
    recs = []
    base = os.path.basename(a.file)
    pre = (a.label + ": ") if a.label else ""
    for t in res["tables"]:
        if "error" in t:
            continue
        where = "%s%s" % (base, "[%s]" % t["sheet"] if t["sheet"] else "")
        recs.append(R("profile", pre + "Data rows (%s)" % where,
                      t["rows"], "rows", "count of non-blank rows below the header row",
                      [{"file": base, "sheet": t["sheet"], "aggregation": "count rows"}],
                      "row count", "dqg-locale"))
        for d in t["date_columns"]:
            if d.get("period"):
                recs.append(R("profile", pre + "Covered period, %s (%s)" % (d["column"], where),
                              "%s to %s" % (d["period"]["first"], d["period"]["last"]), "date range",
                              "min and max date present in the rows",
                              [{"file": base, "sheet": t["sheet"], "column": d["column"], "aggregation": "min, max"}],
                              "period echo", "dqg-period"))
        if a.trace_sums:
            excl = len(t["totals_rows"])
            for col, v in sorted(t["measure_sums_excl_totals"].items()):
                recs.append(R("profile", pre + "Sum of %s, totals rows excluded (%s)" % (col, where), v, None,
                              "sum of %s over rows, %d totals row(s) excluded" % (col, excl),
                              [{"file": base, "sheet": t["sheet"], "column": col,
                                "filter": "totals rows excluded", "aggregation": "sum", "value": v}],
                              "column sum", "dqg-locale"))
    return res, recs


def c_prop_diff(a):
    _confidence(a.confidence)
    structure = _structure(a)
    r = m_stats.prop_diff(a.x1, a.n1, a.x2, a.n2, a.confidence)
    if a.material is not None:
        r["classification"] = m_stats.classify(r["ci_low"], r["ci_high"], a.material, structure,
                                               a.trend_gate == "cleared")
    lab = a.label or "Rate difference"
    ins = _inputs(a, ["x1 (successes, group 1)", "n1 (trials, group 1)", "x2 (successes, group 2)",
                      "n2 (trials, group 2)"], [a.x1, a.n1, a.x2, a.n2])
    pct = int(round(a.confidence * 100))
    recs = [
        R("prop-diff", lab + ": group 1 rate", r["p1"], "rate", "x1 / n1", ins[:2], "proportion", "arithmetic"),
        R("prop-diff", lab + ": group 2 rate", r["p2"], "rate", "x2 / n2", ins[2:], "proportion", "arithmetic"),
        R("prop-diff", lab + ": difference", r["difference"], "pp", "x2/n2 - x1/n1", ins,
          "difference of proportions", "arithmetic"),
        R("prop-diff", lab + ": %d%% CI low" % pct, r["ci_low"], "pp", "Newcombe hybrid score (method 10) lower limit",
          ins, "Newcombe interval", "newcombe1998"),
        R("prop-diff", lab + ": %d%% CI high" % pct, r["ci_high"], "pp", "Newcombe hybrid score (method 10) upper limit",
          ins, "Newcombe interval", "newcombe1998"),
        R("prop-diff", lab + ": relative change", r["relative_change"], "share", "(p2 - p1) / p1", ins,
          "relative change", "arithmetic"),
        R("prop-diff", lab + ": p-value", r["p_value"], "p",
          "two-sided " + ("Fisher exact" if r["test"] == "fisher_exact" else "pooled two-proportion z"), ins,
          r["test"], "fisher1935" if r["test"] == "fisher_exact" else "arithmetic"),
    ]
    if "classification" in r:
        recs.append(R("prop-diff", lab + ": outcome", r["classification"]["outcome"], None,
                      "interval read against material threshold %s (%s)" % (a.material, structure), ins,
                      "statistical sufficiency Step 3", "playbook-sufficiency"))
    return dict({"command": "prop-diff"}, **r), recs


def c_welch(a):
    _confidence(a.confidence)
    structure = _structure(a)
    note = None
    if a.summary:
        m1, s1, n1, m2, s2, n2 = a.summary
        if s1 < 0 or s2 < 0:
            raise tabular.InputError("standard deviations must be non-negative")
        if not (float(n1).is_integer() and float(n2).is_integer()):
            raise tabular.InputError("n1 and n2 must be whole numbers")
        r = m_stats.welch(m1, s1, int(n1), m2, s2, int(n2), a.confidence)
        ins = _inputs(a, ["mean1", "sd1", "n1", "mean2", "sd2", "n2"], [m1, s1, n1, m2, s2, n2])
    elif a.a and a.b:
        r = m_stats.welch_samples(_floats(a.a), _floats(a.b), a.confidence)
        ins = _inputs(a, ["sample 1", "sample 2"], [None, None])
    elif a.file:
        if not (a.value_col and a.group_col and a.groups):
            raise tabular.InputError("--file needs --value-col, --group-col and --groups G1,G2")
        tbl = tabular.load(a.file, a.sheet)
        typed = tabular.Typed(tbl, a.decimal, a.date_order)
        vals, grp = typed.numbers(a.value_col), typed.texts(a.group_col)
        gs = [g.strip() for g in a.groups.split(",")]
        if len(gs) != 2:
            raise tabular.InputError("--groups needs exactly two values, G1,G2")
        g1, g2 = gs
        s1 = [v for v, g in zip(vals, grp) if g == g1 and v is not None]
        s2 = [v for v, g in zip(vals, grp) if g == g2 and v is not None]
        r = m_stats.welch_samples(s1, s2, a.confidence)
        dw, note = typed.dropped([a.value_col])
        r["warnings"] = typed.warnings + dw
        base = os.path.basename(a.file)
        ins = [{"file": base, "sheet": tbl.name, "column": a.value_col, "filter": "%s = group %d" % (a.group_col, k),
                "aggregation": "mean, sd, n", "value": n} for k, n in ((1, len(s1)), (2, len(s2)))]
    else:
        raise tabular.InputError("welch needs --summary, --a/--b, or --file")
    if a.material is not None:
        r["classification"] = m_stats.classify(r["ci_low"], r["ci_high"], a.material, structure,
                                               a.trend_gate == "cleared")
    lab = a.label or "Mean difference"
    recs = [R("welch", lab + ": difference", r["difference"], a.unit, "mean2 - mean1", ins, "difference in means",
              "arithmetic", note),
            R("welch", lab + ": CI low", r["ci_low"], a.unit, "diff - t(df) * se, Welch-Satterthwaite df", ins,
              "Welch interval", "welch1947", note),
            R("welch", lab + ": CI high", r["ci_high"], a.unit, "diff + t(df) * se, Welch-Satterthwaite df", ins,
              "Welch interval", "welch1947", note),
            R("welch", lab + ": p-value", r["p_value"], "p", "two-sided Welch t", ins, "Welch t-test", "welch1947",
              note)]
    if "classification" in r:
        recs.append(R("welch", lab + ": outcome", r["classification"]["outcome"], None,
                      "interval read against material threshold %s (%s)" % (a.material, structure), ins,
                      "statistical sufficiency Step 3", "playbook-sufficiency"))
    return dict({"command": "welch"}, **r), recs


def c_holm(a):
    ps = []
    for x in a.pvalues:
        ps += _floats(x, "p-value")
    if not ps:
        raise tabular.InputError("holm needs at least one p-value")
    bad = [p for p in ps if not 0 <= p <= 1]
    if bad:
        raise tabular.InputError("p-values must lie in [0, 1], got %s" % ", ".join(repr(b) for b in bad))
    if not 0 < a.alpha < 1:
        raise tabular.InputError("--alpha must lie strictly between 0 and 1")
    labels = [x.strip() for x in a.labels.split(",")] if a.labels else ["comparison %d" % (i + 1)
                                                                          for i in range(len(ps))]
    if len(labels) != len(ps):
        raise tabular.InputError("--labels has %d label(s) for %d p-value(s)" % (len(labels), len(ps)))
    r = m_stats.holm(ps, a.alpha)
    pre = (a.label + ": ") if a.label else ""
    recs = [R("holm", pre + "Holm-adjusted p, %s" % lab, adj, "p", "Holm step-down over %d p-values" % len(ps),
              [{"column": "p-values", "value": p}], "Holm adjustment", "holm1979")
            for lab, p, adj in zip(labels, ps, r["adjusted"])]
    return dict({"command": "holm", "pvalues": ps, "labels": labels}, **r), recs


def c_srm(a):
    obs = _counts(a.counts)
    if len(obs) >= 2 and sum(obs) == 0:
        raise tabular.InputError("counts sum to zero: there is no assignment to check")
    ratios = _floats(a.ratios, "ratio") if a.ratios else None
    if not 0 < a.threshold < 1:
        raise tabular.InputError("--threshold must lie strictly between 0 and 1")
    r = m_stats.srm(obs, ratios, a.threshold)
    lab = a.label or "Sample ratio check"
    ins = _inputs(a, ["arm %d count" % (i + 1) for i in range(len(obs))], obs)
    recs = [R("srm", lab + ": chi-square", r["chi2"], None, "sum (observed - expected)^2 / expected", ins,
              "chi-square goodness of fit", "pearson1900"),
            R("srm", lab + ": p-value", r["p_value"], "p", "chi-square sf, df = arms - 1", ins,
              "SRM check", "fabijan2019"),
            R("srm", lab + ": mismatch", r["mismatch"], None, "p < %s" % a.threshold, ins, "SRM check", "fabijan2019")]
    return dict({"command": "srm"}, **r), recs


def c_classify(a):
    structure = _structure(a) if (a.low is not None and a.high is not None) else (a.structure or "independent")
    r = m_stats.classify(a.low, a.high, a.material, structure, a.trend_gate == "cleared",
                         a.not_applicable, a.untested_reason)
    rec = R("classify", (a.label or "Outcome"), r["outcome"], None,
            "interval [%s, %s] against material %s (%s)" % (a.low, a.high, a.material, structure),
            [{"column": "interval", "value": [a.low, a.high]}], "statistical sufficiency Step 3",
            "playbook-sufficiency")
    return dict({"command": "classify",
                 "section": "references/analysis-playbook.md §Statistical sufficiency, Step 3"}, **r), [rec]


def c_cohort(a):
    r = m_cohort.cohort(a.file, a.cohort_col, a.export_date, a.value_col, a.age_col, a.wide, a.size_col,
                        a.value_kind, a.cohort_span, a.sheet, a.decimal, a.date_order)
    base = os.path.basename(a.file)
    pre = _lab(a, "Cohort retention (%s)" % (a.value_col or "wide offsets"))
    note = r.get("dropped_note")
    recs = [R("cohort", pre + ": censored (unobserved) cells", r["cells"]["censored"], "cells",
              "cells with cohort_last_day + offset > export date %s" % r["export_date"],
              [{"file": base, "sheet": r["sheet"], "column": a.cohort_col, "aggregation": "count cells"}],
              "right-censoring rule", "dqg-cohort", note)]
    for h in r["horizons"]:
        if h.get("weighted_rate") is None:
            continue
        weighted = "cohort_size_sum" in h
        recs.append(R("cohort", "%s: %s rate, mature cohorts" % (pre, h["horizon"]), h["weighted_rate"], "rate",
                      ("sum retained / sum cohort size over %d mature cohorts" if weighted else
                       "unweighted mean of %d mature cohort rates") % h["mature_cohorts"],
                      [{"file": base, "sheet": r["sheet"], "column": h["horizon"] if a.wide else a.value_col,
                        "filter": "mature cohorts only (%d excluded as immature)" % h["immature_cohorts"],
                        "aggregation": "sum" if weighted else "mean", "value": h.get("retained")}]
                      + ([{"file": base, "sheet": r["sheet"], "column": a.size_col, "filter": "same cohorts",
                           "aggregation": "sum", "value": h.get("cohort_size_sum")}] if weighted else []),
                      "size-weighted mature-cohort rate" if weighted else "mean of mature-cohort rates",
                      "dqg-cohort", note))
    return r, recs


def c_anomaly(a):
    r = m_anomaly.anomaly(a.file, a.date_col, a.metric_col, a.group_col, a.sheet, a.decimal, a.date_order,
                          a.trend_window, a.test_window, a.sigma, a.weekday_weeks)
    base = os.path.basename(a.file)
    pre = _lab(a, a.metric_col)
    note = r.get("dropped_note")
    recs = []
    for s in r["series"]:
        grp = (", %s = %s" % (a.group_col, s["group"])) if s["group"] else ""
        for meth, key in (("rolling-sigma", "rolling_sigma"), ("same-weekday", "same_weekday")):
            block = s[key]
            if not block["run"]:
                recs.append(R("anomaly", "%s: %s scan%s" % (pre, meth, grp), block["reason"], None, "history check",
                              [{"file": base, "sheet": r["sheet"], "column": a.metric_col,
                                "aggregation": "daily sum", "value": s["dates"]}], meth, "dqg-anomaly", note))
                continue
            for f in block["flags"]:
                recs.append(R("anomaly", "%s: %s z-score %s%s%s" % (pre, meth, f["date"], grp,
                                                                  " (low-power)" if f.get("low_power") else ""),
                              f["z"], "z",
                              "(log change - mean of %d prior changes) / sd" % a.trend_window
                              if key == "rolling_sigma"
                              else "(value - mean of %d prior same weekdays) / sd" % f.get("baseline_points", 0),
                              [{"file": base, "sheet": r["sheet"], "column": a.metric_col,
                                "filter": "date = %s%s" % (f["date"], grp), "aggregation": "daily sum",
                                "value": f["value"]}],
                              meth, "dqg-anomaly", note))
    return r, recs


def c_join(a):
    keys = [k.strip() for k in a.keys.split(",")]
    rk = [k.strip() for k in a.right_keys.split(",")] if a.right_keys else None
    r = m_joins.join_audit(a.left, a.right, keys, rk, a.left_sheet, a.right_sheet, a.casefold, a.min_coverage)
    ins = [{"file": r["left"]["file"], "sheet": a.left_sheet, "column": ",".join(keys), "aggregation": "count rows",
            "value": r["left"]["rows"]},
           {"file": r["right"]["file"], "sheet": a.right_sheet, "column": ",".join(rk or keys),
            "aggregation": "count rows", "value": r["right"]["rows"]}]
    pre = _lab(a, "Join %s x %s on %s" % (r["left"]["file"], r["right"]["file"], ",".join(keys)))
    recs = [R("join-audit", pre + ": rows after inner join", r["rows_after"]["inner"], "rows",
              "sum over matched keys of left count x right count", ins, "join row count", "dqg-join"),
            R("join-audit", pre + ": fan-out factor", r["fan_out"]["inner_rows_over_larger_input"], "x",
              "inner join rows / larger input rows", ins, "fan-out check", "dqg-join"),
            R("join-audit", pre + ": join verdict (mechanical)", r["mechanical_verdict"], None,
              "cardinality %s; coverage left %s, right %s" % (r["cardinality"], r["coverage"]["left_rows_matched_share"],
                                                           r["coverage"]["right_rows_matched_share"]),
              ins, "Join Safety Gate Q4, Q5, Q8 (counts feed Q1); mechanical upper bound", "dqg-join")]
    return r, recs


def _excl_text(r):
    n = len(r.get("excluded_rows") or [])
    return ("%d totals/subtotal row(s) excluded" % n) if n else ""


def _decompose_records(r, a, base, label=None):
    num, den, seg, pcol = r["num"], r["den"], r["segment_col"], a.period_col
    pre = label or "%s/%s by %s" % (num, den, seg)
    note = r.get("dropped_note")
    excl = _excl_text(r)

    def ins(p, extra=None):
        f = "%s = %s" % (pcol, p) + (", %s" % extra if extra else "")
        f += ("; " + excl) if excl else ""
        return [{"file": base, "sheet": r["sheet"], "column": num, "filter": f, "aggregation": "sum"},
                {"file": base, "sheet": r["sheet"], "column": den, "filter": f, "aggregation": "sum"}]
    both = ins(a.base) + ins(a.compare)
    K = "kitagawa1955"
    recs = [R("decompose", "%s: blended rate, base %s" % (pre, a.base), r["base"]["rate"], "rate",
              "sum %s / sum %s" % (num, den), ins(a.base), "blended rate", "arithmetic", note),
            R("decompose", "%s: blended rate, compare %s" % (pre, a.compare), r["compare"]["rate"], "rate",
              "sum %s / sum %s" % (num, den), ins(a.compare), "blended rate", "arithmetic", note),
            R("decompose", "%s: blended change" % pre, r["blended_change"], "pp", "compare rate - base rate", both,
              "difference of rates", "arithmetic", note),
            R("decompose", "%s: rate effect" % pre, r["rate_effect"], "pp",
              "sum_i (r1 - r0) (c0 + c1) / 2 over %s" % seg, both, "Kitagawa symmetric split", K, note),
            R("decompose", "%s: mix effect" % pre, r["mix_effect"], "pp",
              "sum_i (c1 - c0) (r0 + r1) / 2 over %s" % seg, both, "Kitagawa symmetric split", K, note)]
    for sg in r["segments"]:
        f = "%s = %s" % (seg, sg["segment"])
        s_both = ins(a.base, f) + ins(a.compare, f)
        recs += [
            R("decompose", "%s: %s rate, base %s" % (pre, f, a.base), sg["base"]["rate"], "rate",
              "sum %s / sum %s" % (num, den), ins(a.base, f), "segment rate", "arithmetic", note),
            R("decompose", "%s: %s rate, compare %s" % (pre, f, a.compare), sg["compare"]["rate"], "rate",
              "sum %s / sum %s" % (num, den), ins(a.compare, f), "segment rate", "arithmetic", note),
            R("decompose", "%s: %s rate term" % (pre, f), sg["rate_effect"], "pp", "(r1 - r0) (c0 + c1) / 2",
              s_both, "Kitagawa symmetric split, per segment", K, note),
            R("decompose", "%s: %s mix contribution" % (pre, f), sg["mix_contribution"], "pp",
              "(c1 - c0) ((r0 + r1) / 2 - (R0 + R1) / 2); sums to the mix effect", s_both,
              "Kitagawa mix term centered on the average blend, per segment", K, note)]
    return recs


def c_decompose(a):
    r = m_decompose.decompose(a.file, a.segment_col, a.num, a.den, a.period_col, a.base, a.compare, a.sheet,
                              a.decimal, a.date_order, _labels_arg(a))
    return r, _decompose_records(r, a, os.path.basename(a.file), a.label)


def c_drivers(a):
    dims = [d.strip() for d in a.dims.split(",") if d.strip()]
    r = m_drivers.drivers(a.file, a.metric_col, a.period_col, a.base, a.compare, dims, a.sheet, a.min_share,
                          a.cum_stop, a.den, a.force_additive, a.decimal, a.date_order, _labels_arg(a))
    base = os.path.basename(a.file)
    if r.get("error"):
        return r, []
    if r.get("delegated"):
        recs = []
        for sub in r["results"]:
            recs += _decompose_records(sub, a, base, (a.label + ", by " + sub["segment_col"]) if a.label else None)
        return r, recs
    pre = _lab(a, a.metric_col)
    note = r.get("dropped_note")
    excl = _excl_text(r)

    def inp(p, v, extra=None):
        return {"file": base, "sheet": r["sheet"], "column": a.metric_col,
                "filter": "%s = %s%s%s" % (a.period_col, p, (", " + extra) if extra else "",
                                           ("; " + excl) if excl else ""),
                "aggregation": "sum", "value": v}
    ins = [inp(a.base, r["base"]["total"]), inp(a.compare, r["compare"]["total"])]
    recs = [R("drivers", "%s: total, base %s" % (pre, a.base), r["base"]["total"], None, "sum of %s" % a.metric_col,
              ins[:1], "sum", "arithmetic", note),
            R("drivers", "%s: total, compare %s" % (pre, a.compare), r["compare"]["total"], None,
              "sum of %s" % a.metric_col, ins[1:], "sum", "arithmetic", note),
            R("drivers", "%s: change, %s to %s" % (pre, a.base, a.compare), r["total_change"], None,
              "compare total - base total", ins, "difference of totals", "arithmetic", note),
            R("drivers", "%s: relative change, %s to %s" % (pre, a.base, a.compare), r["relative_change"], "share",
              "(compare total - base total) / base total", ins, "relative change", "arithmetic", note)]

    def members(block, dim, within=None):
        out = []
        for m in block["ranked"]:
            f = "%s = %s" % (dim, m["value"]) + ((", " + within) if within else "")
            mi = [inp(a.base, m["base"], f), inp(a.compare, m["compare"], f)]
            out.append(R("drivers", "%s: change, %s" % (pre, f), m["delta"], None, "compare - base", mi,
                         "member change", "contribution", note))
            out.append(R("drivers", "%s: share of %s change, %s" % (pre, "the top member's" if within else "total", f),
                         m["share_of_total_change"], "share",
                         "member change / %s change" % ("top member's" if within else "total"), mi,
                         "contribution share", "contribution", note))
        return out
    for b in r["dimensions"]:
        recs += members(b, b["dimension"])
    if r.get("drill"):
        d = r["drill"]
        recs += members(d, d["by"], "%s = %s" % (d["within"]["dimension"], d["within"]["value"]))
    return r, recs


def c_aggregate(a):
    metrics = [m.strip() for x in (a.metric or []) for m in x.split(",") if m.strip()]
    r = m_aggregate.aggregate(a.file, metrics, a.agg, a.den, a.group_by, a.filter, a.period_col, a.period,
                              a.sheet, a.decimal, a.date_order, _labels_arg(a))
    base = os.path.basename(a.file)
    note = r.get("dropped_note")
    scope = ", ".join(r["filters"] + (["%s = %s" % (a.period_col, a.period)] if a.period_col else []))
    excl = _excl_text(r)
    recs = []
    for x in r["results"]:
        m = x["metric"]
        what = {"ratio": "sum %s / sum %s" % (m, a.den), "count": "count of rows" + (" with %s" % m if m else "")
                }.get(a.agg, "%s of %s" % (a.agg, m))
        pre = a.label or what
        grp = (", %s = %s" % (a.group_by, x["group"])) if x["scope"] == "group" else ""
        lab = "%s%s%s" % (pre, (" [%s]" % scope) if scope else "", grp)
        filt = "; ".join(b for b in (scope, grp.lstrip(", "), excl) if b)
        if a.agg == "ratio":
            ins = [{"file": base, "sheet": r["sheet"], "column": m, "filter": filt, "aggregation": "sum",
                    "value": x["num_sum"]},
                   {"file": base, "sheet": r["sheet"], "column": a.den, "filter": filt, "aggregation": "sum",
                    "value": x["den_sum"]}]
        else:
            ins = [{"file": base, "sheet": r["sheet"], "column": m, "filter": filt, "aggregation": a.agg,
                    "value": x.get("values_used", x["rows"])}]
        if len(metrics) > 1 and a.label:
            lab = "%s (%s)%s" % (a.label, m, grp)
        recs.append(R("aggregate", lab, x["value"], a.unit if a.agg != "ratio" else (a.unit or "rate"),
                      what, ins, "plain aggregation", "aggregate", note))
    return r, recs


def c_trace_render(a):
    recs = m_trace.read(a.path)
    sys.stdout.write(m_trace.render(recs, a.format, a.lang))
    return None, []


# ---------------------------------------------------------------------------


def build_parser():
    p = argparse.ArgumentParser(prog="dbcalc.py", description=__doc__.split("\n\n")[0])
    p.add_argument("--version", action="version", version="dbcalc " + VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, file_opts=True):
        sp.add_argument("--trace", metavar="PATH", help="append trace records (JSON lines) to PATH")
        sp.add_argument("--label", help="label prefix for trace records")
        if file_opts:
            sp.add_argument("--sheet", help="xlsx sheet name (default: first sheet)")
            sp.add_argument("--decimal", choices=("auto", "dot", "comma"), default="auto")
            sp.add_argument("--date-order", choices=("auto", "dmy", "mdy"), default="auto")

    def excl(sp):
        sp.add_argument("--exclude-rows", action="append", metavar="LABELS",
                        help="comma-separated dimension labels whose rows are left out (repeatable), "
                             "e.g. the subtotal labels profile reported")

    s = sub.add_parser("profile", help="structure, locale, grain keys, totals rows, period, PII flags")
    s.add_argument("file")
    s.add_argument("--trace-sums", action="store_true",
                   help="also trace each measure column's sum (totals rows excluded)")
    common(s)
    s.set_defaults(fn=c_profile)

    st = sub.add_parser("stats", help="statistical tests")
    ss = st.add_subparsers(dest="stat", required=True)
    s = ss.add_parser("prop-diff", help="x1 n1 x2 n2: p2 - p1 with Newcombe CI and p-value")
    for k in ("x1", "n1", "x2", "n2"):
        s.add_argument(k, type=int)
    s.add_argument("--confidence", type=float, default=0.95)
    s.add_argument("--material", type=float, help="material effect as a proportion (0.005 = 0.5pp); "
                                                   "needs --structure")
    s.add_argument("--structure", choices=("independent", "single-series"), default=None,
                   help="independent groups (A/B arms) or one series before/after; required with --material")
    s.add_argument("--trend-gate", choices=("cleared", "not-cleared"), default="not-cleared")
    s.add_argument("--inputs-json", help="JSON list of {file, sheet, column, filter, aggregation} for x1 n1 x2 n2")
    common(s, False)
    s.set_defaults(fn=c_prop_diff)
    s = ss.add_parser("welch", help="difference in means, Welch interval")
    s.add_argument("--summary", nargs=6, type=float, metavar=("MEAN1", "SD1", "N1", "MEAN2", "SD2", "N2"))
    s.add_argument("--a", help="comma-separated sample 1")
    s.add_argument("--b", help="comma-separated sample 2")
    s.add_argument("--file")
    s.add_argument("--value-col")
    s.add_argument("--group-col")
    s.add_argument("--groups", help="G1,G2 (difference is G2 - G1)")
    s.add_argument("--confidence", type=float, default=0.95)
    s.add_argument("--material", type=float, help="material effect in the metric's units; needs --structure")
    s.add_argument("--structure", choices=("independent", "single-series"), default=None)
    s.add_argument("--trend-gate", choices=("cleared", "not-cleared"), default="not-cleared")
    s.add_argument("--unit", default=None)
    s.add_argument("--inputs-json")
    common(s)
    s.set_defaults(fn=c_welch)
    s = ss.add_parser("holm", help="Holm-adjusted p-values")
    s.add_argument("pvalues", nargs="+")
    s.add_argument("--alpha", type=float, default=0.05)
    s.add_argument("--labels", help="comma-separated labels, one per p-value")
    common(s, False)
    s.set_defaults(fn=c_holm)
    s = ss.add_parser("srm", help="sample ratio mismatch (chi-square)")
    s.add_argument("--counts", required=True, help="assigned units per arm (users, not conversions), comma-separated")
    s.add_argument("--ratios", help="intended allocation, e.g. 50,50 (default equal)")
    s.add_argument("--threshold", type=float, default=m_stats.SRM_THRESHOLD)
    s.add_argument("--inputs-json")
    common(s, False)
    s.set_defaults(fn=c_srm)
    s = ss.add_parser("classify", help="SUPPORTED / NEGLIGIBLE / INCONCLUSIVE / UNTESTED / NOT APPLICABLE")
    s.add_argument("--low", type=float)
    s.add_argument("--high", type=float)
    s.add_argument("--material", type=float)
    s.add_argument("--structure", choices=("independent", "single-series"), default=None,
                   help="required with an interval and --material")
    s.add_argument("--trend-gate", choices=("cleared", "not-cleared"), default="not-cleared")
    s.add_argument("--not-applicable", action="store_true")
    s.add_argument("--untested-reason")
    common(s, False)
    s.set_defaults(fn=c_classify)

    s = sub.add_parser("cohort", help="cohort matrix with right-censored cells marked missing")
    s.add_argument("file")
    s.add_argument("--cohort-col", required=True)
    s.add_argument("--export-date", required=True, help="YYYY-MM-DD")
    s.add_argument("--wide", action="store_true", help="offset columns such as D1, D7, W1, M1")
    s.add_argument("--age-col", help="long format: offset column")
    s.add_argument("--value-col", help="long format: value column")
    s.add_argument("--size-col", help="cohort size column (weights)")
    s.add_argument("--value-kind", choices=("auto", "count", "rate", "rate_percent"), default="auto")
    s.add_argument("--cohort-span", choices=("auto", "day", "week", "month"), default="auto")
    common(s)
    s.set_defaults(fn=c_cohort)

    s = sub.add_parser("anomaly", help="rolling 3-sigma scan and same-weekday baseline")
    s.add_argument("file")
    s.add_argument("--date-col", required=True)
    s.add_argument("--metric-col", required=True)
    s.add_argument("--group-col")
    s.add_argument("--trend-window", type=int, default=m_anomaly.TREND)
    s.add_argument("--test-window", type=int, default=m_anomaly.TEST)
    s.add_argument("--sigma", type=float, default=m_anomaly.SIGMA)
    s.add_argument("--weekday-weeks", type=int, default=m_anomaly.SAME_WD_WEEKS,
                   help="prior same weekdays in the baseline (default 4; 8 gives full power)")
    common(s)
    s.set_defaults(fn=c_anomaly)

    s = sub.add_parser("join-audit", help="key uniqueness, fan-out, coverage before a join")
    s.add_argument("left")
    s.add_argument("right")
    s.add_argument("--keys", required=True)
    s.add_argument("--right-keys")
    s.add_argument("--left-sheet")
    s.add_argument("--right-sheet")
    s.add_argument("--casefold", action="store_true")
    s.add_argument("--min-coverage", type=float, default=m_joins.MIN_COVERAGE)
    common(s, False)
    s.set_defaults(fn=c_join)

    s = sub.add_parser("decompose", help="Kitagawa rate/mix decomposition of a blended rate change")
    s.add_argument("file")
    s.add_argument("--segment-col", required=True)
    s.add_argument("--num", required=True)
    s.add_argument("--den", required=True)
    s.add_argument("--period-col", required=True)
    s.add_argument("--base", required=True, help="value, YYYY-MM, or YYYY-MM-DD..YYYY-MM-DD")
    s.add_argument("--compare", required=True)
    excl(s)
    common(s)
    s.set_defaults(fn=c_decompose)

    s = sub.add_parser("drivers", help="contribution analysis of an additive total's change")
    s.add_argument("file")
    s.add_argument("--metric-col", required=True)
    s.add_argument("--period-col", required=True)
    s.add_argument("--base", required=True)
    s.add_argument("--compare", required=True)
    s.add_argument("--dims", required=True, help="d1,d2,...")
    s.add_argument("--min-share", type=float, default=0.25)
    s.add_argument("--cum-stop", type=float, default=0.5)
    s.add_argument("--den", help="denominator column: treats the metric as a ratio and runs decompose")
    s.add_argument("--force-additive", action="store_true")
    excl(s)
    common(s)
    s.set_defaults(fn=c_drivers)

    s = sub.add_parser("aggregate", help="plain KPI values: sum, count, mean, min, max, ratio of sums")
    s.add_argument("file")
    s.add_argument("--metric", action="append", help="metric column(s), comma-separated or repeated")
    s.add_argument("--agg", choices=m_aggregate.AGGS, default="sum")
    s.add_argument("--den", help="denominator column for --agg ratio (sum metric / sum den)")
    s.add_argument("--group-by", help="one dimension column; values are printed scrubbed")
    s.add_argument("--filter", action="append", metavar="COL=VALUE", help="exact-match row filter (repeatable, ANDed)")
    s.add_argument("--period-col")
    s.add_argument("--period", help="value, YYYY-MM, or YYYY-MM-DD..YYYY-MM-DD")
    s.add_argument("--unit", help="unit for the trace (e.g. a currency code from the source)")
    excl(s)
    common(s)
    s.set_defaults(fn=c_aggregate)

    s = sub.add_parser("trace", help="render a trace file")
    ts = s.add_subparsers(dest="tcmd", required=True)
    r = ts.add_parser("render")
    r.add_argument("path")
    r.add_argument("--format", choices=("md", "html"), default="md")
    r.add_argument("--lang", choices=("en", "tr"), default="en",
                   help="table language and number format; label tokens stay in English")
    r.set_defaults(fn=c_trace_render)
    return p


def _error(cmd, msg, kind=None):
    doc = {"command": cmd, "error": msg}
    if kind:
        doc["error_type"] = kind
    sys.stdout.write(json.dumps(doc, ensure_ascii=False) + "\n")
    return 2


def main(argv=None):
    p = build_parser()
    a = p.parse_args(argv)
    cmd = a.cmd if a.cmd != "stats" else a.stat
    try:
        res, recs = a.fn(a)
        if res is not None and getattr(a, "trace", None):
            n = m_trace.append(a.trace, [_clean(r) for r in recs])
            res["trace"] = {"path": os.path.basename(a.trace), "records_appended": n,
                            "records_already_present": len(recs) - n}
    except (tabular.InputError, ValueError) as e:  # includes trace.TraceError and json errors
        return _error(cmd, str(e))
    except csv.Error as e:
        return _error(cmd, "the file could not be parsed as CSV: %s" % e, "csv")
    except zipfile.BadZipFile:
        return _error(cmd, "the workbook is not a valid .xlsx (zip) file", "xlsx")
    except UnicodeDecodeError:
        return _error(cmd, "the file is not valid text in UTF-8", "encoding")
    except OSError as e:
        return _error(cmd, "file could not be read: %s" % (e.strerror or type(e).__name__), "io")
    except (KeyError, ZeroDivisionError, TypeError, IndexError, AttributeError) as e:
        return _error(cmd, "internal error (%s): %s; the input likely has an unexpected shape"
                      % (type(e).__name__, e), "internal")
    except Exception as e:  # noqa: BLE001 - never a traceback (e.g. a workbook parser error)
        return _error(cmd, "could not process the input (%s): %s" % (type(e).__name__, e), "internal")
    if res is None:
        return 0
    sys.stdout.write(json.dumps(_clean(res), ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    return 0 if not res.get("error") else 2


if __name__ == "__main__":
    sys.exit(main())
