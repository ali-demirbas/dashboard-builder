# Contributing

## Editing the skill

The skill is `skills/dashboard-builder/SKILL.md` plus its `references/*.md` files. Edit the source files, not `dashboard-builder-consolidated.md` — that file is generated and gets overwritten (see `CLAUDE.md` rule 1).

After any behavioral change:

1. Update `MAINTENANCE-LEDGER.md` — bump `current_pass`, set the touched module's `last_changed_pass`/`last_audited_pass`, note what changed and why.
2. Run `bash scripts/validate.sh`.
3. Regenerate `dashboard-builder-consolidated.md` only if this is a release — day-to-day edits don't need it (`MAINTENANCE-LEDGER.md`'s own operational note explains why).

## Adding a metric definition or benchmark

Goes in `kpi-framework.md` (formulas/benchmarks) or `research/raw/*.md` (vendor-sourced definitions with URLs). Every entry needs a source — a fetched vendor doc, a cited paper, or an explicit "unverified" label (`CLAUDE.md` rule 3). Where sources disagree, record both as a conflict rather than picking one silently — this repo has existing examples of that pattern in `comparability-rules.md`.

## Adding a comparability rule or hard block

`comparability-rules.md` — every hard block needs the specific counting mechanic that makes the comparison invalid, not a general "these differ" note. Look at an existing entry in §2 for the expected level of specificity before adding a new one.

## Testing

```bash
bash scripts/validate.sh
python3 -m unittest discover -s tests -v
```

Both run in CI (`.github/workflows/validate.yml`) on every PR. `TEST-SUITE-regression-benchmark.md` holds the skill's own end-to-end regression cases (synthetic data only, per `CLAUDE.md` rule 5) — see `MAINTENANCE-LEDGER.md`'s `open_findings` for which cases are still unexecuted.

## Language

Repo docs, skill instructions, and code comments are English. The skill itself answers the end user in whatever language they write in — that's runtime behavior, not something to translate here.

## What not to do

- Don't name an external AI tool, model, or commercial product as the source of a change (`CLAUDE.md` rule 4).
- Don't commit real account or business data from a live test, even anonymized-looking (`CLAUDE.md` rule 5).
- Don't add a metric, benchmark, or comparability rule without a source.
