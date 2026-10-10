# KPI Framework — formulas, variants, action triggers

Every formula below is traceable to a vendor doc or paper (see `research/raw/`). Where sources genuinely disagree, **both variants are listed** — pick one, state which, and never mix them in a single table.

## How to read a row

`Metric | Formula | Definitional variance (which one am I looking at?) | Action trigger (what does a bad reading tell me to check?)`

**A trigger is a check to run, not a diagnosis.** "CTR falling with stable CPM" does not establish creative fatigue; it makes creative fatigue the first explanation worth testing. Every trigger below is written as *pattern → leading explanation to check → the data that would confirm or rule it out*, and whatever it leads to is still a hypothesis until the evidence standard in `comparability-rules.md` §2.6 is met. Never copy a trigger's explanation into an output as the cause.

**For this skill's purposes**, a dashboard-worthy KPI has a defined decision use — an action trigger. This is this skill's own operating discipline, not a universal definition of what counts as a KPI in general. If you cannot state what a bad reading would change, do not put it on a dashboard produced by this skill.

**Applied bluntly, though, that rule strips out metrics a good dashboard needs.** A North Star, a guardrail, and a diagnostic metric all legitimately lack their own action trigger and still belong on the page. The fix isn't to relax the rule — it's to say which job each component is doing, so "no action trigger" is only disqualifying for the type that requires one:

| Component type | What it's for | Action trigger required? |
|---|---|---|
| **DECISION KPI** | Directly drives a call — scale, cut, fix, investigate | **Yes.** No trigger, no place on the dashboard |
| **GUARDRAIL** | Bounds a decision made elsewhere — refund rate next to a conversion push, unsubscribe rate next to a send-volume increase | No trigger of its own; its job is to catch a win that came at a cost. Must be paired with the DECISION KPI it guards |
| **DIAGNOSTIC** | Explains *why* a decision KPI moved — the drivers under a top-line number | No. It earns its place by decomposing something else |
| **CONTEXT** | Establishes scale or baseline so the rest is readable | No. Keep these few — context is where dashboard bloat starts |

Tag every component with one of the four when specifying the blueprint. A dashboard that is all DECISION KPIs is unreadable; one with no DECISION KPI is a report, not a decision system.

**What this file is, in the vocabulary of that space:** this is a lightweight, prose-based **metrics layer** — a shared definition per metric (formula, grain, known variance) that every part of this skill reads from, so "CAC" means the same thing in the KPI card as it does in the funnel analysis. It is deliberately **not** a full semantic layer (no join graph, no dimensional model, no access control) and **not** a metrics store (nothing here is precomputed or cached — every number is recalculated from whatever file was supplied in this session). That's a scope match, not a shortcut: this skill works from whatever files a user hands it in one sitting, not a warehouse serving many consumers, so the parts of that space built for query performance and cross-consumer consistency at scale don't apply. What does transfer directly: define the metric once, state its variant explicitly, never let two parts of one output silently disagree about what a metric means.

---

## 1. Column → KPI standardization

Map raw column names to the taxonomy before analysis. Common aliases:

| Raw variants | Standard KPI |
|---|---|
| `install_count`, `installs`, `new_users`, `first_open` | Installs — **but check: download, first-open, or account-level acquisition?** |
| `media_cost`, `spend`, `ad_spend`, `cost`, `amount_spent` | Marketing Spend |
| `purchase_rev`, `sales`, `revenue`, `conv_value`, `complete_payment` | Revenue — **check: gross, net, tax/shipping included?** GA4 specifically: `purchaseRevenue` (net of refunds) vs `grossPurchaseRevenue` (NOT net of refunds) vs `totalRevenue` (purchase+subscription+ad revenue, net of refunds) — a column headed "Purchase revenue" can trace to either the net or gross API metric; the label alone doesn't say which (`comparability-rules.md` §2.2) |
| `conversions`, `results`, `key_events`, `goal_completions` | Conversions — **check: which platform's counting rule?** |

**Before mapping, record for each source:** counting unit · denominator · attribution window · attribution model · date basis · timezone · currency · observed-vs-modeled status. Without these eight, the column name is not enough to know what the number is. (Cohort maturity is deliberately not on this list: it is a property of a *comparison*, not of a source, so it is checked per comparison — `comparability-rules.md` §1, check 7. That checklist in turn leaves currency, timezone and grain to `data-quality-gate.md`. The two lists are complementary, not two versions of one list.)

### The session metric registry — build it once, read from it everywhere

