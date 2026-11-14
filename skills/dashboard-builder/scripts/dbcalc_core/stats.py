"""Statistical methods used by the dashboard-builder skill.

Pure standard library. Special functions (regularized incomplete beta and
gamma) are implemented with the classic continued-fraction / series
expansions; quantiles are found by bisection, which is slow but exact to
floating precision and fully deterministic.

Nothing here rounds. Rounding happens only at presentation (trace.render).
"""
import math
from statistics import NormalDist

_ND = NormalDist()

# ---------------------------------------------------------------------------
# Special functions
# ---------------------------------------------------------------------------


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (modified Lentz)."""
    fpmin = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = fpmin if abs(d) < fpmin else d
        c = 1.0 + aa / c
        c = fpmin if abs(c) < fpmin else c
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = fpmin if abs(d) < fpmin else d
        c = 1.0 + aa / c
        c = fpmin if abs(c) < fpmin else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
           + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def gammaincc(a, x):
    """Regularized upper incomplete gamma Q(a, x)."""
    if x <= 0.0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:  # series for P, then Q = 1 - P
        ap, s, delta = a, 1.0 / a, 1.0 / a
        for _ in range(10000):
            ap += 1.0
            delta *= x / ap
            s += delta
            if abs(delta) < abs(s) * 1e-16:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gln)
    fpmin = 1e-300  # continued fraction for Q directly (keeps tiny p precise)
    b = x + 1.0 - a
    c = 1.0 / fpmin
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = fpmin if abs(d) < fpmin else d
        c = b + an / c
        c = fpmin if abs(c) < fpmin else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-16:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def norm_ppf(p):
    return _ND.inv_cdf(p)


def t_sf_two_sided(t, df):
    """Two-sided p-value of Student's t with df degrees of freedom."""
    if math.isinf(df):
        return 2.0 * norm_sf(abs(t))
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_ppf_two_sided(alpha, df):
    """q such that P(|T| > q) = alpha, by bisection."""
    lo, hi = 0.0, 1.0
    while t_sf_two_sided(hi, df) > alpha:
        hi *= 2.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_sf_two_sided(mid, df) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def chi2_sf(x, df):
    return gammaincc(df / 2.0, x / 2.0)


# ---------------------------------------------------------------------------
# Proportions
# ---------------------------------------------------------------------------


