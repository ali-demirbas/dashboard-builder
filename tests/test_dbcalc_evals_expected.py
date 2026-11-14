"""Deterministic part of the eval harness: dbcalc on evals/fixtures must
match evals/expected/*.json. Runs in CI; spends no tokens.

Each expected file: {"id", "argv": [...], "assert": [{"path", "equals"|"approx"|"lt"}],
"stdout_absent": [regex, ...], "requires": "openpyxl"?}. File arguments in
argv are resolved against evals/fixtures/.
"""
import contextlib
import glob
import io
import json
import os
import re
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FIXTURES = os.path.join(ROOT, "evals", "fixtures")
EXPECTED = os.path.join(ROOT, "evals", "expected")
sys.path.insert(0, os.path.join(ROOT, "skills", "dashboard-builder", "scripts"))

import dbcalc  # noqa: E402

try:
    import openpyxl  # noqa: F401
    HAVE = {"openpyxl": True}
except ImportError:  # pragma: no cover
    HAVE = {"openpyxl": False}


def resolve(path, doc):
    cur = doc
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def run(argv):
    args = [os.path.join(FIXTURES, a) if os.path.exists(os.path.join(FIXTURES, a)) else a for a in argv]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = dbcalc.main(args)
    return code, buf.getvalue()


class TestExpectedOutputs(unittest.TestCase):
    def test_all_expected_files(self):
        files = sorted(glob.glob(os.path.join(EXPECTED, "*.json")))
        self.assertGreaterEqual(len(files), 10)
        for f in files:
            with open(f, encoding="utf-8") as fh:
                spec = json.load(fh)
            with self.subTest(spec["id"]):
                if spec.get("requires") and not HAVE.get(spec["requires"], False):
                    continue
                code, out = run(spec["argv"])
                self.assertEqual(code, 0, out)
                doc = json.loads(out)
                for pat in spec.get("stdout_absent", []):
                    self.assertIsNone(re.search(pat, out), "%s: stdout contains %r" % (spec["id"], pat))
                for a in spec["assert"]:
                    got = resolve(a["path"], doc)
                    if "equals" in a:
                        self.assertEqual(got, a["equals"], "%s: %s" % (spec["id"], a["path"]))
                    if "approx" in a:
                        self.assertAlmostEqual(got, a["approx"], places=9, msg="%s: %s" % (spec["id"], a["path"]))
                    if "lt" in a:
                        self.assertLess(got, a["lt"], "%s: %s" % (spec["id"], a["path"]))

    def test_cases_reference_existing_fixtures(self):
        for f in sorted(glob.glob(os.path.join(ROOT, "evals", "cases", "*.json"))):
            with open(f, encoding="utf-8") as fh:
                case = json.load(fh)
            with self.subTest(case["id"]):
                for name in case["fixtures"]:
                    self.assertTrue(os.path.exists(os.path.join(FIXTURES, name)), name)
                for c in case["checks"]:
                    self.assertIn(c["type"], ("regex_absent", "regex_present", "file_glob_exists",
                                              "file_regex_absent", "html_title_regex", "llm_judge"))
                    if c["type"] != "llm_judge" and c["type"] != "file_glob_exists":
                        re.compile(c["pattern"])


if __name__ == "__main__":
    unittest.main()
