Both are built from one analysis:

- **Dashboard:** `channel-performance-dashboard-2026-10.html` (self-contained HTML, opens offline)
- **Deck:** `channel-performance-review-2026-10.pptx` (9 slides: cover, summary, two finding slides, actions, a 3-slide calculation appendix, methodology)

**Short answer:** conversion rate fell from 2.84% to 2.65% between August and October. About half of that is a change in channel mix: Paid social's share of traffic grew, and it is your lowest-converting channel. The rest is Paid search converting worse at flat spend. Your first focus should be Paid search. Before putting more budget into Paid social, test whether its extra orders are really incremental.

## What I received

| File | Source | Covered period | Grain | Rows |
|---|---|---|---|---|
| channel_daily.csv | Unidentified: a generic daily channel sheet with no platform-specific fields | 2026-08-01 to 2026-10-31, all 92 days present [2] | date × channel (4 channels) | 368 [1] |

- **Comparison:** October against August. Both months have 31 days. September appears only in the weekly charts. You didn't give a target, so every direction is judged against August.
- **Not stated in the file:** the export date, the reporting lag, the timezone, the currency, and the attribution rule that assigns orders and revenue to a channel. Because of the last one, every comparison below is CONDITIONAL (each figure is valid on its own, but we can't confirm they're measured the same way), not DIRECT. Money figures carry no currency symbol, because the source doesn't specify one.
- **How I read the columns:** `sessions` and `orders` are taken as labeled (INFERRED). `spend` is read as media spend (INFERRED; whether fees are included isn't stated). `revenue` is AMBIGUOUS: it could be gross or net, and tax and shipping aren't stated. I read it as order value credited to the channel.
- **Data quality:** the structure is clean. Each date × channel pair appears once, there are no totals rows, duplicates or nulls, dates are ISO and decimals use dots. One **WARNING**: the attribution rule above is unstated. **INFO:** the anomaly scan flagged 15 single-day scores [3]–[17]. All are one-day moves of 5–21% against thin same-weekday baselines, with no two days in a row. None of them drives a finding. **INFO:** August has 10 weekend days and October has 9; I did not adjust for this.

## Findings

1. **HIGH · Neutral: about half of the decline is channel mix, not worse conversion.**
   - The blended conversion rate fell −0.18pp [32] (Derived (dbcalc)).
   - Splitting that change into mix and rate effects (Kitagawa method): mix accounts for −0.086pp [21], which is 47% [177] of the change.
   - Paid social's share of sessions went from 26.0% to 31.4% [114][115]. Its own conversion rate held, at 1.60% → 1.62% (noise floor −0.05 to +0.09pp [49][50]). Because it converts well below the other channels, a bigger share pulls the blend down.
   - Paid social took 98% [27] of the spend increase.
   - Why HIGH: the business impact is sized. It is not CRITICAL because I can't rule out a tagging or channel-classification change for Paid social from this file. Measurement confidence is Medium, because the comparisons are CONDITIONAL.
2. **HIGH · Unfavorable: Paid search lost orders at flat spend.**
   - Orders fell by 687 [157] (−7.7%), and revenue fell −8.0% [145], while spend moved +0.9% [146].
   - Its conversion rate fell from 3.41% to 3.10% (−0.31pp [40]; noise floor −0.41 to −0.21pp [41][42]).
   - Its rate effect, −0.100pp [172], is 54% [178] of the blended decline.
   - The rate change is UNTESTED as a trend. It is one series with no prior-year data, so I can't check it against seasonality.
   - Other explanations are still open: seasonality, a shift between campaigns or landing pages (the file has no campaign column), a tracking change, a price change, and overlap with Paid social.
   - Recovering 0.25 to 0.50 of the gap back to August's rate is worth 206–412 orders a month [180][182], or 12.7K–25.4K in revenue [181][183]. That is revenue, not profit, because no margin was supplied. Measurement confidence for this sizing is Low, because the rate gap it rests on is UNTESTED.
3. **MEDIUM · Neutral: Paid search's two step-downs fell in the same weeks Paid social spend stepped up** (the weeks of 2026-08-30 and 2026-10-04; see the dashboard's weekly charts).
   - Total orders rose 555 [22], but Paid social was credited with 1,117 [159] more.
   - This timing is a correlation only (E2). It fits audience overlap, or credit shifting from one channel to the other, and it also fits coincidence.
4. **LOW · Neutral: Organic search held** (2.80% → 2.80%; noise floor −0.10 to +0.09pp [65][66]). **Email has too little volume to read** (4.12% → 4.11%; noise floor −0.20 to +0.17pp [57][58]).

