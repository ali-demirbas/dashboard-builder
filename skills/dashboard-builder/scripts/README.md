# dbcalc — computation layer

`dbcalc.py` does the arithmetic the skill must not do in its head (`SKILL.md` principle 11): aggregations, joins, statistical tests, cohort maturity and anomaly scans. It ships with the skill and runs anywhere Python 3.9+ runs, standard library only. Reading `.xlsx` needs the optional `openpyxl` package; without it, an `.xlsx` input returns a JSON error that says so.

```
python3 <skill dir>/scripts/dbcalc.py <command> [options]
```

`<skill dir>` is the skill's base directory exactly as given when the skill loads. Version 0.2.0 (`--version`; every trace record carries it).

## When the skill uses each subcommand

| Computation | Subcommand | Still the analyst's judgement |
|---|---|---|
| Grain, totals and subtotal rows, locale (delimiter, decimal mark, day/month order), covered period, identifier columns, hidden sheets | `profile` on every supplied file, before any figure | What one row represents; which reading of an `ambiguous` or `conflict` value is right (it joins the batched question list); whether a Summary sheet or the Detail rows are the answer |
| Joining two files | `join-audit` before the join | It answers Join Safety Gate (`data-quality-gate.md` §1) Q4 cardinality, Q5 coverage and Q8 fan-out; its key-uniqueness counts feed Q1 grain. Q2 (the join key) is the analyst's choice, passed as `--keys`. Q3 semantic key equivalence, Q6 additivity at the target grain, Q7 temporal alignment and Q9 false alignment stay manual. The verdict is a mechanical upper bound, never CONDITIONAL and never a clearance of Q3, Q6, Q7, Q9 |
| Cohort retention | `cohort --export-date` | The export date itself (ask if unknown); the value kind when auto refuses; whether a horizon with few mature cohorts is reportable |
| Anomalies in a daily metric | `anomaly` | Each flag goes through anomaly triage: a score, not a confirmed defect; low-power same-weekday flags are weak candidates |
| Why an additive total moved (revenue, orders, spend, sessions) | `drivers` | Whether the dimension is exhaustive; the outcome of the change itself (contributions take it, they get no test of their own) |
| Why a blended rate moved (CVR, CTR, ROAS as sum/sum) | `decompose` (or `drivers --den`) | Same; plus whether each segment is large enough to read |
| Plain KPI values (a KPI card's total, a ratio of sums, a value by segment, filtered or for a period) | `aggregate` | The definition: which column, which period, which filter is the KPI |
| Difference between two rates | `stats prop-diff` | The structure (`--structure independent` for A/B arms, `single-series` for a sampled series before/after); the material threshold; a full-population before/after read is `stats classify --not-applicable`, read against the series' own variation |
| Difference between two means | `stats welch` | Same; heavy-tailed revenue may need a bootstrap or the median alongside (own code, hand trace row) |
| Many comparisons | `stats holm` | How many comparisons were scanned (m) |
| Assignment split of an experiment | `stats srm` | Units per arm (users, never conversions) and the intended allocation |
| Outcome label for an interval | `stats classify` | The material threshold and the structure; `--not-applicable` for a population total or a full-population before/after read |
| A figure no command produces (correlation, funnel opportunity range) | none: own code | The method, plus a hand-written trace row (`data-quality-gate.md` §Calc trace) |
| The "How each number was computed" table | `trace render --format md` or `--format html`, `--lang tr` for Turkish | Footnote markers in the artifact link to the rows (`#calc-<command>-<hash>`) |

## Output, errors, warnings

Every command prints one JSON document to stdout. A problem with the input is a JSON object with an `error` field (and sometimes `error_type`) and exit code 2, never a traceback: a missing file or column, a directory, an empty or binary file, a legacy `.xls`, a broken `.xlsx`, an unsupported JSON shape, an ambiguous day/month order, a mixed decimal convention, an out-of-range argument. Output is deterministic: no randomness, no clock reads, stable sort orders, full-precision numbers. Rounding happens only when a trace is rendered.

**Warnings.** File-reading commands return `warnings`, a list of plain sentences. Read every one before using a figure. They report:

- rows left out because a cell could not be read: `column 'date': 2 non-empty cell(s) could not be read as a date; those rows were left out` (the same count goes into `dropped_note` and into each trace record's `inputs[].note`); blank cells are not counted, they are empty, not unreadable;
- rows excluded as totals or subtotals: `excluded 2 row(s) equal to the sum of the other rows in the same period (per-period subtotal): Paid total`;
- blank-dimension rows kept as their own `(blank)` segment;
- a decimal mark settled by fallback, an `.xlsx` saved with a `.csv` or `.xls` extension (read as `.xlsx`), NUL bytes removed, unequal period lengths.

**Locating rows.** `profile` reports instruction-like cells and totals rows by source position: `lines` (CSV: file line, the first line is 1, so a title row and blank lines count), `sheet_rows` (XLSX worksheet row) or `records` (JSON). `row` fields, where present, are 1-based data-row indices below the header.

**PII.** No command prints a raw row. Identifier-like columns (e-mail, phone, person name including joined forms such as `Ad Soyad`, `ad_soyad`, `full name`, `müşteri adı`, customer, user, device ID, advertising, order or transaction ID) are reported by type, count and distinct count only. Commands that print category values (`drivers --dims`, `decompose --segment-col`, `anomaly --group-col`, `aggregate --group-by`) refuse an identifier-like column, by header or by values that are mostly e-mails, phone numbers or UUIDs. Printed labels have e-mails, phone numbers, IDs and credentials redacted. Cells holding instruction-like text (English and Turkish phrasings: ignore/disregard/forget previous or above, system prompt, "you are now", "report X as 10M", önceki talimatları, yok say...) are withheld and located by line. `profile` prints sample values only for short categorical-looking text (at most 40 characters and 5 words, no sentences); long free text is counted under `values_withheld`, and nothing from a hidden sheet's text is printed. Trace records keep a file's basename, never its local path.

## Common options

File-reading commands: `--sheet NAME` (xlsx; default first sheet), `--decimal auto|dot|comma`, `--date-order auto|dmy|mdy`, `--trace PATH`, `--label TEXT`. With `--date-order auto`, a date column whose day/month order no value settles is an error, never a guess. `--label` replaces the default label prefix of every trace record the command writes (the default names the metric). Every computing command (all but `trace render`) accepts `--trace` and `--label`.

**Inputs.** CSV/TSV (UTF-8, UTF-16 with a byte-order mark, then cp1254/cp1252; `,` `;` tab `|`; LF, CRLF or CR-only line endings; very long fields), XLSX (read in streaming mode), and JSON: a list of flat objects, `{"rows": [...]}` (also `data`, `records`, `items`), or `.jsonl`/`.ndjson` with one object per line; nested values are kept as JSON text.

**Numbers.** The decimal mark is settled per column over the full column. `1.234` or `1,234` alone is ambiguous (read by the file's other columns, else as a thousands separator, with a warning); a leading 0 group (`0.125`, `0,125`) is always a decimal. Percent signs are stripped in either position (`12,5%`, `%12,5`, `% 12,5`); currency symbols and codes and `(1.234)` negatives are handled.

**Dates.** ISO dates and datetimes, `YYYY/MM/DD`, `dd.mm.yyyy`/`mm/dd/yyyy` (order settled by the data or `--date-order`), `YYYY-MM` months, `YYYYMMDD`, and ISO weeks `2026-W40` (read as that week's Monday).

## Commands

### `profile FILE [--trace-sums]`

Structure and locale before any number is computed (`data-quality-gate.md` §1–§3, `analysis-playbook.md` §Ingestion).

- CSV: encoding, delimiter, header row and `header_line` (title rows above the header are skipped), duplicate header names.
- XLSX: every sheet, hidden and very hidden included, with state, row counts and hidden-row counts (hidden rows are counted for files up to 10 MB, `null` above); each non-empty sheet is profiled; `cross_sheet_sums` compares same-named numeric columns across sheets (a Summary that disagrees with the Detail rows shows as `match: false`).
- Per column: type (date, month, integer, decimal, percent, text), nulls and null rate, decimal convention (`comma`, `dot`, `ambiguous`, `conflict`), day/month order (`iso`, `dmy`, `mdy`, `ambiguous`), distinct count, min/max/sum for measures (totals rows excluded), sample `values` for short low-cardinality labels.
- Date columns: the covered period (first and last date present: the period echo), missing dates in the span, both readings when the order is ambiguous.
- Totals and subtotal rows: label patterns (Total, Grand Total, Toplam, Genel Toplam, Ara Toplam, All campaigns...), rows with blank dimensions but populated metrics, rows equal to the sum of all other rows (per file and per date). A labeled total is compared against the row sum. `(other)`/`(not set)` buckets are listed separately.
- Grain: up to 8 candidate key columns, combinations of 1–3 tested for uniqueness on non-total rows; `holding` lists the minimal keys that hold.
- Exact duplicate rows, identifier columns, PII patterns in other columns, instruction-like cells, credential-like cells.
- `large_file_note` for files of 20 MB or more (profile holds every row in memory; a 10 MB CSV takes about 5 seconds).
- Trace: row count and covered period per table; `--trace-sums` adds each measure column's sum (totals excluded). Running the same profile twice appends nothing new.

```
python3 dbcalc.py profile channel_daily_tr.csv
python3 dbcalc.py profile sales_workbook.xlsx --trace calc-trace.jsonl --trace-sums
```

### `aggregate FILE --metric M [--agg sum|count|mean|min|max|ratio] [--den D] [--group-by G] [--filter COL=VALUE ...] [--period-col P --period SPEC] [--unit U] [--exclude-rows LABELS]`

The plain values a KPI card shows, each with a trace record, so no headline number needs a hand-written row. `ratio` is sum(metric) / sum(`--den`), never a mean of row ratios. `--metric` takes several columns (comma-separated or repeated). `--group-by` adds one value per group after the all-rows value (the column passes the identifier guard; a blank group is `(blank)`). `--filter` is an exact match, repeatable and ANDed. `--period` takes the same specs as `decompose`. Totals and per-period subtotal rows are excluded first (the period column, else the first date column, else each low-cardinality text column is the period a subtotal sums over); `--exclude-rows` names more. Output: `results` (`metric`, `group`, `scope`, `value`, `rows`, and `num_sum`/`den_sum` for a ratio), `excluded_rows`, `warnings`. A zero denominator gives `value: null` with `Not meaningful — zero <den>`.

```
python3 dbcalc.py aggregate channel_daily.csv --metric revenue --period-col date --period 2026-10-01..2026-10-31 --trace calc-trace.jsonl
python3 dbcalc.py aggregate channel_daily.csv --metric orders --agg ratio --den sessions --group-by channel --label "CVR, October"
```

### `stats`

| Subcommand | Input | Output | Method |
|---|---|---|---|
| `prop-diff X1 N1 X2 N2` | successes and trials per group | p1, p2, difference **p2 − p1**, Newcombe CI, relative change, n, p-value; Fisher exact when any group has fewer than 10 successes or failures, else pooled z. `--material M --structure S` adds the classification | Newcombe (1998) method 10, Wilson (1927), Fisher (1935) |
| `welch` | `--summary M1 SD1 N1 M2 SD2 N2`, or `--a 1,2,3 --b 4,5`, or `--file F --value-col V --group-col G --groups A,B` | mean difference (second − first), Welch–Satterthwaite df, CI, p; `--material M --structure S` adds the classification; `--unit` labels the trace | Welch (1947) |
| `holm P1 P2 ...` | p-values in [0, 1] (`--labels` one per p-value, `--alpha`) | adjusted p in input order, reject flags, Bonferroni interval level 1 − α/m | Holm (1979) |
| `srm --counts A,B [--ratios 50,50] [--threshold 0.001]` | units per arm (non-negative whole numbers), intended allocation | chi-square, p, `mismatch` (p < threshold), severity BLOCKER | Pearson chi-square as the SRM check of Fabijan et al. (2019) |
| `classify --low L --high H --material M --structure S` | an interval and the material threshold, same units | SUPPORTED / NEGLIGIBLE / INCONCLUSIVE (`volume_limit` sub-case) / UNTESTED / NOT APPLICABLE | `analysis-playbook.md` §Statistical sufficiency, Step 3 |

- `--structure independent|single-series` is **required** whenever `--material` is given with an interval (prop-diff, welch, classify), so a before/after read can never be classified as if it were an A/B test by default. `independent`: two separate groups (A/B arms). `single-series`: a **sampled** series read before/after (a sampled report, a panel, a survey); the result is UNTESTED unless `--trend-gate cleared`, with the noise-floor reading kept in `noise_floor_outcome`.
- A before/after rate over **every** unit in the period (all sessions, all orders: the full population, the normal case for an analytics or store export) has no sampling question: `stats classify --not-applicable`, read against the series' own variation (anomaly band, earlier changes) and the trend gate. A prop-diff interval on such data is a sampling-noise floor only.
- `classify --not-applicable` also covers a plain population total; `--untested-reason TEXT` records why no interval exists.
- `--confidence` (prop-diff, welch) lies strictly between 0 and 1. Rates are proportions: `--material 0.005` is 0.5pp. `--inputs-json '[{...}, ...]'` (prop-diff, welch, srm) gives one `{file, sheet, column, filter, aggregation}` per positional number so the trace points at the source columns.
- A leading minus in `--counts` needs the `=` form (`--counts=-5,10`); it is then rejected as negative.

```
python3 dbcalc.py stats prop-diff 16 800 20 820 --material 0.005 --structure independent
python3 dbcalc.py stats classify --not-applicable --label "CVR, Oct vs Sep (all sessions)"
python3 dbcalc.py stats srm --counts 821588,815482 --ratios 50,50
python3 dbcalc.py stats holm 0.01 0.04 0.03 0.005 --labels CVR,AOV,ARPU,Retention
```

### `cohort FILE --cohort-col C --export-date YYYY-MM-DD (--wide | --age-col A --value-col V) [--size-col S] [--value-kind auto|count|rate|rate_percent] [--cohort-span auto|day|week|month]`

Builds the cohort matrix and marks every cell whose offset lies beyond the cohort's age at the export date as `censored`: missing, never 0, even when the export filled it with 0 (`data-quality-gate.md` §3 Right-censored cohort cells). Age is measured from the cohort's last acquisition day (`--cohort-span`; auto reads the spacing of cohort dates). Cohort labels can be dates, months or ISO weeks; a column with no readable cohort date is an error. Wide offset headers: `D1`, `d7`, `day_30`, `W1`, `M3`, `Gün 7`, `retention_d30`.

`--value-kind auto` reads a `%` sign as percentages, values all ≤ 1 as proportions, and whole numbers with a size column as retained counts. It refuses (asks for `--value-kind`) when values are not whole numbers, or when every value is ≤ 100 while every cohort has more than 100 members (40 of 1,000 and 40% read alike).

Per horizon: mature and immature cohort counts, the size-weighted rate over mature cohorts only (unweighted mean of rates without a size column), and, when the file zero-filled unobserved cells, the naive rate those zeros would have produced. Trace: censored cells and each horizon's rate.

```
python3 dbcalc.py cohort retention_cohorts.csv --cohort-col cohort_week --wide --size-col cohort_size --export-date 2026-11-02
```

### `anomaly FILE --date-col D --metric-col M [--group-col G] [--trend-window 7] [--test-window 14] [--sigma 3] [--weekday-weeks 4]`

Daily sums per group, with totals rows excluded first (labeled, blank dimensions with metrics, rows equal to the sum of the other rows of the same date); missing dates reported, never imputed. Then:

- **Rolling-sigma scan** — ln transform, 1-day difference, baseline = mean and sample SD of the 7 preceding changes, z for each of the last 14 dates, flag at |z| > 3. Needs ≥ 22 dates (14 tested days × 7 prior changes + 1), else `not run: insufficient history (need >=22 dates, have N dates present over a S-day calendar span)`. A change across a missing date is labeled `multi_day_gap` and neither scored nor used in a baseline.
- **Same-weekday baseline** — each tested day against the mean and SD of the same weekday in the prior `--weekday-weeks` weeks (default 4); needs a calendar span of ≥ 7 × weeks + 1 days. Working convention (unverified, directional only): no flag with fewer than 4 baseline points; with fewer than 8, every result carries `low_power: true` and the block's `power` says so, because an SD from 4–7 points is itself noisy. `--weekday-weeks 8` gives full power when the history allows.
- A weekday profile (mean per weekday) to show whether weekly seasonality is visible.

Flags are anomaly scores, candidates for the anomaly triage list, not confirmed defects (`data-quality-gate.md` §5). Trace: each flag's z (labeled with metric, date and group) and each scan that could not run.

### `join-audit LEFT RIGHT --keys K1,K2 [--right-keys ...] [--left-sheet S] [--right-sheet S] [--casefold] [--min-coverage 0.6]`

Key uniqueness and null keys per side, cardinality, rows after inner and left join, fan-out factor and whether rows after exceed both inputs, unmatched distinct keys on each side, match rate per side. Mechanical verdict: many-to-many → UNSAFE; one-to-many / many-to-one → SAFE_AFTER_AGGREGATION; coverage below `--min-coverage` → UNSAFE; else SAFE. `gate_coverage` in the output states which Join Safety Gate questions this answers (see the table above). Counts only, no key values.

### `decompose FILE --segment-col S --num N --den D --period-col P --base P0 --compare P1 [--exclude-rows LABELS]`

Kitagawa (1955) decomposition of a blended rate change (blended = Σ share × segment rate). The default is the symmetric two-term split, rate effect + mix effect = total change exactly, no residual; the base-weighted three-term split (rate, mix, interaction) is reported alongside. Flags Simpson's paradox: every segment observed in both periods moved one way and the blend moved the other.

- **Per segment:** rates and shares in both periods, `rate_effect` = (r1 − r0)(c0 + c1)/2, `mix_effect` = the raw Kitagawa term (c1 − c0)(r0 + r1)/2, and `mix_contribution` = (c1 − c0)((r0 + r1)/2 − R̄), with R̄ the average of the two blended rates. The raw mix term is positive for every segment that gained share, whatever its rate, so its sign is not read. Because the share changes sum to zero, centering on R̄ leaves the total unchanged: the `mix_contribution` terms sum exactly to the mix effect, and their sign follows the segment's rate relative to the blend (share moving into an above-blend segment raises the blend). Read the total mix effect; use `mix_contribution` to say which share shifts drove it. `segment_terms_note` repeats this in the output.
- **Rows:** totals and per-period subtotal rows ("All devices", "X total", "Toplam", or a row equal to the sum of the other rows of its period on both columns) are excluded with a warning; `--exclude-rows` names more. A blank segment that is not a sum stays in as `(blank)`, like `(other)` and `(not set)` (`kpi-framework.md` §8).
- **Outcome:** `outcome_note` — the effects take the outcome of the change they split; they get no test of their own.
- Period specs: an exact value, `YYYY-MM` on a date column, or `YYYY-MM-DD..YYYY-MM-DD`; unequal period lengths are warned.
- Trace: blended rates, change, rate and mix effects, and per segment the two rates, the rate term and the mix contribution.

### `drivers FILE --metric-col M --period-col P --base P0 --compare P1 --dims d1,d2 [--min-share 0.25] [--cum-stop 0.5] [--den D] [--force-additive] [--exclude-rows LABELS]`

Contribution analysis of an additive total's change: per dimension, each value's change and share of the total change, ranked by absolute contribution; positive and negative contributors separately; the same-direction contributors that reach a cumulative 50% (`--cum-stop`); one drill level into the top contributor by the next dimension.

- **Verdicts** (`summary`): `concentrated` when one value carries ≥ 50%; `no single driver` when none explains `--min-share`; `offsetting moves` instead of either when the gross movement Σ|Δᵢ| exceeds 3× the net change |ΔT| (`gross_over_net`; working convention, unverified, directional only); `Not meaningful — zero total change` when the total did not move.
- **Rows:** per-period subtotal rows are excluded as in `decompose`; on a single metric column a row equal to the sum of the others counts as a subtotal only when its label reads as an aggregate or it is the sum in every period it appears in, so one coincidence (300 = 100 + 200) is kept. `--exclude-rows` names labels to leave out (for instance the subtotal labels `profile` reported). Dimensions pass the identifier guard.
- A ratio metric (rate, average, ROAS, CPA, AOV, a percentage) is refused with a pointer to `decompose`, or run through `decompose` when `--den` is given (trace records are written for each dimension); `--force-additive` overrides the name check.
- Trace: base and compare totals, change, relative change, and every member's change and share (drill members' shares are of the top member's change).

## Trace format

`--trace PATH` appends one JSON object per computed figure (JSON lines):

```json
{"id": "prop-diff:3f1c9a0b2e", "label": "CVR: 95% CI low", "value": -0.0105384697788766,
 "unit": "pp", "formula": "Newcombe hybrid score (method 10) lower limit",
 "inputs": [{"file": "ab_test.csv", "sheet": null, "column": "conversions", "filter": "arm = control",
             "aggregation": "sum", "value": 16}],
 "method": "Newcombe interval", "citation": "newcombe1998", "script": "dbcalc.py", "version": "0.2.0"}
```

- `id` is a hash of command, label, formula and inputs: the same computation always gets the same id. An identical record is not appended twice; a re-computed figure with the same id replaces the earlier one when rendered.
- `label` names the metric and the segment or member (`revenue: change, channel = Paid search`); `--label` replaces the metric prefix.
- `unit`: `rate`/`share` (proportions, rendered as %), `pp` (a difference of proportions, rendered as percentage points), `p`, `z`, `rows`, `cells`, or a label passed by the caller (`--unit`).
- `inputs`: one entry per value read — file basename, sheet, column, filter, aggregation, value, and `note` when unreadable cells were left out.
- No timestamp is written (determinism). `citation` keys resolve in `dbcalc_core/trace.py` `CITATIONS`.

**Hand-written rows** (a figure no command produces) use the same shape; `id` (e.g. `hand:<slug>`) and `label` are required, and `value` is a number, string, boolean, null or a list of those. `trace render` rejects a file with an invalid row and names its line.

`python3 dbcalc.py trace render PATH --format md|html [--lang en|tr]` renders the records as a compact "How each number was computed" table — figure, value, unit, formula, inputs, method [citation] — followed by the methods cited. Percentages and percentage points show at least three significant digits, so a nonzero value never renders as 0.00. The HTML form is an escaped `<section class="calc-trace">` fragment for a dashboard section, a deck appendix or an answer's footnotes; each row carries `id="calc-<command>-<hash>"` (the record id with `:` replaced by `-`) so a footnote marker can link to it. `--lang tr` gives the Turkish title and headers ("Her rakam nasıl hesaplandı", "Rakam", "Değer", ...) and Turkish number formatting (`1.234,56`, `%12,4`, `+0,440 puan`); label tokens such as SUPPORTED, INCONCLUSIVE and "Not meaningful" stay in English.

## Methods cited

- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *JASA* 22(158), 209–212.
- Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. *Statistics in Medicine* 17(8), 873–890 (method 10).
- Fisher, R. A. (1935). *The Design of Experiments*. Oliver & Boyd.
- Welch, B. L. (1947). The generalization of "Student's" problem when several different population variances are involved. *Biometrika* 34(1–2), 28–35.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics* 6(2), 65–70.
- Pearson, K. (1900). On the criterion that a given system of deviations from the probable... *Philosophical Magazine* 50(302), 157–175.
- Fabijan, A., Gupchup, J., Gupta, S., Omhover, J., Qin, W., Vermeer, L., Dmitriev, P. (2019). Diagnosing Sample Ratio Mismatch in Online Controlled Experiments: A Taxonomy and Rules of Thumb for Practitioners. *KDD '19*. doi:10.1145/3292500.3330722.
- Kitagawa, E. M. (1955). Components of a difference between two rates. *JASA* 50(272), 1168–1194.

## Tests

`python3 -m unittest discover -s tests` from the repo root runs the known-answer tests (`tests/test_dbcalc_stats.py`), the subcommand behavior tests (`tests/test_dbcalc_data.py`), the regression tests for each fixed defect (`tests/test_dbcalc_regressions.py`) and the fixture expectations (`tests/test_dbcalc_evals_expected.py`, against `evals/fixtures/` and `evals/expected/`). When scipy is installed, Fisher, Welch and chi-square are also cross-checked against it.
