"""Known-answer tests for dbcalc's statistical methods.

Published reference values:
- Newcombe (1998), Statistics in Medicine 17:873-890, Table II, method 10
  (hybrid score, no continuity correction): 56/70 - 48/80 -> 0.0524, 0.3339;
  9/10 - 3/10 -> 0.1705, 0.8090; 10/10 - 0/10 -> 0.6075, 1.0000.
- Wilson (1927) score interval, 81/263 -> 0.2553, 0.3662 (Newcombe 1998,
  Statistics in Medicine 17:857-872, method 3).
- Fisher exact, tea-tasting table [[3, 1], [1, 3]]: two-sided p = 34/70.
- SRM: Fabijan et al. (KDD 2019), 821,588 vs 815,482 on a 50/50 design has a
  chance probability below 1 in 500,000.
Welch and chi-square values are cross-checked against scipy when installed.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "dashboard-builder", "scripts"))

from dbcalc_core import stats  # noqa: E402

try:
    import scipy.stats as sps  # noqa: F401
    HAVE_SCIPY = True
except Exception:  # pragma: no cover - optional
    HAVE_SCIPY = False

A1 = [27.5, 21.0, 19.0, 23.6, 17.0, 17.9, 16.9, 20.1, 21.9, 22.6, 23.1, 19.6, 19.0, 21.7, 21.4]
A2 = [27.1, 22.0, 20.8, 23.4, 23.4, 23.5, 25.8, 22.0, 24.8, 20.2, 21.9, 22.1, 22.9, 20.5, 24.4]


class TestNewcombe(unittest.TestCase):
    def test_table2_example_a(self):
        d, lo, hi = stats.newcombe_interval(48, 80, 56, 70)
        self.assertAlmostEqual(d, 0.2, places=12)
        self.assertAlmostEqual(lo, 0.0524, places=4)
        self.assertAlmostEqual(hi, 0.3339, places=4)

    def test_table2_example_b(self):
        _, lo, hi = stats.newcombe_interval(3, 10, 9, 10)
        self.assertAlmostEqual(lo, 0.1705, places=4)
        self.assertAlmostEqual(hi, 0.8090, places=4)

    def test_table2_example_h_boundary(self):
        _, lo, hi = stats.newcombe_interval(0, 10, 10, 10)
        self.assertAlmostEqual(lo, 0.6075, places=4)
        self.assertEqual(hi, 1.0)

    def test_direction_is_second_minus_first(self):
        d, lo, hi = stats.newcombe_interval(56, 70, 48, 80)
        self.assertAlmostEqual(d, -0.2, places=12)
        self.assertAlmostEqual(lo, -0.3339, places=4)
        self.assertAlmostEqual(hi, -0.0524, places=4)


class TestWilson(unittest.TestCase):
    def test_81_of_263(self):
        lo, hi = stats.wilson_interval(81, 263)
        self.assertAlmostEqual(lo, 0.2553, places=4)
        self.assertAlmostEqual(hi, 0.3662, places=4)

    def test_zero_and_full(self):
        lo, hi = stats.wilson_interval(0, 20)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.1611, places=4)
        lo, hi = stats.wilson_interval(20, 20)
        self.assertEqual(hi, 1.0)
        self.assertAlmostEqual(lo, 1 - 0.1611, places=4)


class TestFisher(unittest.TestCase):
    def test_tea_tasting(self):
        p, odds = stats.fisher_exact(3, 1, 1, 3)
        self.assertAlmostEqual(p, 34 / 70, places=12)
        self.assertEqual(odds, 9.0)

    def test_extreme_table(self):
        p, _ = stats.fisher_exact(4, 0, 0, 4)
        self.assertAlmostEqual(p, 2 / 70, places=12)

    def test_prop_diff_routes_small_counts_to_fisher(self):
        r = stats.prop_diff(1, 10, 6, 10)
        self.assertEqual(r["test"], "fisher_exact")
        r = stats.prop_diff(48, 80, 56, 70)
        self.assertEqual(r["test"], "two_proportion_z")

    @unittest.skipUnless(HAVE_SCIPY, "scipy not installed")
    def test_against_scipy(self):
        for t in ([[3, 1], [1, 3]], [[1, 9], [11, 3]], [[0, 5], [6, 2]], [[12, 5], [7, 30]]):
            p, _ = stats.fisher_exact(t[0][0], t[0][1], t[1][0], t[1][1])
            self.assertAlmostEqual(p, sps.fisher_exact(t).pvalue, places=10)


class TestPropDiff(unittest.TestCase):
    def test_playbook_example_reports_step2_fields(self):
        r = stats.prop_diff(16, 800, 20, 820)
        self.assertAlmostEqual(r["difference"], 20 / 820 - 0.02, places=12)
        self.assertAlmostEqual(r["relative_change"], (20 / 820 - 0.02) / 0.02, places=12)
        self.assertLess(r["ci_low"], 0)
        self.assertGreater(r["ci_high"], 0)
        self.assertEqual((r["n1"], r["n2"]), (800, 820))

    def test_zero_base_rate_relative_change_not_meaningful(self):
        r = stats.prop_diff(0, 50, 3, 50)
        self.assertIsNone(r["relative_change"])
        self.assertIn("Not meaningful", r["relative_change_note"])


class TestWelch(unittest.TestCase):
    # Reference values reproduced with scipy.stats.ttest_ind(A2, A1, equal_var=False).
    def test_known_values(self):
        r = stats.welch_samples(A1, A2)
        self.assertAlmostEqual(r["t"], 2.455356398286006, places=9)
        self.assertAlmostEqual(r["df"], 24.988529290231416, places=9)
        self.assertAlmostEqual(r["p_value"], 0.021378001462867, places=9)
        self.assertAlmostEqual(r["difference"], 2.1666666666666, places=9)

    @unittest.skipUnless(HAVE_SCIPY, "scipy not installed")
    def test_against_scipy(self):
        r = stats.welch_samples(A1, A2)
        res = sps.ttest_ind(A2, A1, equal_var=False)
        self.assertAlmostEqual(r["p_value"], float(res.pvalue), places=10)
        ci = res.confidence_interval(0.95)
        self.assertAlmostEqual(r["ci_low"], float(ci.low), places=8)
        self.assertAlmostEqual(r["ci_high"], float(ci.high), places=8)


class TestHolm(unittest.TestCase):
    def test_textbook_example(self):
        r = stats.holm([0.01, 0.04, 0.03, 0.005])
        for got, want in zip(r["adjusted"], [0.03, 0.06, 0.06, 0.02]):
            self.assertAlmostEqual(got, want, places=12)
        self.assertEqual(r["reject"], [True, False, False, True])

    def test_capped_at_one_and_monotone(self):
        r = stats.holm([0.6, 0.5, 0.9])
        self.assertEqual(r["adjusted"], [1.0, 1.0, 1.0])


class TestSRM(unittest.TestCase):
    def test_fabijan_example(self):
        r = stats.srm([821588, 815482], [50, 50])
        self.assertTrue(r["mismatch"])
        self.assertLess(r["p_value"], 1 / 500000)
        self.assertEqual(r["severity"], "BLOCKER")

    def test_balanced_passes(self):
        r = stats.srm([5012, 4988])
        self.assertFalse(r["mismatch"])

    def test_threshold_override(self):
        r = stats.srm([1050, 950], threshold=0.05)
        self.assertTrue(r["mismatch"])
        self.assertFalse(stats.srm([1050, 950])["mismatch"])

    @unittest.skipUnless(HAVE_SCIPY, "scipy not installed")
    def test_against_scipy(self):
        obs = [10300, 9700, 10050]
        r = stats.srm(obs, [1, 1, 1])
        res = sps.chisquare(obs)
        self.assertAlmostEqual(r["chi2"], float(res.statistic), places=9)
        self.assertAlmostEqual(r["p_value"], float(res.pvalue), places=12)
        self.assertAlmostEqual(stats.chi2_sf(22.77436884189436, 1), 1.8217928726191854e-06, places=16)


class TestClassify(unittest.TestCase):
    """analysis-playbook.md §Statistical sufficiency, Step 3."""

    def test_supported(self):
        self.assertEqual(stats.classify(0.004, 0.02, 0.01)["outcome"], "SUPPORTED")
        self.assertEqual(stats.classify(-0.03, -0.012, 0.01)["outcome"], "SUPPORTED")

    def test_tight_interval_between_zero_and_threshold_is_negligible(self):
        self.assertEqual(stats.classify(0.001, 0.004, 0.01)["outcome"], "NEGLIGIBLE")

    def test_negligible_including_zero(self):
        self.assertEqual(stats.classify(-0.002, 0.003, 0.01)["outcome"], "NEGLIGIBLE")

    def test_inconclusive_one_side(self):
        r = stats.classify(-0.004, 0.015, 0.01)
        self.assertEqual(r["outcome"], "INCONCLUSIVE")
        self.assertFalse(r["volume_limit"])

    def test_inconclusive_volume_limit(self):
        r = stats.classify(-0.0105, 0.0195, 0.005)
        self.assertEqual(r["outcome"], "INCONCLUSIVE")
        self.assertTrue(r["volume_limit"])

    def test_untested_and_not_applicable(self):
        self.assertEqual(stats.classify()["outcome"], "UNTESTED")
        self.assertEqual(stats.classify(not_applicable=True)["outcome"], "NOT APPLICABLE")

    def test_single_series_without_trend_gate_is_untested(self):
        r = stats.classify(0.004, 0.02, 0.01, structure="single-series", trend_gate_cleared=False)
        self.assertEqual(r["outcome"], "UNTESTED")
        self.assertEqual(r["noise_floor_outcome"], "SUPPORTED")
        r = stats.classify(0.004, 0.02, 0.01, structure="single-series", trend_gate_cleared=True)
        self.assertEqual(r["outcome"], "SUPPORTED")


class TestSpecialFunctions(unittest.TestCase):
    def test_t_quantile(self):
        self.assertAlmostEqual(stats.t_ppf_two_sided(0.05, 10), 2.2281388519649385, places=9)
        self.assertAlmostEqual(stats.t_ppf_two_sided(0.05, 1), 12.706204736174698, places=7)

    def test_chi2(self):
        self.assertAlmostEqual(stats.chi2_sf(3.841458820694124, 1), 0.05, places=12)
        self.assertAlmostEqual(stats.chi2_sf(5.991464547107979, 2), 0.05, places=12)


if __name__ == "__main__":
    unittest.main()
