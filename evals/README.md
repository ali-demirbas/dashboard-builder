# Evals

Two layers, both on synthetic data only (`CLAUDE.md` rule 5).

| Layer | What it checks | Cost | Where it runs |
|---|---|---|---|
| **Deterministic** — `evals/expected/*.json` | `dbcalc.py` output on the fixtures: decimal comma and day/month order on the Turkish channel file, right-censored cells on the cohort file, the duplicated month and the join fan-out on the MRR file, summary vs. detail and the hidden sheet on the workbook, PII and instruction-like text never echoed, Kitagawa/Simpson, SRM, the inconclusive A/B read | None | CI, via `tests/test_dbcalc_evals_expected.py` |
| **Behavioral** — `evals/cases/*.json` + `evals/run_evals.py` | What the skill actually replies and builds for a realistic request, against the regression cases in [`TEST-SUITE-regression-benchmark.md`](../TEST-SUITE-regression-benchmark.md) | Real model sessions: tokens per case, plus one judge call per `llm_judge` check | By hand, never in CI |

## Running the behavioral evals

```
python3 evals/run_evals.py --list                  # cases, suite IDs, rough cost
python3 evals/run_evals.py --dry-run               # what would run, no model calls
python3 evals/run_evals.py --case workbook-summary-vs-detail
python3 evals/run_evals.py --case exec-dashboard-two-days --no-judge --model sonnet
python3 evals/run_evals.py                         # every case: the most expensive option
```

For each case the runner copies the case's fixtures into a fresh temporary directory outside the repo (so this repo's maintenance `CLAUDE.md` is not in the session), copies this working tree's plugin (`.claude-plugin/`, `skills/`) into a temporary directory whose path has no spaces, and runs `claude -p` in the work directory with:

- that snapshot loaded via `--plugin-dir`, so the skill under test is the one on disk (`--skill-source installed --installed-skill-dir DIR` uses an installed copy instead);
- the prompt prefixed with the skill's slash command when the case's `invoke` is `slash` (the default; tests behavior), or sent plain when it is `auto` (tests whether routing picks the skill). `--invoke` on the command line overrides every case;
- `--max-turns` (default 40), `--max-budget-usd` per run (default 3.0) and a wall-clock timeout per case: the case's `timeout_s`, 1200 s by default and 2400 s for the cases that build a dashboard or deck (`--timeout` overrides all).

### Isolation: what is and is not isolated

Measured with Claude Code CLI 2.1.117; re-check after a CLI upgrade.

| Isolated | How |
|---|---|
| Your user settings: permission allow rules, hooks, enabled plugins, MCP servers, and your global `~/.claude/CLAUDE.md` | `--setting-sources project,local` (the temporary work directory has no project settings). Verified with a probe prompt: with the user source the session sees the global CLAUDE.md, without it, it does not. This matters: a user allow rule such as a bare `Bash` would otherwise widen every allow-list below. |
| Tools | `--tools Skill,Read,Edit,Write,Bash,TodoWrite`: no Glob, Grep, web tools, subagents or notebook editing; `--strict-mcp-config` with no servers. |
| Permissions | `--permission-mode dontAsk`: anything not allowed is denied, never asked. Allowed: Read inside the work dir and the plugin snapshot; Edit/Write inside the work dir; Bash only `python3 <snapshot>/skills/dashboard-builder/scripts/dbcalc.py …` (an output redirect into the work dir is allowed; `python3 -c`, other scripts, and commands touching paths outside these directories such as `ls /` are denied, as are Read/Write outside them — verified with a probe run). The CLI itself also lets read-only shell commands (`ls`, `| head`) run inside the work dir and the snapshot without a rule, as seen in a live run; that is no wider than the Read scope. Denials are recorded in `result.json` (`permission_denials`). |
| Judge | The judge call gets no tools, no user settings, and the reply and file text inside `<<<BEGIN_…>>>`/`<<<END_…>>>` fences it is told are data, never instructions; its verdict is parsed from the last JSON object carrying a boolean `pass`. |

