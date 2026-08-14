# Growth & Unit-Economics Metrics — raw research

> Every entry backed by a page fetched in this session. Academic PDFs were downloaded and text-extracted, so those quotes are from actual paper text. Unverifiable sources are listed at the end rather than filled in from memory.

---

## 1. Customer Acquisition Cost (CAC)

**Three competing scopes:**
- **a16z** — "the *full* cost of acquiring users, stated on a per user basis." Splits into **Blended CAC** and **Paid CAC**.
- **Andrew Chen — "Fully Loaded CAC"** — media *plus* salaries, allocated overhead, tooling.
- **SaaS Metrics Standards Board** — "fully loaded S&M expenses": variable comp, bonuses, benefits, allocated shared costs, commissions fully burdened upfront, Customer Success where allocated to acquisition, and for PLG models **delivery costs such as hosting and product infrastructure**.

```
Blended CAC = total acquisition cost / total new customers across all channels   (a16z)
Paid CAC    = total acquisition cost / new customers from paid marketing         (a16z)
CAC         = Total Marketing + Sales Expenses / # New Customers                 (Chen, naive form)

Chen's sales-cycle-adjusted form (60-day lead-to-customer cycle):
CAC = (Marketing(n-60) + ½ Sales(n-30) + ½ Sales(n)) / New Customers(n)
```

**When it breaks:**
- a16z's listed errors: "Failing to include referral fees, credits, or discounts; calculating blended instead of paid CAC."
- **Chen names the denominator error precisely:** "The mistake is only including marketing and sales expenses in the numerator for new customers, but including **all** customers (including returning customers) in the denominator."
- Chen flags genuinely unsettled inclusions and **does not resolve them** — they are business-model dependent: for freemium, whether product/eng/support costs belong if the free tier drives acquisition; for SaaS, whether Customer Success belongs; for subscription e-commerce, whether trial fulfillment belongs.
- **SMSB timing rule:** expenses must **lag** new revenue by the sales-cycle length (Q1 expense matched to Q2 new CARR for a 90-day cycle). **Mismatched periods silently corrupt the number.**

**Benchmarks stated:** None. a16z, Chen and SMSB all decline to publish CAC benchmarks.

**Sources** — a16z.com/16-startup-metrics/ · andrewchen.com/how-to-actually-calculate-cac/ · saasmetricsboard.com/cac-payback-period

---

## 2. LTV / CLV

**This is the metric with the most genuine disagreement.** Fader & Hardie have published a formal critique of the standard formula that invalidates most practitioner versions in specific settings.

### 2a. Practitioner formulas
- **a16z** — "the present value of the future **net profit** from the customer over the duration of the relationship."
- **David Skok** — "the **Gross Margin** that you would expect to make from that customer over the lifetime… Gross Margin should take into consideration any support, installation, and servicing costs."
- **Bessemer (CLTV)** — "the net present value of the recurring profit streams of a given customer **less the acquisition cost**." **Bessemer nets out CAC inside CLTV; a16z and Skok do not.**
- **Shopify** — AOV × purchase frequency × lifespan.

```
a16z (contribution-margin chain):
  Avg. life span (months) = 1 / monthly churn
  LTV = contribution margin × average lifespan

Skok:
  Customer Lifetime = 1 / Churn Rate
  LTV = Gross Profit per Account / Annual Churn Rate
  LTV = (ARPA × Gross Margin %) / Churn Rate
  With revenue expansion / negative churn:
  LTV = (a / (d − g)) × (1 − Kⁿ) / (1 − K)

Shopify:
  CLV = (AOV × Purchase Frequency) × Average Customer Lifespan
  CLV = Gross Margin Per Customer Lifespan × [Retention Rate / (1 + Discount Rate − Retention Rate)]
```

**When these break:**
- a16z's common error: "Estimating LTV as revenue or gross margin instead of net profit."
- **Skok:** "The old formula that everyone uses… ceases to work properly when you have very long customer lifetimes and negative churn. **LTV can become infinite**, which clearly doesn't reflect reality."
- **Discount rate (Skok):** standardize on ~10%; by stage, 15% for scaling private companies ($10M+ ARR, 40%+ growth), 20–25% earlier.
- **Note:** Shopify's second formula is algebraically Fader & Hardie's **Case 2** (`mr/(1+d−r)`), while a16z/Skok's `1/churn × margin` is an undiscounted approximation. **These are not the same number.**

**Sources** — a16z.com/16-startup-metrics/ · forentrepreneurs.com/ltv/ · forentrepreneurs.com/startup-killer/ · bvp.com/atlas/cloud-computing-metrics · shopify.com/blog/customer-lifetime-value

### 2b. Fader & Hardie — three competing textbook CLV formulas
```
Blattberg et al. / Steenburgh & Avery:              CLV = m(1+d)/(1+d−r)   (1)
Capon / Kotler & Keller / Lehmann & Winer:          CLV = mr/(1+d−r)       (2)
Ofek / Davis:                                       CLV = m/(1+d−r)        (3)
```
**Which is correct depends on two things (verbatim):** "i) whether we include the customer's first payment in the calculation, and ii) whether the net cashflow associated with each period is 'booked' at the beginning or the end of the period." Case 1 gives the expected LTV of an **as-yet-to-be-acquired** customer and "serves as an upper bound for how much we might be willing to spend in order to acquire a new customer."

Their comment on practice: "a large number of our colleagues around the world who are teaching customer lifetime value in Marketing courses **are unaware of the existence of these 'competing' formulas**."

**Source** — brucehardie.com/notes/024/reconciling_clv_formulas.pdf