## Where to focus

1. **(HIGH) Find where Paid search's drop sits.**
   - Break Paid search down by campaign, keyword theme, landing page and device, comparing August with October.
   - Check change logs for the weeks of 2026-08-30 and 2026-10-04.
   - Validation: once fixed, weekly conversion rate should hold near August's level for three or more weeks. Last year's August–October export would rule seasonality in or out.
2. **(HIGH) Change how conversion is reported to leadership.** Show conversion rate per channel, plus each month's split into mix and rate, instead of the blended rate alone. Otherwise, scaling a low-converting channel keeps looking like a site problem.
3. **(MEDIUM) Run a geo holdout on the Paid social increase before adding more budget.** Use Paid search orders as the guardrail. The success metric is incremental orders per unit of spend. Design the test with your experimentation tooling.

**Not recommended yet**

- **Scaling Paid social because its attributed cost per order held** (17.49 → 17.71 [128][130]). That cost is based on attributed orders, not proven incremental ones (E2). With no gross margin, there is also no break-even ROAS to judge it against. This would need the holdout above, plus your gross margin.
- **Cutting Paid social to bring the blended rate back up.** Its own conversion rate didn't fall; the blend fell because its share grew. A cut would raise the blended rate on paper and could lose orders. This would need evidence that its orders aren't incremental.
- **A site-wide conversion program.** The rate decline is confined to Paid search. This would need a decline in more than one channel.

## How the deliverables were checked

- **Dashboard:** I rendered it in headless Chrome and confirmed every chart panel draws its marks. The QA gate passed: channel figures sum to the totals, the card numbers match the charts, the detail table is sorted, ↓ arrows are coloured by each metric's good direction, and all 163 footnotes resolve to rows of the trace. It uses a system font, because Inter isn't installed here.
- **Deck:** **not visually verified**, because no PDF converter worked in this environment. The structural checks passed: shapes stay inside the slide, the two charts are native, every slide has speaker notes, colours come only from the design tokens, and there are no raw rows. Inter isn't embedded, so PowerPoint may substitute a font.
- **Trace:** `calc-trace.jsonl` (248 rows) sits next to the outputs and holds aggregates only. The rows behind the figures above are listed below.

## How each number was computed (rows used above; full trace in calc-trace.jsonl)

