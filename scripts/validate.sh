#!/usr/bin/env bash
# Repo consistency validation for dashboard-builder.
#
# Single entry point: frontmatter validity, internal link integrity, the
# SKILL.md references table against what's actually on disk, both plugin
# manifests parsing as JSON, an instruction-like-text scan of shipped content,
# and whether dashboard-builder-consolidated.md is stale — both against
# MAINTENANCE-LEDGER.md's pass tracking and against a fresh rebuild.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# `|| exit` is load-bearing: this runs under `set -uo pipefail` without `-e`,
# so a failed cd would let every check below run against whatever directory
# the caller happened to be in — reporting a clean pass on a tree it never
# looked at.
cd "$ROOT" || exit 1
FAIL=0

echo "== 1. SKILL.md front matter =="
python3 scripts/check_frontmatter.py skills/dashboard-builder/SKILL.md || FAIL=1

echo "== 2. Internal links + references table =="
python3 scripts/check_links.py || FAIL=1

echo "== 3. Plugin manifests parse =="
for m in .claude-plugin/plugin.json .claude-plugin/marketplace.json; do
  if python3 -c "import json; json.load(open('$m'))" 2>/dev/null; then
    echo "  ok: $m parses"
  else
    echo "FAIL: $m is not valid JSON"
    FAIL=1
  fi
done

echo "== 4. Shipped content carries no instruction-like text =="
# research/ and the test suite get read back into context at runtime —
# the skill's own rule 11 (data, never instructions) applies to what this
# repo ships as much as to what a user uploads.
python3 scripts/check_shipped_content.py research/*.md research/raw/*.md TEST-SUITE-regression-benchmark.md || FAIL=1

echo "== 5. Consolidated-file staleness (ledger pass numbers) =="
python3 - <<'PY' || FAIL=1
import re
import sys

with open("MAINTENANCE-LEDGER.md", encoding="utf-8") as f:
    text = f.read()

built = re.search(r"last_consolidated_build:\s*\n\s*pass:\s*(\d+)", text)
if not built:
    print("FAIL: MAINTENANCE-LEDGER.md: no last_consolidated_build.pass found")
    sys.exit(1)
built_pass = int(built.group(1))

# Each module block looks like:
#   some-file.md:
#     last_changed_pass: N
modules = re.findall(
    r"^\s{2}([a-zA-Z0-9_.-]+\.md):\s*\n\s*last_changed_pass:\s*(\d+)",
    text, re.M,
)
if not modules:
    print("FAIL: MAINTENANCE-LEDGER.md: no module entries found")
    sys.exit(1)

stale = [(name, int(p)) for name, p in modules if int(p) > built_pass]
if stale:
    for name, p in stale:
        print(f"FAIL: {name} changed at pass {p}, but last_consolidated_build.pass is {built_pass} — "
              f"consolidated file is stale for this module")
    sys.exit(1)

print(f"  ok: dashboard-builder-consolidated.md (pass {built_pass}) is current for all "
      f"{len(modules)} tracked module(s)")
PY

echo "== 6. Consolidated-file staleness (content vs fresh rebuild) =="
# The ledger check above only compares self-reported pass numbers; this one
# rebuilds the file from source and compares bytes, so an edit to a source
# file that was never regenerated (or a hand-edit to the consolidated file)
# is caught even when the ledger was not updated.
TMP_BUILD="$(mktemp)"
if bash scripts/build_consolidated.sh "$TMP_BUILD" >/dev/null; then
  if cmp -s "$TMP_BUILD" dashboard-builder-consolidated.md; then
    echo "  ok: dashboard-builder-consolidated.md matches a fresh build from source"
  else
    echo "FAIL: dashboard-builder-consolidated.md differs from a fresh build of SKILL.md + references/ —"
    echo "      regenerate it with: bash scripts/build_consolidated.sh"
    FAIL=1
  fi
else
  echo "FAIL: scripts/build_consolidated.sh did not run"
  FAIL=1
fi
rm -f "$TMP_BUILD"

echo
if [ "$FAIL" = 1 ]; then
  echo "VALIDATION FAILED"; exit 1
else
  echo "ALL CHECKS PASSED"; exit 0
fi