### 2c. Fader & Hardie — five reasons the standard formula is wrong
1. **It's an expectation, not a value.** "We never know the true value of a customer until they have 'died.'" Write `E(CLV)`, not `CLV`.
2. **Truncation.** A finite `T` "is ignoring the residual value of the customer beyond that point in time… **just don't call it lifetime value. Call it what it is — the expected present value of the customer over a horizon of T+1 periods.**"
3. **Lower bound.** Starting the sum at t=1 vs t=0 is the as-yet-to-be-acquired vs just-acquired distinction. "Nearly all introductory discussions of CLV fail to make this distinction clear."
4. **Constant retention rate is an artifact of aggregation** (verbatim): "when we track a cohort of customers… we do **not** observe a constant retention rate; rather, retention rates tend to **increase** as a function of customer tenure. The relatively constant retention rates observed in company-reported summaries are in fact the result of **aggregation across different cohorts**." Fix: replace `rᵗ` with `∏rᵢ`.
5. **In noncontractual settings there is no retention rate at all.** "As we do not know how many customers we have lost in a given period, we cannot compute a retention rate. This means the above CLV formulas are **of no use in noncontractual settings**." Substituting a *repeat rate* is "completely wrong."

**The "average lifetime" trap (footnote 3), with worked numbers:** at r=0.8, d=0.1, average lifetime = 5 years. Summing 5 years gives **2.92m**; assuming all customers survive exactly 5 years gives **4.17m**; the correct `E(CLV)` is **3.67m**. The first "ignores the future cashflows from the 32.8% of customers with a longer-than-average lifetime"; the second "ignores the fact that 20% of the customers will not survive beyond the first year."

**Their bottom line, verbatim:** "**there is no 'one formula' that can be used to compute customer lifetime value.**"

**Correct general form:**
```
E(CLV) = Σ_t  E[net cash flow in period t | alive] × P(alive in period t) × discount factor
```
**Source** — brucehardie.com/notes/033/what_is_wrong_with_this_CLV_formula.pdf

### 2d. BTYD / probability models
```
E(CLV) = ∫₀^∞ E[v(t)]·S(t)·d(t) dt
E(RLV) = ∫_T^∞ E[v(t)]·S(t | t > T)·d(t − T) dt      (existing customer, standing at time T)
E(RLV) = margin × E(M | p,q,γ,mₓ,x) × DERT(δ | r,α,s,β,x,tₓ,T)     (noncontractual)
```
The general integral is "Definitional; of little use by itself. We must operationalize E[v(t)], S(t), and d(t) in a specific business setting."

**Three distinct quantities that get conflated:** expected LTV of an as-yet-to-be-acquired customer; of a just-acquired customer; expected **residual** lifetime value E(RLV) of an existing customer.

Models: Pareto/NBD (Poisson purchasing, exponential lifetime, gamma heterogeneity) and BG/NBD.

**Source** — brucehardie.com/talks/ho_cba_tut_art_09.pdf

---

## 3. LTV:CAC Ratio

**Who published the "3x": David Skok / forEntrepreneurs.** His wording: "It appears that LTV should be about 3 x CAC for a viable SaaS or other form of recurring revenue model." He is explicit it is an **observation, not a derivation**: "Most of the public companies like Salesforce.com, ConstantContact, etc., have multiples that are more like **5 x CAC**," and elsewhere "The best SaaS businesses have a LTV to CAC ratio that is higher than 3, sometimes as high as **7 or 8**." Bessemer independently states "CLTV/CAC 3x or higher."

**Caveats the sources attach:**
- **Skok's central caveat is that the ratio alone is insufficient.** He pairs it with payback: "the profitability is anemic if the time to recover CAC extends beyond 12 months." **A company can hit 3x LTV:CAC and still be uninvestable on cash grounds.**
- The LTV term must be **gross margin**, not revenue — otherwise 3x is meaningless.
- Because LTV inherits every problem in §2 (especially cohort truncation and the noncontractual case), **the ratio is only as trustworthy as the LTV estimate feeding it.**

**Sources** — forentrepreneurs.com/startup-killer/ · forentrepreneurs.com/saas-metrics-2/ · a16z.com/16-startup-metrics/ · bvp.com/atlas/10-laws-of-cloud

---

## 4. CAC Payback Period

**The gross-margin adjustment is the fault line:**
- **SMSB** — "the number of months it takes for the **gross profits** from new customer ARR to pay back the sales and marketing expenses." Margin is *inside* the definition.
- **Bessemer (10 Laws)** — "on a **gross margin adjusted** basis."
- **Bessemer (Scaling to $100M)** — looser, no margin term.
- **The SaaS CFO** — unadjusted.

```
Gross-margin-adjusted (SMSB):
  Fully Loaded S&M Expenses ÷ (New CARR × Gross Margin %) × 12 = months
Unadjusted (The SaaS CFO):
  CAC for New Customers ÷ MRR from New Customers
```
**The adjusted payback is always longer, by a factor of 1/gross margin.** An 80%-margin company's unadjusted 10-month payback is 12.5 months adjusted.

**When it breaks:** SMSB's expense-lag rule; usage-based pricing requires ramping assumptions; commission treatment vs ASC 606; and comparability — payback "is expressed in terms of months instead of as a ratio," so **it is not comparable to a CAC ratio, and an unadjusted payback is not comparable to an adjusted one.**

**Benchmarks — note the publisher contradicts itself:**

