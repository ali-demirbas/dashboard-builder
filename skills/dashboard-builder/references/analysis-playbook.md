# Analysis Playbook: Ingestion → Quality → Diagnosis

## Ingestion

### Step 1 — Inventory
For every file record: filename, file type, source/platform, date range, rows, columns, granularity, likely business purpose.

| File | Source | Period | Granularity | Purpose |
|---|---|---|---|---|
| installs.xlsx | Adjust | Jan–Jun | Daily / Channel | Acquisition |
| crm.xlsx | Braze | Jan–Jun | Campaign | Lifecycle |
| revenue.xlsx | Finance | Jan–Jun | Monthly | Financial |

### Step 2 — Schema detection
Identify: date fields, channel/campaign fields, source/medium, country, platform, OS, device, user/customer IDs, campaign IDs, revenue, cost/spend, conversion metrics, retention metrics. Then map to the standard taxonomy (kpi-framework.md).

**Source identification: precedence and ambiguity — resolve before trusting either signal alone.**
- **Filename vs. schema conflict.** A filename is a label someone typed; the column schema is the actual export. When they disagree (e.g. `ga4_export.csv` but the columns are Campaign/Spend/Impressions/Clicks/CTR — an ad-platform shape, not a GA4 one), **schema evidence wins.** State the conflict explicitly ("filename suggests GA4, but the columns match an ad-platform export — treating as [platform] based on schema") rather than silently trusting either signal without saying so.
- **Ambiguous source.** A generic file (e.g. Date/Users/Revenue/Orders with no other identifying columns, naming convention, or metadata) may not match any known platform pattern at all. Do not guess a platform from weak cues — a wrong platform guess silently imports that platform's counting-unit and attribution-window assumptions into every downstream comparability check. State **"Source: unidentified — treating as a generic/user-provided KPI sheet"** and proceed with whatever of the eight facts (`SKILL.md` step 1) can still be inferred or must be asked for.
- **Record a confidence level with every source identification, not just a name.** "Source: GA4" and "Source: probably GA4" lead to very different downstream behavior, and collapsing them loses the distinction exactly where it matters. Tag each source and name the evidence:

  | Level | Basis | Downstream effect |
  |---|---|---|
  | **HIGH** | Multiple platform-distinctive columns or a recognizable export structure (e.g. `sessionDefaultChannelGroup` + `eventName` + a property-style layout) | Apply that platform's counting rules, attribution defaults, and named hard blocks in full |
  | **MEDIUM** | Column names are consistent with the platform but not distinctive to it | Apply platform rules, but **state that the identification is inferred** — a rule applied to a misidentified source is worse than no rule |
  | **LOW** | Only a filename, a single suggestive column, or the user's say-so with no schema corroboration | Do **not** apply platform-specific semantic rules. Treat as a generic sheet and ask |
  | **UNKNOWN** | No signal | As "Ambiguous source" above |

  This feeds the metric registry's `mapping_confidence` field directly (`kpi-framework.md` §1): a column can only be mapped EXACT if its source is identified at HIGH confidence.

