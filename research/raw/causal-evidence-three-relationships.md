# Causal/Experimental Evidence — three growth relationships

> Fills the three gaps left in `research/search-playbook.md`'s priority list (items 2, 5, 8). Tier system: Tier 1 = experiment/peer-reviewed/platform research team. Tier 2 = large-N with disclosed methodology. Tier 3 = experienced practitioner (hypothesis source only). Tier 4 = SEO listicle — never used.

---

## Relationship 1: CPI ↓ → Retention ↓ (acquisition-quality problem)

**This is the weakest-evidenced of the three relationships — flagged explicitly rather than papered over.**

**Tier 1 — indirect (a fraud mechanism, not a direct CPI/retention regression).** Bing et al., "Understanding Incentivized Mobile App Installs on Google Play Store," ACM IMC 2020 (dl.acm.org/doi/10.1145/3419394.3423662, arxiv.org/abs/2010.01497). First systematic study of Android incentivized-install campaigns: they "artificially inflate" DAU, session length, and revenue metrics. **Gap:** the abstract gives no quantitative retention comparison between incentivized and organic users; full text was paywalled. This proves incentivized-install traffic is manufactured — **not** a general CPI-level → retention dose-response curve.

**Tier 2 — a direct counter-case.** Liftoff performance index (via search synthesis, raw report not independently fetched — methodology unverified): Apple Search Ads has the **lowest average iOS CPI (~$2.96)** among major channels and shows **38% stronger Day-30 retention than the iOS network average.** The cheapest channel is also the highest-retention one. AppsFlyer/Adjust aggregate D1/7/30 retention benchmarks (26%/11%/5.4% cross-category) exist but a channel-level CPI-vs-retention cross-tab with disclosed N could not be confirmed.

**What the evidence actually shows vs. what practitioners claim:** practitioners routinely assert "cheap CPI = junk users" as a blanket rule. The one mechanism with real evidence (incentivized/click-farm installs) is a **specific fraud/incentive-design problem, not a general property of low CPI.** The Apple Search Ads case shows low CPI and high retention coexisting when the channel captures high-intent search behavior — **CPI is a function of targeting mechanism, not spend level per se.**

**Verdict: no Tier 1 study directly regresses CPI on retention across channels.** State the relationship as HYPOTHESIS with a named counter-case, never as FACT.

---

## Relationship 2: Send frequency ↑ → diminishing conversion returns (not just unsubscribe)

**Strong Tier 1 evidence — a genuine RCT.**

**Baek, Chen, Ma, Mitrofanov, "Balancing Customer Engagement and Annoyance in Online Retail: Insights from a Field Experiment," 2025** (columbia.edu/~wm2428/papers/customer_engagement.pdf, full text read). Design: randomized daily vs every-other-day email for one week at a major North American e-commerce retailer, plus historical panel data for long-run effects.

**Verbatim:** "sending fewer emails significantly reduces unsubscription (proxy for churn) by **59%** and thus increases future customer survival, **but at the cost of a 5-8% decrease in short-term revenue and purchase rate.**"

**The actual diminishing-returns/CLV curve:** a myopic revenue-maximizing frequency policy raises CLV by **6.8%** over a daily-email baseline; a full CLV-optimal policy (accounting for churn) raises CLV by **8.3%.** Under a coupon-budget constraint, the gain shrinks to **+4.5%.** Unsubscribing itself carries a **36% decrease in customer spending** in the historical data.

**Explicit author caveat:** effects are heterogeneous — frequency reduction helps retention most among newer/low-coupon-usage customers, but **reduces short-run spend most among high-volume customers**, so there is no single universal optimal frequency; it is segment-dependent.

**Tier 1 — related, not email-specific.** Chae, Bruno, Feinberg, "Wearout or Weariness? Measuring Potential Negative Consequences of Online Ad Volume and Placement on Website Visits," *Journal of Marketing Research*, 2019 (journals.sagepub.com/doi/10.1177/0022243718820587). N = 12,000+ users across 400+ websites, hierarchical Bayesian mixture model. **~24% of users show true "weariness" — a negative marginal effect from additional exposures, not just diminishing returns.** Optimal frequency-capping improved deployment efficacy by up to 15%. Caveat: measures website visits, not direct purchase conversion; sensitive to correctly modeling response-heterogeneity.

**Tier 2 — ESP data, correlational, vendor states the limitation itself.** Braze, "Send Frequency 2021" (braze.com, based on "more than a trillion messages" sent in 2020, by industry vertical). Productivity apps at 8.2 msgs/month underperform; 1-2 msgs/month shows **6.5x engagement and 4.8x conversion lift.** Financial planning: >7 msgs/month shows "significantly lower" engagement/conversion. Insurance: 2-5 msgs/month shows 2.5x engagement, +75% conversion vs higher-frequency senders. **Braze's own caveat:** "we offer these analyses as a starting point for your brand's own frequency testing... rather than as a one-size-fits-all optimal benchmark" — correlational across brands, not controlled, and the vendor says so.

**Is there a documented point of diminishing returns?** Yes — Baek et al. is the standout: the marginal revenue from added frequency turns negative in **present-value/CLV terms** well before it turns negative in raw next-day revenue terms. No universal "N sends/week" threshold exists in Tier 1 sources; Braze gives vertical-specific numbers without experimental rigor.

---

## Relationship 3: Ad spend ↑ → diminishing marginal returns (saturation curve)

**Best-evidenced of the three relationships — multiple Tier 1 sources, including RCT-based ones.**