| Source | Benchmark | Caveat |
|---|---|---|
| Skok | Best SaaS recover CAC in **5–7 months**; aim for **<12 months** | "Banks and wireless phone companies ignore this rule, but they have access to tons of capital" |
| Bessemer, State of the Cloud 2023 | Good 12–18 mo / Better 6–12 mo / **Best 0–6 mo** | Series B/C enterprise software only |
| Bessemer, Scaling to $100M | SMB <12 mo, mid-market <18 mo, enterprise <24 mo; ~15 mo avg at $1–10MM ARR | Portfolio 2010–1H21, "not a random sample" |
| Bessemer, 10 Laws of Cloud | **Enterprise 24–36 mo**, SMB 6–18 mo | **Directly conflicts with Bessemer's own State of the Cloud tiers** |
| Benchmarkit 2025 (2024 data) | Median ~12 months; up 12.5% at median since 2022 | Sample sizes not consistently disclosed |

---

## 5. Retention: N-day vs unbounded vs bracket/range

**The tools genuinely disagree on naming.** This is the single most common source of non-comparable retention numbers across companies.

| Concept | Amplitude | Mixpanel | CleverTap / general | Lenny's |
|---|---|---|---|---|
| Returned **exactly on** day N | **Return On (N-Day)** | **"On" (bounded)** | **Classic retention** | **X-day (N-day)** — "the most conservative approach" |
| Returned **on or after** day N | **Return On or After (unbounded)** | **"On or After" — Mixpanel's default** | **Rolling retention** | **Unbounded (rolling)** |
| Custom multi-day windows | **Return On (Custom)** | (via time-unit selection) | **Range / bracket retention** | — |
| Other | — | **"On or Before"** (for property sums, e.g. 30-day LTV/ARPU); **Streak mode** | — | — |

```
Rolling Retention (%) = (Users whose last activity is on or after Day N ÷ Users who started on Day 0) × 100
```

**Vendor guidance differs:** Mixpanel — "'On or After' retention gives you a better sense of how long you are holding on to your users in an absolute sense" (hence the default); "'On' retention… when your product relies on users returning on every time unit." Amplitude gives no product-type guidance.

**When these break:**
- **Rolling ≥ classic always. A product can double its headline retention by switching from N-day to unbounded with no behavior change.** Any cross-company benchmark that doesn't name the definition is unusable.
- **Amplitude's two required inputs:** the **critical event** and the **usage interval** ("the time it takes for most users to take that critical action a second time," found by identifying when 80% of users repeat it). **Change either and the number changes substantially.** The denominator cohort is also a choice: Current / New / Resurrected User Retention.
- **Andrew Chen** separates two routinely conflated things: **overall retention** is cumulative ("30% overall retention in Week 3 means 30% of users who started at the beginning of Week 1 are still around"), while **week-to-week retention** is the step ("Week 2 at 40% and Week 3 at 30% means week-to-week retention is 75%").
- **Brian Balfour on benchmarks generally:** "Averages are useless. You want to benchmark against best in class"; different companies measure the same metric differently so benchmarks are "almost never apples to apples"; "Most benchmarks lack context." He frames retention as an **output**, driven by activation and other inputs.

