# Web Search Guide for KPI Relationships

This guide is for searching **relationships between KPIs**, not **KPI definitions**.
Definitions already come from vendor documentation (`research/raw/`). This guide covers a different kind of information:

> "If CPI is falling while retention is also falling, what does that mean?" — that is not a **definition**, it is a **causal claim**.

Most of what the web says on this is unevidenced blog content. The single goal of the search strategy is to **separate sources that produced evidence from sources that did not.**

---

## 1. Why a separate strategy is needed

| Information type | Right source | Wrong source |
|---|---|---|
| "How is CTOR calculated?" | Vendor documentation | Agency blog |
| "What is the average open rate?" | Vendor benchmark report (with a stated methodology) | "2026 email benchmarks" listicles |
| **"Open rate is up but conversion is down — why?"** | **Experiment/incrementality studies, MMM literature, academic marketing research** | **Everyone else, especially SEO-driven "10 reasons why" content** |

The third row is the scope of this guide. A relationship claim is only worth recording if it is backed by one of:
1. **A randomized experiment** (A/B, holdout, geo-lift, PSA test)
2. **Modeling** (MMM, causal inference, difference-in-differences)
3. **Large-N observational data with a stated methodology** (e.g. "12,000 campaigns, normalized as follows")

If none applies, the claim is recorded with a **HYPOTHESIS** label, not as FACT.

---

## 2. Source tiers

**Tier 1 — Sources that ran experiments (most valuable)**
- Platforms' own science teams: Meta Research, Google Research / Think with Google *measurement* articles, Microsoft ExP (experimentation platform team), Netflix/Airbnb/Booking tech blogs (experiment design)
- Marketing science: Marketing Science Institute (MSI), Journal of Marketing / Journal of Marketing Research, SSRN marketing papers
- Meta-analyses: Ehrenberg-Bass Institute (Byron Sharp), Analytic Partners, Nielsen/Kantar measurement studies
- Well-known incrementality studies: eBay's search-advertising experiment (Blake, Nosko, Tadelis), the "Ghost Ads" paper (Johnson, Lewis, Nubbemeyer), Lewis & Rao "The Unfavorable Economics of Measuring the Returns to Advertising"

**Tier 2 — Stated methodology, large data holders**
- Product-analytics benchmark reports
- MMP and app-intelligence industry reports
- SaaS benchmark publications from investors and research firms
- ESP/CRM benchmark reports (only those with a methodology section)

**Tier 3 — Experienced practitioners: weak evidence, useful signal**
- Practitioner newsletters and essays
- Use these as a source of hypotheses, not as a source of evidence.

**Tier 4 — Do not use**
- "Ultimate guide to X metrics" SEO content
- Benchmark lists with no methodology
- "Why your CAC is high" articles written to sell the author's own product

---

## 3. Search patterns

### A. Causality / incrementality
```
"incrementality" AND "holdout" [channel name] site:research.facebook.com
ghost ads experiment advertising effectiveness filetype:pdf
"geo experiment" measurement methodology site:research.google
"incremental ROAS" methodology holdout study
advertising effectiveness randomized experiment site:ssrn.com
```

### B. The relationship between two metrics
Pattern: `[metric A] "correlation" OR "relationship" [metric B] + an evidence keyword`
```
"retention" "correlation" "acquisition channel" cohort study
CPI retention quality paid user acquisition study site:adjust.com
"email frequency" "unsubscribe rate" experiment diminishing returns
"open rate" "conversion" correlation weak signal Apple MPP
LTV CAC ratio benchmark methodology "how we calculated"
```

### C. The origin of a "rule" (important)
Many numbers circulating in the industry have no clear owner. Do not use one before its source is found.
```
"3x" "LTV to CAC" origin who said forEntrepreneurs
"rule of 40" original source Brad Feld
"0.3%" spam complaint rate site:support.google.com
"50 conversions" learning phase site:facebook.com/business/help
```

### D. Operators that narrow the source type
```
site:support.google.com          → official GA4/Ads definition
site:braze.com/docs              → ESP metric definition
site:help.adjust.com             → MMP definition
site:developer.apple.com         → SKAN / MPP specifics
filetype:pdf "methodology"       → an actual study, not a blog
site:ssrn.com OR site:nber.org   → academic
site:github.com [metric] SQL     → the metric written as code
after:2024                       → post-GA4/SKAN/MPP context
```

### E. Turkey / MENA context
```
Insider "conversion rate" metric definition site:useinsider.com
D·engage metric documentation
Turkey e-commerce conversion rate benchmark [year] methodology
```

---

## 4. Four filters to apply to every candidate source

1. **Is there a methodology section?** If not, downgrade to Tier 3.
2. **What is N?** "We saw this in our customers" is not "40,000 campaigns".
3. **Is it dated after GA4 / iOS 14.5 / Apple MPP?** Pre-2021 attribution and open-rate content is largely obsolete.
4. **Who wrote it, and what do they sell?** If a vendor is promoting its own metric, discount the claim but still take the definition.

---

## 5. Recording format

Record each source in this format before it is added under `research/raw/`:

```
SOURCE: <url>
WHO: <organization/author> — <what they sell / any conflict of interest>
DATE: <publication date>
CLAIM: <one sentence: which KPI affects which KPI, and how>
EVIDENCE TYPE: experiment / model / observational / none
N: <sample size>
NOTE: <any doubts>
```

A bare URL is acceptable when the other fields are not yet known, but the "who wrote it, what do they sell" fields speed up evaluation.

---

## 6. Priority list — first-round relationships

The eight relationships that most often change decisions and are most often misunderstood:

1. Done — Attributed ROAS vs incremental ROAS gap (holdout evidence) — `unit-economics-metrics.md` §13, eBay / Lewis-Rao / Gordon et al.
2. Done — Falling CPI vs retention/quality (channel quality) — `causal-evidence-three-relationships.md` §1. **Result: weak evidence, no Tier 1 study — kept as HYPOTHESIS; a search-ads counter-example exists**
3. Done — The real origin of LTV:CAC thresholds and the gross-margin condition — `unit-economics-metrics.md` §3, Skok's own wording
4. Done — Cohort maturity bias — `unit-economics-metrics.md` §8, Fader & Hardie
5. Done — Rising email/push frequency vs unsubscribes and conversion per user — `causal-evidence-three-relationships.md` §2. **Result: strong Tier 1 RCT evidence (Baek et al. 2025, Chae/Bruno/Feinberg 2019)**
6. Done — The information value of open rate after Apple MPP — `crm-lifecycle-metrics.md` §6
7. Done — Brand/paid search cannibalization (eBay experiment) — `unit-economics-metrics.md` §13e, Blake/Nosko/Tadelis
8. Done — Spend increase vs marginal return (saturation / diminishing-returns curve, MMM literature) — `causal-evidence-three-relationships.md` §3. **Result: the best-evidenced relationship — Shapiro/Hitsch/Tuchman 2021 (N=288 brands), Lodish et al. 1995 (389 experiments)**

All eight are reflected in the "Outside evidence tier" column of the co-movement table in `skills/dashboard-builder/references/kpi-framework.md` §8.