The eight facts above are recorded **per source**. That isn't enough on its own: two metrics inside the same file can have different scopes (a GA4 export's `Revenue` and `Users` are not the same population), and the same canonical KPI can arrive from two sources with two different definitions. Without one place holding that state, a metric can silently drift across the workflow — step 1 maps "Revenue" to a purchase-revenue column, step 5 reasons about a total-revenue figure, and the dashboard KPI card renders a third source's number. Each step looks defensible alone; the output is incoherent.

**So: as ingestion completes, build an internal registry with one entry per (source × metric) actually in play.** Hold it for the whole session and read every later figure from it rather than re-deriving what a column meant:

```
canonical_name      the KPI taxonomy name (Revenue, CAC, Retention…)
source              which file/platform
raw_column          the exact column header it came from
definition          the specific variant, not the family — "purchase revenue,
                    net of refunds", not "revenue"
numerator/denominator  for any ratio, both sides named explicitly
grain               what one row represents
entity              what is being counted (device / user / account / session / message)
time_basis          dated to the click, the conversion, the order, the payment?
attribution         window + model, or "n/a" for non-attributed metrics
currency            code, or "unstated in source"
provenance          Measured / User-provided / Derived / Estimated-Modeled
mapping_confidence  EXACT / INFERRED / AMBIGUOUS (see below)
comparability       which other registry entries this one can and cannot be
                    compared to, and under which of the four states
decomposes_into     if this metric is one side of a known identity (§8),
                    name it — e.g. Revenue → "Orders × AOV". Leave blank for
                    a metric with no identity, don't force one
```

**This is deliberately not a formal metric-contract file, and must not become one.** No YAML to author, no schema to validate, nothing written to disk, nothing carried between sessions — a real metric-contract system needs validators, ownership, and approval enforcement, which is infrastructure this skill correctly doesn't have (see the metrics-layer scoping note in this file's intro). What it *is*: internal working state, held for one session, so that "Revenue" means exactly one thing from ingestion through to the rendered KPI card.

**Surface only the parts that carry a finding.** The whole registry does not belong in the output — an unstated fact, an AMBIGUOUS mapping, or a NOT_COMPARABLE pair does (per `SKILL.md` step 2). Silence in the registry is itself reportable; a full dump of it is noise.

### Mapping confidence — EXACT / INFERRED / AMBIGUOUS

An alias table match is not proof of meaning. Tag every column → KPI mapping:

| Level | When | What to do |
|---|---|---|
| **EXACT** | The column is a known, named field of an identified platform whose definition is documented — `purchaseRevenue` from a confirmed GA4 export, `amount_spent` from a confirmed Meta export | Map it, record the documented definition in the registry, proceed |
| **INFERRED** | The mapping is very likely but rests on an assumption — a column called `media_cost` in an unidentified file is almost certainly Marketing Spend, but which cost scope (media only vs. media+fees) is not established | Map it, **state the assumption inline the first time the metric appears**, record the assumption in the registry |
| **AMBIGUOUS** | Multiple genuinely different definitions fit the column name and nothing in the data settles it — a bare `revenue` column could be gross, net, purchase-only, attributed conversion value, or GMV | **Do not silently pick one.** Either ask, or name the interpretation you're using and list the alternatives you ruled out. An AMBIGUOUS metric may not anchor a headline KPI card or a comparison without that disclosure |

The bar for EXACT is the platform being *identified* (`analysis-playbook.md` §Source identification), not the column name looking familiar. A `purchase_revenue` header in a file whose source is unidentified is INFERRED at best — the name matches GA4's field, but nothing confirms GA4 produced it.

---

## 2. Acquisition