**Benchmarks (Lenny's — the one fetched source publishing them with an explicit definition).** Definition: "the percentage of users who signed up and are still active… **six months later**."

| Category | GOOD | GREAT |
|---|---|---|
| Consumer social | ~25% | ~45% |
| Consumer transactional | ~30% | ~50% |
| Consumer SaaS | ~40% | ~70% |
| SMB/Mid-Market SaaS | ~60% | ~80% |
| Enterprise SaaS | ~70% | ~90% |

Caveat attached: lower retention can be acceptable for early-stage startups, businesses with low CAC, and non-venture-scale businesses.

**Sources** — amplitude.com/docs/analytics/charts/retention-analysis/retention-analysis-interpret · docs.mixpanel.com/docs/reports/retention · clevertap.com/blog/user-retention-guide/ · lennysnewsletter.com/p/what-is-good-retention-issue-29 · andrewchen.com/retention-is-king/ · brianbalfour.com/quick-takes/retention-benchmarks

---

## 6. Churn and the denominator problem

```
a16z:
  Monthly unit churn = lost customers / prior month total
  Gross churn = MRR lost in month / MRR at beginning of month
  Net churn   = (MRR lost − MRR from upsells) / MRR at beginning of month

ChartMogul (adjusted numerator):
  (# churned − # joined & churned − # churned & reactivated) ÷ # customers at start

Maxio (three denominators, same behavior):
  Basic:     Churn ÷ Customers₁
  Adjusted:  Churn ÷ ((Customers₁ + Customersₙ) ÷ 2)
  Granular:  Σ inactive customers per day ÷ Σ active customers per day

Paddle "Shopify method":
  churned customers ÷ average customer count across all days in the period
```

**The denominator problem, stated by the sources:**
- **Maxio:** the basic start-of-period formula "can misrepresent your company's numbers if it is experiencing a period of rapid growth."
- **Paddle demonstrates it directly:** identical underlying customer behavior across two months produces "**two completely different churn rates**." "It looks like your churn rate has gone down, but the underlying behavior has remained the same."
- **ChartMogul** notes the opposite distortion: "Rapid growth can lead to higher churn rates, especially in early-stage B2C companies."
- **Fader & Hardie's structural objection applies here too:** in noncontractual settings a churn/retention rate is **not computable at all**.

**Bessemer's three-way split:** logo churn % (customer names lost), CMRR churn % (CMRR lost), CMRR renewal %. **Maxio's warning:** logo churn is a customer count while revenue churn is "a ratio of recurring revenue lost as a percentage of **renewal candidates**" — a different denominator, **which alone makes the two non-comparable**.

**Benchmarks:** Bessemer — "top performing cloud companies benefit from annual logo churn below **7%** and CMRR churn below **5%**." Skok — "If your Net Revenue Churn is high (**above 2% per month**) it is an indicator that there is something wrong." ChartMogul median monthly customer churn: <$300k ARR 6.5%; $1–3M ARR 3.7%; >$8M ARR 3.1%; ARPA <$25 6.1%; ARPA >$500 2.2%. Paddle: SaaS average "around 5%" — **attaches no methodology note; treat with caution given their own denominator argument.**

**Negative churn (Skok):** losing 10% of customers can be only 3.4% revenue churn if the departed accounts were low-value.

---

## 7. GRR vs NRR/NDR

**The real disagreement is cohort method vs formula method**, and SMSB says the choice materially changes the number.

```
GRR — Cohort method (SMSB preferred):
  Adjusted MRR at end ÷ MRR at beginning
  where "Adjusted MRR is the lesser of the beginning MRR or the current month's MRR"
  (expansion is capped away, not netted)

GRR — Formula method:
  ((Beginning MRR − Churned MRR − Down-Sell MRR) ÷ Beginning MRR) × 100

NRR — Cohort method (SMSB preferred):
  MRR at end from the same customers ÷ MRR at beginning

NRR — "Double back" variant (usage-based pricing):
  months 13–24 revenue ÷ months 1–12 revenue
```

**Denominator rule:** SMSB is explicit the cohort is **all customers active at the beginning of the period, regardless of renewal eligibility** — this rules out the renewal-eligible-base variant some practitioners use.

**When it breaks:**
- SMSB: cohort method is "more accurate"; the formula method carries "out of cycle errors" risk. It also flags live debate over **whether usage-based overages belong in NRR at all.**
- **The beginning-of-period cohort rule is routinely violated.** Mostly Metrics names the abuse — the **"Rope-a-Dope"**: expansion dollars from customers less than 12 months old land in the numerator while those customers never appear in the denominator, inflating the result.
- **Cohort method's own blind spot (SMSB):** it "does not capture the retention performance of recently acquired customers" and is unusable for young businesses.
- GRR can never exceed 100%; NRR can.

**Benchmarks:**

| Source | Value | Sample / caveat |
|---|---|---|
| Bessemer, State of the Cloud 2023 | NRR Good 100% / Better 110% / Best 120%+; Logo retention >85% / >90% / 95%+ | Series B/C enterprise software |
| Bessemer, Scaling to $100M | Net retention 140% avg at $1–10MM ARR; 120% at $10–100MM+ | "Not a random sample"; selection bias toward successful companies |
| SaaS Capital 2025 | Median NRR 102% ($25–50K ACV); 75th pct 111%, 25th pct 97% | Private B2B SaaS >$1M ARR; "benchmarking retention against public SaaS companies is of limited usefulness" |
| SaaS Capital 2026, bootstrapped | NRR median 103% / 90th pct 117.9%; GRR median 91% / 90th pct 100% | **Bootstrapped, $3M–$20M ARR only** |
| Benchmarkit 2025 | NRR median 101%; GRR median 88% (declining from 90% over three years) | **>$100M ARR cohort is six companies**; selection bias noted |
| Lenny's (12-mo NRR) | Consumer SaaS ~55%/~80%; Bottom-up SaaS ~100%/~120%; SMB/Mid-Market ~90%/~110%; Enterprise ~110%/~130% | GOOD / GREAT |

**Unreconciled conflict:** Userpilot reports a Kyle Poyar/ChartMogul Dec-2025 analysis of 3,500 software businesses giving B2B SaaS median GRR of **63%** and AI-native median GRR of **40%** — irreconcilable with SaaS Capital's 91% and Benchmarkit's 88%. Underlying study not fetchable. **Flagged, not endorsed.**

---

## 8. Cohort maturity / truncation bias

**Two distinct biases that pull in opposite directions (Fader & Hardie).**

**Bias 1 — truncation (right-censoring) understates LTV.** Cutting at a finite `T` "is ignoring the residual value of the customer beyond that point." Prescription: call it **truncated CLV**, not lifetime value. **A 12-month cohort LTV compared against a 36-month cohort LTV is comparing two different quantities, not two different performances.**

**Bias 2 — cross-cohort aggregation masks the true retention shape.** Verbatim: "New customers (with relatively low retention rates) are being averaged-in with existing customers (with higher retention rates), thereby masking the pattern (of **increasing** retention rates over time) that we would typically see for any given cohort by itself."

**Consequence for existing customers:** residual value depends on customer age. "For a customer who has made one renewal to date, we discard r₁… **Clearly the expected residual lifetime value of a customer who has made several renewals will be greater than the expected lifetime value of an as-yet-to-be-acquired customer.**"

**a16z's cohort guidance:** define the cohort period, track 100% baseline engagement, calculate retention in subsequent periods, repeat per cohort. Desirable: stabilization after 6–12 months, newer cohorts outperforming older ones. **a16z warns against cumulative charts — they "falsely inflate performance perception" — and truncated Y-axes.**

---

## 9. ARPU / ARPPU / ARPDAU, AOV, RFM

### ARPU family — the denominator is the whole disagreement
- **a16z** — "total revenue divided by the number of users for a specific time period."
- **Amplitude (cohort-based, different)** — ARPU is "a new user cohort's cumulative total revenue as of the hour/day/week/month you're looking at, divided by the number of users in the cohort." **ARPPU "considers paying users only. A paying user is a user who has *ever* triggered a revenue event, even if their first revenue event occurs *after* the specific data point you're looking at."**
- **devtodev** — ARPU is "the average revenue per active user for the period"; ARPDAU is the daily version.

```
ARPU = Revenue / Users      ARPPU = Revenue / Paying Users      ARPDAU = Revenue / DAU
ARPU = ARPPU × Paying Share
```

**When it breaks:**
- **Amplitude's ARPPU is a lifetime-paying-user definition, not a period definition** — a user who first pays in month 6 is in the month-1 ARPPU denominator. **This is not devtodev's or the standard gaming definition, and the two will not match.**
- devtodev: "Daily ARPPU and monthly ARPPU are completely different values."
- **The pricing trap:** raising prices may increase ARPPU while decreasing paying share, reducing total revenue. Because `ARPU = ARPPU × Paying Share`, **optimizing ARPPU alone is actively dangerous.**

### AOV and purchase frequency (Shopify)
```
AOV = Total Revenue ÷ Number of Orders
Purchase Frequency = Total Orders ÷ Total Unique Customers
Average Customer Lifespan = Total Years All Customers Active ÷ Total Customers
```
**When AOV misleads:** **the mean/mode gap** — in Shopify's worked example "the mean order value is $24. But the mode… is only $15. A handful of high-value purchases pull up the average, masking the reality that most customers spend much less." And: "a higher AOV doesn't always equal higher profits."

**Benchmarks (Shopify):** global average ~$145; luxury/jewelry >$300; apparel/accessories $40–$170; beauty/personal care $15–$90.

### RFM (Fader, Hardie & Lee)
```
E(RLV) = f(R, F, M) = DERT × g(F, M)
E(RLV) = margin × E(M | p,q,γ,mₓ,x) × DERT(δ | r,α,s,β,x,tₓ,T)
```
A Pareto/NBD transaction model plus a gamma-gamma spend sub-model; RFM treated as **sufficient statistics**.

**When naive RFM breaks:** the model "reveals a number of subtle but important non-linear associations that would be missed by relying on observed data alone." They warn against the obvious shortcut — multiplying DET by observed average monetary value. **Empirically, CLV varies most on recency, then frequency, and least on monetary value — the inverse of how RFM scoring is usually weighted in practice.**

**Source** — brucehardie.com/papers/rfm_clv_2005-02-16.pdf

---

## 10. Contribution margin, gross margin, and why ROAS without margin misleads

```
Contribution Margin       = Net Sales Revenue − Variable Costs
Contribution Margin Ratio = (Net Sales Revenue − Variable Costs) / Sales Revenue
```
Variable costs: direct materials, production supplies, per-unit labor, commissions, freight, variable utilities. Fixed costs excluded.

**Gross margin benchmarks — the sources disagree, and it matters:**
- **a16z:** software should target the **80%–90% range**.
- **Bessemer (portfolio actuals):** **65–70%, middle 50% within ~60–80%.**

Aspiration vs observation. **Using a16z's 80–90% as an operating assumption inside a gross-margin-adjusted CAC payback will understate payback by ~20%.**

**Why ROAS without margin misleads:**
```
Breakeven ROAS = 1 ÷ Gross Profit Margin            (RedTrack)
Breakeven ROAS = AOV ÷ (AOV − Product Costs)        (RedTrack)
Break-even MER = 1 ÷ Contribution Margin            (Daymark)
```
RedTrack calls unadjusted ROAS **"a vanity metric"**: a 3:1 ROAS looks healthy, but **at a 25% margin you need 4:1 to break even — that campaign is losing money.** Worked values: e-commerce $80 product / 49.5% margin → 2.02; SaaS $50/mo, 70% margin → 1.43; dropshipping $60 product, 18.3% margin → 5.46.

**A real disagreement:** RedTrack anchors on **gross margin**; Daymark on **contribution margin** (which also nets fees, shipping, refunds). **Contribution margin always yields a higher, safer break-even threshold.** Triple Whale adds that BEROAS omits G&A, so **hitting break-even ROAS exactly still loses money at the company level.**

**Benchmarks:** none, correctly — break-even ROAS is derived from your own unit economics and is not benchmarkable.

---

## 11. Growth-efficiency metrics

### Burn Multiple (David Sacks)
`Burn Multiple = Net Burn / Net New ARR` — "how much is the startup burning in order to generate each incremental dollar of ARR?"

Sacks explicitly derives it in opposition to Bessemer: "I think Bessemer has the right idea but **I prefer to flip the numerator and denominator**." Bessemer's **Efficiency Score = Net New ARR ÷ Net Burn** is the reciprocal — a Bessemer 1.5x+ ("best") is a Burn Multiple of ~0.67. Bessemer cites an "ideal private profile" of "100% Revenue Growth and a 1.2X Burn multiple."

**Sacks' benchmark table is published as an image; thresholds not machine-readable — not stated here.**

### Rule of 40
**Origin:** Brad Feld's post attributes it to **"a late stage investor" at a board meeting** who described "what his firm called the 40% rule for a healthy software company." **Feld did not claim invention and did not name the firm.**

`Growth Rate (%) + Profit Margin (%) ≥ 40%`

**The profit term — sources genuinely disagree:** Feld prefers **EBITDA**; SMSB recommends **ARR Growth + Free Cash Flow Margin**; Bessemer's structurally identical **Efficiency Score = ARR growth + FCF margin of ARR** (>40% for public companies; BVP Nasdaq Emerging Cloud Index averaging ~45%).

**Caveats:** **Feld's scope limit — "for SaaS companies at scale – assume at least $50 million in revenue."** SMSB: "Ensure you disclose the model you are using to all current and potential investors" — **the lack of a standard profit definition enables metric shopping.** Bessemer: less relevant for early-stage with negative FCF.

### Rule of X (Bessemer)
`Rule of X = (Growth Rate × Multiplier) + FCF margin`, multiplier ~2x private, ~2–3x public. Rationale: "a margin increase has a linear impact on value, while a growth rate increase can have a **compounding** impact." Bessemer states "a 1% increase in growth rate has **2.3x** the positive impact on valuation multiple versus a 1% increase in FCF margin." Caveats: the multiplier "will float over time"; "cannot be used in a vacuum."

### Magic Number
**Origin:** **Rory O'Driscoll, Scale Venture Partners**, circa 2005, evaluating Omniture.

```
Scale VP's own (GAAP revenue):
  (ΔSubscription Revenue between two quarters × 4) ÷ S&M Spend (earlier quarter)
ARR variant (The SaaS CFO):
  (ARR Growth in Current Quarter × 4) ÷ S&M Spend in Prior Quarter
Bessemer CAC Ratio (gross-margin-adjusted cousin):
  Gross Profit from New Customers ÷ Customer Acquisition Costs   (1.0 = break even within one year)
```
Scale deliberately uses **GAAP revenue** because public SaaS companies don't disclose ARR.

**Thresholds disagree:** Scale VP (originator) — **"a Magic Number of 0.7x is a fairly healthy efficiency baseline"**; ≥1.0x compelling, 0.5–1.0x capital-inefficient, <0.5x "the company hasn't figured out its model." Wall Street Prep — <0.75 inefficient, >1.0 very efficient. The SaaS CFO — 0.75–1.0 time to scale.

**Note: the widely repeated 0.75 threshold does not appear in Scale VP's own pages — their stated baseline is 0.7x.**

**When it breaks (Scale VP's own criticism):** it "oversimplifies by ignoring" churn, gross margins, new sales vs upsells, and rep productivity. Scale further observes it can **disguise** inefficient scaling — companies chasing premature growth hit the headline number while efficiency "quickly degrade[s]."

### SaaS Quick Ratio
`(New MRR + Expansion MRR) ÷ (Churned MRR + Contraction MRR)` — **Mamoon Hamid**, SaaStr 2015. His benchmark: "a quick ratio of four… four or above."

**The originator's own warning:** the quick ratio becomes **"quite deceiving" at scale**, because the denominator inflates and churn percentages look artificially small. ChartMogul adds that a quick ratio of 4 can coexist with monthly churn of 5%+, so **it masks churn**; and for first-year companies whose customers are still in commitment periods it "isn't a reliable indicator of anything."

---

## 12. Payback vs ROAS vs MER

**MER — sources genuinely disagree on the *direction of the ratio*:**

| Source | Formula as written |
|---|---|
| Northbeam | `MER = Total Revenue ÷ Total Marketing/Ad Spend` |
| Shopify | `MER = total revenue ÷ total marketing spend` ($200k ÷ $50k = 4) |
| Daymark | `MER = Total Revenue / Total Marketing Spend` |
| **Triple Whale** | **`MER = Blended Ad Spend ÷ Order Revenue`** (inverted) |

**This is load-bearing.** Triple Whale reports MER as a percentage where **lower is better** (2025 median 41%); the others report a multiple where **higher is better** (4.0x). **41% and 2.44x are the same number. Any MER benchmark quoted without naming its source convention is ambiguous.**

**Break-even MER (Daymark):** `1 / Contribution Margin`. 60% margin → 1.67x; 40% → 2.50x; 25% → 4.00x.

**Note on ROAS itself:** the Google Ads help page **does not use the term "ROAS."** It defines the equivalent as **"Conversion value per cost."** The platform most often cited for ROAS doesn't use the word.

**Where MER is preferred over channel ROAS:**
- **Daymark is the most explicit:** Apple's ATT broke pixel-based attribution; "Reported ROAS stopped matching reality" as platforms moved to modeled conversions; **MER "never asks a platform to claim anything,"** depending only on your own revenue and spend totals.
- **Disagreement worth flagging:** Triple Whale's MER page **never mentions iOS 14, ATT, attribution loss, or double counting.** Their argument is scope and cost coverage, not attribution decay.

**When MER breaks:** no campaign-level actionability; it moves with anything that moves revenue (seasonality, retention, organic) — **silently crediting or blaming marketing for non-marketing effects**; "changes based on how 'spend' and 'revenue' are defined"; and **MER is not an incrementality metric.**

**Benchmarks:** Northbeam "around 5.0 or higher," caveated as varying widely. Triple Whale (spend÷revenue, lower better): 2025 median 41%; Automotive 27% … Pets 52%. Shopify: healthy 3.0–5.0x (third-party study, not independently fetched). **Daymark refuses universal benchmarks — "A good MER is any MER above your break-even MER."**

---

## 13. Incrementality: iROAS, geo lift, and why attributed ≠ incremental

### 13a. Google Ads Conversion Lift
```
Incremental conversions = Treatment conversions − Control conversions
Relative lift           = Incremental conversions / Control conversions
iCPA                    = Total ad spend / Incremental conversions
iROAS                   = Incremental conversion value / Total ad spend
```
**Google contradicts itself on the denominator:** the user-based page divides by **total ad spend**; the geo-based page states "Incremental conversion value/**Incremental Cost** = iROAS." These differ whenever baseline spend is nonzero.

**Limitations Google states:** relative lift is not comparable across studies — "studies with lower control group activity naturally produce higher percentage lifts"; modeling is used when conversions can't be linked; geo studies "typically require a higher budget"; over-targeting starves the test.

### 13b. Geo experiments — Google Research (Vaver & Koehler, 2011)
```
(1)  y_i,1 = β₀ + β₁·y_i,0 + β₂·δ_i + ε_i        weights w_i = 1/y_i,0
(2)  s_i,1 = γ₀ + γ₁·s_i,0 + μ_i                  control geos only
(3)  δ_i   = s_i,1 − (γ₀ + γ₁·s_i,0)  for i ∈ T ;  δ_i = 0 for i ∈ C
```
**β₂ is the ROAS.** β₀ and β₁ absorb pretest-to-test seasonality.

**Design conditions:** ads servable by geography; spend and response trackable at geo level; **grouping geos by size before randomization "can reduce the confidence interval of the ROAS measurement by 10%, or more"**; the test period must extend past the spend change by a lag ν.

**Known limitations:** Google's own follow-up (Kerman, Wang & Vaver 2017) notes the geo regression has limits "when few geographic units are available." Chen & Au (Annals of Applied Statistics) define iROAS as "the ratio of the strategy's causal effect on some response metric relative to its causal effect on the ad spend," and note reliable estimates are hard because "only a small number of highly heterogeneous units are used" and budget constraints "introduce interference between the experimental units." They also note Vaver & Koehler assume **"the unit-level iROAS θg are all identical"** — an assumption their analysis suggests is violated.

### 13c. Meta GeoLift (synthetic control)
"a campaign's incremental effect is the difference between what we observed… and what would have happened in a world where it didn't take place (counterfactual)." Builds "an artificial unit that is as similar as possible to the test unit" from untreated control locations. Augmented SCM + Generalized Synthetic Controls + parametric bootstrapping. **No formulas published.** Stated limitations: SCMs are "subject to biases due to inexact matching"; geo tests typically have small effect sizes with "significant chance to fail."

### 13d. Practitioner iROAS (Measured)
`iROAS = Incremental Revenue / Ad Spend` · `Lift % = (Incremental Outcome / Control Outcome) × 100`
Benchmarks: iROAS >3.0 strong; 1.5–3.0 profitable; 1.0–1.5 marginal; <1.0 unprofitable. **Their caveat:** "These thresholds vary by business model, margin structure, and LTV considerations." Design guidance: 80% power minimum (90% high-stakes), "at least 10–20 markets per group to detect a 10% lift."

### 13e. Why attributed ≠ incremental — the primary evidence

**Blake, Nosko & Tadelis (eBay, Econometrica 2015).** ROI defined as `ROI ≡ ΔR/ΔS − 1`.

**The headline result, verbatim:** OLS "result in a ROI of over **4,100%** without time and geographic controls, and a ROI of over **1,400%** with such controls. We then used our experimental methods to control for endogeneity and found a ROI of **−63%**, with a 95% confidence interval of [−124%, −3%], rejecting the hypothesis that the channel yields any short run positive returns."

- **Brand keywords:** eBay halted brand paid search on Yahoo!/MSN. **"almost all (99.5 percent) of the forgone click traffic… was immediately captured by natural search traffic."** Raw clicks fell 5.6%, but difference-in-differences against Google as a seasonality control showed "only 0.529 percent of the click traffic is lost" — a **lower bound** on retention.
- **Non-brand:** Nielsen DMA-level randomization across 210 US DMAs, ads suspended in ~30%. Result: 41% drop in paid clicks, **2% drop in total clicks**, implying "42 percent of paid search clicks are newly acquired." A 1% drop in paid search visits → 0.5% increase in natural search visits.
- **The indictment, verbatim:** "typical regressions of sales on advertising spend result in **astronomical ROI estimates that vastly overestimate the true ROI**, which can only be estimated using controlled experiments." And: "In the absence of causal measures, the industry relies on 'attribution' measures which correlate clicks and purchases. By this measure, eBay performed very well… Our findings suggest, however, that **even incremental clicks do not translate into incremental sales**."
- **Mechanism:** heavy buyers who "still use paid search clicks for 4 percent of their" purchases "would purchase anyway."

**Lewis & Rao (QJE 2015) — the measurement-cost constraint.** "Twenty-five large field experiments… collectively representing $2.8 million in digital advertising expenditure, reveal that measuring the returns to advertising is difficult. **The median confidence interval on return on investment is over 100 percentage points wide**… a coefficient of variation of 10 is common. Hence, informative advertising experiments can easily require more than **10 million person-weeks**."

- Median standard error on ROI: 26.1% (retail), 115% (brokerages). The median campaign "would have to be **nine times larger** to reliably distinguish a wildly profitable campaign (+50% ROI) from one that broke even"; distinguishing a 10% ROI difference requires it to be **62 times larger**.
- **Why observational methods cannot be rescued:** to net +25% ROI the median campaign had to raise per-person sales by $0.35 against a mean of $7 and SD of $75 — "the R² for a highly profitable campaign would be on the order of **0.0000054**." So an observational method "must not omit endogenous factors… to a degree that would generate an R² on the order of only 0.000001. **This appears to be an impossible statistical feat** in an environment where selection effects are expected to be as large as **30 times** the true treatment effect." They name difference-in-differences and propensity score matching as vulnerable. For comparison, in wage/schooling regressions endogeneity is typically 10–30% of the treatment effect.

**Gordon, Zettelmeyer, Bhargava & Chapsky (Facebook, Marketing Science 2019).** 15 US Facebook experiments, 500M user-experiment observations, 1.6B impressions. "The observational methods we analyze **mostly overestimate the RCT lift**, although in some cases, they significantly underestimate this lift. The bias can be high: **in 50% of our studies, the estimated percentage increase in purchase outcomes is off by a factor of three** across all methods." Biases "persist even after conditioning on a rich set of observables." Extreme case: Study 9 had an RCT lift of **2.4%** against a closest observational estimate of **1306%**. Nuance: observational methods "do a better job… for registration and page-view outcomes than for purchases," and no single observational method dominates.

### 13f. Holdout / PSA lift testing and its failure modes
(Johnson, Lewis & Nubbemeyer, MSI Working Paper 15-122)

- **PSA holdout** — control group served neutral/charity ads. **ITT** — differences the entire treatment group against the entire control group. **Ghost Ads** — "a log entry in the ad platform's ad serving database that flags occasions where the ad platform *would have* served an experimental ad to a user in the control group."

**Stated failure modes of PSA holdouts:**
1. **Optimization invalidates the design.** "Performance-optimized campaigns break PSA experiments: to maximize performance… the ad platform will assign different types of people to be exposed to the PSA or treatment ad… **the PSA-exposed users are no longer a valid holdout group**." They call this "central for the online display ad industry because **two thirds of dollars spent there make use of performance-optimizing technology**."
2. **Cost and coordination** — "PSAs are expensive and prone to errors."
3. **Cost distorts design.** Of Lewis & Rao's 25 experiments, "only 8 use PSAs"; in one case the control group was **"less than 2% of users,"** crippling power.
4. **ITT's weakness is precision, not validity** — unbiased but "less precise"; collapses when "the proportion of treated users can be very small (e.g., 3% or less)."
5. **Contamination via lookalikes.** "Similar audiences," look-alike and broad-match technologies "can lead to control-group users being exposed to the treatment ads."

**Ghost ads (the authors' own method — treat the improvement claim accordingly):** "can reduce the cost of experimentation, improve measurement precision **tenfold**, and work with ad platforms that optimize ad delivery in real time." Deployed on Google's Display Network recording "more than 100 million experimental ad impressions daily." Gordon et al. describe Facebook's equivalent: when a control user would have won the auction for the focal ad, "the auction's second-place ad is served to the control user."

**Geo-test tooling calibration (Recast simulation, 32,000 simulated experiments against known ground truth of 7.5% lift vs 0%):** "**Every tool forces a choice between two errors**: false positives… and false negatives." Meta GeoLift: 92–95% interval coverage, 3–5% false positives, but intervals **"contain zero in 95.7% of runs, meaning most tests come back inconclusive."** Causal Impact: highest power (52–66%) but **"fires false alarms nearly 30% of the time"** with consistent positive bias. Google Matched Markets and CausalPy in between at 76–86% coverage, 14–25% false positives. **With only 30 days of pre-period, false positives exceed 24%** for CausalPy and Causal Impact. **This is one vendor's simulation, not a neutral referee** — but it is the only head-to-head calibration test found, and it contradicts any claim that geo testing is a settled, low-error method.

**Sources** — faculty.haas.berkeley.edu/stadelis/BNT_ECMA_rev.pdf · gwern.net/doc/economics/advertising/2015-lewis.pdf · kellogg.northwestern.edu/faculty/gordon_b/files/fb_comparison.pdf · thearf-org-unified-admin.s3.amazonaws.com/MSI/2020/06/MSI_Report_15-122.pdf · research.getrecast.com/geolift-sim-study · services.google.com/fh/files/blogs/geo_experiments_final_version.pdf · arxiv.org/pdf/1908.02922

---

## Explicit conflicts found (reported as conflicts, not resolved)

1. **Retention naming.** Amplitude "Return On" = Mixpanel "On" = CleverTap "classic" = N-day. Amplitude "Return On or After" = Mixpanel "On or After" (**their default**) = rolling/unbounded. **Rolling is always ≥ classic.**
2. **CLV formula.** Three mutually inconsistent textbook formulas. Fader & Hardie: "there is no 'one formula.'"
3. **CAC payback benchmarks — Bessemer vs Bessemer.** State of the Cloud 2023 says 0–6 months is "best"; 10 Laws of Cloud says enterprise payback is 24–36 months.
4. **NRR/GRR method.** Cohort vs formula method produce different numbers.
5. **GRR benchmarks.** SaaS Capital 91% and Benchmarkit 88% vs a circulating ChartMogul/Poyar figure of 63% / 40%. Unreconciled.
6. **MER direction.** Triple Whale computes spend÷revenue; others compute revenue÷spend. **Benchmarks are not portable between conventions.**
7. **Break-even margin basis.** RedTrack uses gross margin; Daymark uses contribution margin (strictly higher, safer).
8. **iROAS denominator.** Google's user-based page divides by *total* ad spend; its geo-based page by *incremental* cost.
9. **Gross margin target.** a16z 80–90% vs Bessemer portfolio actuals 65–70%.
10. **Magic Number threshold.** The widely cited 0.75 is not in Scale VP's own pages — the originator states **0.7x**.
11. **Does CLTV include CAC?** Bessemer nets it inside; a16z and Skok do not. Fader & Hardie: if CLV is used "to estimate an upper bound for spending on customer acquisition, the −AC term should clearly be excluded."

---

## Could not verify — deliberately omitted
Reichheld & Sasser "Zero Defections" (HBR 1990) — the page serves only the abstract; the "5% defection cut raises profits 25–85%" figures appear only in third-party summaries. **Meta Business Help Center Conversion Lift pages — all `facebook.com/business/help` URLs returned 404**; Meta methodology above comes from Meta's open-source GeoLift docs and Gordon et al. Sacks' Burn Multiple benchmark table (image). Skok's `saas-metrics-2-definitions` formulas (embedded images). OpenView SaaS Benchmarks (firm wound down). KeyBanc/KBCM SaaS Survey. SaaS Capital 2023 PDF (unparseable). Eightx 2026 MER study. Bracket retention as a *named CleverTap* metric.
