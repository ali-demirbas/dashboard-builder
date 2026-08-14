# Semantic Layers, MMM & CLV Libraries — raw research

> Continues the earlier GitHub recon (`github-skills-recon.md` covers Claude-skill collections; `dbt-data-quality-tests.md` covers dbt-utils/dbt-expectations). This file covers semantic layers, product-analytics math, MMM libraries, and CLV/BTYD libraries. All stars/license/archived status pulled live via `gh api`; file contents pulled via raw.githubusercontent.com, not guessed.

---

## 1. Semantic/metrics layers

### dbt-labs/metricflow
1,737★ · **Apache-2.0** · not archived · github.com/dbt-labs/metricflow

**What it encodes:** the only OSS semantic layer with a formal, typed metric taxonomy — `simple`, `ratio`, `derived`, `cumulative`, `conversion`. The **conversion** type is the most valuable for marketing: a literal funnel-conversion-rate definition with an attribution `window`, a `base_measure`, `conversion_measure`, keyed by `entity`.

**Most valuable file** (real content, `metricflow_semantics/test_helpers/semantic_manifest_yamls/simple_manifest/metrics.yaml`):
```yaml
metric:
  name: visit_buy_conversion_rate_7days
  type: conversion
  type_params:
    conversion_type_params:
      base_measure: visits
      conversion_measure: buys
      window: 7 days
      entity: user
      calculation: conversion_rate
```
Plus a ratio example (`bookings_per_booker`, `bookings_per_view`) at the same path.

**Borrow:** the YAML schema/vocabulary (metric types, `window`, `entity`, `calculation` fields) freely — Apache-2.0, no constraint.

**Vs. vendor defs:** the only project that formalizes "conversion window" as a first-class parameter the way Adjust/attribution vendors do — a clean schema template for a funnel/CAC metric spec.

### cube-js/cube
20,620★ · dual **Apache-2.0/MIT** · not archived · github.com/cube-js/cube

**What it encodes:** a worked, non-trivial **cohort retention** SQL+YAML recipe — the exact self-join pattern for a user × activity-month grid plus a `percentage_of_active` measure.

**Most valuable file** (`docs-mintlify/recipes/data-modeling/cohort-retention.mdx`):
```yaml
- name: percentage_of_active
  sql: "1.0 * {total_active_count} / NULLIF({total_count}, 0)"
  type: number
  format: percent
```

**Vs. vendor defs:** "any activity in the month" is closer to Amplitude's **"Return On or After"** than a strict single-day return — but it's a docs recipe, not a product-enforced definition, so treat as a template not a spec.

### lightdash/lightdash
6,033★ · **MIT** (core; `ee` carved out separately) · not archived · github.com/lightdash/lightdash

**What it encodes:** standard dbt-metrics YAML syntax (`meta.metrics.<name>.type: count | count_distinct | sum | min | max`). **Not marketing-specific** — no retention/CAC examples found in public example repos; value is purely the metrics.yml authoring pattern. **Could not find a Lightdash example with marketing KPIs** — flagged rather than invented.

---

## 2. Product/marketing analytics — the actual math

### PostHog/posthog
37,656★ · **MIT** for core (`ee/` under separate license) · not archived · github.com/PostHog/posthog

**What it encodes:** retention and stickiness computed in code, not just described.

- **Retention:** two anchor semantics via `RETENTION_RECURRING` vs `RETENTION_FIRST_OCCURRENCE_MATCHING_FILTERS`/`RETENTION_FIRST_EVER_OCCURRENCE` (`posthog/constants.py`), plus a `cumulative` flag (`_wrap_base_query_for_cumulative_retention`) that turns a strict "returned on day N" cohort into "returned by day N or later." **This is the direct code-level equivalent of Amplitude's "Return On" vs "Return On or After."**
- **Stickiness:** per-user count of distinct active periods in a range, bucketed, computed in HogQL — not a static ratio.

**Most valuable files:**
- `posthog/hogql_queries/insights/retention/retention_query_runner.py` (RETENTION_TYPE handling, cumulative wrapping)
- `posthog/hogql_queries/insights/retention/retention_base_query_rolling.py` (rolling vs fixed-interval windowing)
- `products/product_analytics/backend/hogql_queries/stickiness/stickiness_query_runner.py`

**Borrow:** the retention-type taxonomy (recurring / first-occurrence / cumulative) as spec vocabulary — MIT, safe. Check `ee/` license before lifting any specific file.

**Vs. vendor defs:** matches Amplitude's dual-mode retention more closely than GA4 does (GA4 has no such toggle) — good source for documenting *why* two "retention rate" numbers from different tools disagree.

### GrowthBook/growthbook
8,119★ · **MIT** for core (`packages/back-end/src/enterprise` carved out) · not archived · github.com/growthbook/growthbook

**What it encodes:** a real statistics engine (`gbstats`), not marketing copy.

