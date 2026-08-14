# Evals

This repo's end-to-end regression cases live in [`TEST-SUITE-regression-benchmark.md`](../TEST-SUITE-regression-benchmark.md) at the repo root — 50 manual golden-test cases across five categories (Clean, Ambiguous, Missing-data, Cross-source, Adversarial), each specifying the input shape and the expected behavior (which rule should fire, what the skill should refuse or flag).

This directory is a placeholder for turning those into runnable evals — spawning the skill against a synthetic input and checking the output against the case's expected behavior — once enough of them have been manually verified to be worth automating. See `MAINTENANCE-LEDGER.md`'s `open_findings` for how many cases are currently executed vs. still a checklist only.

All eval inputs are synthetic. Real account or business data never enters this directory (`CLAUDE.md` rule 5).