| Metric | Formula | Variance | Action trigger |
|---|---|---|---|
| CTR | Clicks ÷ Impressions | **Meta:** link vs all (all includes reactions, comments, shares, profile taps). **TikTok:** destination vs all. **LinkedIn:** chargeable clicks only, and the video-views objective has **zero** chargeable clicks | CTR falling with stable CPM → check creative fatigue first: is frequency rising on the same creatives, and does CTR recover on fresh ones? Rule out a placement or audience mix shift before touching targeting |
| CPC | Spend ÷ Clicks | Google Avg. CPC is actual charges, not bid. Meta CPC is cost per **link** click | Rising CPC with stable CTR → auction pressure is the leading explanation (creative isn't indicated while CTR holds). Confirm with impression share / auction insights or a seasonal comparison; rule out a bid-strategy or budget change |
| CPM | Spend ÷ Impressions × 1,000 | Denominator is served impressions, **not viewable** | Rising CPM + flat conversion → check audience saturation (reach flattening, frequency rising) against seasonal auction pressure (same period last year); the two call for different responses |
| CVR | Conversions ÷ Clicks (ad platforms); on-site CVR divides by sessions or users — state which denominator | **TikTok's UI CVR uses impressions**; its API `conversion_rate` uses clicks. Google's denominator is *interactions*, and the rate can legitimately exceed 100% | CVR drop with stable CTR → the post-click experience is where to look first: landing-page changes, load time, offer or price changes, a broken step. Also rule out a tracking change and a shift in traffic mix before concluding the page is the cause |
| CPI | Spend ÷ Installs | **Adjust:** ÷ installs. **AppsFlyer eCPI:** ÷ **attributions** (installs + re-engagements + re-attributions) | **CPI falling while D7 retention falls → don't book it as a win.** Lower acquisition quality is the leading explanation; check retention by source at matched cohort maturity before scaling (a counter-case exists — §9) |
| CAC | Marketing Spend ÷ New Customers | **Blended vs Paid** (a16z). **Fully-loaded** adds salaries, overhead, tooling (Chen); SMSB adds hosting/infra for PLG. Expenses must **lag** new revenue by the sales-cycle length. **When computing CAC alongside CAC Payback** (§5 below), both must use the same customer definition, the same acquisition period, and the same blended-vs-paid scope — mixing a blended CAC here with a paid-only Payback calculation produces two numbers that look related but aren't | CAC rising while LTV flat → check channel mix before cutting budget |
| Activation Rate | Activated users ÷ New users | "Activated" is your definition — state it | Installs ↑ + activation ↓ → check whether the added traffic is lower-intent (activation by source) or whether onboarding changed in the same window; either produces this pattern |

**Denominator trap (Chen):** the most common CAC error is putting new-customer spend in the numerator and **all** customers in the denominator. Fix both sides or neither.

---

## 3. Engagement and retention

| Metric | Formula | Variance | Action trigger |
|---|---|---|---|
| DAU / MAU / stickiness | DAU ÷ MAU | **MAU window differs by platform: GA4/Firebase 30 days, Play Console 28 days, Braze rolling 30.** Braze counts API-only profile updates as activity | Stickiness falling with flat DAU → MAU is growing without matching daily use; check whether newly acquired users are the ones not returning (stickiness by cohort) |
| Day-N retention | Users returning N days after acquisition ÷ users acquired that day | **Classic/N-day** (returned exactly on day N) vs **rolling/unbounded** (returned on or after). Mixpanel's default is unbounded; Amplitude names them Return On vs Return On or After. **Rolling is always ≥ classic within one consistent measurement system** (same cohort, same event definition, same tool) — this is a mathematical guarantee, not an empirical tendency. It does **not** automatically hold across two different tools, since a switch in anchor mode is rarely the *only* thing that differs between them (event definition, dedup, and cohort-entry timing can differ too) — confirm anchor mode via `comparability-rules.md` §2.3 before assuming the inequality carries over to a cross-tool comparison | A retention curve still declining at month 6–12, with no plateau → a signal worth raising about fit for that cohort, not a verdict; check whether other cohorts or segments flatten, and whether the cohort is mature enough to show a plateau at all |
| Retention (Play Console) | — | Measures whether the app **stayed installed**, not whether it opened | Never read as engagement |
| Churn | Lost customers ÷ prior-period total | **Denominator problem:** start-of-period vs midpoint vs daily-average produce different rates from **identical behavior** during growth. Logo churn ≠ revenue churn (different denominators) | Churn rising while acquisition rises → check whether it's a denominator artifact first |
| GRR | Σ per customer min(MRR at beginning, MRR at end) ÷ Σ MRR at beginning — the min is taken **per customer**, never on the two aggregate totals | **Cohort method vs formula method give different numbers.** Cohort is all customers active at period start, **regardless of renewal eligibility**. **Computed per customer, then summed** — for each customer active at period start, take min(their beginning MRR, their current MRR), sum those capped values, divide by the sum of beginning MRR. Do not take the min of the two *aggregate* totals — with a mix of expanding and contracting customers, that produces a different (and wrong) number | GRR below the §7 benchmark band (median 88–91%) in B2B SaaS → look at retention before growth; check which segment or plan the lost revenue concentrates in (the benchmark has its own sample caveats, §7) |
| NRR | MRR at end from the same customers ÷ MRR at beginning | Excludes customers acquired during the period. **Cohort method vs formula method give different numbers here too** — the same SMSB distinction as GRR, state which. **The "Rope-a-Dope":** expansion from <12-month-old customers in the numerator while they're absent from the denominator | NRR > 100% with GRR below the §7 benchmark band (median 88–91%) → expansion may be masking churn in the base; show the two side by side rather than NRR alone |

**Amplitude's two required inputs for any retention number:** the **critical event** and the **usage interval** (the time by which 80% of users repeat the critical action). Change either and the number changes substantially. State both.

---

## 4. Monetization

| Metric | Formula | Variance | Action trigger |
|---|---|---|---|
| ARPU | Revenue ÷ Users | Cohort-based (Amplitude) vs period-based (devtodev, a16z) | ARPU declining while user count grows → check conversion and paying share by cohort to tell weaker monetization from a benign mix shift toward newer users |
| ARPPU | Revenue ÷ Paying Users | **Amplitude's paying-user denominator includes anyone who *ever* paid, even after the data point.** Daily and monthly ARPPU are different quantities | **ARPPU ↑ with paying share ↓ can reduce total revenue** — `ARPU = ARPPU × Paying Share`. Never optimize ARPPU alone |
| ARPDAU | Revenue ÷ DAU | **Not cohorted**, while Amplitude-style cohort ARPU **is** (period ARPU, §8, is not) — mixing them in one deck produces numbers that never reconcile | ARPDAU rising while ARPU (cohorted) is flat → likely a mix-shift artifact (more of the recent-active base happens to be old, higher-spending users that day), not a genuine monetization improvement — check the cohort figure before reporting a win |
| AOV | Revenue ÷ Orders | — | **Check the mode, not just the mean.** Shopify's example: mean $24, mode $15 — a few high-value orders mask what most customers spend. AOV rising while order count falls → check whether it's a genuine basket-size win or just fewer, larger orders from the same or fewer customers |
| Purchase frequency | Orders ÷ Unique customers | — | Frequency falling while AOV rises and revenue is flat → check whether customers are consolidating orders (still healthy) or churning down to fewer, larger purchases before leaving (not healthy) — retention data resolves which |

---

## 5. Financial and unit economics

| Metric | Formula | Variance | Action trigger |
|---|---|---|---|
| ROAS | Revenue ÷ Marketing Spend | **Adjust: ratio, and its numerator is cohort revenue + the app's own ad revenue. AppsFlyer: percentage** (×100), purchase revenue only — so ×100 does not reconcile the two (`comparability-rules.md` §2.2). Google reports "Conv. value/cost" as a ratio while Target ROAS is a percentage. Meta's Purchase ROAS is **"approximate"** and can model the assigned *values*. **Before comparing two ROAS figures from the same source over time, confirm "Revenue" and "Spend" mean the same thing in both periods** — same currency, same gross-vs-net-of-tax/refund treatment, same cost scope (media only vs media+fees) — a change in any of these moves ROAS with no change in performance | Compare against **break-even ROAS**, never against a generic benchmark |
| Break-even ROAS | 1 ÷ Gross Margin, or AOV ÷ (AOV − product costs) | **RedTrack uses gross margin; Daymark uses contribution margin** (nets fees, shipping, refunds) — contribution margin gives a higher, safer floor. **Both omit G&A**, so hitting break-even exactly still loses money at company level | A 3:1 ROAS at 25% margin is **losing money** — you need 4:1 |
| MER | Revenue ÷ Total Marketing Spend | **Triple Whale inverts it** (spend ÷ revenue, lower is better). 41% and 2.44x are the same number | Preferred over channel ROAS when attribution is degraded — it "never asks a platform to claim anything." **But it moves with seasonality, retention and organic, and gives no channel-level action** |
| LTV | See variants below | **Three mutually inconsistent textbook formulas.** a16z *defines* it as net profit (while its own worked chain, below, multiplies contribution margin by lifespan); Skok says gross margin; Bessemer nets CAC **inside** CLTV | Never quote LTV without its horizon and cohort maturity |
| LTV:CAC | LTV ÷ CAC | LTV must be **gross-margin-based**, not revenue | **The ratio alone is insufficient** — pair it with payback |
| CAC Payback | Fully-loaded S&M ÷ (New CARR × Gross Margin %) × 12 | **The gross-margin adjustment is the fault line.** Unadjusted payback is shorter by a factor of 1/GM — an 80%-margin company's 10-month unadjusted payback is 12.5 months adjusted. **Unit contract:** S&M and New CARR must be measured over the **same acquisition period** (e.g. the S&M spent in a given month against the CARR of customers acquired that same month) — mixing a quarterly S&M figure against an annual New CARR figure produces a meaningless ratio, not a smaller error | Skok: "profitability is anemic if the time to recover CAC extends beyond 12 months" |
| Contribution margin | Net Sales Revenue − Variable Costs | Variable = materials, per-unit labor, commissions, freight, variable utilities. Fixed excluded | Contribution margin turning negative on any channel/product → stop scaling it regardless of what ROAS or MER say, since neither of those catches a negative-contribution unit economically |
| iROAS | Incremental conversion value ÷ ad spend | **Google contradicts itself:** the user-based page divides by **total** spend; the geo-based page by **incremental** cost | iROAS supports a causal claim **only when its "incremental" numerator was actually produced by a valid experimental design** — an E4-tier holdout or a **randomized** geo experiment, per the Evidence Ladder in `comparability-rules.md` §2.6. A column labeled "incremental" produced by a statistical model, or by a synthetic-control geo-lift tool (Meta GeoLift and similar are E3, not E4 — see the Evidence Ladder), does not earn the causal claim just because of its name. Check the method before trusting the label |

### LTV formula variants — pick one and say which

```
a16z / Skok (undiscounted approximation):
  Lifetime = 1 / churn ;  LTV = contribution margin × lifetime
  Skok:  LTV = (ARPA × Gross Margin %) / Churn Rate

Fader & Hardie Case 1 — as-yet-to-be-acquired customer (upper bound on acquisition spend):
  E(CLV) = m(1+d)/(1+d-r)
Case 2 — excludes the initial payment (this is also Shopify's second formula):
  E(CLV) = mr/(1+d-r)
Case 3:
  E(CLV) = m/(1+d-r)

Correct general form:
  E(CLV) = Σ_t  E[net cash flow in t | alive] × P(alive in t) × discount factor
```

**Five things that break the standard formula (Fader & Hardie):**
1. It is an **expectation** — write `E(CLV)`.
2. **Truncation** understates it. A finite horizon gives *truncated CLV over T+1 periods*, not lifetime value.
3. Starting at t=0 vs t=1 is the just-acquired vs as-yet-to-be-acquired distinction — "nearly all introductory discussions fail to make this clear."
4. **A constant retention rate is an artifact of cross-cohort aggregation.** Within a cohort, retention *increases* with tenure. Replace `rᵗ` with `∏rᵢ`.
5. **In noncontractual settings there is no retention rate at all** — the formulas "are of no use," and substituting a repeat rate is "completely wrong."

Their bottom line: **"there is no 'one formula' that can be used to compute customer lifetime value."**

**The average-lifetime trap, worked:** at r=0.8, d=0.1, average lifetime = 5 years. Summing 5 years gives **2.92m**; assuming everyone survives exactly 5 years gives **4.17m**; correct `E(CLV)` is **3.67m**.

**RFM, if you have transaction data:** CLV varies most on **recency**, then frequency, and **least on monetary value** — the inverse of how RFM scoring is usually weighted.

---

## 6. CRM / lifecycle

| Metric | Formula | Variance | Action trigger |
|---|---|---|---|
| Delivery rate | Deliveries ÷ Sends | Deliveries are usually **derived by subtraction** (Sends − Bounces), not independently observed | Delivery rate dropping → check sender reputation/deliverability (`comparability-rules.md` §2.2 on the Gmail/Yahoo spam-rate threshold, and the §3 soft flag on reading an open-rate drop as a deliverability signal) before assuming a list-quality problem |
| Open rate | Unique opens ÷ **Delivered** | **Klaviyo divides by Recipients.** MPP inflates all of them | **Do not read as a deliverability signal** — Google: "Low open rates aren't necessarily an accurate indicator of deliverability" |
| CTOR | Unique clicks ÷ Unique opens | **Braze includes machine opens in the denominator. Iterable's denominator is "opens *or* clicks." Insider uses unique clicks ÷ unique opens.** Three vendors, three quantities | Prefer Other Opens + Unique Clicks on Apple-heavy lists |
| Spam complaint rate | Complaints ÷ Sends (Braze) or ÷ Recipients (Klaviyo) | **Google/Yahoo's 0.3% threshold uses inbox-delivered mail only** — a sender in deep trouble can show a deceptively low ESP-reported rate | Google: stay **below 0.10%**, never reach **0.30%** — **measured on the Postmaster Tools spam rate, not the ESP-reported rate** (different denominator; comparing the ESP figure to this threshold is a hard block, `comparability-rules.md` §2.2); recovery requires 7 consecutive days below 0.3% |
| Unsubscribe rate | Unsubscribes ÷ Deliveries | Braze counts **Braze-handled paths only** | Send volume ↑ + unsubscribe ↑ → fatigue is the leading explanation; check conversion per user (not total conversions) and unsubscribes by send frequency band |
| Push open rate | Direct opens ÷ Deliveries | **Never sum Direct and Influenced opens** — influenced is correlational. Iterable's "delivered" includes devices with notifications disabled, understating the rate | Push open rate falling across the board (not one campaign) → check OS-level notification permission changes or an app update that reset permissions before treating it as a content/targeting problem |
| SMS delivery | Confirmed deliveries ÷ Sends | **Some carriers never return receipts.** D·engage splits this into five buckets and the rate changes depending on when you pull the report | Don't compare an SMS delivery rate pulled today against one pulled a week ago for the same send — re-pull both at the same elapsed time since send, or the "drop" may just be unresolved receipts still draining in |
| Incremental uplift | (Treatment CR − Control CR) ÷ Control CR | Braze publishes this; **Klaviyo and D·engage publish no lift formula.** Insider's incremental values **cannot go negative — they display as 0** | Without a holdout, state that **incremental causality cannot be established**. **Check sample size before trusting the number even with a holdout** — a control group of a few dozen users produces an uplift figure with a confidence interval wide enough to contain zero; Meta's own Conversion Lift minimum is ≥500 conversions per arm for a reason. If the user's control/treatment groups are small, say so and treat the point estimate as directional only |

---

## 7. Benchmarks — with the caveat each source attached

**Never quote a benchmark without its source, its sample, and its definition — and never quote one whose sample doesn't plausibly match the user's business.** A benchmark's stated population (business model, geography, category, company stage) is a fit-check, not decoration: the AOV table below is already segmented by category for this reason — use the matching row, not the global figure, whenever a category is stated and known. Benchmarks below are directional anchors for framing a question, not targets.

**Freshness note:** every benchmark below carries the year of its source report — that's deliberate, not an oversight, and it's the correct way to cite a point-in-time figure. But it also means every one of these numbers is a snapshot that WILL be superseded: SaaS/growth benchmarks (NRR, CAC payback, retention percentages) shift year to year, and a report from 2023 is already dated. Treat anything more than ~18–24 months old as directional only, and prefer the user's own live data or a fresher report over these figures when either is available.

**This benchmark table is not in tension with the non-negotiable rule against benchmarking plain ROAS.** That rule (never compare ROAS to a generic benchmark, compare to break-even ROAS) is specific to attributed ROAS, which is a unit-economics ratio with no universal healthy value — it depends entirely on the business's own margin. The metrics benchmarked below (LTV:CAC, CAC payback, NRR, retention, Rule of 40, etc.) are different: their benchmarks come from disclosed peer-company samples and are legitimate directional anchors precisely because they're sourced and captioned with their population, the same way this table requires. iROAS is the one benchmarked-ROAS-family exception, and even there the source's own caveat ("varies by business model, margin structure, and LTV") still applies.

| Metric | Value | Source and stated caveat |
|---|---|---|
| LTV:CAC | ~3x viable; public companies "more like 5x"; best "7 or 8" | Skok — an **observation, not a derivation**. Insufficient without payback |
| CAC payback | 5–7 months best-in-class; <12 months target | Skok. "Banks and wireless phone companies ignore this rule, but they have access to tons of capital" |
| CAC payback | Good 12–18 / Better 6–12 / **Best 0–6 months** | Bessemer State of the Cloud 2023 — Series B/C enterprise software only. **Bessemer's own 10 Laws says enterprise is 24–36 months — the publisher contradicts itself** |
| NRR | Good 100% / Better 110% / Best 120%+ | Bessemer, same sample caveat |
| NRR / GRR | NRR median 102%; GRR median 88–91% | SaaS Capital / Benchmarkit. **Benchmarkit's >$100M ARR cohort is six companies.** A circulating ChartMogul figure of 63% GRR is irreconcilable and unverified |
| 6-month retention | Consumer social 25/45% · Consumer transactional 30/50% · Consumer SaaS 40/70% · SMB SaaS 60/80% · Enterprise SaaS 70/90% (GOOD/GREAT) | Lenny's Newsletter — definition stated as "signed up and still active six months later." Lower is acceptable for early-stage, low-CAC, or non-venture-scale businesses |
| Annual churn | Logo <7%, CMRR <5% | Bessemer, "top performing cloud companies" |
| Net revenue churn | Above 2%/month indicates "something wrong" | Skok |
| Gross margin (software) | **a16z: 80–90% target. Bessemer portfolio actuals: 65–70%, middle 50% at 60–80%** | Aspiration vs observation. **Using 80–90% inside a margin-adjusted payback understates payback by ~20%** |
| Rule of 40 | Growth % + Profit % ≥ 40 | Feld — attributed to an unnamed "late stage investor," **scoped to companies at ≥$50M revenue**. Profit term is unstandardized (EBITDA vs FCF), which **enables metric shopping** |
| Magic Number | **0.7x** healthy baseline | Scale VP (originator). **The widely cited 0.75 does not appear in their pages** |
| SaaS Quick Ratio | 4+ desirable | Mamoon Hamid (originator), who warns it becomes **"quite deceiving" at scale** and can coexist with 5%+ monthly churn |
| MER | TW median 41% (spend÷revenue, ≈2.44x). The often-quoted "~5.0+" revenue÷spend figure has no traceable source — **directional folklore, not a benchmark** | **Direction differs by vendor.** Daymark refuses universal benchmarks: "A good MER is any MER above your break-even MER" |
| iROAS | >3.0 strong · 1.5–3.0 profitable · 1.0–1.5 marginal · <1.0 unprofitable | Measured — "these thresholds vary by business model, margin structure, and LTV" |
| AOV | Global ~$145; luxury >$300; apparel $40–170; beauty $15–90 | Shopify |
| Gmail spam rate | Below 0.10%; never reach 0.30% | Google — **denominator is inbox-delivered mail only** |

---

## 8. Metric identities — vs. the relationship clusters below

The clusters in the next table (Installs → Spend/CPI/retention, CAC → LTV/payback…) are **"read together"** relationships — co-movement patterns worth checking, not equations. A smaller, separate set of metrics are true **identities** — one is mathematically defined in terms of the others, with no approximation:

```
Revenue          = Orders × AOV
Orders            = Sessions × CVR         (or Users × CVR, state which population)
MRR               = Customer Count × ARPA
Net New MRR       = New MRR + Expansion MRR − Contraction MRR − Churned MRR
CAC               = Marketing Spend ÷ New Customers   (for whichever spend scope — paid /
                                                        blended / fully-loaded, §2 — the registry recorded)
ARPU              = Revenue ÷ Users
Stickiness        = DAU ÷ MAU
```

This is the reference other sections point to instead of re-deriving a decomposition ad hoc: the KPI decomposition tree chart form (`dashboard-blueprints.md`) renders these; the hypothesis-elimination pattern (`analysis-playbook.md`) checks these first when a top-line metric moves, since an identity is a free, non-speculative explanation ("Revenue fell because AOV fell, not because Orders fell" is arithmetic, not a hypothesis); the metric registry (§1) records which identity a component belongs to via its `decomposes_into` field, so a KPI card and a decomposition tree referencing the same metric read from one definition rather than two independently-derived ones.

**Only list a pair here if it's a true identity — a real equation, not a strong correlation.** CAC and LTV move together in practice but LTV is not *defined* in terms of CAC in the a16z/Skok/Fader-Hardie forms used here (Bessemer's variant, which nets CAC inside CLTV, is the exception — §5); that pair belongs in the relationship clusters below, not here. Confusing the two is worse than having neither: presenting a correlation as an identity implies a certainty about *why* a metric moved that the data doesn't support.

