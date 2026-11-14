# Analysis Playbook: Ingestion → Quality → Diagnosis

## Ingestion

### Step 1 — Inventory
For every file record: filename, file type, source/platform, date range, rows, columns, granularity, likely business purpose. With code execution, date range, rows, columns, grain and locale come from `profile` (`SKILL.md` step 1), not from reading the file.

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
- **Record a source-identification confidence with every source identification, not just a name.** "Source: GA4" and "Source: probably GA4" lead to very different downstream behavior, and collapsing them loses the distinction exactly where it matters. Tag each source and name the evidence (the values are deliberately not the CRITICAL/HIGH/MEDIUM/LOW priority words; `SKILL.md` §Label vocabulary):

  | Level | Basis | Downstream effect |
  |---|---|---|
  | **Strong** | Multiple platform-distinctive columns or a recognizable export structure (e.g. `sessionDefaultChannelGroup` + `eventName` + a property-style layout) | Apply that platform's counting rules, attribution defaults, and named hard blocks in full |
  | **Moderate** | Column names are consistent with the platform but not distinctive to it | Apply platform rules, but **state that the identification is inferred** — a rule applied to a misidentified source is worse than no rule |
  | **Weak** | Only a filename, a single suggestive column, or the user's say-so with no schema corroboration | Do **not** apply platform-specific semantic rules. Treat as a generic sheet and ask |
  | **Unidentified** | No signal | As "Ambiguous source" above |

  This feeds the metric registry's `mapping_confidence` field directly (`kpi-framework.md` §1): a column can only be mapped EXACT if its source identification is Strong.

**Non-tabular and locale-specific sources — check before assuming a clean table:**
- **PDF exports.** Extract tables first; if the PDF is a rendered dashboard screenshot or a narrative report rather than a real table, state that explicitly ("this PDF has no extractable table — figures below are read off the page, not parsed, and should be spot-checked") rather than silently treating OCR'd/read numbers as equivalent to a parsed export. **Multi-page PDF tables commonly repeat their header row on every page** — check that a repeated header hasn't been ingested as a data row (a giveaway: a "row" whose values are all column-name-shaped strings, not numbers).
- **Duplicate or multi-row headers.** Two columns sharing one name (e.g. two "Clicks" columns — one Search, one Display, a real Google Ads export pattern) must be disambiguated before mapping, not silently merged or overwritten by whichever one a naive read keeps last. A header spanning two rows (category on row 1, metric name on row 2) needs both rows read together — state which convention you used if it wasn't obvious from the file.
- **Multi-sheet Excel files.** Check every sheet, not just the first — a common failure is a "Summary" sheet with pre-aggregated (and sometimes stale or differently-filtered) numbers sitting in front of the real per-row data on another tab.
- **Multi-table CSV exports.** Some tools stack several distinct breakdowns into one CSV (a GA4 Explore export can hold a traffic table, a landing-page table, and a cohort table back to back, each with its own header row and blank-line separators). Detect table boundaries before parsing — a header row appearing mid-file is a new table, not a data row — and register each sub-table as its own source. Every sub-table then counts separately for the Coverage integrity check (`dashboard-blueprints.md` §Dashboard QA gate): one that was read but never used or named is a silent omission.
- **Locale-specific number formats.** `1.234,56` (comma decimal, dot thousands — standard in Turkey and much of Europe) vs `1,234.56` (US/UK). Misreading one for the other silently shifts every value by a factor of ~1000. If a column's values look implausibly large or small, check the locale before assuming a data error. The output side is a separate step (`SKILL.md` principle 12): a Turkish output writes `1.234,56` and `%12,4` (decimal comma, dot grouping, percent sign first; Unicode CLDR `tr` locale data: percent pattern `%#,##0`, decimal `,`, group `.`, github.com/unicode-org/cldr, `common/main/tr.xml`, read 2026-11-14), an English output `1,234.56` and `12.4%`.
- **Merged cells, header rows not on row 1, hidden sheets/rows.** State what you assumed about header location if it wasn't obvious.
- **Non-UTF-8 encoding.** A CSV exported from Excel or an older BI tool routinely carries Latin-1/Windows-1252 bytes (curly quotes, accented city/region names, non-breaking spaces) that a strict UTF-8 read chokes on mid-file, not at row 1 — the read can succeed for thousands of rows before hitting the first offending byte. Don't treat a decode error as "corrupt file"; retry with a Latin-1/`cp1252` fallback before concluding anything's wrong, and note which encoding was actually used.
- **Fiscal year vs. calendar year.** A finance/BI export's "Q1," "monthly," or "YTD" labels can be fiscal, not calendar — a company on a July–June fiscal year has its "Q1" run July–September. Silently assuming calendar-year boundaries when the source is fiscal misaligns every MoM/QoQ/YoY comparison without any number looking obviously wrong. Check the file's own date values against its period labels before trusting either; if genuinely ambiguous, ask rather than assume calendar-year.