**Non-tabular and locale-specific sources — check before assuming a clean table:**
- **PDF exports.** Extract tables first; if the PDF is a rendered dashboard screenshot or a narrative report rather than a real table, state that explicitly ("this PDF has no extractable table — figures below are read off the page, not parsed, and should be spot-checked") rather than silently treating OCR'd/read numbers as equivalent to a parsed export. **Multi-page PDF tables commonly repeat their header row on every page** — check that a repeated header hasn't been ingested as a data row (a giveaway: a "row" whose values are all column-name-shaped strings, not numbers).
- **Duplicate or multi-row headers.** Two columns sharing one name (e.g. two "Clicks" columns — one Search, one Display, a real Google Ads export pattern) must be disambiguated before mapping, not silently merged or overwritten by whichever one a naive read keeps last. A header spanning two rows (category on row 1, metric name on row 2) needs both rows read together — state which convention you used if it wasn't obvious from the file.
- **Multi-sheet Excel files.** Check every sheet, not just the first — a common failure is a "Summary" sheet with pre-aggregated (and sometimes stale or differently-filtered) numbers sitting in front of the real per-row data on another tab.
- **Locale-specific number formats.** `1.234,56` (comma decimal, dot thousands — standard in Turkey and much of Europe) vs `1,234.56` (US/UK). Misreading one for the other silently shifts every value by a factor of ~1000. If a column's values look implausibly large or small, check the locale before assuming a data error.
- **Merged cells, header rows not on row 1, hidden sheets/rows.** State what you assumed about header location if it wasn't obvious.
- **Non-UTF-8 encoding.** A CSV exported from Excel or an older BI tool routinely carries Latin-1/Windows-1252 bytes (curly quotes, accented city/region names, non-breaking spaces) that a strict UTF-8 read chokes on mid-file, not at row 1 — the read can succeed for thousands of rows before hitting the first offending byte. Don't treat a decode error as "corrupt file"; retry with a Latin-1/`cp1252` fallback before concluding anything's wrong, and note which encoding was actually used.
- **Fiscal year vs. calendar year.** A finance/BI export's "Q1," "monthly," or "YTD" labels can be fiscal, not calendar — a company on a July–June fiscal year has its "Q1" run July–September. Silently assuming calendar-year boundaries when the source is fiscal misaligns every MoM/QoQ/YoY comparison without any number looking obviously wrong. Check the file's own date values against its period labels before trusting either; if genuinely ambiguous, ask rather than assume calendar-year.

**Schema drift across periods.** If comparing an export to a prior period's export (or the user mentions "it used to have a column called X"), check for: a column renamed (partially covered by the alias table in `kpi-framework.md` §1, but a genuinely new name won't be in that table), a column that disappeared, a data type change (a column that was numeric now has text), or a grain change (daily became weekly). Flag any of these as a WARNING before treating the two periods as comparable — this is the same discipline as the platform-configuration-change checks in `comparability-rules.md` §2.4, applied to the data file itself rather than the vendor's platform.

## Data quality audit (before any analysis)

**Full check sequence, severity rules and anomaly triage now live in `data-quality-gate.md` — load it here.** Summary: structure/grain → completeness → validity → consistency → distributional (rolling-sigma, not just fixed bounds) → cross-source reconciliation. A BLOCKER stops analysis of the affected slice; never silently correct suspicious data.

## Time-series analysis

When time-based data exists, analyze: MoM, WoW, YoY (where available), trend direction, growth acceleration/deceleration, peaks, troughs, structural breaks, outliers, seasonality, campaign-driven movements.

Do not overinterpret a single-period change. Distinguish: **Level → Change → Trend → Structural shift**.

**Concentration risk — check before interpreting any trend as broad-based.** When any single dimension member (a channel, campaign, customer, or product) accounts for ≥50% of a metric's total in the window being analyzed, flag it explicitly before writing up a trend on that metric: "X% of this metric's movement traces to a single contributor — the trend is not broad-based." A trend driven by one contributor is fragile in a way a broad-based trend isn't, and reporting the aggregate move without naming the concentration risks implying stability that isn't there. Classify the flag FACT or RISK per the skill's existing labeling, not folded silently into the trend narrative.

**Unequal-length or partial-period comparisons — check before any MoM/WoW/YoY.** Confirm both periods cover the same number of days (and, where weekly seasonality matters, the same day-of-week composition) before comparing them as if the comparison were normal. The single most common real-world instance: a dashboard requested mid-month, where "this month" is a partial period (e.g. the 1st–15th) and gets compared raw against a full prior month (the 1st–31st) — this reads as a sharp decline that is actually just fewer elapsed days, not a demand change. A partial current period must be labeled partial and compared against the **same elapsed-day window** of the prior period (1st–15th vs. 1st–15th), or — if a full-period comparison is genuinely needed — annotated with a run-rate projection explicitly labeled **Derived**, stating the method, never presented as a raw completed-period comparison.

