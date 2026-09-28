# Dashboard Blueprints: Options, Design Spec, Output Format

## Output mode 1 — first response after files arrive

**DO NOT immediately produce a giant dashboard.** Always provide, in this order:

1. **Data ingestion summary:** files detected, data sources, date coverage, KPI coverage, data quality status, important limitations.
2. **Initial diagnosis:** maximum 5–10 high-value observations.
3. **Template options:** present only the templates that fit the detected data — see "Template matching" below, not the full catalog every time.

**If the user already named a specific template** (their original request matches one below by name or clear intent, e.g. "build me the acquisition dashboard," "give me an e-commerce report"), skip asking them to choose — go straight to that template's full blueprint after step 2, since re-asking what they already told you is friction, not rigor. **If the request was open-ended** ("analyze this data," "build a dashboard"), present the fitting templates and wait for a selection. Either way, steps 1 and 2 are never skipped — the quality gate and initial diagnosis matter regardless of which template is built, and the diagnosis may reveal the requested template isn't well-supported by the data, which is itself worth surfacing before building it. **When the requested template genuinely isn't supported, don't just say no — name what would make it possible.** Two or three concrete paths forward (a specific missing file/column that would unblock it; a narrower Tier 2 template the current data *does* support; proceeding with the gaps explicitly labeled "Not available") beats a bare refusal every time — the user came with a question, and "here's what's actually answerable right now" is a better response than a dead end.

## Template catalog

Eleven templates in two tiers. Tier 1 assumes a blended dataset spanning multiple domains (the original four); Tier 2 is triggered by one specific data shape and goes deep on it rather than wide. A template isn't a design skin — it's a different answer to "what does this data want to say," so the catalog grows by data shape, not by chart-color scheme.

**Ten of these eleven are dashboards — J is not.** J (Cross-Source Reconciliation) is catalogued here because it's selected the same way (matched against a data shape), but its deliverable is a written reconciliation finding, not a KPI-strip-plus-charts dashboard. Building it through the standard Visual Conventions / Dashboard Composition pipeline (below) would be a category error — see J's own entry for what it actually renders as.

**Deliberately not in this catalog: one template per ad platform.** A reference worth naming honestly, since it's the most obvious alternative structure — some competing template libraries ship a separate named template per platform (a Google Ads dashboard, a Facebook Ads dashboard, a TikTok Ads dashboard, a LinkedIn Ads dashboard, and so on, often ten or more near-identical entries). This skill deliberately uses one platform-agnostic template instead — **I, Single-Channel Deep Dive** — because the platform-specific nuance that actually matters (Meta's CTR link-vs-all split, TikTok's zero-minimum video view, LinkedIn's zero-chargeable-click video objective, and the rest) already lives in `kpi-framework.md`'s per-metric variance column, not in the template shell around it. Ten near-duplicate templates would drift from that shared source of truth the first time one of them got edited in isolation; one template that reads whichever platform's columns are present doesn't have that failure mode. If a specific platform needs a genuinely different KPI set (not just different counting rules for the same KPIs), that's a signal to extend `kpi-framework.md`, not to fork this template.

### Tier 1 — blended dataset

**A — Executive C-Level Summary**
Question: *"Is growth healthy, efficient and profitable?"*
Components: Revenue, Revenue Growth, Gross Profit, Gross Margin, Marketing Spend, ROAS, CAC, LTV, LTV/CAC, Active Users, Retention.
Visual hierarchy: 1) Executive KPI cards (Revenue Growth, ROAS, CAC, LTV/CAC, Active Users as delta-carrying stat tiles, not separate charts) 2) Revenue & Gross Profit trend — both currency, one axis 3) Gross Margin trend — its own chart, **never combined with the $ trend above** (% and ₺ on one axis is the dual-axis mistake) 4) Marketing Spend vs Revenue — index both to 100 at the period start if scaling matters more than the raw shape, since raw ₺ and ₺ can still misread as correlated when their trend lines happen to cross 5) LTV/CAC — a line trend, optionally paired with a Meter against the named benchmark band (`kpi-framework.md` §7: ~3x viable, 5x+ strong) — **caption it "vs. industry benchmark band, not a company-specific target"** whenever the user hasn't stated their own LTV/CAC goal; a Meter visually reads as progress-toward-a-target, and an external benchmark shown in that form risks implying it's the user's own stated goal 6) Channel contribution to revenue — sorted bar-in-cell table (part-to-whole across channels), not a vague "matrix" 6b) If Revenue genuinely factors into named drivers the data supports (Traffic × CVR × AOV, or similar) — a KPI decomposition tree as a deep-dive, showing which driver actually moved the top line instead of leaving the reader to infer it from three separate cards 7) Retention — one blended trend line here; route the real cohort-maturity-correct view (the heatmap) to a deep-dive, don't build the full triangle at exec-summary altitude 8) Critical risks / Opportunities / Executive recommendations — these are narrative list items from Output mode 2 steps 6–8, not charts; don't force them into a visual form.

**B — Growth & Acquisition**
Question: *"Where are we acquiring users and how efficiently?"*
Components: Spend, Impressions, Clicks, CTR, Installs, CPI, CAC, Activation, Conversion, Retention, LTV.
Visuals: acquisition funnel (Click→Install→Activation→Conversion — this is where Activation and Conversion get charted, not a separate component), channel performance table (spend/CPI/CAC/CTR per channel — a table by the "more than ~7 classes" rule, not a bespoke chart), CAC trend, CPI trend, LTV and CAC as a **grouped bar per channel** (both absolute numbers, not just the ratio — a bare ratio hides which side of it actually moved), cohort retention (the heatmap — this is the template where it earns full billing, unlike A), spend vs revenue (both currency, one axis — note this explicitly so it never gets mistaken for spend-vs-ROAS, which *would* be dual-axis), channel efficiency quadrant (≤7 channels only; 8+, plain scatter per the table above).

