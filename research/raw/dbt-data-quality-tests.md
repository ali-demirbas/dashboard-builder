# dbt Generic Data-Quality Tests — raw research

> Verified 2026-08-13 via authenticated `gh` CLI. Every path, macro name, argument and number read from the live repo tree/blobs.

## A. dbt-labs/dbt-utils

**Metadata (verified):** 1,789★ · **Apache-2.0** · branch `main` · archived `false` · last push 2026-07-07.

### Complete `macros/generic_tests/` — 16 files
`accepted_range` · `at_least_one` · `cardinality_equality` · `equal_rowcount` · `equality` · `expression_is_true` · `fewer_rows_than` · `mutually_exclusive_ranges` · `not_accepted_values` · `not_constant` · `not_empty_string` · `not_null_proportion` · `recency` · `relationships_where` · `sequential_values` · `unique_combination_of_columns`

### The five that matter for marketing data

**`recency`** — `{% test recency(model, field, datepart, interval, ignore_time_component=False, group_by_columns=[]) %}`
Computes `max(field) as most_recent` (per group if grouped) and `threshold = cast(dateadd(datepart, interval * -1, current_timestamp) as timestamp|date)`.
**Fails when** `most_recent < threshold` — the newest row is older than `interval` `datepart`s ago — **or** `most_recent is null` (null clause suppressed under `dbt build --empty`).

**`accepted_range`** — `{% test accepted_range(model, column_name, min_value=none, max_value=none, inclusive=true) %}`
SQL: `select * from model where 1 = 2 [or not column >[=] min_value] [or not column <[=] max_value]`. The `1 = 2` seed guarantees an empty set when neither bound is given.
**Gotcha: NULLs do not fail** — three-valued logic makes `not (null > x)` null.

**`expression_is_true`** — `{% test expression_is_true(model, expression, column_name=None) %}`
`where not({{ expression }})`, or `where not({{ column_name }} {{ expression }})` at column level (so you write `expression: ">= 0"`).
**Gotcha: NULL results are not caught** (`not(null)` is null).

**`not_null_proportion`** — declared as a legacy `{% macro test_not_null_proportion(model, group_by_columns=[]) %}` pulling the rest from kwargs. `at_most` effectively defaults to **1**; `column_name` and `at_least` have **no literal default** (both fall back to `kwargs.get('arg')`).
`sum(case when column is null then 0 else 1 end) / cast(count(*) as numeric)`. **Fails when** proportion `< at_least` or `> at_most`, for any group when grouped.

**`unique_combination_of_columns`** — `{% test unique_combination_of_columns(model, combination_of_columns, quote_columns=false) %}`
`select <cols> from model group by <cols> having count(*) > 1`. **This is the grain check** — fails when the declared grain is violated.

### Most valuable single file
https://github.com/dbt-labs/dbt-utils/blob/main/macros/generic_tests/recency.sql — freshness is the failure mode that silently poisons every downstream marketing number (**a stalled ad-platform sync looks like "spend went to zero"**), and this is the only macro in the package anchored to wall-clock time. `group_by_columns` asserts per-platform or per-account freshness in a single call.

---

## B. calogica/dbt-expectations — DEPRECATED, with a named successor

| Field | Value |
|---|---|
| Stars | 1,232 · **Apache-2.0** |
| Last push | 2024-12-16, commit "Update README.md" |
| Latest release | 0.10.4 (2024-09-10) |
| GitHub `archived` flag | **`false`** — deprecation is stated in the README, not enforced via archival |

**Evidence:** line 1 of the README reads `## Note: This package is no longer actively supported.` The final commit is the one that added it.