## Funnel analysis

Reconstruct the available funnel, e.g. Impression → Click → Install → Activation → Registration → Product View → Purchase.

**Cross-source funnels are population approximations, not verified user-level journeys, unless stated otherwise.** Before presenting a funnel whose stages come from different measurement systems (e.g. Search Console clicks → GA4 sessions → a CRM's signups → an e-commerce platform's purchases), confirm whether a shared identifier (session ID, user ID, order ID) actually links the same individuals across every stage. If it doesn't — the normal case when chaining tools that don't share an identity system — label the funnel **"population approximation, not a verified user-level journey"** and name the weakest handoff (usually the first cross-system boundary, e.g. a Search Console click that never produces a linkable GA4 session). Reporting stage-to-stage conversion percentages without this caveat implies the same people were tracked through every stage, which a population count sitting next to another population count does not establish.

Per stage: volume, conversion rate, drop-off, change vs previous period, contribution to final conversion. Identify the **largest economically meaningful bottleneck**, not merely the largest percentage drop.

**Quantify "economically meaningful," don't just eyeball it.** A 70% drop-off at checkout and a 20% drop-off at activation aren't comparable by percentage alone — size the opportunity. **"Lost users" is ambiguous unless you define the gap explicitly — don't leave it implicit:**

```
Incremental conversions = Eligible population × (Target CVR − Baseline CVR) × Recovery factor
Opportunity             = Incremental conversions × Expected value per converted user
                         (Expected value per user = AOV × gross margin, or ARPU × expected lifetime, per kpi-framework.md §5)
```

- **Eligible population** — users who reached this funnel stage in the period, not the whole top-of-funnel.
- **Target CVR** — the benchmark you're recovering toward: the best-performing comparable segment's rate, a prior period's rate, or a stated goal. Name which.
- **Baseline CVR** — this stage's current rate.
- **Recovery factor** — how much of that gap you actually expect to close, as a named scenario, not an implicit guess: **0.25 (conservative) / 0.50 (moderate) / 0.75 (aggressive)** unless you have a specific reason to use another value. State which scenario each number in a reported range uses.

Report it as a range across at least two recovery-factor scenarios with a stated confidence (e.g. "₺0.9–1.8M/month at 0.25–0.50 recovery — Medium confidence, assumes AOV and target CVR both hold"), and label it **Derived**. This is what turns "checkout is the bottleneck" into a prioritization decision instead of an observation.

## Channel analysis

Per channel: Spend, Traffic, Installs, Customers, CAC, CPI, Conversion, Retention, LTV, Revenue, ROAS, Profitability.

Never declare a channel "best" on one metric. A low-CPI channel with poor retention may be inferior to a higher-CPI channel with substantially higher LTV. Prioritize: **unit economics + quality + scalability** — and define both of the latter two explicitly rather than using them as vague virtues:

- **Channel quality** — no single mandatory formula, but ground it in something measurable: D30 retention by source, activation rate by source, or LTV by source at matched cohort maturity (never compare cohorts of different ages — see `comparability-rules.md` §2.5). If you compute a blended quality score, show the formula and label it **Derived**, not a vendor-defined metric.
- **Scalability** — how does efficiency change as spend increases on this channel? Evidence: marginal CAC trend as spend scales up (is CPI/CAC rising as you add budget — a saturation signal, see `kpi-framework.md` §9), available audience size relative to current reach, or spend elasticity if enough history exists. Don't assert a channel is "scalable" without naming which of these you checked.

## CRM / lifecycle analysis (Braze, email, SMS, push)

- **Reach:** Audience, Delivered, Delivery Rate
- **Engagement:** Open Rate, CTR, CTOR
- **Conversion:** Conversion Rate, Purchases, Revenue, Revenue/User
- **Negative signals:** Unsubscribe, Complaint, Churn, Fatigue

