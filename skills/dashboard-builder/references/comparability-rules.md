# Comparability Rules — when two numbers must not be compared

Load this **before** putting any two figures side by side, ranking channels, building a cross-platform table, or reading a trend across a tooling change.

Every rule below traces to a vendor's own documentation or a peer-reviewed paper (full citations in `research/raw/`). The few lines that are instead a working heuristic or a vendor-run simulation are labeled as such where they appear. These are not opinions about best practice; they are counting mechanics that make the arithmetic invalid.

**Freshness note:** attribution windows, lookback defaults, and other vendor-specific numbers below (Adjust's 7-day default, Google's 30-day, GA4's 90-day, LinkedIn's 90-day recommendation, etc.) reflect vendor documentation as last verified in August 2026 (per-file dates and unreachable source links: `research/FRESHNESS-LEDGER.md`). Platforms change these defaults — the point of this file is that configuration changes move numbers with no change in behavior, and that applies to the vendor facts recorded here too. Spot-check a specific window/threshold against the live platform before it drives a budget or bidding decision; don't treat a number below as permanently fixed.

## How to use this file

When an analysis requires comparing two numbers, classify the comparison into one of four states — don't just binary-flag it "blocked" or "fine":

| State | Meaning | What to do |
|---|---|---|
| **DIRECT** | All checklist dimensions (§1) match, no named hard block applies (§2), **and** you've explicitly confirmed deduplication, fraud-filtering, and event-replay handling are comparable too — not just silence on those three | Compare as-is |
| **NORMALIZABLE** | Dimensions differ but the difference is a pure unit/scale/format conversion with no underlying definitional gap (e.g. MER as spend÷revenue vs revenue÷spend — a reciprocal, nothing else differs) | Convert one side to the other's convention, state which, then compare |
| **CONDITIONAL** | Both figures are individually valid but answer different questions or cover different scopes (e.g. Adjust installs vs GA4 new users — neither is wrong, each serves a different purpose) | State what each number is actually valid for; do not rank or net them against each other |
| **NOT_COMPARABLE** | A named hard block applies (§2) and no normalization exists — the definitions themselves diverge, not just their units | Refuse: state `Not comparable: <rule>`, give the reason, and name what evidence/normalization would be required to make it comparable |

Never silently pick a side. Never average two incompatible numbers. State which of the four states applies and *why* — "not comparable" and "comparable after converting units" are different findings and must not be reported the same way.

---

## 1. The pre-comparison checklist

Before any side-by-side, confirm all seven match. Any mismatch rules out DIRECT — determine whether the comparison is NORMALIZABLE, CONDITIONAL, or NOT_COMPARABLE instead (see the state table above).

**This checklist is necessary, not sufficient — passing it does not by itself earn DIRECT.** Deduplication logic, fraud filtering, and event-replay handling can all differ even when counting unit, window, model, and date basis line up, and none of those three has its own checklist row; **currency, timezone, and grain are checked separately in `data-quality-gate.md`, not here** — a clean pass on both files is what DIRECT actually requires, not this checklist alone. Also run the specific named hard blocks in §2, which cover exactly this kind of gap (e.g. "Conversions summed across ad platforms" in §2.1 is a dedup issue the seven-point checklist alone would not catch). Treat §1 as the first filter, §2 as the list of known failure modes that survive it, and `data-quality-gate.md`'s validity/consistency checks as the layer underneath both.