def wilson_interval(x, n, confidence=0.95):
    """Wilson score interval for a single binomial proportion.

    Method: Wilson, E. B. (1927). Probable inference, the law of succession,
    and statistical inference. Journal of the American Statistical
    Association, 22(158), 209-212. Citation key ``wilson1927``.

    Known answer: 81/263 gives 0.2553 to 0.3662 (Newcombe 1998, Statistics in
    Medicine 17:857-872, the single-proportion companion paper, method 3).
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= x <= n:
        raise ValueError("x must lie in [0, n]")
    z = norm_ppf(1.0 - (1.0 - confidence) / 2.0)
    p = x / n
    z2 = z * z
    centre = 2 * n * p + z2
    half = z * math.sqrt(z2 + 4 * n * p * (1 - p))
    denom = 2 * (n + z2)
    lo = (centre - half) / denom
    hi = (centre + half) / denom
    # Exact boundary values when x is 0 or n.
    if x == 0:
        lo = 0.0
    if x == n:
        hi = 1.0
    return lo, hi


def newcombe_interval(x1, n1, x2, n2, confidence=0.95):
    """Newcombe hybrid-score interval for p2 - p1 (independent proportions).

    Method 10 of Newcombe, R. G. (1998). Interval estimation for the
    difference between independent proportions: comparison of eleven
    methods. Statistics in Medicine, 17(8), 873-890. Citation key
    ``newcombe1998``. Built from the Wilson (1927) score limits of each
    proportion, no continuity correction.

    Known answer (paper's Table II, example a): 56/70 - 48/80 = 0.2000,
    95% CI 0.0524 to 0.3339. Here the difference is second minus first, so
    ``newcombe_interval(48, 80, 56, 70)`` returns that interval.
    """
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson_interval(x1, n1, confidence)
    l2, u2 = wilson_interval(x2, n2, confidence)
    d = p2 - p1
    lower = d - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2)
    upper = d + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)
    return d, lower, upper


def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact test for the 2x2 table [[a, b], [c, d]].

    Method: Fisher, R. A. (1935). The Design of Experiments, Oliver & Boyd
    (the exact conditional test on a 2x2 table with fixed margins); also
    Fisher, R. A. (1922), On the interpretation of chi-square from
    contingency tables, JRSS 85(1), 87-94. Citation key ``fisher1935``.

    Two-sided p sums every table, with the same margins, whose hypergeometric
    probability does not exceed the observed one (relative tolerance 1e-7, the
    convention of common statistical software). Known answer: the
    tea-tasting table [[3, 1], [1, 3]] gives p = 0.4857 (= 34/70).
    Returns (p_value, sample_odds_ratio or None when undefined).
    """
    for v in (a, b, c, d):
        if v < 0 or int(v) != v:
            raise ValueError("cells must be non-negative integers")
    a, b, c, d = int(a), int(b), int(c), int(d)
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    lo, hi = max(0, c1 - r2), min(r1, c1)

    def lp(k):
        return (math.lgamma(r1 + 1) - math.lgamma(k + 1) - math.lgamma(r1 - k + 1)
                + math.lgamma(r2 + 1) - math.lgamma(c1 - k + 1) - math.lgamma(r2 - c1 + k + 1)
                - math.lgamma(n + 1) + math.lgamma(c1 + 1) + math.lgamma(n - c1 + 1))

    obs = lp(a)
    thresh = obs + math.log1p(1e-7)
    p = 0.0
    for k in range(lo, hi + 1):
        lk = lp(k)
        if lk <= thresh:
            p += math.exp(lk)
    p = min(1.0, p)
    odds = None if b * c == 0 else (a * d) / (b * c)
    return p, odds


def two_proportion_z(x1, n1, x2, n2):
    """Pooled two-proportion z-test of p2 - p1 (normal approximation).

    Two-sided p from the standard normal. Returns (z, p) or (None, None)
    when the pooled variance is zero (both groups all-success or all-failure).
    """
    pp = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    if se == 0:
        return None, None
    z = (x2 / n2 - x1 / n1) / se
    return z, 2.0 * norm_sf(abs(z))


SMALL_COUNT = 10


def prop_diff(x1, n1, x2, n2, confidence=0.95):
    """Difference between two independent proportions, p2 - p1.

    Reports what analysis-playbook.md §Statistical sufficiency Step 2 asks
    for together: absolute difference, relative change, the Newcombe (1998,
    method 10) hybrid-score interval, n per group, and a two-sided p.
    The p-value is Fisher's exact test (Fisher 1935) when any group has
    fewer than 10 successes or 10 failures (the playbook's rule of thumb),
    otherwise the pooled two-proportion z-test.
    Citation keys: ``newcombe1998``, ``wilson1927``, ``fisher1935``.
    """
    for x, n in ((x1, n1), (x2, n2)):
        if n <= 0 or not 0 <= x <= n:
            raise ValueError("each group needs 0 <= x <= n and n > 0")
    p1, p2 = x1 / n1, x2 / n2
    d, lo, hi = newcombe_interval(x1, n1, x2, n2, confidence)
    small = min(x1, n1 - x1, x2, n2 - x2) < SMALL_COUNT
    if small:
        p, odds = fisher_exact(x2, n2 - x2, x1, n1 - x1)
        test, z = "fisher_exact", None
    else:
        z, p = two_proportion_z(x1, n1, x2, n2)
        test, odds = "two_proportion_z", None
        if p is None:
            p = 1.0
    rel = None if p1 == 0 else (p2 - p1) / p1
    return {
        "p1": p1, "p2": p2, "n1": n1, "n2": n2, "x1": x1, "x2": x2,
        "difference": d, "ci_low": lo, "ci_high": hi, "confidence": confidence,
        "relative_change": rel,
        "relative_change_note": None if rel is not None else "Not meaningful — zero base rate",
        "p_value": p, "test": test, "z": z, "odds_ratio": odds,
        "wilson_1": list(wilson_interval(x1, n1, confidence)),
        "wilson_2": list(wilson_interval(x2, n2, confidence)),
        "interval_method": "newcombe_hybrid_score_method10",
    }


# ---------------------------------------------------------------------------
# Means
# ---------------------------------------------------------------------------


def welch(mean1, sd1, n1, mean2, sd2, n2, confidence=0.95):
    """Welch interval and test for mean2 - mean1 with unequal variances.

    Method: Welch, B. L. (1947). The generalization of 'Student's' problem
    when several different population variances are involved. Biometrika,
    34(1-2), 28-35. Degrees of freedom by the Welch-Satterthwaite
    approximation. Citation key ``welch1947``.
    """
    if n1 < 2 or n2 < 2:
        raise ValueError("each sample needs n >= 2")
    v1, v2 = sd1 * sd1 / n1, sd2 * sd2 / n2
    se = math.sqrt(v1 + v2)
    diff = mean2 - mean1
    if se == 0:
        raise ValueError("both samples have zero variance; the interval is undefined")
    df = (v1 + v2) ** 2 / (v1 * v1 / (n1 - 1) + v2 * v2 / (n2 - 1))
    t = diff / se
    p = t_sf_two_sided(t, df)
    q = t_ppf_two_sided(1.0 - confidence, df)
    return {
        "mean1": mean1, "mean2": mean2, "sd1": sd1, "sd2": sd2, "n1": n1, "n2": n2,
        "difference": diff, "se": se, "df": df, "t": t, "p_value": p,
        "ci_low": diff - q * se, "ci_high": diff + q * se, "confidence": confidence,
        "relative_change": None if mean1 == 0 else diff / mean1,
    }


def welch_samples(a, b, confidence=0.95):
    """Welch (1947) on two raw samples (sample SD with n - 1)."""
    import statistics
    return welch(statistics.fmean(a), statistics.stdev(a), len(a),
                 statistics.fmean(b), statistics.stdev(b), len(b), confidence)


# ---------------------------------------------------------------------------
# Multiple comparisons, SRM
# ---------------------------------------------------------------------------


def holm(pvalues, alpha=0.05):
    """Holm step-down adjusted p-values, returned in the input order.

    Method: Holm, S. (1979). A simple sequentially rejective multiple test
    procedure. Scandinavian Journal of Statistics, 6(2), 65-70. Citation key
    ``holm1979``. adj_(i) = max_{j<=i} min(1, (m - j + 1) p_(j)); ties are
    ordered by input position so the result is deterministic.
    """
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: (pvalues[i], i))
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvalues[i])
        running = max(running, val)
        adj[i] = running
    return {"m": m, "alpha": alpha, "adjusted": adj,
            "reject": [a <= alpha for a in adj],
            "bonferroni_interval_confidence": 1.0 - alpha / m if m else None}