| # | Figure | Value | Formula | Inputs | Method |
|---|---|---|---|---|---|
| 1 | Data rows (channel_daily.csv) | 368 | count of non-blank rows below the header row | channel_daily.csv · count rows | row count [dqg-locale] |
| 2 | Covered period, date | 2026-08-01 to 2026-10-31 | min and max date present in the rows | channel_daily.csv · date · min, max | period echo [dqg-period] |
| 3 | same-weekday z-score 2026-10-21 (Paid search) | 7.119 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · spend · date = 2026-10-21 · daily sum = 1,344.42 | same-weekday [dqg-anomaly] |
| 4 | same-weekday z-score 2026-10-28 (Paid search) | 5.043 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · spend · date = 2026-10-28 · daily sum = 1,477.45 | same-weekday [dqg-anomaly] |
| 5 | rolling-sigma z-score 2026-10-20 (Paid social) | 3.106 | (log change - mean of 7 prior) / sd | channel_daily.csv · spend · date = 2026-10-20 · daily sum = 2,692.93 | rolling-sigma [dqg-anomaly] |
| 6 | rolling-sigma z-score 2026-10-31 (Paid search) | -3.038 | (log change - mean of 7 prior) / sd | channel_daily.csv · revenue · date = 2026-10-31 · daily sum = 14,167.99 | rolling-sigma [dqg-anomaly] |
| 7 | same-weekday z-score 2026-10-23 (Paid search) | 3.010 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · revenue · date = 2026-10-23 · daily sum = 18,343.66 | same-weekday [dqg-anomaly] |
| 8 | same-weekday z-score 2026-10-27 (Paid search) | -5.488 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · revenue · date = 2026-10-27 · daily sum = 15,513.86 | same-weekday [dqg-anomaly] |
| 9 | same-weekday z-score 2026-10-30 (Paid social) | 5.843 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · revenue · date = 2026-10-30 · daily sum = 9,201.54 | same-weekday [dqg-anomaly] |
| 10 | same-weekday z-score 2026-10-20 (Email) | 3.186 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · orders · date = 2026-10-20 · daily sum = 131 | same-weekday [dqg-anomaly] |
| 11 | same-weekday z-score 2026-10-31 (Email) | 3.271 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · orders · date = 2026-10-31 · daily sum = 118 | same-weekday [dqg-anomaly] |
| 12 | same-weekday z-score 2026-10-27 (Paid search) | -3.746 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · orders · date = 2026-10-27 · daily sum = 256 | same-weekday [dqg-anomaly] |
| 13 | same-weekday z-score 2026-10-30 (Paid social) | 9.487 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · orders · date = 2026-10-30 · daily sum = 166 | same-weekday [dqg-anomaly] |
| 14 | same-weekday z-score 2026-10-20 (Email) | 6.606 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · sessions · date = 2026-10-20 · daily sum = 3,097 | same-weekday [dqg-anomaly] |
| 15 | same-weekday z-score 2026-10-25 (Paid search) | 3.287 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · sessions · date = 2026-10-25 · daily sum = 7,836 | same-weekday [dqg-anomaly] |
| 16 | same-weekday z-score 2026-10-26 (Paid search) | -3.474 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · sessions · date = 2026-10-26 · daily sum = 8,282 | same-weekday [dqg-anomaly] |
| 17 | same-weekday z-score 2026-10-30 (Paid social) | 3.719 | (value - mean of 4 prior same weekdays) / sd | channel_daily.csv · sessions · date = 2026-10-30 · daily sum = 9,880 | same-weekday [dqg-anomaly] |
| 21 | Mix effect | -0.09 pp | sum_i (c1 - c0) (r0 + r1) / 2 over channel | channel_daily.csv · orders · date = 2026-08 · sum; channel_daily.csv · sessions · date = 2026-08 · sum; channel_daily.csv · orders · date = 2026-10 · sum; channel_daily.csv · sessions · date = 2026-10 · sum | Kitagawa symmetric split [kitagawa1955] |
| 22 | orders change | 555 | compare total - base total | channel_daily.csv · orders · date = 2026-08 · sum = 22,235; channel_daily.csv · orders · date = 2026-10 · sum = 22,790 | difference of totals [arithmetic] |
| 27 | Top contributor by channel: Paid social | 98.25% | value's change / total change | channel_daily.csv · spend · date = 2026-08 · sum = 99,696.62; channel_daily.csv · spend · date = 2026-10 · sum = 120,569.98 | contribution share [contribution] |
| 32 | Blended CVR Aug vs Oct: difference | -0.18 pp | x2/n2 - x1/n1 | channel_daily.csv · orders · date in 2026-08, all channels · sum = 22,235; channel_daily.csv · sessions · date in 2026-08, all channels · sum = 783,659; channel_daily.csv · orders · date in 2026-10, all channels · sum = 22,790; channel_daily.csv · sessions · date in 2026-10, all channels · sum = 858,629 | difference of proportions [arithmetic] |
| 40 | Paid search CVR Aug vs Oct: difference | -0.31 pp | x2/n2 - x1/n1 | channel_daily.csv · orders · date in 2026-08, channel = Paid search · sum = 8,912; channel_daily.csv · sessions · date in 2026-08, channel = Paid search · sum = 261,672; channel_daily.csv · orders · date in 2026-10, channel = Paid search · sum = 8,225; channel_daily.csv · sessions · date in 2026-10, channel = Paid search · sum = 265,675 | difference of proportions [arithmetic] |
| 41 | Paid search CVR Aug vs Oct: 95% CI low | -0.41 pp | Newcombe hybrid score (method 10) lower limit | channel_daily.csv · orders · date in 2026-08, channel = Paid search · sum = 8,912; channel_daily.csv · sessions · date in 2026-08, channel = Paid search · sum = 261,672; channel_daily.csv · orders · date in 2026-10, channel = Paid search · sum = 8,225; channel_daily.csv · sessions · date in 2026-10, channel = Paid search · sum = 265,675 | Newcombe interval [newcombe1998] |
| 42 | Paid search CVR Aug vs Oct: 95% CI high | -0.21 pp | Newcombe hybrid score (method 10) upper limit | channel_daily.csv · orders · date in 2026-08, channel = Paid search · sum = 8,912; channel_daily.csv · sessions · date in 2026-08, channel = Paid search · sum = 261,672; channel_daily.csv · orders · date in 2026-10, channel = Paid search · sum = 8,225; channel_daily.csv · sessions · date in 2026-10, channel = Paid search · sum = 265,675 | Newcombe interval [newcombe1998] |
| 49 | Paid social CVR Aug vs Oct: 95% CI low | -0.05 pp | Newcombe hybrid score (method 10) lower limit | channel_daily.csv · orders · date in 2026-08, channel = Paid social · sum = 3,262; channel_daily.csv · sessions · date in 2026-08, channel = Paid social · sum = 203,454; channel_daily.csv · orders · date in 2026-10, channel = Paid social · sum = 4,379; channel_daily.csv · sessions · date in 2026-10, channel = Paid social · sum = 270,019 | Newcombe interval [newcombe1998] |
| 50 | Paid social CVR Aug vs Oct: 95% CI high | +0.09 pp | Newcombe hybrid score (method 10) upper limit | channel_daily.csv · orders · date in 2026-08, channel = Paid social · sum = 3,262; channel_daily.csv · sessions · date in 2026-08, channel = Paid social · sum = 203,454; channel_daily.csv · orders · date in 2026-10, channel = Paid social · sum = 4,379; channel_daily.csv · sessions · date in 2026-10, channel = Paid social · sum = 270,019 | Newcombe interval [newcombe1998] |
| 57 | Email CVR Aug vs Oct: 95% CI low | -0.20 pp | Newcombe hybrid score (method 10) lower limit | channel_daily.csv · orders · date in 2026-08, channel = Email · sum = 3,560; channel_daily.csv · sessions · date in 2026-08, channel = Email · sum = 86,351; channel_daily.csv · orders · date in 2026-10, channel = Email · sum = 3,623; channel_daily.csv · sessions · date in 2026-10, channel = Email · sum = 88,241 | Newcombe interval [newcombe1998] |
| 58 | Email CVR Aug vs Oct: 95% CI high | +0.17 pp | Newcombe hybrid score (method 10) upper limit | channel_daily.csv · orders · date in 2026-08, channel = Email · sum = 3,560; channel_daily.csv · sessions · date in 2026-08, channel = Email · sum = 86,351; channel_daily.csv · orders · date in 2026-10, channel = Email · sum = 3,623; channel_daily.csv · sessions · date in 2026-10, channel = Email · sum = 88,241 | Newcombe interval [newcombe1998] |
| 65 | Organic search CVR Aug vs Oct: 95% CI low | -0.10 pp | Newcombe hybrid score (method 10) lower limit | channel_daily.csv · orders · date in 2026-08, channel = Organic search · sum = 6,501; channel_daily.csv · sessions · date in 2026-08, channel = Organic search · sum = 232,182; channel_daily.csv · orders · date in 2026-10, channel = Organic search · sum = 6,563; channel_daily.csv · sessions · date in 2026-10, channel = Organic search · sum = 234,694 | Newcombe interval [newcombe1998] |
| 66 | Organic search CVR Aug vs Oct: 95% CI high | +0.09 pp | Newcombe hybrid score (method 10) upper limit | channel_daily.csv · orders · date in 2026-08, channel = Organic search · sum = 6,501; channel_daily.csv · sessions · date in 2026-08, channel = Organic search · sum = 232,182; channel_daily.csv · orders · date in 2026-10, channel = Organic search · sum = 6,563; channel_daily.csv · sessions · date in 2026-10, channel = Organic search · sum = 234,694 | Newcombe interval [newcombe1998] |
| 114 | Session share, Paid social, Aug 2026 | 25.96% | channel sessions / all-channel sessions | channel_daily.csv · sessions · date in 2026-08, channel = Paid social · sum = 203,454; channel_daily.csv · sessions · date in 2026-08, all channels · sum = 783,659 | arithmetic [arithmetic] |
| 115 | Session share, Paid social, Oct 2026 | 31.45% | channel sessions / all-channel sessions | channel_daily.csv · sessions · date in 2026-10, channel = Paid social · sum = 270,019; channel_daily.csv · sessions · date in 2026-10, all channels · sum = 858,629 | arithmetic [arithmetic] |
| 128 | Cost per order, Paid social, Aug 2026 | 17.49 | sum spend / sum orders | channel_daily.csv · spend · date in 2026-08, channel = Paid social · sum = 57,062.05; channel_daily.csv · orders · date in 2026-08, channel = Paid social · sum = 3,262 | arithmetic [arithmetic] |
| 130 | Cost per order, Paid social, Oct 2026 | 17.71 | sum spend / sum orders | channel_daily.csv · spend · date in 2026-10, channel = Paid social · sum = 77,569.11; channel_daily.csv · orders · date in 2026-10, channel = Paid social · sum = 4,379 | arithmetic [arithmetic] |
| 145 | Revenue change Oct vs Aug, Paid search | -7.97% | Oct revenue / Aug revenue - 1 | channel_daily.csv · revenue · date in 2026-08, channel = Paid search · sum = 550,776.23; channel_daily.csv · revenue · date in 2026-10, channel = Paid search · sum = 506,898.46 | arithmetic [arithmetic] |
| 146 | Spend change Oct vs Aug, Paid search | 0.86% | Oct spend / Aug spend - 1 | channel_daily.csv · spend · date in 2026-08, channel = Paid search · sum = 42,634.57; channel_daily.csv · spend · date in 2026-10, channel = Paid search · sum = 43,000.87 | arithmetic [arithmetic] |
| 157 | Orders change Oct minus Aug, Paid search | -687 | Oct orders - Aug orders | channel_daily.csv · orders · date in 2026-08, channel = Paid search · sum = 8,912; channel_daily.csv · orders · date in 2026-10, channel = Paid search · sum = 8,225 | arithmetic (also reported per channel by dbcalc drivers) [arithmetic] |
| 159 | Orders change Oct minus Aug, Paid social | 1,117 | Oct orders - Aug orders | channel_daily.csv · orders · date in 2026-08, channel = Paid social · sum = 3,262; channel_daily.csv · orders · date in 2026-10, channel = Paid social · sum = 4,379 | arithmetic (also reported per channel by dbcalc drivers) [arithmetic] |
| 172 | Rate effect, Paid search (CVR Aug to Oct) | -0.10 pp | (r1 - r0)(c0 + c1)/2 | channel_daily.csv · orders · date in 2026-08 vs 2026-10, channel = Paid search · sum; channel_daily.csv · sessions · date in 2026-08 vs 2026-10, channel = Paid search · sum | Kitagawa symmetric two-factor split, segment term (from dbcalc decompose output; segment terms are not auto-traced) [kitagawa1955] |
| 177 | Mix effect as share of blended CVR change | 46.91% | mix effect / blended change | dbcalc decompose mix effect and blended change | ratio of decomposition terms [kitagawa1955] |
| 178 | Paid search rate effect as share of blended CVR change | 54.44% | Paid search rate effect / blended change | decompose segment output | ratio of decomposition terms [kitagawa1955] |
| 180 | Paid search recoverable orders per month at 0.25 recovery | 205.8 | Oct Paid search sessions x (Aug CVR - Oct CVR) x recovery factor | channel_daily.csv · sessions · date in 2026-10, channel = Paid search · sum = 265,675; CVR gap from prop-diff trace (Aug 3.406% target, Oct 3.096% baseline) = 0.003099 | funnel opportunity sizing, playbook §Funnel analysis (target = Aug rate) [arithmetic] |
| 181 | Paid search recoverable revenue per month at 0.25 recovery (revenue, not profit) | 12,685.31 | recoverable orders x Oct Paid search AOV | rows above | funnel opportunity sizing; gross margin not supplied, so value per order = AOV [arithmetic] |
| 182 | Paid search recoverable orders per month at 0.50 recovery | 411.7 | Oct Paid search sessions x (Aug CVR - Oct CVR) x recovery factor | channel_daily.csv · sessions · date in 2026-10, channel = Paid search · sum = 265,675; CVR gap from prop-diff trace (Aug 3.406% target, Oct 3.096% baseline) = 0.003099 | funnel opportunity sizing, playbook §Funnel analysis (target = Aug rate) [arithmetic] |
| 183 | Paid search recoverable revenue per month at 0.50 recovery (revenue, not profit) | 25,370.62 | recoverable orders x Oct Paid search AOV | rows above | funnel opportunity sizing; gross margin not supplied, so value per order = AOV [arithmetic] |

Methods cited: [dqg-locale] references/data-quality-gate.md §1 Structure and grain, §3 Validity (locale).; [dqg-period] references/data-quality-gate.md §2 Completeness (covered period).; [dqg-anomaly] references/data-quality-gate.md §5 Distributional (rolling-sigma scan with 7-day trend window, 14-day test window, 3 sigma; same-weekday baseline over 4 prior weekdays).; [kitagawa1955] Kitagawa, E. M. (1955). Components of a difference between two rates. Journal of the American Statistical Association, 50(272), 1168-1194.; [arithmetic] Direct arithmetic on supplied values.; [contribution] Additive contribution of each segment to a total's change (delta and share of total delta); references/analysis-playbook.md §Time-series analysis (concentration risk).; [newcombe1998] Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. Statistics in Medicine, 17(8), 873-890 (method 10, hybrid score).
