# Example: channel performance, August–October

A worked example of the skill, run end to end on one file. **All data here is synthetic**, written for this example; it describes no real business.

## The prompt

> Here's our channel data for Aug–Oct. Build me a dashboard and a short deck for the leadership meeting — what's driving the conversion rate change, and where should we focus?

Input: [`input/channel_daily.csv`](input/channel_daily.csv) holds daily sessions, orders, revenue and spend for four channels. It has 368 rows and contains no margin, no target and no currency.

## What the skill produced

Both artifacts are built from one analysis (SKILL.md step 6, branch E):

| File | What it is |
|---|---|
| [`channel-performance-dashboard-2026-10.html`](channel-performance-dashboard-2026-10.html) | Self-contained HTML dashboard: Template B, Limited. Every figure is footnoted to its trace row |
| [`channel-performance-review-2026-10.pptx`](channel-performance-review-2026-10.pptx) | 9-slide deck with native charts and speaker notes |
| [`answer.md`](answer.md) | The reply that accompanied the two files |
| [`calc-trace.jsonl`](calc-trace.jsonl) | One row per computed figure, 248 in all, from `dbcalc` or hand-computed |
| [`dashboard.png`](dashboard.png) | Screenshot of the dashboard's top section |

**Headline:** conversion rate fell from 2.84% to 2.65%. About half of the decline is channel mix: Paid social's share of sessions grew while its own rate held. The rest is Paid search converting worse at flat spend.

## What to look at

- **Period echo.** The dashboard's context line, the answer's ingestion table and the deck's Methodology slide all state the covered period, 2026-08-01 to 2026-10-31. They also state what the file doesn't say: the export date, the reporting lag, the currency and the attribution rule.
- **Mix vs rate.** `dbcalc decompose` splits the −0.18pp change into −0.086pp of mix and −0.097pp of rate, and nearly all of the rate effect sits in Paid search. The dashboard shows this split as a waterfall, and the deck shows it as layout D.
- **Statistical labels.** Each before/after rate change is computed over every session in the period, so, like the period totals (orders, revenue), it is NOT APPLICABLE for a sampling test; its two-proportion interval is shown only as a noise floor. Whether a move is more than ordinary variation is a trend-gate question, and with no prior-year data seasonality stays an open alternative, which is why the Paid search finding is HIGH and not CRITICAL. (`answer.md` was written before this rule was settled and calls the rate change "UNTESTED as a trend": read that as "not tested against seasonality".)
- **Template fit.** The file has spend on its paid channels only, which is Template B's shape (≥2 channels, spend for the paid ones); the unpaid channels are read on volume and rate.
- **Trace section.** The dashboard ends with "How each number was computed", and every number on the page links to a row there. The deck carries the rows behind its own figures as an appendix before Methodology.
- **"Not recommended yet".** Three actions leadership is likely to reach for are not supported yet:
  - Scaling Paid social on its flat attributed cost per order.
  - Cutting Paid social to restore the blended rate.
  - Starting a site-wide conversion programme.

  Each one names the evidence it would need.
- **Data-quality notes.**
  - One WARNING: the rule that assigns orders to channels is not stated, so the comparisons are CONDITIONAL.
  - The revenue mapping is flagged AMBIGUOUS.
  - Money figures are printed without a symbol, because the source names no currency.
  - 15 single-day anomaly scores were triaged rather than reported as findings.

The deck was checked structurally (bounds, native charts, notes, colour tokens), not rendered, because no PDF converter was available when it was built. The dashboard was rendered and screenshotted.