**Reporting requirement:** you do not need to print all seven rows every time — but you must name **every check that fails or is unknown**, not just the clearest one or two. "Unknown/not stated" is a mismatch, not a pass: if a source's attribution window or date basis isn't in the file, that check fails the checklist exactly like a confirmed mismatch does, and both are named in the state finding (and in the §4 refusal, if the comparison ends up NOT_COMPARABLE — see the next paragraph for why it usually doesn't).

**An unknown check rules out DIRECT specifically — it does not by itself force NOT_COMPARABLE.** Real exports routinely omit attribution-window/model metadata entirely, and treating every such gap as an automatic hard refusal would make most real-world cross-source comparisons unusable. Failing this checklist only means DIRECT isn't available; per the state table above, NOT_COMPARABLE additionally requires a *named hard block from §2* to actually apply. Absent one, an unknown-but-not-confirmed-mismatched dimension resolves to CONDITIONAL by default (state what each side is valid for) — not a refusal. Reserve NOT_COMPARABLE for when §2 actually names the mechanism, exactly as its own definition requires.

| # | Check | Why it breaks things |
|---|---|---|
| 1 | **Counting unit** | Device vs user vs account vs app instance vs session vs message |
| 2 | **Denominator** | Sent vs delivered vs recipients; impressions vs clicks vs users |
| 3 | **Attribution window** | 1-day view vs 90-day view is not a performance difference |
| 4 | **Attribution model** | Last-touch vs data-driven vs install-touch vs incremental |
| 5 | **Date basis** | Dated to the click/impression vs dated to the conversion |
| 6 | **Observed vs modeled** | Modeled/estimated figures have no matching row anywhere |
| 7 | **Cohort maturity** | A 12-month cohort's LTV is not a smaller version of a 36-month cohort's |

---

## 2. Hard blocks — never compare these

### 2.1 Across ad platforms and measurement systems

**Install/conversion counts across an MMP, GA4, and an ad platform — ranked, netted, or summed against each other.** (Placing them side by side with each one's valid use stated is CONDITIONAL, not blocked — that's the reconciliation `data-quality-gate.md` §6 exists for. Treating the gap as a performance difference, or picking one as "the real number," is what's blocked.) At minimum these differ by attribution window length, attribution method, date basis, identity model, session rules, fraud filtering, and SKAN deduplication. Adjust's default click window is 7 days, and Adjust's own discrepancy documentation cites partner-side windows of Google 30 days and Facebook 60 days as its example. (That Facebook figure is Adjust's — re-read on Adjust's live page on 2026-10-10, which still says "Google uses 30 days, Facebook uses 60 days"; it conflicts with Meta's own current 7-day-click default — §4's worked example — and with AppsFlyer's SRN table, which lists Meta at 7 days. Recorded as a conflict between vendor docs, not resolved here: read the window off the actual account.) Installs landing in whatever gap exists are **Organic in the MMP and paid in the network dashboard.**

**Conversions summed across ad platforms.** Each platform dedupes only within itself. Meta dedupes across Facebook and Instagram; LinkedIn dedupes to member accounts; TikTok produces its own estimate. **Platform-reported conversions cannot be assumed additive unless cross-platform deduplication is independently established — which in practice is rare, so treat a naive sum as an over-count by default.** Google states the same dedup-only-within-itself limitation for its own data-driven model.

**Revenue summed across ad platforms and a platform-of-record.** The same failure as above, on the metric most likely to end up on an executive KPI card. GA4 revenue, Meta attributed revenue, and Google Ads conversion value are each that platform's own attributed credit for transactions that also appear — once — in the underlying e-commerce/finance system (Shopify, Stripe, a finance export). None of these is "this platform's own separate revenue"; they are the same transactions viewed and credited differently. **"Total Revenue" on any KPI card or dashboard must come from exactly one authoritative source — the transaction/finance system of record, never an ad platform.** Per-platform attributed revenue may be reported alongside it, but labeled explicitly `Attributed (Platform X)`, never summed into the total. A dashboard showing GA4 (1M) + Meta (400K) + Google Ads (500K) + Shopify (1M) as "Total Revenue = 2.9M" against a true ~1M figure is not a rounding error — it is this hard-block category's highest-stakes instance, the one most likely to reach a CFO's desk unchallenged because every input number is individually real.

**Any cross-platform ROAS table built on each platform's recommended settings.** LinkedIn recommends 90-day click / 90-day view. Meta's default view window is 1 day. TikTok's maximum is 7. These are three different counting universes wearing one column header.

**Meta ad sets on different attribution models, inside one Meta table.** Meta's own warning: "Results cannot be compared in the Campaign Overview table across ad sets with different attribution models… comparing across different attribution models will lead to inaccurate conclusions."

### 2.2 Across metric names that look identical

*Two entries in this section — MER between vendors, and Google Ads ROAS vs Target ROAS — are tagged NORMALIZABLE. They sit here because they are look-alikes that get confused, not because they are blocked.*

**CTR between Meta and Google, or between Meta's own two columns.** Meta ships CTR (link) and CTR (all) in the same column picker; Clicks (all) includes reactions, comments, shares and profile taps. Google's account-level blended CTR mixes Search and Display behavior. **Reporting "CTR" without naming which one is an easy and consequential Meta reporting error.**

**"Video views" across platforms.** Meta = 3 seconds, replays excluded. TikTok = **a play start with no minimum duration**. LinkedIn = 2 continuous seconds at ≥50% on screen. Google = 30 seconds in-stream / 10 seconds in-feed. A blended cross-platform view rate is arithmetic over incompatible units.

**Video completion rates between TikTok and LinkedIn.** TikTok's quartiles exclude replays; LinkedIn's quartiles **include viewers who skipped ahead to that point**. The two are biased in opposite directions.

**"Impressions" as a quality measure.** Under IAB/MRC a served impression only requires the ad to "begin to render" and "does not require any portion of the ad to be visible or displayed on screen." LinkedIn gates Sponsored Content at 50%/1s desktop but applies **no gate** on its Audience Network. TikTok exposes `gross_impressions` including invalid impressions. Meta states its video impression counting "differs from industry standards."

**GA4's own "purchase revenue" family — `purchaseRevenue` vs `grossPurchaseRevenue` vs `totalRevenue`.** GA4's Data API defines these as genuinely different scopes, not synonyms: `purchaseRevenue` is net of refunds; `grossPurchaseRevenue` is explicitly **not** net of refunds; `totalRevenue` adds subscription and ad revenue on top of purchase revenue, still net of refunds. A column headed "Purchase revenue" in an export can trace to either the net or the gross metric — the UI label alone does not disambiguate. Confirm which API metric produced the export before treating any GA4 "revenue" figure as net or gross.

**GA4's own `returnOnAdSpend` — the same ad-revenue conflation as Adjust's ROAS, under a different vendor.** `returnOnAdSpend = totalRevenue ÷ advertiserAdCost`, and since `totalRevenue` (above) folds in the app's own ad revenue alongside purchase/subscription revenue, GA4's native ROAS inherits the identical numerator-conflation problem already named for Adjust below — a sixth vendor-specific ROAS definition, not comparable to a pure e-commerce ROAS from AppsFlyer, Meta, Google Ads, or Triple Whale/MER without checking whether ad revenue is present in the numerator.

**Open rate across ESPs.** The denominator is **Delivered** in Braze, Insider, Iterable and D·engage, but **Recipients** in Klaviyo. The same list reads systematically lower in Klaviyo.

**CTOR across ESPs.** Braze's denominator explicitly **includes machine (MPP) opens**. Iterable's denominator is "opens **or clicks**," so every clicker is in the denominator by construction and CTOR can never exceed 100%. Insider uses unique clicks over unique opens. Three different quantities, one acronym.

**CTR inside Insider.** Email CTR uses **unique** clicks; web push and SMS CTR use **total** clicks. Same vendor, same word, different math.

**Spam complaint rate against the Gmail/Yahoo 0.3% threshold.** Google and Yahoo compute spam rate on **inbox-delivered mail only**; Braze divides by Sends and Klaviyo by Recipients. An ESP-reported spam rate is structurally lower than the number the threshold refers to.

**ROAS between Adjust and AppsFlyer — NOT_COMPARABLE, and it's not just a ratio-vs-percentage issue.** Adjust reports a **ratio**; AppsFlyer reports a **percentage** — the same campaign reads 0.8 and 80, and ×100 alone looks like it should fix that. It doesn't: **Adjust's ROAS numerator is `(Cohort revenue + Cohort ad revenue) ÷ Ad Spend`, while AppsFlyer's is plain `Revenue ÷ cost × 100`.** Adjust folds in ad revenue the app itself earned from showing ads to users; AppsFlyer does not. Even after converting the scale, the two are measuring different things unless you know whether ad revenue is present and back it out — this is a genuine definitional gap, not a NORMALIZABLE unit conversion.

**eCPI between Adjust and AppsFlyer.** Adjust divides by installs; AppsFlyer divides by **attributions** (installs + re-engagements + re-attributions).

**MER between vendors — NORMALIZABLE, not a hard block.** Northbeam, Shopify and Daymark compute revenue ÷ spend (a multiple, higher is better). Triple Whale computes **spend ÷ revenue** (a percentage, lower is better). Unlike the ROAS case above, both sides use the exact same two inputs (total revenue, total marketing spend) — this is a pure reciprocal, `MER_TripleWhale = 1 / MER_others`. Take the reciprocal, state which convention you converted to, then compare. **Any MER benchmark quoted without stating its convention is ambiguous**, but the fix is a one-line conversion, not a refusal.

**Google Ads "ROAS" vs the Target ROAS setting — NORMALIZABLE, not a hard block.** Reported as a ratio (4.0); the bid setting is a percentage (400%). Same inputs, pure scale — multiply by 100 and compare. Listed here only because it's the single most-confused pair in a Google Ads export, not because the definitions differ.

### 2.3 Across identity and platform layers

**Bounce rate between a self-hosted analytics tool (Matomo/Piwik-family) and GA4.** Matomo's bounce rate is a classic **single-pageview** definition — visits that started and ended on one page, ÷ visits that started on that page. GA4 has no such metric; its bounce rate is the **inverse of engaged sessions** (not engaged = <10s, no key event, <2 page/screen views). These are categorically different signals sharing one name, not two measurements of the same behavior. *(source: `matomo-org/matomo` `BounceRate.php` vs GA4 engagement-rate docs — see `research/raw/semantic-layers-mmm-clv.md` and `google-stack-metrics.md`)*

**Retention rate between two product-analytics tools without checking the anchor mode.** Amplitude's "Return On" vs "Return On or After" is not just a naming difference — it is the same distinction PostHog implements in code as `RETENTION_FIRST_OCCURRENCE_MATCHING_FILTERS` (non-cumulative) vs a `cumulative` flag (returned by day N *or later*). Before comparing a retention % between any two tools, confirm which mode both are running — not just which vendor.

**Play Console vs Firebase vs an MMP.** Play counts **Google accounts across devices**; Firebase counts **SDK-identified app instances**; MMPs count **devices**. Play MAU is a rolling **28 days**; GA4/Firebase MAU is **30 days**. These disagree by construction before any behavioral difference.

**Play "retained installers" vs Firebase Day-N retention.** Play measures whether the app **stayed installed**; Play states explicitly this "does not mean the app was opened." Firebase requires an actual **return visit**. The same app can read on the order of ~70% D30 in Play and ~20% in Firebase (illustrative magnitudes, not a measured pair) and **both are correct**.

**Play install events vs store listing acquisitions vs Firebase `first_open`.** Three different counting units. A download with no first launch produces zero `first_open`; a reinstall produces a **new** `first_open`.

**Play "user loss" vs Firebase `app_remove`.** Play counts a user lost after **30 days of device inactivity without any uninstall**; `app_remove` fires on actual package removal and is **Android-only**. Neither validates the other.

**GA4 User acquisition vs Traffic acquisition reports.** Google explicitly warns not to compare metric values across them, and both display identically named metrics. Worked example: a user who arrives once from Google then returns 10 times directly puts **all 11 sessions under "Google"** in User acquisition, but 1 under Google and 10 under "(direct)" in Traffic acquisition.

**GA4 "Users" against Universal Analytics "Users."** GA4 reports show **Active users**; the UA analogue is **Total users**, available only in Explorations. Google's own tolerance bands are ±10% on pageviews and ±20% on user/session metrics — **any trendline spanning the migration carries a built-in step change of up to 20% that is not a real business change.**

**GA4 item-scoped vs. event-scoped reports, joined by date.** GA4's Data API blocks a genuinely incompatible dimension/metric combination (e.g. an item-scoped dimension like `itemName` alongside several event-scoped metrics) from ever landing in one export — so this specific mismatch can't arrive as a single file. It can still arrive as **two** files: an item-level report and an event/user-level report, pulled separately and joined by date. Treat that join with the same cross-file grain-match discipline as any other two-file join (`data-quality-gate.md` §1) — it reproduces as a grain mismatch, not a GA4-specific bug.

**GA4 UI against BigQuery export.** Modeled data is **not available in BigQuery**; Google Signals data is **not available in BigQuery** but is in the UI; session counts are a HyperLogLog++ **estimate** and will never tie to `COUNT(DISTINCT ga_session_id)`. **Neither surface is complete.**

**GSC organic CTR against Google Ads CTR.** Identical arithmetic, incompatible denominators: GSC counts a result "present on the page" with **no scroll or viewability requirement**, including results the user demonstrably never looked at.

**Two GSC numbers from the same report.** The chart is always property-aggregated while the table **silently switches to page aggregation** when you select Pages or Search Appearance. CTR and average position are generally higher under property aggregation.

### 2.4 Across time and configuration changes

**Any Google Ads conversion trend covering the last 30 days.** Primary conversion columns are dated to the **click, not the conversion**, so the recent window is permanently incomplete and keeps filling in. **The same past date returns different numbers when re-pulled weeks later.** Use the separate "Conversions (by conv. time)" column for third-party comparison.

**Any Meta trend covering recent days.** Same mechanic: conversions are reported on the date of the impression or click.

**Before vs after a GA4 reporting-identity change.** Switching Blended/Observed/Device-based is **fully retroactive** — every historical user count in the property changes the moment someone flips it, with no annotation in reports.

**Before vs after a GA4 attribution-model change.** Applies to **historical and future** data, silently restating past reports. First click, linear, time decay and position-based were removed in November 2023, so pre-2024 model comparisons cannot be reproduced.

**Before vs after a Klaviyo attribution-window change.** "Any changes to attribution will apply to both historical and future conversions."

**Before vs after a lookback-window change in Google Ads, GA4 key events, or an MMP.** These apply **going forward only**, creating an invisible discontinuity mid-series.

**Before vs after a Conversions API deployment.** CAPI raises matched events, which raises attributed conversions. **A step-change with no change in real demand.**

**Any trend spanning an OS- or browser-level privacy rollout — Apple's App Tracking Transparency (iOS 14.5, April 2021), Apple Mail Privacy Protection (iOS/macOS, 2021), or a Google Privacy Sandbox / third-party-cookie-deprecation milestone.** These are not campaign or product changes — they are platform-side measurement breaks that hit every advertiser simultaneously, at a known date. A cliff in iOS installs, SKAN-vs-MMP install gap, or paid-search-conversion drop that lines up with one of these dates is a measurement artifact until proven otherwise, not a demand or creative problem. Check the rollout date against the trend break **before** any other anomaly explanation.

**Before vs after turning on MMP fraud prevention.** Blocked installs are removed from attributed traffic, mechanically **lowering paid installs and raising Organic** against an unchanged invoice.

**Before vs after adding a soft action to Google Ads primary conversions.** CPA "improves" with zero business change.

**Before vs after re-designating a GA4 key event.** Engaged sessions, engagement rate and bounce rate all move with no traffic change. Renaming an event that is already a key event **silently removes its key-event status.**

**A GA4 event name over 40 characters marked as a key event.** Google's own collection-limits documentation: event names are capped at 40 characters, and a key event past that limit **fails to report as a key event** because the internal `_c` suffix that marks it can't be appended. The event still fires and still shows up in raw event counts — it just silently stops counting toward conversions, attribution, and audiences built on it. A conversion-rate cliff with unchanged raw event volume is the signature; check event-name length before writing a demand-side explanation.

**Any comparison spanning a retention-definition change.** Rolling/unbounded retention is **always ≥** classic N-day retention. A product can double its headline retention by switching definitions with no behavior change.

**Crashlytics crash-free rate across different period lengths.** Firebase states it "should not be compared across different time periods" — it is an aggregation over the window, so **a longer window mechanically lowers it.**

### 2.5 Cohort and lifetime comparisons

**LTV across cohorts of different maturity.** Truncating at a finite horizon "is ignoring the residual value of the customer beyond that point." Fader & Hardie's prescription: call it **truncated CLV over T+1 periods**, not lifetime value. **A 12-month cohort LTV and a 36-month cohort LTV are two different quantities, not two performances.**

**A blended retention curve read as a cohort curve.** Retention rates **increase** with customer tenure within a cohort; the flat curves in company-reported summaries "are in fact the result of aggregation across different cohorts." Averaging new customers in with existing ones masks the real shape.

**LTV computed from two different formulas.** Three mutually inconsistent textbook forms circulate (`m(1+d)/(1+d-r)`, `mr/(1+d-r)`, `m/(1+d-r)`), differing on whether the first payment counts and whether cash books at period start or end. **Fader & Hardie: "there is no 'one formula' that can be used to compute customer lifetime value."**

**Any retention or churn rate in a noncontractual setting.** "As we do not know how many customers we have lost in a given period, we cannot compute a retention rate." Substituting a repeat rate is **"completely wrong"** — it computes the probability of purchasing in t consecutive periods, not the probability of being alive.

**Churn rates across periods of different growth.** With identical underlying behavior, a start-of-period denominator produces "two completely different churn rates" in a fast-growing month versus a flat one.

**Logo churn against revenue churn.** Different denominators — revenue churn is often computed over **renewal candidates**, logo churn over all customers.

**NRR or GRR computed by the cohort method vs the formula method.** These produce different numbers; SMSB prefers cohort but concedes it "does not capture the retention performance of recently acquired customers."

**Amplitude ARPPU against a standard period ARPPU.** Amplitude's paying-user denominator includes anyone who **ever** triggered a revenue event, "even if their first revenue event occurs after the specific data point you're looking at."

### 2.6 Attribution vs incrementality — the category error

**Attributed conversions are not incremental conversions, and the platforms say so.**

Meta states Conversion Lift results and Ads Manager attributed conversions are **"not meant to be compared"** — incremental conversions are computed after scaling the holdout to the test group's size, so no clean "incrementality factor" exists by dividing one into the other. Google states incremental conversions **ignore your attribution settings entirely** and use the full study duration.

Reconciling Meta to an MMP to GA4 harmonizes three *attribution* systems. **It does not move any of them closer to causal truth.**

The empirical scale of the gap, from controlled experiments:
- eBay (Blake, Nosko & Tadelis, *Econometrica* 2015): observational regressions gave ROI of **+4,100%** uncontrolled and **+1,400%** with time and geographic controls; the randomized experiment gave **−63%**. On brand keywords, **99.5% of forgone paid click traffic was immediately recaptured by natural search.** Their conclusion: "even incremental clicks do not translate into incremental sales."
- Facebook (Gordon et al., *Marketing Science* 2019, 15 experiments / 500M observations): **"in 50% of our studies, the estimated percentage increase in purchase outcomes is off by a factor of three."** Extreme case: RCT lift 2.4% vs closest observational estimate 1306%. Biases "persist even after conditioning on a rich set of observables."
- Lewis & Rao (*QJE* 2015, 25 experiments / $2.8M spend): the median ROI confidence interval is **over 100 percentage points wide.** For a highly profitable campaign "the R² would be on the order of 0.0000054," so an observational method would need to avoid misspecification at an R² of ~0.000001 — **"an impossible statistical feat"** where selection effects run up to **30× the true treatment effect.** They name difference-in-differences and propensity score matching as vulnerable.

**Practical rule:** when a user asks "which channel is working," the honest answer distinguishes *what got credited* from *what was caused*, and names the experiment that would settle it. Never present an attributed ROAS as a causal claim.

### Evidence Ladder — label every causal-sounding claim by what actually produced it

Not all "evidence for causality" is equal, and lumping them together is exactly the mistake this whole section exists to prevent. Before writing a sentence that implies X caused Y, classify the evidence:

| Level | What it is | Example | Can it support a causal sentence? |
|---|---|---|---|
| **E0 — Raw observation** | A single number or fact | "CVR was 2.1% in June" | No — it's not a comparison yet |
| **E1 — Descriptive pattern** | A trend or co-movement over time, one series (a *single*-period move is still E0 — see the trend gate below) | "CVR has fallen three months running" | No — and don't write "trending" language until the move clears both bars in the trend gate below |
| **E2 — Correlation** | Two metrics move together, no control group | "CVR fell as CPI rose" | No — state as correlation, name the confound risk |
| **E3 — Quasi-experimental design** | A named identification strategy with its assumption explicitly checked: difference-in-differences, regression discontinuity, instrumental variables, or a matched/synthetic control — **the design, not the comparison** | "DiD on treated vs. matched control geos, parallel trends shown for the pre-period" | **A conditional causal statement only** — "under [the named assumption], X is estimated to have changed Y by …" — never an unqualified "X caused Y." Three things appear together or the claim drops to E2: the identification assumption, named (parallel trends, no sorting at the cutoff, instrument exclusion); the check actually run on it (pre-period trends shown, a placebo test); the estimate with its interval. Still weaker than E4 — this is the tier eBay's *controlled* regression (time + geo controls) got +1,400% ROI wrong on; the uncontrolled +4,100% figure is E2. A design merely *labeled* quasi-experimental, assumption unchecked, does not reach this tier |
| **E4 — Controlled experiment** | A/B test or holdout **with real randomization** — including a genuinely randomized geo experiment, where geos are randomly assigned to treatment/control before the test runs (the Vaver & Koehler / Google Research design) | Meta Conversion Lift, Google Conversion Lift (user-based), a randomized geo experiment | **Yes**, within that test's own confidence interval and duration |
| **E5 — Replicated causal evidence** | The same effect confirmed across multiple **independent** E4 studies — independent in method, not just independent runs of the same tool | — | **Yes**, with the highest confidence this framework recognizes. **Replication only counts if the studies don't share the same systematic bias** — three runs of the same flawed measurement approach is not replication, it's a repeated error |

**The ladder grades causal claims, and only causal claims.** A descriptive finding — "revenue fell 12%," "Channel A's CPI is twice Channel B's" — asserts no cause and needs no tier above E1 to be stated plainly and with full confidence. How far to trust the number itself is *measurement confidence* (`analysis-playbook.md` §Confidence): a separate label, driven by data quality, comparability and statistical support, never by the evidence tier.

**Geo-lift tools are not automatically E4 — check the mechanism, not the name.** "Geo-lift" bundles two different methodologies that this skill's own research distinguishes: (1) a **randomized geo experiment**, where geos are actually randomly split into treatment/control before the test starts — this is E4. (2) A **synthetic-control geo-lift tool** (e.g. Meta's GeoLift, built on Augmented Synthetic Control + Generalized Synthetic Controls), which constructs a counterfactual from *non-randomly-selected* control markets after the fact — this is closer to E3, not E4, because the control was matched/weighted, not randomly assigned. The performance gap is not theoretical: Recast's 32,000-run simulation (vendor-run, not peer-reviewed; cited in the soft-flags table below) found Meta GeoLift's confidence intervals contain zero in 95.7% of runs and Causal Impact fires false alarms nearly 30% of the time — these tools measurably do not perform like a true randomized experiment. Before citing any "geo-lift" result as E4, confirm the specific tool used randomized geo assignment; if it used synthetic/matched controls, treat it as E3 and hedge accordingly.