**Schema drift across periods.** If comparing an export to a prior period's export (or the user mentions "it used to have a column called X"), check for: a column renamed (partially covered by the alias table in `kpi-framework.md` §1, but a genuinely new name won't be in that table), a column that disappeared, a data type change (a column that was numeric now has text), or a grain change (daily became weekly). Flag any of these as a WARNING before treating the two periods as comparable — this is the same discipline as the platform-configuration-change checks in `comparability-rules.md` §2.4, applied to the data file itself rather than the vendor's platform.

## Data quality audit (before any analysis)

**Full check sequence, severity rules and anomaly triage now live in `data-quality-gate.md` — load it here.** Summary: structure/grain → completeness → validity → consistency → distributional (rolling-sigma, not just fixed bounds) → cross-source reconciliation. A BLOCKER stops analysis of the affected slice; never silently correct suspicious data.

## Time-series analysis

When time-based data exists, analyze: MoM, WoW, YoY (where available), trend direction, growth acceleration/deceleration, peaks, troughs, structural breaks, outliers, seasonality, campaign-driven movements.

Do not overinterpret a single-period change. Distinguish: **Level → Change → Trend → Structural shift**.

**Concentration risk — check before interpreting any trend as broad-based.** When any single dimension member (a channel, campaign, customer, or product) accounts for ≥50% of a metric's total in the window being analyzed, flag it explicitly before writing up a trend on that metric: "X% of this metric's movement traces to a single contributor — the trend is not broad-based." A trend driven by one contributor is fragile in a way a broad-based trend isn't, and reporting the aggregate move without naming the concentration risks implying stability that isn't there. State the concentration as a FACT framed as a RISK (`SKILL.md` §Label vocabulary), not folded silently into the trend narrative.

**Contribution analysis — which members moved an additive total.** For a total that is a plain sum (revenue, orders, spend, sessions, installs; never a rate, an average or a ratio) split by an exhaustive dimension, `drivers` (`SKILL.md` §Computation layer) computes:

- **Contribution share.** Member i's contribution is its own change, Δᵢ = xᵢ(compare) − xᵢ(base); its share is Δᵢ ÷ ΔTotal. The shares sum to exactly 100% because the total is the sum of its members. A member moving against the total has a negative share, so the same-direction shares can exceed 100% (−21,000 on one channel within a −18,300 total is 115%).
- **Ranking.** By |Δᵢ|, with positive and negative contributors reported separately, never netted into one list.
- **Stop rule.** Name the smallest set of same-direction contributors whose cumulative share reaches 50%; the rest are reported together as the remainder.
- **Drill rule.** One level only: the top contributor broken down by the next dimension, with shares taken of that member's own change. Going deeper multiplies the comparisons scanned (§Statistical sufficiency, many comparisons).
- **Labels.** "Concentrated" when one member carries ≥50% of the change: that is the Concentration risk case above, stated as such, and question 4 of the candidate engine reads it. "No single driver" when no member explains ≥25%: a broad-based move, written that way, never pinned on the largest member. A zero total change has no shares ("Not meaningful — zero total change").

