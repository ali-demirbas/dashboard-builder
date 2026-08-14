import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import check_links as cl  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


class TestLinks(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        os.chdir(ROOT)
        self.addCleanup(os.chdir, self._cwd)

    def test_internal_links_resolve_in_this_repo(self):
        # Runs against the real repo tree — this is the check CI actually
        # relies on, not a synthetic fixture.
        self.assertTrue(cl.check_internal_links())

    def test_references_table_matches_disk(self):
        self.assertTrue(cl.check_references_table())

    def test_link_regex_matches_are_all_skip_eligible(self):
        # LINK_RE itself doesn't distinguish external/anchor/relative — that's
        # SKIP_PREFIXES's job in check_internal_links, applied per match. This
        # only asserts the regex finds both links and that each capture is
        # something check_internal_links' skip check can act on directly
        # (either it starts with a skip prefix, or it's a real relative path).
        line = "See [docs](https://example.com/x) and [here](#section)."
        matches = [m.group(1) for m in cl.LINK_RE.finditer(line)]
        self.assertEqual(len(matches), 2)
        self.assertTrue(matches[0].startswith("https://"))
        self.assertTrue(matches[1].startswith("#"))


if __name__ == "__main__":
    unittest.main()