**The trend gate — two bars before "trending," sized to the metric, not a fixed count.** A single-period move is E0 (a raw observation), not E1. Before writing trend language, clear both:

1. **Persistence** — the direction held long enough to be a pattern rather than a point. **How long depends on the metric's cadence and the business context, not a universal number:** as working heuristics rather than sourced thresholds — a monthly SaaS MRR series needs ~3 periods; a daily revenue series usually needs more than 3 days, since daily marketing data is noisy and weekly-seasonal; a 3-day flash sale has no "3 periods" to hold across at all — there, the campaign *is* the unit, and the right comparison is against a comparable prior campaign, not against three of its own days. State which cadence and how many periods you applied, rather than asserting "the trend" and leaving the reader to guess the basis.
2. **Not just the cycle repeating** — check the move against the same period last cycle (last week/month/quarter/season). A move consistent with a known seasonal pattern is the pattern recurring, not a new trend, and reporting it as new is one of the easiest ways to manufacture a finding out of ordinary rhythm.

**A bare pre/post or cohort comparison is NOT E3 — it is E1 or E2, and this distinction matters more than it looks.** "CVR before vs. after the tracking change" and "the March cohort retained better than the January cohort" are *descriptive comparisons*: two numbers placed side by side with no control, no counterfactual, and no identification strategy. Calling them quasi-experimental grants them a methodological standing they haven't earned, and quasi-experimental sits close enough to "experiment" that the label alone does most of the work of convincing a reader. The comparison only becomes E3 when a design is actually applied to it — a matched control group, a parallel-trends check, a discontinuity, an instrument — and that design's assumption is stated and checked. Without that, a pre/post read is E1 (one series over time) and a cohort comparison is E2 at best (two groups co-varying with an unmeasured selection difference between them).