| Not isolated | Why, and what to do |
|---|---|
| Your login | Auth comes from your normal login (keychain). `--config-dir DIR` runs with `CLAUDE_CONFIG_DIR=DIR` for a fully separate config, but a fresh directory is not logged in: log in once under it, or use `--bare` with `ANTHROPIC_API_KEY` (no CLAUDE.md discovery, hooks, plugin sync or keychain reads). |
| The operating system | There is no OS sandbox: `dbcalc` runs as you (it only reads the files it is given). A case with `"build_scripts": true` (the deck case, for python-generated `.pptx`) also allows `python3 <work dir>/*.py`: a script the model wrote, i.e. arbitrary code run as you, and the glob also matches `..` paths. Leave it off unless a case needs it. |
| Routing runs (`invoke: auto`) | To measure skill selection against a realistic set, `--routing-env installed` (the default) passes your `enabledPlugins` through `--settings` and exposes `~/.claude/skills` as a temporary plugin of symlinks; the installed copy of dashboard-builder is disabled so only the snapshot under test competes. Those plugins' own hooks can run. User permission rules, hooks and CLAUDE.md still do not load. `--routing-env none` loads only the skill under test. Auto-memory behavior without the user setting source was not verified. |

Everything a run writes stays in the work dir and is copied out, so no supplied data leaves the machine through the session's tools (no web tools, no MCP, no shell beyond dbcalc); the model call itself of course sends the prompt and file contents the model reads to the API.

Everything lands in `evals/runs/<UTC timestamp>/<case>/` (gitignored): `reply.md`, `transcript.jsonl` (the stream-json session), `files/` (every file the run produced), `command.json` and `result.json`. The summary table prints status, checks passed, cost and how the skill was loaded; the exit code is non-zero if any case fails.

## Check types

Every case gets an automatic `skill_invoked` check (the skill was invoked, or registered and called by slash command). The rest are listed in the case file:

| Type | Fields | Passes when |
|---|---|---|
| `regex_present` | `pattern`, optional `target`: `reply` (default), `files`, `all` | the pattern matches |
| `regex_absent` | same | the pattern does not match |
| `file_glob_exists` | `glob` (e.g. `**/*.html`) | at least one produced file matches |
| `file_regex_absent` | `glob`, `pattern` | no matching produced file contains the pattern (no matching file at all is reported as vacuous) |
| `html_title_regex` | `glob`, `pattern`, optional `absent_pattern` | every matching HTML file's `<title>` matches `pattern` and not `absent_pattern` |
| `llm_judge` | `rubric` | a second `claude -p` call (no tools, no user settings, `--judge-model`, default sonnet) given the rubric, the request, and the fenced reply and produced-file text returns `{"pass": true}`; `--no-judge` skips these and a case that passes everything else is reported `PASS*` |

Any check can carry `"soft": true`: it is reported but does not fail the case (used for "a .pptx was produced", which depends on the environment's toolkit). A check can carry a `note` explaining it.

Label tokens (CRITICAL / HIGH / MEDIUM / LOW, SUPPORTED / INCONCLUSIVE / ...) stay in English in every reply language (`SKILL.md` principle 12), so a regex check on a label accepts only the English token; Turkish prose around it is expected.

## Case fields

`id`, `test_suite_id` (every case names its `TEST-SUITE-regression-benchmark.md` ID; `related_test_suite_ids` for others it touches), `fixtures`, `cost`, `prompt`, `checks`, and optionally `timeout_s`, `invoke` (`slash` or `auto`), `metric` (`behavior`, the default, or `routing`: the case measures whether the plain prompt selects the skill, read from its automatic `skill_invoked` check), `build_scripts` (see Isolation) and `note`. `routing-marketing-xlsx-auto` is the routing case: a weekly channel-performance workbook and a plain Turkish request; report its pass rate over several runs as the routing metric, separately from the behavior cases.

## Adding a case

1. Put a synthetic fixture in `evals/fixtures/`, preferably by adding a function to `make_fixtures.py` (fixed arithmetic, no randomness; e-mails on `example.com`, fictitious phone numbers). Run it twice and confirm the files are byte-identical.
2. If a `dbcalc` result on that fixture is deterministic and worth pinning, add `evals/expected/<id>.json`: `{"id", "argv", "assert": [{"path": "a.0.b", "equals" | "approx" | "lt": ...}], "stdout_absent": [regex...]}`. File names in `argv` resolve against `evals/fixtures/`.
3. Add `evals/cases/<id>.json`: `{"id", "test_suite_id", "fixtures", "cost", "prompt", "checks"}` plus the optional fields above (`timeout_s: 2400` if it builds an artifact). Write the prompt the way a real user would (Turkish or English). Prefer a regex check where the required behavior has a fixed surface form, and an `llm_judge` rubric that names the exact facts in the fixture (the numbers, the trap) and states both PASS and FAIL conditions.
4. `python3 -m unittest discover -s tests` checks that every case's fixtures exist, its patterns compile, it has a suite ID, and artifact cases get the long timeout (`tests/test_run_evals.py` also pins the allow-list and the judge fencing); then run the case once with `run_evals.py --case <id>`.