**Shapiro, Hitsch, Tuchman, "TV Advertising Effectiveness and Profitability: Generalizable Results From 288 Brands," *Econometrica* 89(4), 2021** (econometricsociety.org, SSRN 3273476 — paywalled, confirmed via Kellogg faculty summary + secondary confirmations). Large-N structural/causal estimation across 288 brands' TV ad elasticities. **"negative ROIs at the margin for more than 80% of brands, implying over-investment in advertising"; overall advertising ROI is positive for only one-third of all brands.** Elasticities are "substantially smaller" than prior literature, many statistically insignificant or negative. **Stronger than a generic saturation claim — most firms are already past the point of positive marginal return, not just approaching diminishing returns.**

**Lodish, Abraham, Kalmenson, Livelsberger, Lubetkin, Richardson, Stevens, "How T.V. Advertising Works: A Meta-Analysis of 389 Real World Split Cable T.V. Advertising Experiments," *Journal of Marketing Research*, 1995** (journals.sagepub.com/doi/10.1177/002224379503200201). 389 genuinely randomized BehaviorScan split-cable household experiments (1982–1988). **Average advertising elasticity of only 0.05 for established products**; increasing spend relative to competitors "does not increase sales in general"; competitive interference further dilutes the focal brand's elasticity. **New-product advertising is markedly more effective than advertising for established products** — an important segmentation caveat.

**Google Meridian's own documentation** (developers.google.com/meridian/docs/advanced-modeling/media-saturation-lagging, full text read). States explicitly: "as spending on a given media channel within any given time period increases, you eventually see diminishing marginal returns, for example, saturation," modeled via the three-parameter **Hill function** `Hill(x;ec,slope) = 1/(1+(x/ec)^-slope)`. **Google's own caveat:** "the model's estimation of the Hill function parameters is based on the observed range of media data... results based on extrapolation should be interpreted with an appropriate level of caution" — **Google itself flags that saturation-point estimates are unreliable outside the historically observed spend range.**

**Simon & Arndt, "The Shape of the Advertising Response Function," *Journal of Advertising Research* 20(4), 1980** — the classic paper. Concluded the response function is generally **concave** (diminishing returns), not S-shaped.

**Important qualification — a direct peer-reviewed challenge.** Vakratsas, Feinberg, Bass, Kalyanaram, "The Shape of Advertising Response Functions Revisited: A Model of Dynamic Probabilistic Thresholds," *Marketing Science* 23(1), 2004 (full text read, webuser.bus.umich.edu PDF). Using econometric models on SUV and minivan sales, they find **threshold effects do exist and response is "not necessarily globally concave."** But critically, in the one **mature, frequently-purchased nondurable category they tested (liquid detergent), no threshold effects were found** — the classic concave/diminishing-returns shape held there. **The shape of the curve depends on category maturity and dynamics** (durables with active competitive entry vs mature nondurables) — not a universal S-curve or universal concave curve.

**What the evidence actually shows vs. what practitioners claim:** practitioners typically wave at "the S-curve" or "Hill saturation curve" as an established universal law. The academic record is more contested: Simon & Arndt (1980) argued concave/diminishing returns; Vakratsas et al. (2004) show it's category-and-dynamics-dependent; Shapiro et al. (2021) — the most rigorous, largest, most recent Tier 1 study — found the practical reality for most brands is **worse than "diminishing returns": most firms are already spending past the point of positive marginal ROI.**

**Counter-evidence/exceptions:** new-product advertising (Lodish et al. 1995) and evolving/durable categories with active competitive entry (Vakratsas et al. 2004) show different, sometimes non-concave dynamics. **The diminishing-returns story is strongest for mature, frequently-purchased categories, weaker/absent elsewhere.**

---

## Summary table

| Relationship | Best tier found | Key number | Gap flagged |
|---|---|---|---|
| 1. CPI↓ → retention↓ | Tier 1 (fraud mechanism only) + Tier 2 (counter-case) | Apple Search Ads: 38% higher D30 retention *despite* lowest CPI | **No Tier 1 study directly regresses CPI on retention across channels — state as HYPOTHESIS, never FACT** |
| 2. Send frequency↑ → diminishing conversion returns | **Tier 1 (RCT)** | CLV +8.3% at reduced frequency vs daily baseline; ~24% of users show true negative marginal returns (JMR 2019) | Strong evidence — no major gap |
| 3. Ad spend↑ → saturation | **Tier 1 (multiple, incl. RCT-based)** | 80%+ of brands already have negative marginal ROI (Econometrica 2021, N=288 brands) | Strong evidence — no major gap; **shape is category-dependent, not universal** |

## Sources fetched and read directly
dl.acm.org/doi/10.1145/3419394.3423662 · arxiv.org/abs/2010.01497 · columbia.edu/~wm2428/papers/customer_engagement.pdf (full text) · journals.sagepub.com/doi/abs/10.1177/0022243718820587 · braze.com send-frequency-2021 (full text) · developers.google.com/meridian saturation docs (full text) · webuser.bus.umich.edu Vakratsas et al. 2004 PDF (full text) · Kellogg faculty summary of Shapiro/Hitsch/Tuchman 2021 · journals.sagepub.com/doi/10.1177/002224379503200201 (Lodish et al. 1995)

**Not independently verified full-text (paywalled/403, relied on abstract or secondary summary):** Shapiro/Hitsch/Tuchman 2021 full text; the incentivized-installs IMC 2020 full-text PDF.
