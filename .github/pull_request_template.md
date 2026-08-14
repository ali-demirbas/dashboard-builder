## What this changes

## Checklist

- [ ] `bash scripts/validate.sh` passes locally
- [ ] `python3 -m unittest discover -s tests -v` passes locally
- [ ] `MAINTENANCE-LEDGER.md` updated (module status + `current_pass`) if a reference file changed
- [ ] New/changed metric definitions and benchmarks carry a source (`CLAUDE.md` rule 3)
- [ ] No external AI tool/product named as a source (`CLAUDE.md` rule 4)
- [ ] No real account or business data included, even as an example (`CLAUDE.md` rule 5)
- [ ] `dashboard-builder-consolidated.md` **not** touched, unless this PR is specifically a release regeneration