High Open Rate ≠ successful campaign. Prioritize **incremental business outcome over vanity engagement**. If control/holdout data exists, prioritize incremental lift; if it doesn't, explicitly state that incremental causality cannot be established.

## Correlation & relationship engine

Search for meaningful co-movements. **The full pattern table, with the evidence needed to confirm each reading, lives in `kpi-framework.md` §9 — load it here.** For every co-movement, separate: observed relationship / possible explanation / evidence required for causality. Never collapse the three, and never treat a pre/post or cohort comparison as equivalent to a real experiment — **grade every piece of evidence on the Evidence Ladder in `comparability-rules.md` §2.6 (E0 raw observation through E5 replicated causal evidence)** before writing a causal sentence. Only E4/E5 evidence (a real A/B test, holdout, or geo experiment) supports "X caused Y"; everything below that is a hypothesis to state as a hypothesis.

### Hypothesis-elimination pattern for diagnosing a metric move

**Check identities before hypotheses.** If the moved metric decomposes into named components (`kpi-framework.md` §8 — Revenue = Orders × AOV, MRR = Customers × ARPA), check which side of the identity actually moved *first*. This is arithmetic, not a hypothesis — it costs nothing to check and it's frequently the whole answer ("Revenue fell because AOV fell 15%, Orders were flat" closes the question outright) or narrows which hypotheses are even worth enumerating (if AOV is what moved, H1-style traffic-quality hypotheses are the wrong branch). Only move to the hypothesis-elimination pattern below for *why* the identity's component moved, not *whether* it moved.

When a KPI moves and the cause isn't obvious, don't jump to the first plausible story. Enumerate competing hypotheses, mark what the data does and doesn't support, and state a diagnosis with a confidence level — not a single narrative presented as certain:

```
Observation: CVR declined 18% MoM (Derived, from <source>)

Possible hypotheses:
  H1 — traffic quality deteriorated (e.g. a channel mix shift toward lower-intent sources)
  H2 — a funnel step broke (checkout failure, page error, broken redirect)
  H3 — price/offer competitiveness declined
  H4 — tracking or attribution setting changed (check comparability-rules.md §2.4 first)
  H5 — seasonality

Evidence:
  H1 — supported (channel mix shifted toward Channel X, which has 40% lower CVR historically)
  H2 — unsupported (checkout completion rate flat)
  H3 — unknown (no competitor pricing data supplied)
  H4 — partially supported (GA4 attribution model changed 2 weeks before the decline)
  H5 — unknown (only 1 month of history, can't test seasonality)

Diagnosis: most likely H1 + H4 jointly explain the decline.
Confidence: Medium — H3 remains untested for lack of data; state this explicitly rather than
implying the diagnosis is complete.
```

This replaces "I noticed X and Y moved together, so X caused Y" with a structure that forces alternative explanations onto the table before landing on one — the same discipline as the anomaly-triage list in `data-quality-gate.md`, applied to any metric move, not just anomalies.

**What "Confidence: Medium" actually means — don't leave it as a vibe.** Base it on the weakest of these three, not an average, since one bad dimension undermines the whole diagnosis:

| | Low | Medium | High |
|---|---|---|---|
| **Data quality** | A BLOCKER touches an input | Only WARNING-level issues, if any | Clean, or only INFO-level notes |
| **Evidence tier** (`comparability-rules.md` §2.6) | E0/E1 only | E2/E3 | E4/E5, or an E1/E2 pattern with no plausible confound named |
| **Comparability** (`comparability-rules.md` "How to use this file") | A key input is NOT_COMPARABLE | CONDITIONAL or NORMALIZABLE | DIRECT |

State which dimension is holding the confidence level down (as in the worked example above: "H3 remains untested" is what keeps this at Medium, not High) — a confidence label without a stated reason is not more useful than no label at all.