This is the standard additive decomposition of a sum's change into its members' changes: exact by construction, no model behind it. The 50% stop and the 25% "no single driver" thresholds are working conventions, unverified, directional only; the 50% concentration threshold is the Concentration risk rule above. A contribution is arithmetic, not a test: a member's change still passes Statistical sufficiency before it is called a finding.

**Unequal-length or partial-period comparisons — check before any MoM/WoW/YoY.** Confirm both periods cover the same number of days (and, where weekly seasonality matters, the same day-of-week composition) before comparing them as if the comparison were normal. The typical real-world instance: a dashboard requested mid-month, where "this month" is a partial period (e.g. the 1st–15th) and gets compared raw against a full prior month (the 1st–31st) — this reads as a sharp decline that is actually just fewer elapsed days, not a demand change. A partial current period must be labeled partial and compared against the **same elapsed-day window** of the prior period (1st–15th vs. 1st–15th), or — if a full-period comparison is genuinely needed — annotated with a run-rate projection explicitly labeled **Derived**, stating the method, never presented as a raw completed-period comparison.

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
- **No margin supplied.** Size the opportunity in revenue instead (expected value per user = AOV, or revenue per converted user), and label the figure **"revenue, not profit"** wherever it appears. No margin is assumed (`SKILL.md` principle 2), no break-even or profit figure is derived from it, and the sizing still counts as an economic handle for candidate-engine question 5. The margin joins step 6's batched questions only when the user asked about profit or break-even.

Report it as a range across at least two recovery-factor scenarios with its assumptions named and the inputs' measurement confidence stated (§Confidence) — e.g. "₺0.9–1.8M/month at 0.25–0.50 recovery, assumes AOV and target CVR both hold; measurement confidence Medium (comparability: target CVR is from a CONDITIONAL segment)" — and label it **Derived**. This is what turns "checkout is the bottleneck" into a prioritization decision instead of an observation.

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

Search for meaningful co-movements. **The full pattern table, with the evidence needed to confirm each reading, lives in `kpi-framework.md` §9 — load it here.** For every co-movement, separate: observed relationship / possible explanation / evidence required for causality. Never collapse the three, and never treat a pre/post or cohort comparison as equivalent to a real experiment — **grade every piece of evidence on the Evidence Ladder in `comparability-rules.md` §2.6 (E0 raw observation through E5 replicated causal evidence)** before writing a causal sentence. An unqualified "X caused Y" needs E4/E5 (a real A/B test, holdout, or randomized geo experiment); a checked E3 design supports only the conditional form defined there; E0–E2 is an observation or a hypothesis and is written as one.

### Hypothesis-elimination pattern for diagnosing a metric move

**Check identities before hypotheses.** If the moved metric decomposes into named components (`kpi-framework.md` §8 — Revenue = Orders × AOV, MRR = Customers × ARPA), check which side of the identity actually moved *first*. This is arithmetic, not a hypothesis — it costs nothing to check and it's frequently the whole answer ("Revenue fell because AOV fell 15%, Orders were flat" closes the question outright) or narrows which hypotheses are even worth enumerating (if AOV is what moved, H1-style traffic-quality hypotheses are the wrong branch). Only move to the hypothesis-elimination pattern below for *why* the identity's component moved, not *whether* it moved. **A blended rate with a segment breakdown gets the same treatment:** when CVR, CTR, ROAS, CAC, AOV or any other ratio moves and the supplied data splits it by channel, device, country or another exhaustive segment, run the mix vs rate decomposition (`kpi-framework.md` §8) before enumerating hypotheses. It says whether the blend moved because segment shares shifted (mix — which points to H1-type traffic-composition hypotheses) or because segments themselves changed (rate), and it catches the Simpson's-paradox case where every segment moved one way and the blend the other — a blended move that no segment actually made is never reported as a performance change.