**C — Lifecycle & CRM**
Question: *"How effectively are we activating, retaining and monetizing existing users?"*
Components: DAU/WAU/MAU, Activation, Retention, Churn, Reactivation, Campaign reach, Open Rate, CTR, CTOR, Conversion, Revenue, Revenue/User.
Visuals: lifecycle funnel, retention curve (one blended trend, for the quick read) **and** cohort matrix (the maturity-correct heatmap, for the real read — these are complementary, not redundant: the curve is the headline, the matrix is what backs it), CRM campaign leaderboard (sorted bar-in-cell table), engagement-vs-conversion **scatter** (one point per campaign — quadrant guide lines if there are ≤7 campaigns in the window, plain scatter with outliers emphasized at 8+), churn trend, frequency-vs-conversion **scatter** (same rule — this is a relationship between two continuous metrics per user segment, not a generic "analysis").

**D — All-in-One Growth Tower**
Question: *"What is the complete growth system telling us?"*
Layers, with the visual form named per layer instead of left implicit: 1) **Executive** — reuse A's KPI-strip + trend treatment 2) **Acquisition** — reuse B's funnel/table/trend/quadrant set 3) **Product** — Activation/Engagement/Conversion as the funnel stages already covered by B's funnel 4) **Lifecycle** — reuse C's retention curve + cohort matrix + churn trend 5) **Monetization** — ARPU/AOV/Revenue/LTV as currency trends, one axis, but check scale before combining (ARPU and total Revenue can differ by orders of magnitude even in the same currency — index or separate per the "same unit isn't the same chart" rule above) 6) **Profitability** — Gross Profit (currency, can share A's revenue axis) vs. Margin and ROI (both %/ratios — their own chart, not combined with the currency trend) 7) **Intelligence** — split this layer explicitly: **Correlations** are charts (scatter, per the relationship rows above); **Anomalies** are annotations on the existing trend lines, not a new chart type; **Risks** and **Opportunities** are narrative list items (Output mode 2 steps 6–7), never forced into a visual. Layer 7 is the one place this template most often goes wrong — resist the pull to draw a chart for something that's actually a sentence.

### Tier 2 — single-domain data

**E — E-commerce & Revenue**
Question: *"Are we selling well, and to whom?"*
Components: Revenue, Orders, AOV, Units/Order, Repeat Purchase Rate, Revenue by Product/Category, New vs Returning Customer Revenue, Gross Margin, Refund Rate.
**If ad-spend data is supplied alongside the order data** (the common real case — a store owner connects Shopify plus their ad platforms), fold in CAC and ROAS from B's KPI set rather than reaching for A: the audience is still "how's the store doing," not "how's the whole growth system," so it stays this template with two components added, not a jump to the blended Executive Summary.
Visuals: revenue trend (indexed if no spend data exists to pair it against), Gross Margin as its **own** trend, not combined onto the revenue axis (% next to ₺ is the dual-axis mistake even when both happen to be "financial"), AOV as a **histogram of order values** with the mean and mode both marked on it — per `kpi-framework.md` §4's mean-vs-mode trap, a bucketed distribution shows *why* they diverge, two stat tiles only show *that* they do, Units/Order as a stat tile/trend alongside AOV, product/category revenue ranking (sorted bar-in-cell table), new-vs-returning revenue split as a **stacked bar** (two categories — a donut is tempting here and wrong: angle and area are harder to compare precisely than bar length, so a donut buries exactly the "which is bigger" question this component exists to answer), repeat-purchase funnel (1st→2nd→3rd order), refund-rate trend.

**F — SaaS / Subscription Unit Economics**
Question: *"Is the subscription base healthy and growing sustainably?"*
Components: MRR, ARR, New MRR, Expansion MRR, Contraction MRR, Churned MRR, Net New MRR, GRR, NRR, Logo Churn, Customer Count, ARPA.
Visuals: MRR movement bridge (new/expansion/contraction/churn reconciling to net — floating diverging bars, not a line, since the story is composition not just level), GRR/NRR trend, logo churn and revenue churn as two single-axis charts side by side (never one dual-axis combo), cohort NRR by acquisition month (the same triangular heatmap as cohort retention, just with NRR% in the cells instead of retention%), Customer Count and ARPA each as their own stat tile + trend — **never plotted against MRR on one axis just because all three are counts-or-currency**: ARPA is a per-customer average and typically differs from total MRR by an order of magnitude, so combining them flattens ARPA to a near-flat line at the bottom of the chart. MRR = Customer Count × ARPA is a genuine identity — a KPI decomposition tree rooted at MRR, with Customer Count and ARPA as its two children, is the more direct way to show which side of that equation actually drove a move than reading two separate trend lines and multiplying in your head.

**G — Mobile App & Store Performance**
Question: *"How is the app performing in the stores, and are people sticking with it?"*
Components: Installs, Uninstalls, Retained Installers, Store Listing Conversion Rate, Rating, Review Volume, Crash-free Rate, Update Adoption.
Visuals: install vs uninstall trend, with Retained Installers as the derived net line on the same chart (installs − uninstalls running total, same unit, same axis — this is a legitimate same-axis case, unlike the MRR/ARPA one above, because the three series share both unit *and* scale); store-listing funnel (impression→listing view→install — Store Listing Conversion Rate is this funnel's stage percentages, not a separate chart); rating trend (a bounded 1–5 line) with review volume as a **separate bar chart** (a count, different job from a bounded score — never overlaid on the rating's axis); Update Adoption as a stat tile/trend (% of base on latest version since release); crash-free rate trend — never compared across different-length periods, per `comparability-rules.md` §2.4.

**H — Web Analytics (no paid-media data)**
Question: *"How are visitors behaving on the site, independent of what brought them there?"*
Components: Sessions, Users, Engagement Rate, Pages/Session, On-site Conversion Rate, Traffic Source Mix, Landing Page Performance, Site Search Usage.
Visuals: Sessions and Users as a multi-line trend by source (small multiples or a sorted-bar breakdown work too — never a stacked area, which hides each source's own trend behind the total), Pages/Session and Engagement Rate as their own stat tiles/trends (ratios, a different scale from raw session counts — don't share the traffic-trend axis), on-site funnel, landing-page ranking (bar-in-cell table), Site Search Usage as a stat tile (% of sessions that searched) **plus** a ranked table of top search terms — "what are people searching for" is inherently a ranking question, the same form as the landing-page table, not a trend line.

**I — Single-Channel Deep Dive**
Question: *"How is this one channel actually performing, campaign by campaign?"*
Components: Spend, Impressions, Clicks, CTR, CPC, CPM, Conversions, CPA/CAC, campaign- and ad-set-level breakdown, creative-level performance (if available), Frequency, learning-phase status.
Visuals: campaign ranking (sorted bar-in-cell table), creative/ad-level performance table, frequency-vs-CTR as a **plain scatter, one point per ad set** (dozens of ad sets is the normal case here, not the ≤7 that a quadrant needs — emphasize the fatigue outliers, don't try to label every point) — the fatigue signal from `kpi-framework.md` §2, spend pacing vs. budget as a **Meter** (a single ratio against a limit, not a trend line). Use this template instead of B whenever only one ad platform's export is supplied — B's cross-channel components (channel table, efficiency quadrant) have nothing to compare against and shouldn't be built empty.

**J — Cross-Source Reconciliation**
Question: *"Why don't these two platforms agree, and which one should I trust for what?"*
Components: per-source figure, the gap, the seven-point checklist result, the DIRECT/NORMALIZABLE/CONDITIONAL/NOT_COMPARABLE classification, what each source is actually valid for.
Visuals: this template is mostly narrative, not charts, and shouldn't be dressed up as one — per-source figures as **stat tiles placed side by side, never merged into one number**; the classification as a status-colored pill (reusing the existing 🔴/🟠/🟡/🟢-family badge, not inventing a new indicator); the written reconciliation statement from `data-quality-gate.md` §"Cross-source reconciliation" as the centerpiece prose, not a footnote under a chart. This template's deliverable **is** the comparability finding — use it instead of forcing conflicting numbers into another template's KPI cards when reconciliation is the actual ask ("these numbers don't match").

**J bypasses the standard rendering pipeline.** Skip the 5–8 card KPI strip, the 2–3 mid-size chart tier, and the deep-dive/alerts/insights/actions sequence in "Visual conventions" and Output mode 2 below — those are built for a dashboard reporting on a system's performance, and J is reporting on why two numbers disagree, a different question with a different shape. Render it as: the two (or more) per-source stat tiles → the classification pill → the reconciliation statement. Nothing else is required, and adding the standard dashboard scaffolding around it dilutes the one finding that's actually the point.

**K — SEO & Organic Search**
Question: *"Is organic search actually bringing people in, and for what?"*
Components: Clicks, Impressions, CTR, Average Position, by-query breakdown, by-page breakdown, indexation/coverage status if supplied. A genuinely different data shape from H — a Search Console-style export is impression/position data about queries that never became a session if there was no click, which GA4-style web analytics doesn't carry at all; don't force this data into H's Traffic Source Mix component, it's missing the dimension (query) that makes this data useful.
Visuals: clicks + impressions trend (two series, same "count" unit — legitimate one-axis case; CTR and Average Position each get their own trend, never sharing the count axis, same dual-axis discipline as everywhere else in this file), top-queries ranking (sorted bar-in-cell table by clicks, CTR shown as a supporting column — a high-impression/low-CTR query is the single most actionable row in this table and the caption should say so), top-pages ranking (same form), position distribution as a histogram if the query list is long enough to have a real distribution rather than just a top-N. **Average Position needs the same "lower is better" framing check as CAC** — don't let a rising bar chart imply improvement when the number is a rank.

## Template matching — data shape narrows it, the business question picks it

**Data shape alone does not determine what a dashboard should say.** The matching table below answers "which templates are *possible* given what was supplied" — a necessary filter, and the thing most template systems skip entirely. But it is not sufficient on its own: one common combination (GA4 + an e-commerce export + ad-platform data) legitimately supports an executive summary, an acquisition diagnosis, a revenue diagnosis, a funnel diagnosis, and an SEO read. All five are buildable from identical columns. Only the question being asked separates them.

So run three filters in order, not one:

```
1. DATA SHAPE      → which templates are structurally possible?
                     (the matching table below — hard filter, unmet needs = not offered)
2. BUSINESS QUESTION → what is the user actually trying to decide?
                     (their own words if they gave any; otherwise what the
                      step-6 diagnosis surfaced as the live problem)
3. AVAILABLE EVIDENCE → which of those questions can this data actually answer
                     at a defensible evidence tier, and at sufficient sample size?
                     A question the data can only answer at E2 shouldn't be
                     framed as the dashboard that settles it
```

The user's original request is the strongest signal for filter 2 and usually settles it outright ("why is CAC up" → a diagnosis, not an executive summary — even though both are shape-possible). When the request was open-ended, **filter 2 comes from step 6's diagnosis, not from a default**: if the 5-10 observations concentrate on a retention collapse, the fitting template is the one that interrogates retention, not whichever one uses the most columns. Say in one line which question drove the choice — "offering B (Growth & Acquisition) because the live finding is a CAC deterioration, not a monetization issue" — rather than presenting a shape-match as if it were self-evidently the right answer.

### The data-shape filter

Don't offer every template every time. Match against what step 1–2 (`analysis-playbook.md` Inventory + Schema detection) actually found — **both** the data-shape column below **and** the minimum-history column: a data shape can be present with far too little history to build the template's trend/cohort components meaningfully, and the two checks catch different failures.

| Template | Needs, at minimum | Min. history |
|---|---|---|
| A — Executive Summary | revenue/spend across ≥2 domains (acquisition + at least one of lifecycle/monetization) | ≥30 days (trend + cohort components) |
| B — Growth & Acquisition | an ad platform or MMP export (spend, installs/clicks), ≥2 channels to compare | ≥30 days (cohort retention heatmap) |
| C — Lifecycle & CRM | a CRM/messaging export (sends, opens, conversions) or retention/churn data | ≥2 full cohort periods |
| D — All-in-One Growth Tower | acquisition + lifecycle + monetization all present | ≥30 days |
| E — E-commerce & Revenue | order/transaction-level data (order ID, revenue, product) | ≥14 days |
| F — SaaS / Subscription | subscription/billing data (MRR/ARR, plan, cancel date) | ≥14 days |
| G — Mobile App & Store | a store-console export (installs, ratings, uninstalls) — distinct from an MMP export | ≥14 days |
| H — Web Analytics | on-site behavioral data (GA4/web analytics) with no ad-spend file supplied | ≥14 days |
| I — Single-Channel Deep Dive | exactly one ad platform's export, no second channel to compare against | ≥14 days |
| J — Cross-Source Reconciliation | ≥2 sources reporting the same KPI with a material, unexplained gap | none — single-point reconciliation |
| K — SEO & Organic Search | a Search Console-style export (clicks, impressions, position, by query/page) — distinct from a GA4/web-analytics export, which has no query dimension | ≥14 days |

**Below the minimum, don't withhold the template outright or build it at full scope — offer it with the gap named explicitly:** "available, trend/cohort components limited by short history (N days, template calls for M)." A 2-day revenue file requesting the Executive Summary should get exactly this caveat, not a normal trend chart built from two points and not a bare refusal.

**The history column is a calendar gate, and calendar time alone is the weakest of three sufficiency tests — run all three.** 14 days carrying 10,000 transactions and 14 days carrying 40 are not the same dataset, and no day-count threshold can tell them apart:

1. **Calendar history** — the column above. Enough elapsed time for the template's trend and period-comparison components to have anything to plot.
2. **Sample size** — enough volume for the *rates* on the dashboard to be meaningful, per `analysis-playbook.md` §Statistical sufficiency. A CVR card built on 40 sessions is a number, not a measurement, regardless of how many days those sessions span.
3. **Metric-specific horizon** — the longest horizon any single component actually requires, which is frequently longer than the template's calendar gate. D30 retention needs 30 days *plus* cohort maturity, not 14. A seasonality claim needs at least a full cycle, and usually more than one. A SaaS MRR trend over 14 days is two data points on a monthly-grain metric. Search Console query data is volatile enough day to day that a short window mostly measures its own noise.

When a component fails test 2 or 3 but the template passes test 1, **drop or caveat that component specifically** — don't withhold the whole template, and don't build the component as if it were supported. Name which of the three gates failed, so the user knows whether waiting, collecting more volume, or picking a different metric is the fix.

**This detection step is deliberate, not decoration.** Most template/report systems in the wild solve "which template" by making the user declare a vertical up front (a `/plan ecommerce` style flag, a picker, a fixed one-size-template) rather than reading it off the data — that's a real, common shortcut, not a strawman. Detecting from the actual columns present is more work to build and more work to keep honest, which is exactly why it's worth doing: **a user who already knows they have SaaS data doesn't need this skill to ask them** — the value is in surfacing the right template when they *don't* know, or when the data only partially supports what they asked for.

**Only present a template whose "needs" row is actually satisfied by what step 1 found.** A template with an unmet requirement doesn't belong in the list — offering it anyway is the same mistake as building a dashboard for data you don't have, just moved one step earlier. When more than one template fits (common: a single ad-platform export satisfies both B, loosely, and I, exactly), prefer the one that uses more of what's actually there and say why in one line — don't silently pick. When the data exactly matches what the user asked for by name, skip straight to that template's blueprint per the "already named" rule above, whether it's a Tier 1 letter or a Tier 2 name.

**A template's component list is a floor, not a ceiling.** Once a template is selected, Output mode 1's diagnosis (step 6, the 5–10 prioritized observations) may surface a metric that genuinely drives the story but isn't in the selected template's default component list — e.g. Template E's list has no "Churn," but the diagnosis implicates repeat-purchase decay. Add it, as a KPI card or a deep-dive callout, rather than dropping it for not being on the list. The template defines what's expected to be there by default given that data shape, not a cap on what the analysis is allowed to show.

## Dashboard design specification

For every component in the selected blueprint, specify:

| Field | Requirement |
|---|---|
| Component | Name |
| Business Question | What decision does it support? |
| KPI | Primary metric |
| Supporting KPIs | Related metrics |
| Visualization | Chart/card/table |
| Dimension | Channel/cohort/campaign/etc. |
| Time Comparison | WoW/MoM/YoY |
| Interaction | Filter/drill-down |
| Insight Logic | What should be detected? |
| Priority | Critical/High/Medium/Low |

No chart exists because it looks attractive; every visualization answers a business question. The **Insight Logic** field is not internal planning notes — it is what gets rendered as that component's caption in the final artifact (see "Every chart carries a caption" below). If you can't state the insight logic in one plain sentence, the component isn't ready to ship.

## KPI card rules

Every card contains, **where applicable**: current value, previous-period comparison, absolute change, percentage change, direction indicator, business interpretation where meaningful. A previous-period comparison doesn't apply to every card — a first-ever cohort LTV figure, a one-off experiment lift result, or a benchmark-anchored metric with no prior-period equivalent in the data should state "no prior period to compare" rather than forcing a manufactured comparison or omitting the card.

Example:

> **CAC** — ₺245, ↓ 12.4% MoM. Interpretation: acquisition efficiency improved.

No KPI card without contextual comparison — but "comparison" isn't only prior-period. Prior-period, a benchmark, a stated target, a cohort comparison, or a confidence interval all count; "no prior period to compare" is itself valid context as long as one of the others is present or the absence is stated explicitly, per the previous paragraph.

**Redundancy check — two cards telling one story is one card and one distraction.** Before finalizing the strip, check whether any card adds decision value the cards beside it don't already carry. Sessions and Users on the same GA4 strip usually move together and answer the same question; Revenue and Orders next to each other with no AOV is the same story told twice without the piece that would distinguish them. Where two cards are near-duplicates, **keep the one closer to a decision and drop the other** — or replace the pair with the ratio that actually separates them (Sessions + Users → Sessions per User, if that's the live question). The 8-card ceiling is a limit on space; redundancy is a limit on attention, and it binds sooner.

**Status color.** Reuse the skill's 🔴/🟠/🟡/🟢 priority scale as the KPI-vs-target status on every card, not only on the strategic-insights list — one vocabulary end to end, not a second color system invented for cards.

**No sparklines, no icons, no gradients inside a KPI card — a deliberate restriction, not an oversight.** The big number plus a colored delta pill already carries the signal a card needs; a sparkline competes with that restraint rather than adding to it. If trend context matters, it belongs in a real chart (per the chart-form table below), not compressed into a card decoration. This was previously stated as "add a sparkline where the data supports one" — reversed on review: the card's job is a single clean readout, not a second, smaller chart.

## Visual conventions

**Layout, top to bottom, one column:**

1. **Executive KPI strip** — up to 8 cards, hard cap, **no floor.** Ship exactly as many cards as the selected template's genuinely meaningful components support — 3 or 4 is correct for a sparse template (e.g. K with only Clicks/Impressions/CTR/Average Position at the core), not a defect to pad around. Needing more than 8 means step 6's diagnosis wasn't distilled enough; move the rest into a deep-dive. Padding to reach a perceived minimum is the same defect as inventing data, just wearing real numbers.
2. **2–3 mid-size charts** — trend, funnel, or channel comparison, whichever the selected archetype's visuals call for. Never more than 3 at this tier.
3. **One detail table** — pre-sorted by the metric that matters, not a dump of every available column.
4. **Deep-dive section(s)** — cohort/retention, CRM, or channel-mix detail. Keep these visually secondary to the top strip — cohort data especially supports one specific insight, it is not a standalone panel with equal billing to the headline KPIs.
5. **Alerts → strategic insights → recommended actions** — as specified in Output mode 2 below.

**Chart form follows the question — never pick a chart because it looks better:**

| Component | Chart form | Why this form |
|---|---|---|
| KPI / stat card | Big number + delta pill, no sparkline | Single value with direction context; a sparkline is a second, smaller chart competing with the card's own restraint — trend belongs in a real chart, not a card decoration |
| A single ratio against a fixed limit (spend pacing vs. budget, a rate against a compliance threshold) | Meter / progress track | It's one number relative to one ceiling — a full trend chart or a two-slice pie both overstate what there is to read. **If the ceiling is an industry benchmark rather than a limit the user actually set (a budget, a compliance threshold), caption it as "vs. benchmark" explicitly** — a Meter reads as progress-toward-a-target by shape alone, and an unlabeled external benchmark in that shape implies a goal the user never stated |
| A metric that factors into named sub-drivers (Revenue = Traffic × CVR × AOV; MRR = Customers × ARPA) | KPI decomposition tree: the top metric as the root, each factor as a child node, each node carrying its own value + delta + status pill (reuse the KPI card convention, not a new indicator) | A flat KPI strip can tell you Revenue moved; it can't tell you *which factor* moved it. The tree answers "where did this come from" in one glance instead of forcing the reader to hold three separate stat tiles in their head and do the arithmetic themselves. Use it only where the factors are a genuine identity (Revenue really does equal Traffic × CVR × AOV) — not for a vague "contributing factors" list, which is just alerts dressed up as a diagram |
| Distribution of individual values (order value, session length) | Bucketed bar (histogram) — count or share per value-range bucket | Same "magnitude, low→high" job as any bar chart, just applied to bucketed continuous data. A mean/mode pair as two stat tiles states *that* they differ; a histogram shows *why* |
| Part-to-whole snapshot (revenue by category, new-vs-returning split) | Stacked bar, horizontal for many or long-named categories | Never a pie/donut for comparing close values — a bar keeps the comparison precise. A pie is defensible only for a single ≤4-category share-at-a-glance case, and even there a sorted bar is the safer default |
| A score across several named dimensions at once (e.g. an audit health score broken into spend-waste / reach / efficiency / compliance) | A sorted bar, one bar per dimension — never a radar/spider chart | Same failure as the donut, one level up: a radar's area and axis-order are both arbitrary, so two genuinely different shapes can *look* similarly "balanced," and a shape that reads as bigger isn't necessarily better on the metric that matters most. A bar keeps every dimension independently and precisely readable, which is the entire job here |
| Signed period-over-period composition (MRR movement: new/expansion/contraction/churn → net) | Floating "waterfall" bars anchored to the running total, diverging color (growth components one hue, shrink components the opposite) | A bar-chart variant, not a line — the story is the *composition* of a change, not a level over time |
| Acquisition funnel | Vertical stage bars sized to volume by default (horizontal only if labels force wrapping — see "Component anatomy" below), drop-off % labeled between stages | The shape every real implementation converges on; a Sankey or sunburst reads as decoration here, not signal |
| Channel comparison / ranking | A bar **sorted by the ranked metric, never alphabetically** — drawn inside a table's value cell when the rows already carry a label column (see "Component anatomy" below), or a standalone bar chart otherwise. **If a volume metric (sessions, spend, installs) is being ranked and a quality metric exists at the same dimension (engagement rate, CVR, retention, LTV) — pair them, don't ship volume alone.** A second sorted bar, a two-column table, or a quadrant (per the relationship-chart rows above) all satisfy this; the form matters less than not leaving a quality signal unused when it was already sitting in the data | The sort order *is* the finding — an unsorted bar chart hides the answer the reader came for. **A volume-only channel ranking risks the exact mistake `analysis-playbook.md`'s Channel analysis section already bans in prose** ("never declare a channel best on one metric") — the visual layer has to carry that discipline too, or the rule is true in the text and false in what actually gets shown |
| Cohort metric over elapsed time (retention, cohort NRR, cohort LTV) | Triangular heatmap: rows = cohort, columns = elapsed period, cell color = the metric (one sequential hue, light→dark) | The de facto standard shape for this data everywhere it's analyzed — and the only form that keeps cohort maturity visible instead of blending cohorts into one misleadingly smooth curve, per `comparability-rules.md` §2.5 |
| Relationship between two continuous metrics, a small number of entities (≤7: channels, campaigns) where quadrant framing aids a decision | Two-axis scatter with quadrant guide lines, each point labeled | This is the one place two differently-scaled metrics legitimately share a chart — as the two axes of a single scatter, not as a dual-axis line/bar overlay |
| Relationship between two continuous metrics, many entities (8+ campaigns/ad-sets/creatives) | Plain scatter, no quadrant guide lines | Past 7 points, quadrant lines and full labeling clutter faster than they clarify — emphasize the outliers (per the dataviz emphasis principle) instead of labeling everyone |
| A channel/spend-vs-outcome correlation (e.g. "does this channel's spend track with sales") | Sorted bar of the correlation coefficient per channel, or the underlying scatter if there's only one channel — but **the caption is not optional here**: state the Evidence Ladder tier (`comparability-rules.md` §2.6) explicitly — a computed R is E2 (correlation, no control group) by construction, never E4/E5 | This is the exact failure mode this skill exists to prevent: a correlation coefficient printed next to a chart reads as authoritative precisely because it's a number, and a reader who isn't told "correlation, not causation, here" will take "R = 0.78" as proof the spend caused the sales. Printing the number without the caption is worse than not computing it |
| Spend / revenue / CAC / LTV over time | Single-axis time series; index differently-scaled series to a common base, or use small multiples, instead of overlaying | **Never a dual-axis chart with two y-scales.** Two scales sharing one set of gridlines invites a false visual correlation — this is the single most common chart-reading mistake, and the fact that it's a common shortcut elsewhere doesn't make it a safe one here. **Same unit isn't automatically the same chart, either** — MRR (a total) and ARPA (a per-customer average) are both currency, but if they differ by an order of magnitude, plotting them on one axis flattens the smaller one to near-zero; index or separate exactly as if the units differed |

**Component anatomy — the details that separate a polished artifact from a rough one:**

- **KPI card:** the big bold number is what the eye lands on first — put it above a small muted-gray label naming the metric, not the other way round. The delta is a small rounded pill badge with a status-colored background, never bare text next to the number — a pill reads as a signal, plain text reads as an afterthought.
- **Chart card:** bold dark title, a smaller muted-gray subtitle line beneath it (the scope/comparison window), then the legend as small colored squares + labels in their own row above the plot area — never crammed into a corner or left implicit. Gridlines are horizontal-only and light gray; a vertical grid adds clutter with no reading benefit. Give the plot generous internal padding (16–24px) — a chart pushed flush to its card edges reads as unfinished regardless of what data it holds.
- **Funnel:** default to vertical bars, not horizontal — they read top-to-bottom like the journey they represent and sit naturally in a one-column layout; fall back to horizontal only when stage labels are long enough to force awkward wrapping. Pin the value/% as a small callout box above each bar rather than only printing it inside, and fade the undelivered portion of each bar toward the card background instead of leaving it a flat block — a gradient reads as "the gap," a flat fill reads as "dead space."
- **Channel/category comparison:** prefer a table with the colored bar drawn *inside* the value cell over a separate freestanding bar chart whenever the rows already need a label column — it's more information-dense per pixel and, per the heatmap rule above, the table already doubles as its own accessibility fallback. Reserve a standalone bar chart for when the comparison needs to sit beside other charts at equal visual weight in a multi-chart row.

**Every chart carries a one-line caption — not optional polish.** A plain-language sentence above or beside the chart, taken directly from that component's Insight Logic field. This is the single convention that separates an artifact a reader acts on from a data dump a reader scrolls past. A chart shipped without its caption is as incomplete as a KPI card with no comparison context.

**But the caption states what the chart honestly supports — not every chart owes the reader an action.** Forcing an action line onto a component that only shows a level is how a dashboard starts inventing urgency, which is the same failure as inventing data with the recommendation step doing the inventing. Pick the strongest type the evidence actually reaches, and no higher:

| Caption type | When | Example |
|---|---|---|
| **OBSERVATION** | The chart shows a level or a movement, nothing further is established | "Revenue rose 12% over the period." |
| **INTERPRETATION** | The movement's composition or driver is visible *in this chart* | "Revenue rose 12%, driven almost entirely by AOV — order count was flat." |
| **INSIGHT** | The pattern implies something about the business that isn't visible from the numbers alone | "Order count has been flat for six months while AOV carries all growth — acquisition has stalled and is being masked at the revenue line." |
| **ALERT** | A threshold, guardrail, or expected range was crossed | "Refund rate crossed 4% in March, above its trailing 12-month band." |
| **ACTION** | An insight or alert with a decision genuinely attached, and the evidence to support taking it | "Order count flat for six months — investigate top-of-funnel before scaling spend further." |

Most charts on a well-built dashboard are OBSERVATION or INTERPRETATION, and that is correct, not lazy. ACTION belongs to the small number of components that genuinely earned it, and to the Recommended Actions section (Output mode 2 step 8) — an every-chart-has-an-action dashboard reads as urgent about everything, which is indistinguishable from urgent about nothing.

**Accessibility, non-negotiable:** a legend whenever a chart has ≥2 series (none needed for a single series — the caption already names it); status or series identity is never color-alone, pair it with a label or icon; a plain data table exists somewhere in the artifact for every chart, as a screen-reader and copy-paste fallback; the artifact must still be legible with the color signal stripped out entirely. The cohort heatmap is the one component where the fallback is free: build it as an actual `<table>` with cell background-color for the heat, not a `<div>` grid — it renders identically and the accessibility fallback is the same element, not a second one to maintain.

## Visual system: Lab UI

Every dashboard this skill renders uses **Lab UI**, the visual language shared by all the Lab tools and their home, alidemirbas.com.tr/lab: stone ink on white paper, one brand blue for what is chosen or actionable, one sans family, plain-case labels, rounded tiles and pill controls. The spec above says what each component contains; this section fixes what it looks like, so two runs of this skill (and this skill next to any other Lab tool) read as the same product instead of each run inventing a palette.

**Inline the kit, don't restyle it.** Copy `references/lab-ui.css` verbatim into the artifact's `<style>`, between a `/* lab-ui:begin */` and a `/* lab-ui:end */` line, then add only this dashboard's own layout rules after it. Never link it (the artifact renders offline and loads nothing third-party), never edit its tokens, never add a second palette. Put `class="lab"` on `<body>` and the content in a `.lab-page` wrapper.

| Dashboard part | Lab UI |
|---|---|
| Page head | `.lab-eyebrow` (source and period, plain case) above `.lab-title`, then a `.lab-lede` sentence |
| Section heading | `.lab-h2`, plain case: no uppercase tracked labels, no trailing rules |
| KPI card | `.lab-tile .lab-kpi`: `.lab-kpi-value` above `.lab-kpi-label`, the delta as `.lab-delta` with a status tint |
| Status (🔴 🟠 🟡 🟢) | `lab-t-bad`, `lab-t-warn`, `lab-t-watch`, `lab-t-good`: the same four everywhere the scale appears (cards, alerts, insights, tables) |
| Chart card | `.lab-tile` with a `.lab-h3` title, a `.lab-small .lab-subtle` scope line, the caption as `.lab-muted`, legend as chips above the plot |
| Chart colours | series in order `var(--lab-series-1)` … `var(--lab-series-6)`; a single series in `--lab-series-1`; a sequential heatmap on the brand ramp (`--lab-primary-50` light to `--lab-primary-700` dark); gridlines `var(--lab-line)`, axis text `var(--lab-text-subtle)` at 12px |
| Table | `.lab-table-wrap` + `.lab-table`; an in-cell bar is a `.lab-meter` |
| Alert, insight, action | `.lab-note` with a small status icon tile |
| Filters | `.lab-select`, `.lab-input`; a period switch is a `.lab-seg` |
| Badge | `.lab-badge` + a tint class |

SVG charts take their colours through the CSS variables (`style="fill:var(--lab-series-1)"`, `stroke="var(--lab-line)"`) and their text through `font-family: var(--lab-font)`, so the dark theme the kit ships works without a second drawing. The kit already sets tabular figures for tables and `.num`; KPI values and axis labels should use them too.

## Filter system

Where data supports it: Date, Channel, Campaign, Platform, OS, Country, Product, Customer segment, Acquisition source, Cohort. Filters affect all relevant components consistently — but in the rendered artifact (see "Rendering mechanism" below), a filter is a **stated context line** ("Showing: Jan–Jun 2026, all channels, TR market"), not a live control. Never ship a filter widget that doesn't actually filter anything.

## Rendering mechanism

The final blueprint (Output mode 2) is a visual artifact, not a wall of markdown tables.

**Default: one self-contained HTML file, charts built as hand-drawn inline SVG** — not an imported charting library. Two reasons hold regardless of environment: no build step, no server, and no dependency on a third-party asset loading at render time; and the two hardest chart forms this skill needs — the cohort heatmap and the channel-efficiency quadrant — have no reliable off-the-shelf component in any charting toolkit anyway, so hand-built SVG isn't a compromise, it's what gets built by hand everywhere this kind of chart appears. A lightweight loaded-at-runtime chart library is an acceptable substitute only for a plain single-axis time-series line, and only when the environment reliably has that access — never for the harder chart forms above.

If the environment offers a rendered-artifact surface, use it. Otherwise, write a standalone `.html` file with all data and SVG inlined. Never substitute a screenshot, an ASCII chart, or a markdown table dressed up as "the dashboard" — those are Output mode 1's job, not the final blueprint's.

**Responsive layout, not just correct at one width.** The artifact is a single HTML file, but it doesn't only ever get opened on a wide desktop browser — sent as a file or embedded, it will sometimes render on a laptop split-screen or a phone. Two concrete requirements: (1) every SVG chart carries a `viewBox` and scales to its container (`width="100%"`, no fixed pixel width) instead of a fixed-size drawing that overflows or clips on a narrower screen; (2) the layout reflows at a stated breakpoint — below ~768px, the KPI strip collapses to 2 columns, the 2–3 mid-size chart row stacks to a single column, and the detail table becomes horizontally scrollable within its own container rather than forcing the whole page to scroll sideways. If a component (the cohort heatmap, a wide detail table) is genuinely desktop-only and degrades to a scroll-container rather than reflowing cleanly, that's an honest, stated limitation — not a silent failure to leave undocumented.

**Verify the file actually renders before calling it done — computing the numbers correctly is not the same as the chart showing up.** A real, observed failure mode: a dashboard export where every KPI number and even a stated correlation coefficient (`R = 0.782`) were computed correctly, but every chart panel rendered as an empty box — the chart-building code referenced a library that was never actually loaded into the file, so each chart function hit an early guard clause and silently returned, no console error, no visible failure. The bug was invisible from the KPI strip alone; only opening the file and looking at the chart panels caught it. Hand-drawn inline SVG (the default above) mostly avoids this specific failure — there's no external library reference that can go missing — but the general discipline still applies: open the artifact and confirm every chart panel actually shows marks, not just a title, before presenting it as finished.

## Dashboard QA gate — run before delivering, not after being corrected

Confirming the charts render (above) proves the artifact isn't broken. It does not prove it's *right*. A dashboard can render perfectly and still contradict itself, because its numbers were assembled component by component and nothing checked them against each other. Run all seven before presenting:

| Check | What passes | The failure it catches |
|---|---|---|
| **Numerical integrity** | The KPI card's Revenue equals the revenue chart's total for the same period | A card computed from one file, a chart from another, or one of them scoped to a different date range — the two numbers sit inches apart and disagree |
| **Aggregation integrity** | Per-channel (or per-category) figures sum to the stated overall total, or the gap is explained | A missing channel, a dropped `(other)` bucket, or a filtered subset presented as the whole |
| **Filter integrity** | The stated context line ("Showing: Jan–Jun 2026, TR market") matches what the numbers actually cover | A header claiming a period the data doesn't span — trivially easy to get wrong when one supplied file is shorter than the others |
| **Ranking integrity** | Sorted tables/bars are sorted by the metric named in the header, descending unless stated | An alphabetical or source-order table presented as a ranking — the sort order *is* the finding (see the chart-form table) |
| **Direction integrity** | A ↓ on CAC, CPA, CPI, churn, or Average Position reads as **good**; a ↓ on revenue, retention, or ROAS reads as bad | A blanket "down = red" status color that marks a genuine CAC improvement as a problem — the single most common polish-level dashboard error |
| **Unit integrity** | Every figure carries its unit; currency figures use one currency; % and absolute values are never mixed in one axis or column | A % delta rendered in the same column as a ₺ value, or two currencies in one total |
| **Semantic integrity** | The Revenue KPI card and the Revenue chart resolve to the **same registry entry** (`kpi-framework.md` §1) — same definition, same source, same variant | The drift this skill's whole registry exists to prevent: a card showing one source's revenue and a chart showing another's, both labeled "Revenue" |
| **Coverage integrity** | Every file and every distinct sub-table within a file (per `analysis-playbook.md`'s multi-table-export check) appears in the artifact **either as a used component or as a stated exclusion with a reason** — nothing supplied silently disappears | A file (or a table inside a multi-table export, e.g. a GA4 Explore CSV with several stacked breakdowns) that was read during ingestion but never referenced anywhere in the output, with no note saying so — this reads as thoroughness to a user who can't tell the difference between "checked and set aside" and "never looked at" |

**Coverage integrity is a listing discipline, not a mandate to use everything.** Most supplied data legitimately doesn't make the final 5–8 KPI cards or 2–3 charts — that's the Insight Candidate Engine and the "5–8 cards, no floor" rule working correctly, not a defect. The requirement is narrower: **state what was set aside, don't just quietly not mention it.** A one-line coverage note is enough — "Used: traffic/user acquisition, landing pages, weekly cohort series. Not surfaced: [table], because [reason — redundant with X / below the candidate-engine bar / no linking dimension to build on]." This is the same "Not available in supplied data" discipline already required for missing metrics, applied to the inverse case: data that *was* available and got left out.

A failed check is fixed before delivery, not footnoted. If it genuinely can't be fixed (two sources legitimately disagree and both belong on the page), the disagreement is stated on the artifact itself — that's Template J's job, not a silent inconsistency.

**One static snapshot, not a live BI tool.** No functioning date picker, no working client-side filter, no auto-refresh claim. Every real dashboard tool draws the same line between its live/interactive view and its exported/shared view: the exported one is frozen at whatever state was selected when it was produced. This skill only ever produces the frozen version. If genuine interactive drill-down matters for the request, say so explicitly as a limitation of the current output — don't fake a control that does nothing when clicked.

## Output mode 2 — final dashboard blueprint (after selection)

Render per "Rendering mechanism" and "Visual conventions" above. Structure:

1. **Dashboard objective** — one concise statement.
2. **Executive KPI layer** — the KPI strip (5–8 cards, per "Visual conventions").
3. **Main visualizations** — 2–3 mid-size charts, each with chart type, KPI, dimension, comparison, business question, and its rendered caption.
4. **Detail table** — pre-sorted, not a full column dump.
5. **Deep-dive sections** — Acquisition / Product / Lifecycle / Monetization / Profitability, as applicable, visually secondary to the top strip.
6. **Alerts** — automatically detected critical risks, efficiency deterioration, growth opportunities, anomalies.
7. **Strategic insights** — ranked by priority (🔴/🟠/🟡/🟢).
8. **Recommended actions** — each with: action, expected business impact, supporting evidence, metric to monitor, validation method.
9. **Data coverage note** — one to three lines, per the Coverage integrity check above: what was used where, and what was set aside and why. Not a full audit trail, just enough that "why isn't X in here" has a stated answer instead of an implied "it wasn't looked at."

**Every item in steps 6-8 names the specific component it came from.** Once a dashboard has several charts, a bare narrative claim in Alerts/Strategic Insights/Recommended Actions is no longer traceable to which one produced it. Name the source component in parentheses or as a trailing reference — e.g. "🔴 CAC rose 22% MoM (see: CAC trend, §3)" — so a reader can trace any claim back to its chart without re-deriving it themselves.