**Apply it like this:** "Revenue declined while paid traffic declined" is E1/E2 — write it as an observed co-movement, not as "paid traffic drove the revenue decline." Three permitted forms, one per band: **E4/E5** → an unqualified causal sentence ("X caused Y"), within the test's interval and duration. **E3** → the conditional form from the table, assumption and check stated in the same sentence or the next. **E0–E2** → associational language only ("consistent with," "coincided with," "would need a holdout to confirm") — a hypothesis, labeled as one. Never list a pre/post or cohort read alongside A/B tests, holdouts, and randomized geo experiments as if they were interchangeable forms of causal proof — they generate hypotheses an E4 test would need to confirm.

**Also not incrementality:** ad-platform A/B tests in the sense Meta and Google mean it — comparing two creative/audience *variants*, where every group still sees some ad (Meta's own scoping: "A/B tests do not include randomized holdout groups"). This is narrower than "A/B test" in the general statistics sense (a website conversion-rate A/B test with a true randomized control does establish causality for that specific comparison) — the point here is specifically that a variant-vs-variant ad test is not an ad-vs-no-ad holdout and cannot answer "did advertising cause this at all." Also not incrementality: Google custom experiments (head-to-head of two configurations, not ad-vs-no-ad), Meta's "incremental attribution" delivery model (**modeled prediction, not a holdout**), and MER (an efficiency ratio that moves with seasonality, retention and organic — see the Evidence Ladder above — MER is E1 at best, a single series with no control).

---

## 3. Soft flags — comparable only with a stated caveat

**A soft flag is scoped to a use, and some rows block one use outright.** Where a caveat below says a figure is "not for" something — historical comparison, billing, ranking across studies, reconciling against another count — that specific use is NOT_COMPARABLE exactly as if §2 named it. The row sits in this table because the figure stays valid for its other uses. Such rows are marked **[blocked use: …]**.

| Situation | Required caveat |
|---|---|
| Any Meta figure on the estimated list — **including `spend`, `reach`, `frequency`, Purchase ROAS** | **[blocked use: billing, historical comparison]** Meta permits these for directional guidance but **not for billing and not for historical comparison** |
| Meta's "in development" list — **6-second video plays, Video plays at 100%, Cost per ThruPlay** | **[blocked use: historical comparison]** Explicitly not for historical comparison; a YoY video-completion trend compares two methodologies |
| GA4 channel data from the last ~12 days | Attributed conversion data keeps updating for up to 12 days |
| GA4 rows with data thresholding | Rows **silently vanish rather than showing zero**; a wider date range returns *more* data, which reads as growth |
| Any GA4 table containing an `(other)` row | The table total is not the property total |
| Any GA4 `(not set)` bucket | The cause differs per dimension — it is several unrelated failures, not one traffic category |
| Meta ad sets in the learning phase | Meta: "ad sets are less stable and usually have a higher CPA… results aren't necessarily indicative of future performance." **Acting on the CPA triggers an edit that resets the phase** |
| Meta ad relevance rankings | Relative percentiles against competitors, not absolute performance, **and not auction inputs** |
| Google Ads Impression Share | The denominator is an **estimate**; "Lost IS (budget) = 40%" does not mean uncapping yields 40% more impressions |
| Google Ads Quality Score | Google: "not a key performance indicator and should not be optimized or aggregated with the rest of your data" |
| Email open rate on an Apple-heavy list | MPP fetches remote content **on receipt, not on read** — the open timestamp is a proxy-fetch time, so send-time optimization trained on it is corrupted, not merely noisy |
| Any open-rate drop read as a deliverability signal | Google: **"Low open rates aren't necessarily an accurate indicator of deliverability or spam classification issues."** Use Postmaster spam rate and reputation |
| Any viewability figure | Report the **measured rate** alongside it. Viewable rate's denominator excludes undetermined inventory — 70% viewable at 40% measured describes 28% of the buy |
| Any SKAN revenue figure | The fine conversion value exists **only in the first postback**; D7/D30 SKAN revenue is modeled from a 3-bucket coarse signal |
| Any daily SKAN install curve | Randomized 24–48h / 24–144h postback delays make it a **delivery** curve, not a conversion curve; Google SKAN can lag 45 days |
| Braze Canvas variant vs step conversions | **[blocked use: reconciling the two]** Variant conversions count from entry; step conversions only after the step's message sends. **They will never reconcile** |
| Braze global control group results | **API-triggered campaigns still reach control users** — the holdout is not airtight |
| Insider monthly incrementality summaries | **Negative incremental values display as 0**, so summary-level incrementality is systematically optimistic |
| D·engage SMS delivery rate | Changes depending on **when you pull the report** — Waiting Report drains asynchronously, Not Reported never resolves |
| Iterable holdout vs treated conversion rates | Denominators don't match: **skipped sends (send-level) vs unique delivered (user-level)** |
| Any geo-lift result | Recast's 32,000-run simulation (vendor-run, not peer-reviewed): Meta GeoLift intervals **contain zero in 95.7% of runs**; Causal Impact **"fires false alarms nearly 30% of the time."** With only 30 days of pre-period, false positives exceed 24% |
| Any lift test under 14 days | Google quantifies up to a **17% drop in Absolute Lift** because conversion lag isn't captured |
| Relative lift across two studies | **[blocked use: ranking studies by relative lift]** Google: not comparable — "studies with lower control group activity naturally produce higher percentage lifts." Compare absolute incremental conversions or iCPA |
| PSA-holdout lift on an optimized campaign | **[blocked use: reading the lift as causal]** Optimization assigns different people to PSA vs treatment, so **the PSA group is no longer a valid holdout**. The source study (Johnson, Lewis & Nubbemeyer) puts two-thirds of display dollars on performance-optimizing delivery |

---

## 4. Reporting template when a rule fires

```
⚠️ Not comparable — <rule name>
What was asked:  <the comparison>
Why it fails:    <the counting mechanic, one sentence>
What I can say:  <the valid within-source statement>
To make it comparable: <the specific normalization, or the experiment required>
```

Worked example:

> ⚠️ **Not comparable — attribution window mismatch**
> **What was asked:** rank Meta and LinkedIn by ROAS.
> **Why it fails:** LinkedIn's account is on its recommended 90-day click / 90-day view window; Meta's default is 7-day click / 1-day view / 1-day engage. LinkedIn is crediting a 90× longer view window.
> **What I can say:** each platform's ROAS trend against its own prior period is valid.
> **To make it comparable:** re-pull both at 7-day click / 1-day view, or settle it with a geo holdout — attributed ROAS will not answer this at any window.