**"Why did X move" — route by the metric's kind first.** An additive total gets `drivers` (§Contribution analysis above): ranked contributions, positive and negative apart, cumulative 50% stop, one drill level, "no single driver" when nothing explains 25%. A ratio (CVR, CTR, ROAS, CPA, CAC, AOV, any average or percentage) gets `decompose`: the Kitagawa rate/mix split with the Simpson's-paradox flag, defined in `kpi-framework.md` §8 Mix vs rate. `drivers` refuses a ratio-named metric and points to `decompose`; `--force-additive` is for a column that is a sum despite its name, never for a rate. Either result feeds the hypotheses below: "concentrated" and "no single driver" are the Concentration risk statements (§Time-series analysis), and a mix-dominated change points at traffic composition.

When a KPI moves and the cause isn't obvious, don't jump to the first plausible story. Enumerate competing hypotheses, mark what the data does and doesn't support, and state a diagnosis with its evidence tier and what remains open — not a single narrative presented as certain:

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

Diagnosis: H1 + H4 are the leading hypotheses for the decline.
Evidence tier: E2 (co-movement, no control) — a hypothesis, not a cause.
Still open: H3, H5 — untested for lack of data; say so rather than implying the
diagnosis is complete.
Measurement confidence in the 18% decline itself: stated separately (see below).
```

This replaces "I noticed X and Y moved together, so X caused Y" with a structure that forces alternative explanations onto the table before landing on one — the same discipline as the anomaly-triage list in `data-quality-gate.md`, applied to any metric move, not just anomalies.

### Confidence — two labels that answer two different questions

**Measurement confidence** says how far to trust a number or a descriptive comparison. Every finding carries it. **Evidence tier** (E0–E5, `comparability-rules.md` §2.6) says what a *causal* claim rests on. Only a sentence that explains why something moved carries it. They are not one scale: "revenue fell 12% month over month" can be High measurement confidence at tier E1, because it claims no cause and needs clean data, not an experiment. Requiring E4/E5 for every confident statement would make every descriptive finding look doubtful, and letting clean data stand in for an experiment would make every diagnosis look proven.

Measurement confidence is the weakest of three, not an average. (A BLOCKER on an input produces no finding at all, not a Low one — candidate-engine question 1.)

| | Low | Medium | High |
|---|---|---|---|
| **Data quality** | A WARNING on an input that materially moves the figure | WARNING-level issues that don't move the figure materially, or a figure resting on provisional values (`data-quality-gate.md` §2) | Clean, or only INFO-level notes |
| **Comparability** (`comparability-rules.md` "How to use this file") | A key input is NOT_COMPARABLE (the comparison isn't made) | CONDITIONAL or NORMALIZABLE | DIRECT, or a single-source figure with no comparison involved |
| **Statistical support** (§Statistical sufficiency) | UNTESTED or INCONCLUSIVE | SUPPORTED, but the interval is wide enough that its two ends would lead to different decisions | SUPPORTED with an interval whose two ends lead to the same decision — or NOT APPLICABLE (no sampling question: a total, or a full-population before/after read) |

Name the row holding the label down; a confidence label with no stated reason is no better than none.

A **diagnosis** adds two lines to that label, as in the worked example above: the evidence tier, which fixes the permitted wording (E0–E2 hypothesis, E3 conditional, E4/E5 causal), and the alternative explanations — which were tested, which remain open.

## Anomaly detection

Identify suspicious movements: revenue drop, spend surge, CPI spike, CAC deterioration, retention collapse, conversion collapse, CRM engagement anomaly, unsubscribe spike, revenue/spend divergence.

Do not auto-label an anomaly a problem. **First test the alternative explanations in `data-quality-gate.md` §"Anomaly triage"** — a platform-side configuration or tracking change is a high-priority, cheap-to-check alternative explanation and must be ruled out before a business explanation is written.

## Insight candidate engine — how the 5-10 observations actually get chosen

`SKILL.md` step 6 caps every answer at 5-10 prioritized findings, and Operating Principle 8 names the three dimensions that set priority. That states the *criteria* but not the *procedure* — which leaves the actual selection as an unstated judgment call, exactly the kind of surface-level shortcut this skill's Overview says it exists to refuse.

**This is deliberately a rule-based gate, not a numeric score.** A weighted 0-100 composite over "business impact" was considered and rejected more than once in this skill's development, for a real reason: it manufactures precision that the inputs don't have, and a single number hides which dimension actually drove it. What's needed isn't a score, it's a sequence of yes/no questions with a stated verdict. Run every candidate observation through all eight, in order. **A failure on 1 or 3 (outside the context exception in 3), or a NEGLIGIBLE result on 2, is terminal — stop there, the verdict is set.** Questions 4–8 are all evaluated regardless of each other's answers, and the label block below reads them jointly — a "no" on any of 4–8 changes how the finding is stated or capped, it doesn't end the evaluation:

| # | Question | If no |
|---|---|---|
| 1 | **Is the change real?** Does it clear the data-quality gate — no BLOCKER on its inputs, not an artifact of a missing day, a totals row, or a partial period? (A change resting only on provisional values passes 1 but caps at MEDIUM, `data-quality-gate.md` §2) | **SUPPRESS** — this is a data-quality issue, not a finding. Report it in the data-quality section with its severity instead (`SKILL.md` §Label vocabulary) |
| 2 | **Is it statistically supported?** Run the test the data's structure allows and read the interval against what would matter ("Statistical sufficiency" below). Five outcomes, not yes/no | **SUPPORTED** → continue. **NOT APPLICABLE** (no sampling question: a population total or count, e.g. revenue booked in the period, or a before/after read of a rate over every unit in the period, Step 1) → continue with no cap; the statistical-support row of measurement confidence reads High. **NEGLIGIBLE** → **SUPPRESS** as a change; it returns only as a "held steady" LOW context line under the exception in 3. **INCONCLUSIVE** → continue, cap at MEDIUM, report as inconclusive with the interval — never as "no effect" — except the volume-limit case (Step 3 below), which is not a finding. **UNTESTED** (a test the structure calls for could not run or read: no compute tool, no valid test for this structure, SRM not checked, or a sampled single-series read capped there by Step 1) → continue, cap at MEDIUM, mark "directional, not statistically tested" |
| 3 | **Is it material?** Does the magnitude (the point estimate, for an INCONCLUSIVE or UNTESTED move) matter against the business's own scale — not just against zero? | **SUPPRESS** — a 2% move on a metric representing 0.3% of revenue is arithmetic, not news. **Context exception, the only non-terminal outcome of 1–3:** a small or NEGLIGIBLE move on a metric the reader needs as a guardrail for another finding, or that the user asked about, is kept as one LOW context line ("CVR held steady, 95% CI −0.2pp to +0.3pp") and skips 4–8 |
| 4 | **Is it broad-based?** I.e. does **no** single dimension member drive ≥50% of it (see Concentration risk above)? | Not a suppression and not a cap — the concentration **is** the finding: restate it as such, and assign the label below to that restated finding rather than to a broad-based move |
| 5 | **Is it economically important?** Can it be opportunity-sized, or tied to spend, margin, or retained revenue? | **MEDIUM** at most — an interesting movement with no economic handle isn't a critical one |
| 6 | **Have all plausible alternative explanations been ruled out?** Run the anomaly-triage list and the hypothesis-elimination pattern above | Keep it, but it **cannot be CRITICAL** (HIGH at most — see the label block) and the untested alternative is stated explicitly — a finding with an open competing explanation is not CRITICAL |
| 7 | **Is the evidence sufficient for the claim being made?** Grade it on the Evidence Ladder; an unqualified causal sentence needs E4/E5, a checked E3 design supports the conditional form only | Keep the observation, **rewrite the claim** down to what the evidence supports. Never downgrade the evidence tier to fit the story |
| 8 | **Is it actionable?** Is there a decision, test, or investigation this changes? | **MEDIUM** if 5 passed (economically sized), **LOW** if 5 also failed — real but not urgent |

Then assign, and **name which question drove the label**:

```
CRITICAL  — material and SUPPORTED or NOT APPLICABLE (2), clears 1, 3 and 5,
            actionable, no unresolved alternative explanation (6 passed),
            not resting only on provisional values (1)