## 9. Metric-relationship clusters

Never analyze in isolation when a relationship exists:

| Primary | Must be read with |
|---|---|
| Installs | Spend, CPI, activation, retention |
| CPI | CAC, LTV, retention, **channel quality** |
| CAC | LTV, ARPU, gross profit, payback |
| LTV | CAC, retention, payback, **cohort maturity** |
| ROAS | Revenue, spend, **margin**, incrementality |
| Conversion rate | Traffic source, device, funnel stage |
| Open rate | CTR/CTOR, conversion, unsubscribe, **MPP share** |
| Retention | Acquisition source, activation, engagement |
| Churn | Engagement, CRM exposure, product behavior, **denominator method** |
| Revenue growth | User growth, ARPU, conversion, **gross profit** |
| Ad spend | Revenue, CAC, ROAS, **marginal/incremental return** |

### High-value co-movement patterns

| Pattern | Reading | Evidence needed to confirm | Outside evidence (Evidence Ladder tier, `comparability-rules.md` §2.6 — "Tier 1, strong" below = E4/E5 published experiments) |
|---|---|---|---|
| Spend ↑ + Revenue ↑ | Says nothing about efficiency | Marginal ROAS by spend level; saturation curve | **Tier 1, strong.** Shapiro/Hitsch/Tuchman (*Econometrica* 2021, N=288 brands): >80% of brands already show negative marginal ROI. Google Meridian models this with a Hill saturation curve — but Google itself warns extrapolation beyond observed spend is unreliable |
| CPI ↓ + Retention ↓ | Acquisition-quality problem | Cohort retention by source, matched maturity | **Weak — flag as HYPOTHESIS, not fact.** No Tier 1 study directly regresses CPI on retention across channels. The one real mechanism (incentivized/click-farm installs, ACM IMC 2020) is a fraud-specific effect, not general. Liftoff data shows a direct **counter-case**: Apple Search Ads has the *lowest* iOS CPI and *38% higher* D30 retention than the network average — cheap CPI and high retention can coexist when the channel is high-intent |
| Installs ↑ + Activation ↓ | Traffic isn't producing usable users | Funnel by source | No dedicated causal study found; reason from the funnel data itself |
| Open rate ↑ + Conversion ↓ | Engagement isn't commercial — often MPP | Non-MPP segment only | Mechanical (MPP inflates opens) — see `comparability-rules.md` §2.4 |
| Send volume ↑ + Unsubscribe ↑ | Fatigue | Conversion **per user**, not total | See next row — the CLV cost is better evidenced than the unsubscribe-rate framing alone |
| Frequency ↑ + Conversion/user ↓ | Diminishing, and for a real subset of users *negative*, returns | Frequency-capped holdout | **Tier 1, strong.** Baek/Chen/Ma/Mitrofanov field RCT (2025): full CLV-optimal frequency beats a daily baseline by 8.3% CLV despite a 5–8% short-term revenue cost; reducing frequency cuts unsubscribes 59%. Chae/Bruno/Feinberg (*JMR* 2019, N=12,000+): ~24% of users show a genuinely **negative** marginal effect from more sends, not just diminishing. Effect is segment-heterogeneous — reducing frequency helps new/low-engagement users most and costs high-volume users most |
| Revenue ↑ + Gross profit ↓ | Growth is margin-destructive | Margin by channel/product | Accounting identity, not a hypothesis — always computable if margin data exists |
| Revenue ↑ + Users flat | ARPU or pricing effect | Price/mix decomposition | — |
| Users ↑ + Revenue flat | Monetization deterioration | Conversion and ARPU by cohort | — |
| Spend ↑ + Revenue flat | Efficiency deterioration **or** saturation | Geo holdout — attribution cannot distinguish these | Same Tier 1 saturation evidence as row 1 |