SRM_THRESHOLD = 0.001


def srm(observed, ratios=None, threshold=SRM_THRESHOLD):
    """Sample ratio mismatch check: chi-square goodness of fit of arm counts.

    Method: Pearson's chi-square goodness-of-fit test (Pearson, K. 1900,
    Philosophical Magazine 50(302), 157-175) applied as the SRM check
    described in Fabijan, A., Gupchup, J., Gupta, S., Omhover, J., Qin, W.,
    Vermeer, L., Dmitriev, P. (2019). Diagnosing Sample Ratio Mismatch in
    Online Controlled Experiments: A Taxonomy and Rules of Thumb for
    Practitioners. KDD '19, doi:10.1145/3292500.3330722. Citation key
    ``fabijan2019``. The paper's example, 821,588 vs 815,482 users on a
    50/50 design, has a chance probability below 1 in 500,000.

    Counts are assigned units per arm (users, devices, accounts), never
    conversions. Mismatch is flagged when p < threshold (default 0.001, the
    working convention of references/analysis-playbook.md §Statistical
    sufficiency, "Sample ratio mismatch"; the paper fixes no threshold, so the
    p-value is always reported). A mismatch is a BLOCKER for that result only
    (data-quality-gate.md §Severity rules).
    """
    k = len(observed)
    if k < 2:
        raise ValueError("need at least two arms")
    if ratios is None:
        ratios = [1.0] * k
    if len(ratios) != k or any(r <= 0 for r in ratios):
        raise ValueError("ratios must be positive, one per arm")
    total = float(math.fsum(observed))
    rsum = float(math.fsum(ratios))
    expected = [total * r / rsum for r in ratios]
    chi2 = math.fsum((o - e) ** 2 / e for o, e in zip(observed, expected))
    p = chi2_sf(chi2, k - 1)
    return {
        "observed": list(observed), "expected": expected,
        "observed_share": [o / total for o in observed],
        "expected_share": [r / rsum for r in ratios],
        "chi2": chi2, "df": k - 1, "p_value": p, "threshold": threshold,
        "mismatch": p < threshold,
        "severity": "BLOCKER" if p < threshold else None,
    }