HIGH      — same, but 6 is open (the untested alternative is stated)
MEDIUM    — real, but not economically sized (5 failed), not yet actionable
            with 5 passed (8 failed), statistically INCONCLUSIVE / UNTESTED (2),
            or resting only on provisional values (data-quality-gate.md §2)
LOW       — fails both 5 and 8, or kept by the context exception in 3
SUPPRESS  — fails 1 or 3 (outside the context exception), NEGLIGIBLE on 2, or
            the INCONCLUSIVE volume-limit case. Not shown as a finding
```

Priority says how much attention a finding deserves, not whether it is good news — direction (Favorable / Unfavorable / Neutral) is a separate field and the only one that carries color (`SKILL.md` §Label vocabulary). Question 7 never stays "open" in a delivered output: a claim the evidence can't support is rewritten until it can, so 7 shapes the wording of a finding, not its label.

**SUPPRESS is the point of this engine, not a side effect.** A dashboard's quality is set as much by what it leaves out as by what it shows — an output padded with statistically meaningless moves reads as thorough and is actively worse than a short one, because it costs the reader the same attention per item.

### Statistical sufficiency — pick the test the data's structure allows

Question 2 needs a decision rule, not a feeling, and the rule starts with whether a test is valid at all — a test run on the wrong structure produces a confident wrong answer.

**Step 1 — what is the unit, and are the observations independent?**

| Data structure | What fits | What doesn't |
|---|---|---|
| Two groups of *different* units, each counted once (A/B arms, two channels' users, two separate cohorts) | Two-proportion z-test / interval on the difference, for a rate. With small counts — by the usual rule of thumb, fewer than about 10 successes or 10 failures in either group — Fisher's exact test for the test, and a Newcombe (Wilson-score) interval for the difference, since Fisher yields a p-value and odds ratio, not the risk-difference interval Step 3 reads | — |
| Before vs. after on one time series (this month's CVR vs. last month's) | **Over every unit in the period** (all sessions, all orders the export holds, the normal case for an analytics, store or ad-platform export): the figures are the population, not a sample, so question 2 is **NOT APPLICABLE**, as for a total. Whether the move is more than noise is then a question for the series' own history, not a two-proportion test: read it against the series' ordinary period-to-period variation (the anomaly band, `data-quality-gate.md` §5, or the range of earlier period-to-period changes) as question 3's yardstick; with too little history to know that variation, say so, and seasonality stays an open alternative under question 6. Trend wording still needs the trend gate (`comparability-rules.md` §2.6). A two-proportion interval may be shown alongside as a **sampling-noise floor only**: it never sets the outcome, but a floor that spans both a material loss and a material gain is the volume-limit case (Step 3), stated as a limitation, not a finding. **On a sample** (a sampled report, a panel, a survey): the noise floor and the trend gate decide together; an interval excluding zero reads SUPPORTED only when both trend-gate bars also clear, otherwise UNTESTED, with the noise-floor result stated alongside. Days are autocorrelated and seasonal and the same users sit in both periods, which is why the binomial interval cannot carry the read in either case | Reading its p-value as evidence that an intervention worked; letting the noise floor set the outcome of a full-population read |
| The same units measured twice (same users or accounts in both periods) | A paired comparison — McNemar for a binary outcome, a paired difference for a continuous one — when unit-level rows are supplied | Treating the two periods as independent samples; it overstates precision |
| Assignment by cluster (geo test, store-level or campaign-level rollout) | Analysis at the cluster level (one observation per geo), or cluster-robust intervals | Counting users as n — the effective sample is the number of clusters |
| Continuous metrics (AOV, revenue per user) | Difference in means with a Welch interval; for heavy-tailed revenue, a bootstrap interval, or the median reported alongside | A proportion test |
| Many comparisons at once (every channel × every metric, every segment) | Exploratory by default. Before calling any single result supported, correct for the m comparisons scanned: Holm-adjusted p-values for the test, and intervals at the Bonferroni level (1 − 0.05/m) for the Step 3 read. Otherwise say how many comparisons were scanned | Reporting the one that crossed 95% as a finding |
| Correlation between two series | n, the coefficient, and its interval. For time series, a shared trend or seasonality inflates R and invalidates the usual interval: correlate the differenced (or deseasonalized) series, or state that the interval is not valid | R alone |

If the data is aggregated so the structure a test needs can't be determined — no unit-level rows, unknown overlap between groups — say so and treat the result as UNTESTED rather than assuming independence. (A full-population before/after read needs no independence assumption: it is NOT APPLICABLE, above.)

**Mix effects, rate effects and contributions take the outcome of the change they split.** `decompose` and `drivers` are exact arithmetic splits, not estimates (`kpi-framework.md` §8, §Contribution analysis above): on full-population data each effect is NOT APPLICABLE, like the change itself; on a sample it inherits the sample's outcome. Neither gets a test of its own, and a segment's own rate change is read under the row that fits it. In `stats classify`, a full-population read is `--not-applicable`; `--structure single-series` is for a sampled series.

**Step 2 — report these together, never a p-value alone:** the absolute difference (percentage points, for a rate), the relative change, the interval on the difference, and n per group. "CVR 2.0% → 2.4% (16/800 → 20/820: +0.44pp, +22% relative), 95% CI −1.1pp to +1.9pp." (A worked illustration for two independent groups, as `stats prop-diff 16 800 20 820` computes it: difference +0.439pp, interval −1.054pp to +1.946pp. The interval is Newcombe's hybrid score method, the difference of two Wilson intervals — Newcombe, "Interval estimation for the difference between independent proportions: comparison of eleven methods," *Statistics in Medicine* 17(8), 1998, pp. 873–890, method 10. With no compute tool the same case is reported UNTESTED, without an interval.) Where a decision hangs on the result, add what this sample could have detected — the minimum detectable effect at this n, or the n needed for the effect that would matter.

**Step 3 — read the interval against what would matter.** "What would matter" is the user's stated target or threshold if they gave one; otherwise state the yardstick used (the metric's break-even, or its ordinary period-to-period variation). The interval is the 95% interval, or the corrected level when several comparisons were scanned (Step 1). This gives question 2 its sampled outcomes (NOT APPLICABLE, the fifth, has no sampling question at all: a total, or a full-population before/after read, Step 1):

- **SUPPORTED** — the interval excludes zero *and* reaches an effect that would matter.
- **NEGLIGIBLE** — the interval is tight and excludes any effect that would matter, whether or not it also excludes zero (a tight interval entirely between zero and the material threshold is NEGLIGIBLE, not SUPPORTED). This, and only this, supports "no meaningful change."
- **INCONCLUSIVE** — the interval includes zero *and* effects that would matter. Report it as inconclusive, with the interval. **"Not statistically significant" is never written as "no effect" or "no change."** **Volume-limit case:** when the interval spans both a material loss and a material gain (the example above: the data cannot tell a 1.1pp drop from a 1.9pp gain), it is not a finding; state it once as a limitation ("too little volume to read CVR for this segment") rather than as a movement.
- **UNTESTED** — a test the structure calls for could not run or read: no compute tool, no valid test for the structure, "SRM not checked" (below), or a sampled single-series read that didn't clear the trend gate (Step 1).

**No compute tool:** name the test the structure calls for, give the raw counts and the point difference, mark the result UNTESTED and directional (Operating Principle 11). Don't eyeball significance in either direction.

**Sample ratio mismatch — check the split before reading any A/B test, holdout or lift result.** Compare the observed assignment counts per arm (assigned units — users, devices, accounts — not conversions) against the intended split with a chi-square goodness-of-fit test (degrees of freedom = arms − 1). A sample ratio mismatch (SRM) is a symptom that assignment, execution, log processing or analysis filtering went wrong, and in most cases it invalidates the result outright — a bad change can read as a winner (Fabijan, Gupchup, Gupta, Omhover, Qin, Vermeer & Dmitriev, "Diagnosing Sample Ratio Mismatch in Online Controlled Experiments: A Taxonomy and Rules of Thumb for Practitioners," *KDD 2019*, pp. 2156–2164, doi:10.1145/3292500.3330722; they report roughly 6% of one large experimentation program's experiments showing an SRM). Their example: 821,588 vs. 815,482 users on an intended 50/50 split is only 50.2/49.8, yet χ² ≈ 22.8, p ≈ 2×10⁻⁶.
- **Threshold:** flag an SRM at p < 0.001. The cited paper fixes no threshold; this is a conservative working convention, unverified, directional only — state the p-value either way.
- **Mismatch found** → BLOCKER for that result (`data-quality-gate.md` severity table): the effect, its interval and its evidence tier are not read or reported. Report the SRM in the data-quality section with the intended split, the observed counts and the p-value, and name where to look (assignment, telemetry loss, bot or other filtering, triggering conditions). The rest of the analysis continues.
- **Intended split not stated or not inferable, or no per-arm assignment counts** → the check can't run. Ask for the split in step 6's batched list when a headline depends on the result; meanwhile the result is reported with "SRM not checked — <reason>" and is UNTESTED (MEDIUM at most). With no compute tool the check is "not run — no code execution," same consequence (Operating Principle 11).

**Holdout and lift results** follow the same rules (`kpi-framework.md` §6): a small control group gives a wide interval, which is INCONCLUSIVE, not "no lift."

This skill reads results; it does not design experiments. When a decision needs a properly powered test, say so and hand the design to a dedicated experimentation skill or tool if one is available.

## Data conflict resolution

When two files disagree on the same KPI (e.g. Adjust 100K installs vs GA4 87K new users), **run the seven-point comparability checklist in `comparability-rules.md` §1 before concluding anything.** If the comparison classifies NOT_COMPARABLE, report the conflict using its refusal template (§4 of that file); NORMALIZABLE and CONDITIONAL are reported with their conversion or caveat, not refused (`SKILL.md` non-negotiable rule 3). Either way, do not arbitrarily choose a side, and do not call either value "wrong" without evidence.

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

## Not recommended yet — the actions the evidence doesn't support

A user who asks "which channel is working" or "should we cut X" is usually about to act. When the evidence doesn't support the action they are most likely to take, say so explicitly rather than only omitting it from the recommendations — silence reads as approval. Add a short **Not recommended yet** list to an analysis answer, a dashboard or a deck (placement: `dashboard-blueprints.md` Output mode 1 item 3 and Output mode 2 step 8; `presentation-blueprints.md` §Recommended Actions slide).

- **Not in a pure reconciliation.** A Template J answer ("these numbers don't match", `SKILL.md` step 6 branch B) says which figure is valid for what; it gets this list only when the user also asked what to do.
- **Which actions:** only ones the user named or plainly implied, or the obvious next move from a finding they asked about — e.g. shifting budget to the channel with the highest platform-attributed ROAS, cutting a channel on one period's numbers, scaling a test winner. Up to 3. Not a list of generic cautions.
- **Each item, one or two lines:** the action · why the data doesn't support it yet, naming the gate it failed in this skill's own labels (NOT_COMPARABLE across platforms, E2 at most — attributed, not incremental, INCONCLUSIVE interval, provisional period, immature cohort, SRM BLOCKER, single-period move that hasn't cleared the trend gate) · the evidence that would support it (the experiment, the re-pull date, the cohort age, the missing file).
- **It reuses existing machinery, it doesn't add a label.** Items carry no priority label and are not findings; the "why" is the insufficient-evidence statement (`SKILL.md` principle 2) applied to an action instead of a number — the action-side counterpart of the deck's Analytical State slide (`presentation-blueprints.md` §Analytical State). An action that clears the evidence bar belongs in Recommended actions instead; an action no one is likely to take doesn't belong in either.

```
Not recommended yet
- Move budget from Google Ads to Meta on Meta's higher ROAS — the two ROAS figures are NOT_COMPARABLE
  (different attribution windows) and both are attributed, not incremental (E2).
  Would need: a geo holdout or conversion-lift test on the budget shift.
- Cut the Display campaign after this month's CPA jump — one period, last 12 days provisional.
  Would need: a re-pull after the attribution window closes and the trend gate cleared.
```
