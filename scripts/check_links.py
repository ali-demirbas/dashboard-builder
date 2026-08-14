#!/usr/bin/env python3
"""Check internal markdown links and the SKILL.md references table.

Two things nothing else in this repo checks:

1. **Internal markdown links.** A relative link that pointed at a file
   renamed or moved during an edit fails silently for a human skimming
   prose — the sentence around it still reads fine.

2. **The SKILL.md references table vs. what's actually in `references/`.**
   These are two independent sources of truth about which reference files
   exist and are wired in: the table (what SKILL.md tells the model to
   load, and when) and the directory listing (what's actually on disk). A
   file added to `references/` but never added to the table is invisible
   to the workflow described in SKILL.md — it exists but nothing ever
   loads it. A table row surviving after its file was deleted or renamed
   points the model at a file that no longer exists, which fails only at
   the moment the model actually tries to load it.

Usage:
  check_links.py            (from repo root)
"""
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")
LINK_RE = re.compile(r"\]\(([^)\s]+?)(?:#[^)]*)?\)")


def walk_markdown_files(root="."):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def check_internal_links():
    failed = False
    checked = 0
    for path in walk_markdown_files():
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in LINK_RE.finditer(line):
                    target = m.group(1)
                    if target.startswith(SKIP_PREFIXES) or "{" in target:
                        continue
                    checked += 1
                    resolved = os.path.normpath(
                        os.path.join(os.path.dirname(path), target)
                    )
                    if not os.path.exists(resolved):
                        print("FAIL: %s:%d -> %s (broken)" % (path, lineno, target))
                        failed = True
    if not failed:
        print("  ok: %d internal link(s) resolve" % checked)
    return not failed


def check_references_table():
    skill_path = "skills/dashboard-builder/SKILL.md"
    refs_dir = "skills/dashboard-builder/references"

    if not os.path.exists(skill_path):
        print("FAIL: %s not found" % skill_path)
        return False
    if not os.path.isdir(refs_dir):
        print("FAIL: %s not found" % refs_dir)
        return False

    with open(skill_path, encoding="utf-8") as fh:
        text = fh.read()

    # Rows of the references table look like:
    #   | `references/data-quality-gate.md` | Always, before any conclusion... |
    table_files = set(re.findall(r"`references/([a-z0-9-]+\.md)`", text))
    disk_files = {f for f in os.listdir(refs_dir) if f.endswith(".md")}

    failed = False
    for f in sorted(table_files - disk_files):
        print("FAIL: SKILL.md references table lists '%s' — not found in %s" % (f, refs_dir))
        failed = True
    for f in sorted(disk_files - table_files):
        print("FAIL: %s/%s exists but is not listed in SKILL.md's references table" % (refs_dir, f))
        failed = True

    if not failed:
        print("  ok: %d reference file(s) match between SKILL.md's table and %s" % (len(disk_files), refs_dir))
    return not failed


def main():
    ok_links = check_internal_links()
    ok_table = check_references_table()
    return 0 if (ok_links and ok_table) else 1


if __name__ == "__main__":
    sys.exit(main())
