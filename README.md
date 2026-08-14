# dashboard-builder — marketing & growth KPI dashboards with a comparability engine underneath

A Claude Code skill that turns fragmented marketing and business data into a decision system — KPI intelligence, cross-channel diagnosis, growth-bottleneck identification, unit-economics evaluation, and executive dashboard or presentation output.

## Why this exists

Most marketing analysis fails on **comparing numbers that were never comparable**, not on arithmetic. The same metric name means different things across platforms, and a configuration change moves a number without any change in behavior. Two examples from the research this skill is built on:

- Google Ads dates conversions to the **click**, not the conversion. The last 30 days are permanently incomplete, and the same past date returns a different number when re-pulled weeks later.
- Play Console's "retained installers" measures whether the app **stayed installed**, not whether it opened. The same app can read ~70% D30 in Play and ~20% in Firebase, and both are correct.

The skill's primary job is catching that. The analysis is secondary.

## Structure

```
skills/dashboard-builder/
  SKILL.md                            workflow, operating principles, non-negotiable rules
  references/
    data-quality-gate.md              BLOCKER/WARNING/INFO severity, check sequence, anomaly triage
    comparability-rules.md            when two numbers must not be compared, and what to say instead
    kpi-framework.md                  formulas, definitional variants, action triggers, sourced benchmarks
    analysis-playbook.md              ingestion, time-series, funnel, channel, CRM, executive diagnosis
    dashboard-blueprints.md           the dashboard template catalog, design spec, rendering mechanism
    presentation-blueprints.md        the presentation/deck output format — layouts, content rules, PPTX rendering

research/
  search-playbook.md                  how to search the web for KPI *relationships* (vs definitions)
  raw/                                vendor-sourced metric definitions, every entry with a source URL
    google-stack-metrics.md           GA4, Google Ads, Play Console, Firebase, Search Console
    mmp-attribution-metrics.md        Adjust, AppsFlyer, Branch, Singular, SKAdNetwork/AdAttributionKit
    crm-lifecycle-metrics.md          Braze, Klaviyo, Iterable, Insider, D·engage, MPP, deliverability
    paid-media-metrics.md             Meta, TikTok, LinkedIn, IAB/MRC standards, platform incrementality
    unit-economics-metrics.md         CAC, LTV/CLV, payback, retention, churn, NRR, MER, iROAS
    dbt-data-quality-tests.md         dbt-utils and dbt-expectations generic tests for marketing data

scripts/                              repo validators (frontmatter, internal links, references-table/disk sync)
tests/                                unit tests for the validator scripts
evals/                                pointer to TEST-SUITE-regression-benchmark.md's golden-test cases

dashboard-builder-consolidated.md   generated release artifact — see CLAUDE.md, don't edit directly
MAINTENANCE-LEDGER.md                 pass/module tracking for maintenance and audits
```

## Development

```bash
bash scripts/validate.sh              # frontmatter, internal links, references table, plugin manifest, staleness
python3 -m unittest discover -s tests -v
```

Both run in CI (`.github/workflows/validate.yml`) on every PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the editing workflow and [`CLAUDE.md`](CLAUDE.md) for the repo's binding maintenance rules (source-of-truth discipline, sourcing standard, no real account data in the repo).

## Sourcing standard

Every definition, formula and benchmark in `research/raw/` was verified against a page fetched at research time and carries its source URL. Items that could not be verified are listed as omitted rather than filled in from memory. Where sources genuinely disagree — and they often do — **both positions are recorded as a conflict rather than resolved silently.**

Benchmarks always carry their sample and the caveat the publisher attached. Several widely repeated industry numbers turned out to be misattributed or self-contradictory; those are flagged in place.

## Status

Early build. The skill and its references are complete and internally consistent; end-to-end testing against real exports is pending.

## Prior art

The structural patterns here draw on [aaron-he-zhu/aaron-marketing-skills](https://github.com/aaron-he-zhu/aaron-marketing-skills) (Apache-2.0) for the KPI-matrix format with action triggers and the proxy-vs-outcome measurement model, and on [ai-analyst-lab/ai-analyst](https://github.com/ai-analyst-lab/ai-analyst) (MIT) for the metric-spec template and the severity-graded data-quality gate.
