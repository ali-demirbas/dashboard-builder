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

## Source-link reachability check — 2026-10-10

Automated HTTP check of every source URL cited in `research/raw/` (187 links). **Reachable is not the same as re-verified:** a 200 means the page still exists, not that it still says what the raw file quotes. Content was last read at each file's research date; nothing below was re-read in this pass.

- **163 reachable** (HTTP 200).
- **23 returned 403** — these hosts block automated requests, so their status is **unknown, not dead**. Re-check by hand before relying on a claim that cites one.
- **1 returned 404** — the link is dead; the claim it supported is **unverified until a replacement source is found**.

| Link | Status | Cited in |
|---|---|---|
| `branch.io/resources/blog/whats-the-difference-last-touch-vs-install-touch-attribution/` | 403 | mmp-attribution-metrics.md |
| `clevertap.com/blog/user-retention-guide/` | 403 | unit-economics-metrics.md |
| `dl.acm.org/doi/10.1145/3419394.3423662` | 403 | causal-evidence-three-relationships.md |
| `forentrepreneurs.com/ltv/` | 403 | unit-economics-metrics.md |
| `forentrepreneurs.com/saas-metrics-2/` | 403 | unit-economics-metrics.md |
| `forentrepreneurs.com/startup-killer/` | 403 | unit-economics-metrics.md |
| `help.branch.io/marketer-hub/docs/branch-methodology-overview` | 403 | mmp-attribution-metrics.md |
| `help.branch.io/marketer-hub/docs/deepview-analytics` | 403 | mmp-attribution-metrics.md |
| `journals.sagepub.com/doi/10.1177/0022243718820587` | 403 | causal-evidence-three-relationships.md |
| `journals.sagepub.com/doi/10.1177/002224379503200201` | 403 | causal-evidence-three-relationships.md |
| `journals.sagepub.com/doi/abs/10.1177/0022243718820587` | 403 | causal-evidence-three-relationships.md |
| `support.appsflyer.com/hc/en-us/articles/115005600889` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/207033786` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/207040496` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/207040506` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/207447003` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/208338403` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/218254203` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/4410634145425` | 403 | mmp-attribution-metrics.md |
| `support.appsflyer.com/hc/en-us/articles/4413026674833` | 403 | mmp-attribution-metrics.md |
| `support.iterable.com/hc/en-us/articles/213805923-Metric-Definitions` | 403 | crm-lifecycle-metrics.md |
| `support.singular.net/hc/en-us/articles/43108170707739` | 403 | mmp-attribution-metrics.md |
| `www.branch.io/resources/blog/whats-the-difference-last-touch-vs-install-touch-attribution/` | 403 | mmp-attribution-metrics.md |
| `dengage.com/knowledge-base/` | 404 | crm-lifecycle-metrics.md |

Claims in the skill that rest on a source in this table, or that this pass could not check against any primary source, are to be read as "per vendor documentation as last verified" and re-checked before they drive a decision.

**Re-read in this pass (content, not just reachability):** Adjust's data-discrepancies page — still states "Google uses 30 days, Facebook uses 60 days." **Tried and could not re-read:** Meta's attribution-settings help page (returns only its title to an automated fetch), so Meta's current 7-day-click default stays "as last verified August 2026." The `dengage.com/knowledge-base` 404 supports no claim in the skill — it sits in a raw file's "not verified, deliberately omitted" list.
