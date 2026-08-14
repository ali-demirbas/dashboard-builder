# Freshness Ledger — research corpus maintenance

Not part of the skill's runtime behavior. The skill has no memory across sessions and can't check its own freshness — this is a maintenance tool for whoever (human or Claude) periodically revisits `research/raw/` and the vendor-specific facts baked into `skills/dashboard-builder/references/`.

Every vendor-specific numeric fact in this skill (attribution window defaults, MAU windows, counting-rule specifics, API field names) is a snapshot as of when it was researched. Platforms change these without warning — the whole point of `comparability-rules.md`'s "Freshness note" is that configuration changes move numbers with no change in behavior, and that applies to the vendor facts recorded *about* those platforms too. This ledger exists so a refresh pass can find what's aging without re-reading every file cover to cover.

## How to use this

When doing a refresh pass on one platform's facts: find its row below, re-check the cited facts against the platform's *current* official docs, then update the row. Don't refresh everything at once — refresh the platform that's actually relevant to what's being worked on, the same way research passes have always been triggered by a real need, not a schedule.

| Platform / area | Last verified | Source files carrying its facts | Known-volatile facts (check these first) | Changed since last check? |
|---|---|---|---|---|
| GA4 | 2026-08-14 | `comparability-rules.md` §2.2-2.4, `kpi-framework.md` §1/§5, `research/raw/google-stack-metrics.md` | Key event lookback defaults, attribution model list, data-thresholding behavior, `purchaseRevenue`/`grossPurchaseRevenue`/`totalRevenue` scope | — |
| Meta Ads | 2026-08-13 | `comparability-rules.md` §2.1-2.3, `kpi-framework.md` §2/§5, `research/raw/paid-media-metrics.md` | Estimated-metrics list, attribution window defaults, "in development" metric list | — |
| Google Ads | 2026-08-13 | `comparability-rules.md` §2.1/§2.4, `kpi-framework.md` §2/§5, `research/raw/paid-media-metrics.md` | Conversion window defaults, Impression Share/Quality Score guidance | — |
| TikTok / LinkedIn Ads | 2026-08-13 | `comparability-rules.md` §2.1-2.2 | Attribution window recommendations, video-view definitions | — |
| Adjust / AppsFlyer (MMP) | 2026-08-13 | `comparability-rules.md` §2.1-2.2, `kpi-framework.md` §2/§5, `research/raw/mmp-attribution-metrics.md` | Default click windows, ROAS formula scope (ad-revenue inclusion) | — |
| Play Console / Firebase | 2026-08-13 | `comparability-rules.md` §2.3 | MAU window length, retained-installers definition | — |
| Braze / Klaviyo / Iterable / Insider / D·engage (CRM/ESP) | 2026-08-13 | `comparability-rules.md` §2.2, §3, `kpi-framework.md` §6, `research/raw/crm-lifecycle-metrics.md` | Open/CTOR denominator conventions, incrementality display quirks | — |
| SaaS/unit-economics benchmarks | 2026-08-13 | `kpi-framework.md` §7, `research/raw/unit-economics-metrics.md` | All benchmark tables — these are the fastest-aging facts in the skill, explicitly flagged (`kpi-framework.md` §7's own freshness note: treat >18-24 months as directional only) | — |
| Data-quality tooling dimension taxonomy (benchmarked against, not named in skill files) | 2026-08-14 | `data-quality-gate.md` §1-§5, `research/raw/dbt-data-quality-tests.md` | Macro defaults (3σ/7-day/14-day window) | — |
| Commercial AI-BI product mechanisms (metric-definition/insight architecture benchmarked against) | 2026-08-14 | `comparability-rules.md` Evidence Ladder, `dashboard-blueprints.md` caption types/QA gate | Product mechanisms move fast; re-verify before citing a specific named mechanism as still current | — |

**"Last verified" is the date the underlying fact was actually fetched and read, not the date a file was last edited for wording.** Update it only when the fact itself was re-checked against a live source.