## Anomaly detection

Identify suspicious movements: revenue drop, spend surge, CPI spike, CAC deterioration, retention collapse, conversion collapse, CRM engagement anomaly, unsubscribe spike, revenue/spend divergence.

Do not auto-label an anomaly a problem. **First test the alternative explanations in `data-quality-gate.md` §"Anomaly triage"** — a platform-side configuration or tracking change is a high-priority, cheap-to-check alternative explanation and must be ruled out before a business explanation is written.

## Insight candidate engine — how the 5-10 observations actually get chosen

`SKILL.md` step 6 caps the first-turn output at 5-10 prioritized observations, and Operating Principle 8 names the three dimensions that set priority. That states the *criteria* but not the *procedure* — which leaves the actual selection as an unstated judgment call, exactly the kind of surface-level shortcut this skill's Overview says it exists to refuse.

**This is deliberately a rule-based gate, not a numeric score.** A weighted 0-100 composite over "business impact" was considered and rejected more than once in this skill's development, for a real reason: it manufactures precision that the inputs don't have, and a single number hides which dimension actually drove it. What's needed isn't a score, it's a sequence of yes/no questions with a stated verdict. Run every candidate observation through all eight, in order — the first failure decides the outcome:

| # | Question | If no |
|---|---|---|
| 1 | **Is the change real?** Does it clear the data-quality gate — no BLOCKER on its inputs, not an artifact of a missing day, a totals row, or a partial period? | **SUPPRESS** — this is a data finding, not a business finding. Report it as a quality issue instead |
| 2 | **Is it statistically supportable?** Does the denominator carry enough volume for the move to mean anything (see "Statistical sufficiency" below)? | **SUPPRESS** — a 0.4pt CTR move on 100 impressions is noise wearing a percentage sign |
| 3 | **Is it material?** Does the magnitude matter against the business's own scale — not just against zero? | **LOW** at most, and usually SUPPRESS. A 2% move on a metric representing 0.3% of revenue is arithmetic, not news |
| 4 | **Is it broad or concentrated?** Does one dimension member drive ≥50% of it (see Concentration risk above)? | Not a suppression — but the concentration **is** the finding, and must be stated as such rather than reported as a broad-based move |
| 5 | **Is it economically important?** Can it be opportunity-sized, or tied to spend, margin, or retained revenue? | **MEDIUM** at most — an interesting movement with no economic handle isn't a critical one |
| 6 | **Is there a plausible alternative explanation not yet ruled out?** Run the anomaly-triage list and the hypothesis-elimination pattern above | Keep it, but **downgrade one level** and state the untested alternative — a finding with an open competing explanation is not CRITICAL |
| 7 | **Is the evidence sufficient for the claim being made?** Grade it on the Evidence Ladder; a causal-sounding write-up needs E4/E5 | Keep the observation, **rewrite the claim** down to what the evidence supports. Never downgrade the evidence tier to fit the story |
| 8 | **Is it actionable?** Is there a decision, test, or investigation this changes? | **MEDIUM/LOW** — real but not urgent. Genuine context and guardrail metrics live here legitimately |

Then assign, and **name which question drove the label**:

```
🔴 CRITICAL  — clears 1-3 and 5, actionable, evidence sufficient for the claim made,
               no unresolved alternative explanation
🟠 HIGH      — clears 1-3, actionable, but one of 6/7 is open (stated explicitly)
🟡 MEDIUM    — real and supported, but not economically sized or not yet actionable
🟢 LOW       — real, small, or context/guardrail rather than decision-driving
   SUPPRESS  — fails 1, 2, or 3. Not shown as a business observation at all
```

**SUPPRESS is the point of this engine, not a side effect.** A dashboard's quality is set as much by what it leaves out as by what it shows — an output padded with statistically meaningless moves reads as thorough and is actively worse than a short one, because it costs the reader the same attention per item.

