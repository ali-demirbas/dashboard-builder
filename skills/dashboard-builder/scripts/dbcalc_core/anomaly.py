"""`anomaly`: rolling-sigma scan and same-weekday baseline on a daily metric.

references/data-quality-gate.md §5 Distributional:

- Rolling-sigma scan. Default state window: 7-day trend window, 14-day test
  window, 3-sigma threshold, log transform with a 1-day difference (the
  defaults of the open-source dbt-expectations macro
  expect_column_values_to_be_within_n_moving_stdevs, which the reference
  cites). For day t: change_t = ln(v_t) - ln(v_{t-1}) (a zero value
  contributes 0, as in that macro); baseline = mean and sample SD of the 7
  preceding changes (the current day excluded); z = (change_t - mean) / SD.
  The test window is the last 14 dates in the file (relative to the newest
  date, not today). Every tested day needs 7 prior changes and every change
  needs a prior date, so the scan runs only with >= 22 dates present
  (trend + test + 1). A change across a calendar gap (a missing date) spans
  more than one day: it is labeled ``multi_day_gap`` and neither scored nor
  used in a baseline.
- Same-weekday baseline: the tested day against the mean and sample SD of
  the same weekday in the 4 prior weeks (t-7, -14, -21, -28). Needs >= 28
  days of history before the tested day (>= 29 including it). Working
  convention (unverified, directional only): a day is flagged only with at
  least 4 baseline points (MIN_WEEKDAY_POINTS); with fewer than 8
  (FULL_POWER_POINTS) every result is labeled ``low_power`` — a sample SD
  from 4-7 points is itself noisy, so |z| > 3 happens by chance more often
  than the threshold suggests. ``--weekday-weeks 8`` uses 8 prior weeks.

Totals rows (labeled, blank dimensions with metrics, rows equal to the sum
of the other rows of the same date) are excluded before the daily sum, as in
``profile``.

Output is an anomaly *score*: a flagged day is a candidate for the anomaly
triage list, not a confirmed defect.
"""
import datetime as _dt
import math
import os
import statistics

from . import checks, tabular

TREND, TEST, SIGMA = 7, 14, 3.0
MIN_ROLLING = TREND + TEST + 1      # 22 dates
SAME_WD_WEEKS = 4                   # needs 28 days before the tested day
MIN_WEEKDAY_POINTS = 4              # no flag below this many baseline points
FULL_POWER_POINTS = 8               # below this, results are labeled low-power


def _series(typed, date_col, metric_col, group_col, exclude_rows):
    dates = typed.dates(date_col)
    vals = typed.numbers(metric_col)
    groups = typed.texts(group_col) if group_col else [None] * len(dates)
    agg = {}
    for i, (d, v, g) in enumerate(zip(dates, vals, groups)):
        if i in exclude_rows or d is None or v is None:
            continue
        agg.setdefault(g, {})
        agg[g][d] = agg[g].get(d, 0.0) + v
    return agg


def _have(ds):
    span = (ds[-1] - ds[0]).days + 1 if ds else 0
    return "%d dates present over a %d-day calendar span" % (len(ds), span)


def rolling(series, trend=TREND, test=TEST, sigma=SIGMA):
    ds = sorted(series)
    n = len(ds)
    need = trend + test + 1
    if n < need:
        return {"run": False, "reason": "not run: insufficient history (need >=%d dates, have %s)"
                % (need, _have(ds))}
    lv = [math.log(series[d]) if series[d] > 0 else 0.0 for d in ds]
    change = [None] * n
    gap = [0] * n
    for i in range(1, n):
        days = (ds[i] - ds[i - 1]).days
        if days == 1:
            change[i] = lv[i] - lv[i - 1]
        else:
            gap[i] = days
    tested = []
    for i in range(n - test, n):
        rec = {"date": ds[i].isoformat(), "value": series[ds[i]]}
        if gap[i]:
            rec.update({"z": None, "multi_day_gap": gap[i],
                        "note": "previous date missing: the change spans %d days and is not scored" % gap[i]})
            tested.append(rec)
            continue
        window = [c for c in change[i - trend:i] if c is not None]
        if len(window) < 2:
            rec.update({"z": None, "note": "baseline window too short (date gaps)"})
            tested.append(rec)
            continue
        mu = statistics.fmean(window)
        sd = statistics.stdev(window)
        z = None if sd == 0 else (change[i] - mu) / sd
        rec.update({"log_change": change[i], "baseline_mean": mu, "baseline_sd": sd,
                    "baseline_points": len(window), "z": z, "flag": z is not None and abs(z) > sigma})
        if len(window) < trend:
            rec["note"] = "baseline has %d of %d changes (date gaps)" % (len(window), trend)
        tested.append(rec)
    return {"run": True, "params": {"trend_window": trend, "test_window": test, "sigma": sigma,
                                    "transform": "ln, 1-day difference (changes across date gaps skipped)"},
            "dates_present": n, "span_days": (ds[-1] - ds[0]).days + 1,
            "tested": tested, "flags": [t for t in tested if t.get("flag")]}