**Successor — metaplane/dbt-expectations:** created **2024-12-17** (the day after calogica's last commit), 160★, Apache-2.0, `fork: false` at the API level (re-created, not a GitHub fork), last push 2026-05-17, latest release 0.10.10 (2025-12-02). **A diff of both repos' `macros/schema_tests/` file sets came back identical**, so every macro name and path below applies to the maintained fork. Use metaplane for new work.

### Directory structure under `macros/schema_tests/`
`_generalized/` (5 internal) · `aggregate_functions/` (16) · `column_values_basic/` (11) · `distributional/` (3) · `multi-column/` (6, **hyphen not underscore**) · `string_matching/` (11) · `table_shape/` (16)

### Top tests for marketing / ad-spend QA, with exact signatures

| Test | Marketing use | Signature |
|---|---|---|
| `expect_row_values_to_have_recent_data` | Ad-platform sync freshness | `(model, column_name, datepart, interval, row_condition=None)` |
| **`expect_grouped_row_values_to_have_recent_data`** | Freshness **per platform / per account** — catches one dead connector while others still land | `(model, group_by, timestamp_column, datepart, interval, row_condition=None)` |
| `expect_table_row_count_to_equal_other_table` | Row-count drift raw vs modeled; `factor` handles known fan-out | `(model, compare_model, group_by=None, compare_group_by=None, factor=1, row_condition=None, compare_row_condition=None)` |
| `expect_column_values_to_be_between` | CTR/CVR in `[0,1]`, CPC ≥ 0 | `(model, column_name, min_value=None, max_value=None, row_condition=None, strictly=False)` |
| `expect_column_values_to_not_be_null` | Null rate on `campaign_id`, `spend`, `date` | `(model, column_name, row_condition=None)` |
| `expect_compound_columns_to_be_unique` | Grain: one row per `campaign_id + date` | `(model, column_list, quote_columns=False, ignore_row_if="all_values_are_missing", row_condition=None)` |
| `expect_column_values_to_match_regex` | UTM format + campaign naming convention enforcement | `(model, column_name, regex, row_condition=None, is_raw=False, flags="")` |
| **`expect_column_values_to_be_within_n_moving_stdevs`** | Daily-spend anomaly detection with a rolling baseline | `(model, column_name, date_column_name, group_by=None, period='day', lookback_periods=1, trend_periods=7, test_periods=14, sigma_threshold=3, sigma_threshold_upper=None, sigma_threshold_lower=None, take_diffs=true, take_logs=true)` |
| `expect_column_sum_to_be_between` | Total daily spend inside a budget envelope | `(model, column_name, min_value=None, max_value=None, group_by=None, row_condition=None, strictly=False)` |
| **`expect_row_values_to_have_data_for_every_n_datepart`** | Missing-day gaps in a spend series — **a silent zero-spend day is invisible to row counts** | `(model, date_col, date_part="day", interval=None, row_condition=None, exclusion_condition=None, test_start_date=None, test_end_date=None)` |
| `expect_column_distinct_count_to_equal_other_table` | Campaign-ID coverage: every campaign in raw survives into the model | `(model, compare_model, column_name, compare_column_name, row_condition=None, compare_row_condition=None)` |
| `expect_column_values_to_be_in_set` | Allowed platform / channel / currency codes | `(model, column_name, value_set, quote_values=True, row_condition=None)` |

### Most valuable single file
`macros/schema_tests/distributional/expect_column_values_to_be_within_n_moving_stdevs.sql` — **the capability dbt-utils has no equivalent for.** Range tests only catch impossible values; a rolling-sigma test catches the far more common ad-spend failure where **numbers stay plausible but the trend breaks** (tracking regression, currency switch, halted campaign). `take_diffs`/`take_logs`/`trend_periods` tune it to spend's multiplicative, weekly-seasonal shape.

---

## Caveats
- calogica's GitHub `archived` flag is `false` — **do not report it as "archived."**
- metaplane is a maintained fork by README claim and identical file set, but **not** a GitHub-linked fork. A formal handoff arrangement is **unverified**.
- `not_null_proportion` behavior when `column_name`/`at_least` are omitted is **unverified** (not exercised).