# ---------------------------------------------------------------------------
# Outcome classification
# ---------------------------------------------------------------------------

OUTCOMES = ("SUPPORTED", "NEGLIGIBLE", "INCONCLUSIVE", "UNTESTED", "NOT APPLICABLE")


def classify(low=None, high=None, material=None, structure="independent",
             trend_gate_cleared=None, not_applicable=False, untested_reason=None):
    """Read an interval against the material threshold.

    Implements the five outcomes of question 2 in
    references/analysis-playbook.md §Insight candidate engine, as defined in
    §Statistical sufficiency, Step 3 (and the single-series cap in Step 1):

    - SUPPORTED: the interval excludes zero and reaches an effect that would
      matter (|bound| >= material on the side away from zero).
    - NEGLIGIBLE: the interval is tight and excludes any effect that would
      matter (-material < low and high < material), whether or not it also
      excludes zero; a tight interval between zero and the threshold is
      NEGLIGIBLE, not SUPPORTED.
    - INCONCLUSIVE: the interval includes zero and effects that would matter.
      Volume-limit sub-case: it spans both a material loss and a material
      gain; that is a limitation, not a finding.
    - UNTESTED: no interval (no compute, no valid test for the structure), or
      a single-series before/after read whose trend gate did not clear: the
      interval is then a sampling-noise floor only.
    - NOT APPLICABLE: a plain population total or count with no sampling
      question.

    ``material`` is a positive magnitude in the interval's own units (for a
    rate difference, a proportion: 0.005 = 0.5pp). Citation key
    ``playbook-sufficiency``.
    """
    if not_applicable:
        return {"outcome": "NOT APPLICABLE", "volume_limit": False,
                "reason": "plain population total or count; no sampling question"}
    if low is None or high is None:
        return {"outcome": "UNTESTED", "volume_limit": False,
                "reason": untested_reason or "no interval supplied"}
    if material is None or material <= 0:
        raise ValueError("material threshold must be a positive number")
    if low > high:
        low, high = high, low
    excludes_zero = low > 0 or high < 0
    if -material < low and high < material:
        outcome, vol = "NEGLIGIBLE", False
        reason = "interval lies strictly inside (-material, +material)"
    elif excludes_zero:
        outcome, vol = "SUPPORTED", False
        reason = "interval excludes zero and reaches the material threshold"
    else:
        vol = low <= -material and high >= material
        outcome = "INCONCLUSIVE"
        reason = ("interval spans both a material loss and a material gain "
                  "(volume limit: state as a limitation, not a finding)" if vol
                  else "interval includes zero and a material effect")
    result = {"outcome": outcome, "volume_limit": vol, "reason": reason,
              "low": low, "high": high, "material": material,
              "excludes_zero": excludes_zero}
    if structure == "single-series" and not trend_gate_cleared:
        result["noise_floor_outcome"] = outcome
        result["outcome"] = "UNTESTED"
        result["volume_limit"] = False
        result["reason"] = ("single-series before/after read: the interval is a "
                            "sampling-noise floor only and the trend gate did not "
                            "clear (playbook Step 1); noise-floor reading was "
                            + outcome)
    return result