def same_weekday(series, test=TEST, sigma=SIGMA, weeks=SAME_WD_WEEKS):
    ds = sorted(series)
    if not ds:
        return {"run": False, "reason": "not run: no data"}
    span = (ds[-1] - ds[0]).days + 1
    if span < 7 * weeks + 1:
        return {"run": False, "reason": "not run: insufficient history (need >=%d prior same weekdays / "
                ">=%d-day calendar span including the tested day, have %s)" % (weeks, 7 * weeks + 1, _have(ds))}
    tested = []
    for d in ds[-test:]:
        prior = [d - _dt.timedelta(days=7 * k) for k in range(1, weeks + 1)]
        have = [series[p] for p in prior if p in series]
        rec = {"date": d.isoformat(), "weekday": d.strftime("%A"), "value": series[d],
               "baseline_points": len(have)}
        if len(have) < MIN_WEEKDAY_POINTS or len(have) < 2:
            rec.update({"z": None, "note": "not scored: %d of %d prior %ss present (minimum %d)"
                        % (len(have), weeks, d.strftime("%A"), MIN_WEEKDAY_POINTS)})
        else:
            mu = statistics.fmean(have)
            sd = statistics.stdev(have)
            rec.update({"baseline_mean": mu, "baseline_sd": sd,
                        "pct_vs_baseline": None if mu == 0 else (series[d] - mu) / mu,
                        "z": None if sd == 0 else (series[d] - mu) / sd,
                        "low_power": len(have) < FULL_POWER_POINTS})
            rec["flag"] = rec["z"] is not None and abs(rec["z"]) > sigma
        tested.append(rec)
    low = any(t.get("low_power") for t in tested)
    return {"run": True, "params": {"prior_weeks": weeks, "sigma": sigma,
                                    "min_points_to_flag": MIN_WEEKDAY_POINTS,
                                    "full_power_points": FULL_POWER_POINTS},
            "power": ("low-power: fewer than %d baseline points per day; read flags as weak candidates"
                      % FULL_POWER_POINTS) if low else "full",
            "tested": tested, "flags": [t for t in tested if t.get("flag")]}


def weekday_profile(series):
    by = {}
    for d, v in series.items():
        by.setdefault(d.weekday(), []).append(v)
    if len(by) < 7:
        return None
    means = [statistics.fmean(by[k]) for k in range(7)]
    overall = statistics.fmean(means)
    return {"weekday_means": dict(zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], means)),
            "max_over_min": None if min(means) == 0 else max(means) / min(means),
            "spread_vs_mean": None if overall == 0 else (max(means) - min(means)) / overall}


def anomaly(path, date_col, metric_col, group_col=None, sheet=None, decimal="auto", date_order="auto",
            trend=TREND, test=TEST, sigma=SIGMA, weeks=SAME_WD_WEEKS):
    tbl = tabular.load(path, sheet)
    typed = tabular.Typed(tbl, decimal, date_order)
    if group_col:
        checks.guard_dimension(group_col, typed.texts(group_col), "--group-col")
    others = [h for h in tbl.headers if h not in (date_col, metric_col)]
    kinds = {h: typed.kind(h) for h in others}
    label_cols = {h: typed.texts(h) for h in others if kinds[h] == "text"
                  and not checks.identifier_reason_from_header(h)}
    numeric = {metric_col: typed.numbers(metric_col)}
    for h in others:
        if kinds[h] == "number" and not checks.identifier_reason_from_header(h) \
                and "id" not in checks.header_tokens(h):
            numeric[h] = typed.numbers(h)
    group_key = typed.dates(date_col)
    totals = checks.total_rows(label_cols, numeric, group_key)
    excl = {t["row"] - 1 for t in totals}
    agg = _series(typed, date_col, metric_col, group_col, excl)
    results = []
    for g in sorted(agg, key=lambda x: "" if x is None else x):
        s = agg[g]
        ds = sorted(s)
        gaps = []
        if ds:
            have = set(ds)
            d = ds[0]
            while d <= ds[-1]:
                if d not in have:
                    gaps.append(d.isoformat())
                d += _dt.timedelta(days=1)
        results.append({"group": checks.scrub(g) if g else None,
                        "period": {"first": ds[0].isoformat(), "last": ds[-1].isoformat()} if ds else None,
                        "dates": len(ds), "span_days": (ds[-1] - ds[0]).days + 1 if ds else 0,
                        "missing_dates": gaps[:20], "missing_dates_count": len(gaps),
                        "rolling_sigma": rolling(s, trend, test, sigma),
                        "same_weekday": same_weekday(s, test, sigma, weeks),
                        "weekday_profile": weekday_profile(s)})
    warns, note = typed.dropped([date_col, metric_col])
    return {"command": "anomaly", "file": os.path.basename(path), "sheet": tbl.name,
            "metric": metric_col, "date_col": date_col, "group_col": group_col,
            "excluded_totals_rows": [t["row"] for t in totals],
            "excluded_totals_" + tbl.locator() + "s": [tbl.lines[t["row"] - 1] for t in totals],
            "note": "anomaly scores, not confirmed anomalies: run each flag through anomaly triage",
            "dropped_note": note,
            "series": results, "warnings": typed.warnings + warns}
