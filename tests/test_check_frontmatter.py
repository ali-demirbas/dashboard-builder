import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import check_frontmatter as cf  # noqa: E402


class TestFrontmatter(unittest.TestCase):
    def write(self, text):
        fd, path = tempfile.mkstemp(suffix=".md")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_valid_frontmatter_passes(self):
        path = self.write(
            "---\nname: dashboard-builder\ndescription: Use when the user "
            "supplies marketing data.\n---\n\n# Body\n"
        )
        self.assertEqual(cf.main([path]), 0)

    def test_missing_frontmatter_fails(self):
        path = self.write("# No frontmatter here\n")
        self.assertEqual(cf.main([path]), 1)

    def test_missing_name_fails(self):
        path = self.write("---\ndescription: only a description\n---\nBody\n")
        self.assertEqual(cf.main([path]), 1)

    def test_missing_description_fails(self):
        path = self.write("---\nname: dashboard-builder\n---\nBody\n")
        self.assertEqual(cf.main([path]), 1)

    def test_unquoted_colon_in_scalar_fails(self):
        # `description: style: a Variant` — the real defect this check exists
        # to catch (see the docstring in check_frontmatter.py).
        path = self.write(
            "---\nname: x\ndescription: style: a Variant with a bad colon\n---\nBody\n"
        )
        self.assertEqual(cf.main([path]), 1)

    def test_quoted_colon_in_scalar_passes(self):
        path = self.write(
            '---\nname: x\ndescription: "style: a Variant, properly quoted"\n---\nBody\n'
        )
        self.assertEqual(cf.main([path]), 0)

    def test_no_files_given_returns_usage_error(self):
        self.assertEqual(cf.main([]), 2)


if __name__ == "__main__":
    unittest.main()