**For every pattern, separate three things:** the observed relationship · a possible explanation · the evidence that would establish causality. Never collapse them. Full sourcing for the three annotated rows is in `research/raw/causal-evidence-three-relationships.md`.

---

## 10. When the request exceeds this skill's analysis

This skill's output is diagnosis and dashboard specs across whatever sources are supplied, not model-fitting. If the user's question genuinely needs a fitted model, say so and name the tool — don't approximate a saturation curve or a CLV projection by eye when a real model exists for it.

| The user is really asking for | Name it, don't fake it | Notes |
|---|---|---|
| "What's the true incremental ROI of each channel, adjusting for saturation and carryover?" | **Marketing-mix modeling** (google/meridian — Bayesian, adstock+Hill saturation, Apache-2.0; or facebookexperimental/Robyn — ridge+Nevergrad, MIT). Meridian defines ROI as a counterfactual: expected outcome change when a channel's spend is zeroed out — a causal contrast, not correlation | Needs geo- or time-series-level spend/KPI data, weeks of history, ideally control variables. Not a single-session task. **The output carries real uncertainty — a posterior interval, model fit, and sensitivity to priors — not a single point number; ask for those, don't just report the mean estimate as if it were exact** |
| "Project each customer's/segment's lifetime value from purchase history" | **BTYD/probabilistic models** — BG/NBD, Pareto/NBD, Gamma-Gamma (pymc-labs/pymc-marketing `clv` module, Apache-2.0; the older `lifetimes` package is archived, point to pymc-marketing instead) | Needs an RFM summary per customer (frequency, recency, T) — this schema is the de facto standard input shape. This is the rigorous alternative to the `1/churn × margin` approximation in §5 |
| "Did this specific test/change actually cause the lift, with proper variance reduction?" | **CUPED / sequential testing** (growthbook/growthbook `gbstats`, MIT) implements both as real statistics, not descriptions | Relevant when a user has experiment data, not just observational campaign data. For designing a new test rather than analyzing an existing one, hand off to `ab-test-playbook` per `analysis-playbook.md`'s Insight → Action → Experiment chain |

Use these tools' documented approach as the standard to explain *why* a number from this skill's own analysis is a simplification — not to reimplement their math inline. Point the user to the tool when the question warrants it.