- **CUPED / regression adjustment:** implemented as "RA" (regression-adjusted) statistic types (`statistic_type in ["ratio_ra", "mean_ra"]`), covariate sums tracked per metric, `get_cuped_unadjusted_stat()` for a before/after comparison. Docs: `docs/docs/statistics/cuped-technical.mdx`.
- **Sequential testing:** an mSPRT-style always-valid p-value/confidence sequence, tunable `sequential_tuning_parameter` (ρ), `sequential_rho()`/`sequential_interval_halfwidth()` — a real always-valid-inference implementation.

**Most valuable file:** `packages/stats/gbstats/frequentist/tests.py` — classes `SequentialTTest`, `SequentialTwoSidedTTest`, `SequentialOneSidedTreatmentLesserTTest`.

**Borrow:** the statistical approach (CUPED as covariate-adjusted regression, mSPRT sequential bounds) — published methods, not novel IP; code is MIT. Check file location before lifting verbatim (Bandits code sits closer to enterprise-adjacent features).

**Vs. vendor defs:** most attribution vendors (GA4, Adjust) don't expose experiment-stats internals at all — no direct comparison point, a genuinely unique category.

### Statsig — could not verify
Searched `statsig-io` org and general GitHub search. **Only public repos are client/server SDKs, a status page, and small utilities (max ~772★).** No public core-compute repo; no CUPED/sequential-testing code found anywhere. **Statsig's experiment-analysis engine appears closed-source. Do not cite Statsig as an OSS source.**

### matomo-org/matomo
21,764★ · **GPL-3.0** · not archived · github.com/matomo-org/matomo

**What it encodes:** session/bounce math differs meaningfully from GA4.

**Bounce rate (page-level)** = `entry_bounce_count / entry_nb_visits`, where `entry_bounce_count` counts single-page visits that **started** on this page. Confirmed via code docstring: *"entry_bounce_count (single page visits on this page) / entry_nb_visits (all visits that started on this page)."* A classic single-pageview bounce definition — **not** GA4's engaged-session model (10s / conversion event / 2+ pageviews).

**File:** `plugins/Actions/Columns/Metrics/BounceRate.php`

**Borrow: formula/logic only, described in your own words. DO NOT copy the PHP code — GPL-3.0 is copyleft** and would create a license-compatibility problem in an Apache/MIT skill repo.

**Vs. vendor defs:** the strongest concrete "same metric name, different math" case study — Matomo's bounce rate is single-pageview-based while GA4 replaced bounce rate with the inverse of engaged sessions, a categorically different signal.

---

## 3. Marketing-mix modeling / incrementality

### google/meridian
1,496★ · **Apache-2.0** · not archived · github.com/google/meridian

**Answers:** Bayesian MMM — media-channel incremental contribution to a KPI, plus derived **ROI**, **marginal ROI**, and **CPIK** (cost per incremental KPI).

**ROI definition (from code docstring, `analyzer.py::roi`):** *"The ROI numerator is the change in expected outcome... when one channel's spend is set to zero"* — **ROI defined as a counterfactual causal contrast** (zero-out-spend simulation), denominator = channel spend. Explicit causal-inference framing, not correlation-based attribution.

**Mechanics:** hierarchical Bayesian regression with geometric/Weibull **adstock** decay and a **Hill saturation** curve, fit via MCMC (`meridian/model/adstock_hill.py`, `meridian/model/equations.py`).

**Inputs:** geo-level (or national) time series of media spend/impressions per channel, KPI, optional reach & frequency, control variables.

**File:** `meridian/analysis/analyzer.py` — functions `roi`, `marginal_roi`, `cpik`, `incremental_outcome`.

**Borrow:** the causal framing (counterfactual spend=0 contrast) to document what ROI means in an MMM context vs last-click ROAS.

### google/lightweight_mmm
1,052★ · **Apache-2.0** · **archived: true** (last push June 2025, superseded by Meridian) · github.com/google/lightweight_mmm

**Answers:** same MMM question via a lighter NumPyro/JAX model with three transforms: `adstock`, `hill_adstock`, `carryover`.

**Formula (literal, `lightweight_mmm/media_transforms.py`):**
```python
adstock_value = prev_adstock * lag_weight + data   # geometric adstock recursion
```

**Note for the skill:** flag as archived/superseded — point to Meridian, but the transform math remains a clean reference implementation.

### facebookexperimental/Robyn
1,501★ · **MIT** · not archived · github.com/facebookexperimental/Robyn

**Answers:** same incremental-contribution question, fit via **ridge regression (glmnet) + multi-objective evolutionary hyperparameter search (Nevergrad)** rather than full Bayesian MCMC — optimizes NRMSE (fit) and DECOMP.RSSD (decomposition distance) jointly, with **optional MAPE calibration against known incrementality** (e.g. geo-lift test results).

**File:** `R/R/model.R` (`robyn_run()`).

**Borrow:** the multi-objective calibration idea — using real experiment results (geo-holdout tests) to calibrate/penalize the MMM — is a genuinely useful methodology note. MIT, fully reusable.

### uber/orbit
2,066★ · **Apache-2.0** · not archived · github.com/uber/orbit