### Statistical sufficiency — before any rate or change gets reported

Question 2 above needs a concrete bar, not a feeling. Rates and rate *changes* are the common trap: a percentage looks equally authoritative at any sample size.

- **Rate metrics (CVR, CTR, open rate, retention, churn):** state the denominator alongside the rate, always. Where the denominator is small enough that the rate would move materially on a handful of events, say so and treat the figure as directional — "CTR 2.5% (n=100 impressions — a single click moves this by 1pt)" is honest; a bare "CTR 2.5%, up from 2.1%" at that volume is not.
- **A change in a rate** needs more support than the rate itself. If a plausible re-run of the same period could produce the opposite direction purely from sampling, it is not a finding — it is noise. Where the volume is genuinely too low to distinguish the two, say that instead of reporting the direction.
- **Correlations:** an R value computed over a handful of points is not evidence of anything, regardless of magnitude — state n alongside every correlation coefficient (and the Evidence Ladder tier, per `dashboard-blueprints.md`'s chart-form rule).
- **Holdout and lift results:** already covered in `kpi-framework.md` §6 — a control group of a few dozen users produces an interval wide enough to contain zero.
- **When the data can't support the test, say which test you'd have run** rather than silently skipping it or silently proceeding — same discipline as the anomaly scan's "insufficient history" statement.

## Data conflict resolution

When two files disagree on the same KPI (e.g. Adjust 100K installs vs GA4 87K new users), **run the seven-point comparability checklist in `comparability-rules.md` §1 before concluding anything.** If a hard-block rule fires (§2 of that file), report the conflict using its refusal template — do not arbitrarily choose a side, and do not call either value "wrong" without evidence.

## Executive diagnosis (internal structure)

- **Growth:** Where is growth coming from? Where slowing? Which channels contribute most?
- **Efficiency:** Are CAC / CPI / ROAS improving? Is spend becoming more productive?
- **Quality:** Are new users valuable? Retention improving? LTV increasing?
- **Monetization:** ARPU up? Conversion improving? Revenue growth volume-driven or value-driven?
- **Lifecycle:** Existing users more engaged? Churn increasing? Is CRM generating measurable value?
- **Profitability:** Is revenue growth profitable? Gross profit keeping pace? Acquisition economically sustainable?

## Core decision framework (per major business question)

WHAT HAPPENED? (observed movement) → HOW MUCH? (magnitude) → WHERE? (channel/campaign/segment/funnel stage) → WHY MIGHT IT HAVE HAPPENED? (evidence-backed hypothesis) → SO WHAT? (business impact) → WHAT SHOULD WE DO? (action) → HOW DO WE KNOW? (validation metric or experiment)

## Insight → Action → Experiment chain

Every recommendation in the final output (`dashboard-blueprints.md` Output mode 2, "Recommended actions") should be traceable through this chain, not just an action in isolation:

```
INSIGHT → WHY? → BUSINESS IMPACT → RECOMMENDED ACTION → EXPERIMENT → SUCCESS METRIC → GUARDRAIL → EXPECTED IMPACT
```

Worked example:
```
Insight:          Checkout CVR dropped 14% MoM
Why:               Payment-step abandonment increased (funnel data, H2 in the hypothesis-elimination check above)
Business impact:   Opportunity-sized per the funnel formula above
Recommended action: Investigate payment error rate; test an alternative payment UX
Experiment:        A/B test on the payment step
Success metric:    Completed-purchase rate
Guardrail:         Refund rate (don't win on completions by pushing through bad payments)
Secondary:         Payment failure rate
```

**If the recommended action needs a formal experiment design** (sample size, randomization, stopping rule, statistical test selection) **— that is a different skill's job, not this one's.** This skill diagnoses the problem, sizes the opportunity, and states what a valid test would need to show; the `ab-test-playbook` skill designs the test itself. Hand off rather than improvising test methodology here.