**Correction to the original premise:** Orbit is **not** a marketing-mix or incrementality library — it's a general-purpose Bayesian time-series forecasting package (exponential smoothing / damped local trend), with no media-channel, adstock, or ROI concepts anywhere in the codebase. **Low borrow-worthiness for this use case** — not an MMM peer to Meridian/Robyn/LightweightMMM.

### pymc-labs/pymc-marketing
1,224★ · **Apache-2.0** · not archived · github.com/pymc-labs/pymc-marketing

**Answers two distinct domains in one repo:**
- **MMM module** (`pymc_marketing/mmm/`) — same adstock+saturation Bayesian pattern as Meridian, fully in PyMC.
- **CLV module** (`pymc_marketing/clv/models/`) — implements **BG/NBD** (`beta_geo.py`), **Pareto/NBD** (`pareto_nbd.py`), **BG/BB** (`beta_geo_beta_binom.py`), **Gamma-Gamma** monetary-value model (`gamma_gamma.py`) — fully Bayesian (PyMC) reimplementations of the classic Fader/Hardie/Lee models, **explicitly built to supersede `lifetimes`.** Confirmed in-code: `BetaGeoModel`'s docstring states predictive methods were "adapted from the BetaGeoFitter class in the legacy lifetimes library" and cites the same Fader/Hardie/Lee 2005 paper as the original.

**File:** `pymc_marketing/clv/models/beta_geo.py`

**Borrow:** model assumptions/priors documentation and the `lifetimes`→pymc-marketing API mapping. Apache-2.0.

---

## 4. CLV / BTYD libraries

### CamDavidsonPilon/lifetimes
1,477★ · **MIT** · **archived: true** (last push June 2024) · github.com/CamDavidsonPilon/lifetimes

**Status:** archived and effectively deprecated. **The community successor is confirmed in pymc-marketing's own docstrings — pymc-marketing's CLV module is the explicit successor, not a fork.**

**Still useful as reference:** the textbook non-Bayesian MLE fit of BG/NBD — requires `frequency`, `recency`, `T` (RFM summary) per customer; purchase rate Poisson(λ) with λ~Gamma population prior, dropout probability p~Beta population prior.

**File:** `lifetimes/fitters/beta_geo_fitter.py`

**Borrow:** the RFM-summary data contract (frequency/recency/T columns) as an input-schema convention — **this exact schema is also what pymc-marketing expects**, so it's the de facto standard shape for CLV models in Python. MIT, safe.

---

## Comparison table

| Repo | Category | Metrics defined | License | Archived? | Borrow-worthiness |
|---|---|---|---|---|---|
| dbt-labs/metricflow | Semantic layer | ratio, conversion (with attribution window), derived, cumulative metrics | Apache-2.0 | No | **High** |
| cube-js/cube | Semantic layer | cohort retention % | Apache-2.0/MIT | No | Medium |
| lightdash/lightdash | Semantic layer | generic count/sum metrics (not marketing-specific) | MIT | No | Low-Medium |
| PostHog/posthog | Product analytics | retention (3 anchor modes + cumulative), stickiness | MIT (core) | No | **High** |
| GrowthBook/growthbook | Experimentation stats | CUPED/regression-adjustment, sequential testing (mSPRT) | MIT (core) | No | **High** |
| Statsig | Experimentation stats | not publicly available | N/A | N/A | **None — not verifiable** |
| matomo-org/matomo | Web analytics | bounce rate (single-pageview, differs from GA4) | **GPL-3.0** | No | Medium (definition only, **no code copy**) |
| google/meridian | MMM | ROI/marginal ROI/CPIK via counterfactual spend=0, adstock+Hill | Apache-2.0 | No | **High** |
| google/lightweight_mmm | MMM | adstock/carryover/hill transforms | Apache-2.0 | **Yes** (superseded by Meridian) | Medium |
| facebookexperimental/Robyn | MMM | ridge+Nevergrad MMM, multi-objective calibration against real experiments | MIT | No | High |
| uber/orbit | Forecasting (not MMM) | none marketing-specific | Apache-2.0 | No | Low |
| pymc-labs/pymc-marketing | MMM + CLV | BG/NBD, Pareto/NBD, BG/BB, Gamma-Gamma; MMM adstock/saturation | Apache-2.0 | No | **High** |
| CamDavidsonPilon/lifetimes | CLV/BTYD | BG/NBD MLE, RFM data contract | MIT | **Yes** (deprecated → pymc-marketing) | Medium (schema/reference only) |

## Key flags
- **Matomo is GPL-3.0** — pull the definition, never the code.
- **Statsig has no verifiable open-source stats engine** — don't cite it.
- **`lifetimes` and `lightweight_mmm` are both archived** — point to pymc-marketing CLV and Meridian respectively.
- Best literal quotable "funnel conversion" formula file: dbt-labs/metricflow's `visit_buy_conversion_rate_7days`.
- Best "same metric, different vendor math" case studies: PostHog retention (cumulative vs non-cumulative = Amplitude's Return On vs Return On or After) and Matomo bounce rate vs GA4 engaged sessions.
