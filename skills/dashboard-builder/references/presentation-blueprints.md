# Presentation Blueprints: Executive Deck as an Output Format

A second rendering of the **same analysis** that `dashboard-blueprints.md` renders as a dashboard — not a separate analytical pass. Everything upstream of rendering (ingestion, quality gate, metric registry, comparability, the insight candidate engine) runs exactly once; this file only governs how the result becomes slides instead of (or alongside) an HTML dashboard. If a number, a classification, or an Evidence Ladder tier would differ between the dashboard and the deck for the same dataset, that's a bug — the two outputs must never drift from one shared analysis.

## Output format selection

`SKILL.md` step 6 is the canonical routing. This section says what each format is for.

- **Dashboard** — the HTML artifact per `dashboard-blueprints.md`. Better for exploration, drill-down-by-scrolling, and a reader who wants the detail table and deep-dives available.
- **Presentation** — a slide deck per this file, exported as PPTX. Better for a room, a stakeholder update, or anyone who wasn't in the room for the analysis and needs the narrative walked through in order.
- **Both** — same underlying analysis, rendered twice. Build the dashboard's full component set first (it naturally produces more granular material — the detail table, every deep-dive), then select the subset of findings that clear the deck's tighter bar (below) for the presentation.

The format is asked about only when the user wants an artifact and hasn't said which kind ("give me something I can share with the team"). A request that names it — "sunum yap," "build me a deck," "PPTX ver" — resolves directly. A request for analysis, diagnosis or reconciliation gets its answer with no format question at all.

## Deck composition — tighter than the dashboard, not just smaller

A dashboard can hold a detail table of 10+ rows and several deep-dives because a reader scans it at their own pace. A deck is read in sequence, usually presented out loud — every slide costs the reader's full attention, not a glance. The candidate-engine discipline that already governs the dashboard's 5–10 observations applies here even harder: **by default, a slide exists only for a finding that already cleared CRITICAL or HIGH on the insight candidate engine** (`analysis-playbook.md` §Insight candidate engine). MEDIUM findings fold into Recommended Actions if actionable, or get dropped by default; LOW/SUPPRESS never reach the deck, same as they never reach the dashboard's top strip.

**User override — the default above is a starting point, not a ceiling.** If the user names a specific dashboard section, KPI, or MEDIUM-level finding they want in the presentation ("dashboard'daki şu bölümü de ekle," "put the retention chart in the deck too"), include it — the candidate engine sets what ships *unprompted*, not what the user is allowed to ask for. Place the requested material in whichever layout (below) actually fits its shape, or in an **Appendix** section placed immediately before Methodology if it doesn't fit the deck's narrative flow (Methodology always stays the closing slide). Two things don't change when content is added this way: (1) a MEDIUM finding placed by request keeps its own evidence/caveat framing — it does not inherit a CRITICAL/HIGH finding's visual weight (no spotlight layout, no Key Insight slot) just because a user asked for it; (2) it still passes the same data-quality and comparability checks as everything else — a user request to include something doesn't waive the requirement that it be real, sufficient, and honestly labeled.

**Fixed slides, always present, though not always full-size:**
1. **Cover**
2. **Executive Summary**
3. **Methodology** (closing) — carries the Coverage integrity note (`dashboard-blueprints.md` §Dashboard QA gate) and any data-quality WARNINGs; a deck has no footer real estate for a running data-coverage note the way a dashboard does, so it collects here instead of being dropped. **This slide is mandatory, not conditional — but it scales.** A large, multi-finding deck gets the full definition grid + Data limitations row described below. A small, data-thin deck (few findings, short history) can compress the same content into a single dense slide (it stays its own closing, dark slide — never folded into another slide, since three other rules in this file depend on it existing as the deck's last page) — but the disclosure itself (what was set aside, what caveats apply, what wasn't sufficient) must survive in some visible form. Cutting the slide's size is fine; cutting the disclosure is not — that would contradict this skill's own non-negotiable rule 1 (disclose every gap).

**Everything else is conditional** — the variable middle and the Appendix scale with what the data supports (a 2-finding dataset is not padded to a fixed slide count), and Recommended Actions appears only when a real action exists. Both are specified below.

**Variable middle**, one slide per CRITICAL/HIGH finding that cleared the candidate engine (plus anything added via User override above), each in whichever layout (below) fits its shape — typically 3–8 slides for a real dataset. **No slide count is targeted for its own sake.** A dataset that only clears 2 CRITICAL/HIGH findings gets a 5-slide deck (Cover, Exec Summary, 2 finding slides, Methodology) — padding to hit a rounder number is the deck-format version of the KPI strip's banned floor-padding.

**Recommended Actions** — present only if at least one action exists with real evidence behind it; omitted otherwise, not padded with generic advice.

**Key Insight** — at most one per deck, not one per finding. This is the single strongest, most defensible read of the whole analysis (highest confidence × highest materiality), given the deck's own spotlight treatment (inverse background, largest type on the page). Forcing a second "Key Insight" dilutes the one that earned it — a second-strongest finding is a normal finding slide, not a second spotlight.

**A spotlight slide replaces a finding's regular slide; it is never added on top of it.** Each finding gets exactly one slide — either a content layout (A–D) or a spotlight (Key Risk / Key Opportunity / Key Insight) — so nothing is said twice and the spotlight doesn't inflate the slide count. Use a spotlight when the sentence and two or three numbers carry the finding better than a chart would; use a content layout when the chart is the evidence.

**No slide exists to fill a slot.** A metric the data doesn't have gets no slide and no placeholder. The deck is as short as its supported findings: a dataset with one supported finding yields Cover, Executive Summary, that finding, Methodology.

## Layout catalog

Six content layouts, plus four fixed-purpose skeletons defined further down (the spotlight slide, the Analytical State slide, Recommended Actions, and Methodology). A slide's content type determines its layout — never picked for visual variety.

| Layout | Use when | Anatomy |
|---|---|---|
| **Cover** | Always, slide 1 | Dark ground (`#0E1116` / `#F6F6F4` text). Eyebrow (skill name, small caps) top-left. Title (very large, 800 weight) + period subtitle, vertically centered. Bottom row: "Prepared from" + source list (left), generation date (right). Typography only — no chart, no chrome |
| **Executive Summary** | Always, slide 2 | Eyebrow. Left column: one-sentence headline stating the period's dominant finding, anchored above **up to three** numbered stat readouts (delta colored by direction) — only KPIs the data actually supports; two, one or none is correct when that is what exists, and a readout is never filled with a metric that isn't in the data. Right column: a bordered card, "Key Takeaways," 3–5 short complete sentences (the same cap the content rules set for the Executive Summary), not bullet fragments |
| **A — Big number + evidence** | One dominant KPI's trend is the finding | Headline sentence stating the trend in words. Huge number + delta + "vs previous period" inline beneath it. A single-axis trend chart below, same rules as the dashboard's trend chart (never dual-axis, one annotation only if a real cause is known — never invented). One caption sentence closing it out |
| **B — Chart + takeaway card** | Any chart genuinely needs an adjacent interpretation — funnel, cohort heatmap, scatter, quadrant, or a chart the headline alone doesn't fully explain | Headline sentence. Two-column: chart left (60%), a bordered "Key Takeaway" card right (40%) with one interpretive sentence + 1–2 supporting stat rows. This is the general-purpose layout — most chart types not covered by A, C, or D land here rather than getting a bespoke layout invented for them |
| **C — Ranked comparison** | A channel/category ranking is the finding | Headline sentence carrying the interpretation directly (not a neutral chart title — "Google Ads remained the largest revenue contributor" not "Revenue by channel"). Ranked bars below, sorted, each row showing entity name + bar + value + inline delta (colored). The finding is in the headline; the bars are the evidence for it |
| **D — Decomposition** | A KPI decomposition tree/identity is the finding (Revenue = Orders × AOV) | Eyebrow ("What drove the change"). Headline naming the dominant driver in numbers. Signed horizontal bars from a center axis (waterfall style) — one row per component, ending in a totaled "Net change" row, same construction as the dashboard's waterfall |

**Spotlight layouts** (Key Risk / Key Opportunity / Key Insight) share one skeleton, differentiated by eyebrow color and background:

| Slide | Eyebrow color | Background | Extra element |
|---|---|---|---|
| Key Risk | Danger (`#A11D1D`) | Light | "Priority: Critical" or "Priority: High" pill, top-right — the finding's own priority label, as text |
| Key Opportunity | Success (`#156143`) | Light | None — the opportunity framing itself carries the tone |

The eyebrow colors follow the direction rule, not a second scheme: a Key Risk is by definition an Unfavorable finding (danger), a Key Opportunity a Favorable one (success), a Key Insight takes the neutral info color. Priority still appears only as text.

| Key Insight | Info/lilac (`#8FA3FF`) | **Dark** (`#0E1116`) — the only content slide besides Cover/Methodology that inverts | "Measurement confidence: [level]" plus the evidence tier if the insight is causal, in the footer instead of a source line |

All three: eyebrow → huge headline (the finding, stated as a full sentence, not a chart title) → one supporting paragraph → 2–3 stat readouts in a row, each with its own small label. **No chart on a spotlight slide** — the number and the sentence carry it; a chart here would compete with the one thing the slide exists to say.

## Content & language rules — what makes a slide, not just its shape

The layout catalog above governs where things sit. This section governs what gets written into them. **Most of the underlying discipline already exists elsewhere in this skill — this section adapts it to slide-writing craft, it doesn't duplicate it.** Where a rule below is new to the presentation format specifically (headline construction, banned phrasing, number formatting), it's written in full; where it's the same discipline already stated for dashboards, it's a pointer, not a restatement.

**One slide, one message.** Before writing a slide, answer: *what should the reader take away, in one sentence?* If the honest answer names more than one thing, it's two slides. A slide competing for attention across 3 charts, 5 KPIs, and 2 conclusions asks the reader to do the prioritization the analysis was supposed to do for them.

**The headline states the finding, not the topic.** "Revenue Performance" is a section header; "Revenue growth accelerated in Q2, led by higher order volume" is a headline. Every content slide's `<h1>` should read as a claim, not a label — construct it as *finding → evidence*, e.g. "Paid acquisition grew, but efficiency declined" rather than "Acquisition Overview." **Never use a causal verb ("driven by," "caused by," "led by" in the strong sense, "because of") in a headline unless the underlying finding actually clears E4/E5 on the Evidence Ladder** (`comparability-rules.md` §2.6) — a headline is the most-read line on the slide, and it's exactly where an unearned causal claim does the most damage. A checked E3 design earns the conditional form in body text ("under parallel pre-trends, the campaign is estimated to have added …"), with its assumption stated — not in a headline. Below that, use co-occurrence phrasing: "Revenue growth coincided with higher Google Ads spend," not "Google Ads drove revenue growth."

**Evidence, insight, and implication are three different things — don't collapse them into one label.** This is the same OBSERVATION/INTERPRETATION/INSIGHT distinction already required for dashboard captions (`dashboard-blueprints.md` §"Every chart carries a one-line caption"), applied to slide text: *"Revenue increased 18%"* is an observation; *"Growth was volume-led, not basket-value-led"* is an interpretation of two observations together; *"Sustaining growth may depend on maintaining acquisition volume"* is an implication, one step further and correspondingly more hedged. Never present the third as if it were the first.

**Every claim traces to a number already stated or shown on the slide.** If a word or figure could be deleted without the slide's meaning changing, it shouldn't be there — this is the same discipline as `SKILL.md`'s final quality check ("does every number trace to a supplied file"), applied to prose density instead of data provenance.

**Not every KPI on the slide carries equal weight, and the writing should show that.** Revenue +18% next to Sessions +34% — pick which one is the primary claim (usually the one closer to a business outcome, not the largest percentage) and state it in the headline; the rest are supporting context, visually and verbally smaller. Presenting five deltas with identical typographic weight asks the reader to do the ranking the skill's own candidate engine already did.

**Not every slide ends in a recommended action.** Some slides are Situation, some are Insight, some are Risk, some are Action — appending "Recommendation: …" to every slide regardless of whether one exists is a tell, not a discipline. Action belongs on the Recommended Actions slide and on a Key Risk/Opportunity slide when the finding genuinely has one attached; a trend or diagnosis slide can close on its implication and stop there.

**Recommendations name the evidence inline, not as a separate leap.** "Review Meta campaign mix — CPA +22% while revenue grew only 9%," never a bare "Improve marketing performance" or "Focus on customer experience." Same bar as `SKILL.md` operating principle 9, applied to slide phrasing specifically: action + the number that justifies it, in the same sentence or the same visual row.

**Numbers get their comparison basis stated, and it stays consistent within one deck.** "vs. previous period," "vs. previous year," "vs. target," and "vs. benchmark" are not interchangeable and a reader shouldn't have to infer which one a bare "+18%" means. Pick the basis per metric based on what's genuinely available (per the comparability rules — never fabricate a prior-period or target figure that wasn't supplied) and label it every time the number appears standalone, not just once at the top of the deck.

**Percentage points and percent change are not interchangeable — say which one.** CVR moving 3.2%→2.8% is **−0.4pp**, not "−0.4%" (which would imply moving to 3.19%) — and if the relative change is also worth stating, name it separately: "−0.4pp (−12.5% relative)." Getting this wrong on a slide a room is reading in real time is a fast way to lose the room's trust in every other number on the deck.

**"Significant" is a claim, not an intensifier.** Reserve it for movements that are genuinely large relative to the business's own scale (tie it to the same materiality judgment the candidate engine already makes, `analysis-playbook.md` §Insight candidate engine question 3) — a 1.2% revenue move is not "significant" regardless of how good it would sound. **Never write "statistically significant" unless an actual test was run** — this is the same statistical-sufficiency discipline already required before reporting a rate or a rate change (`analysis-playbook.md` §Statistical sufficiency), just as strict on a slide as in a data table.

**Executive rounding, not raw precision.** ₺12.4M, 124K, 3.2%, 4.5x — not ₺12,438,921.27. A slide read at a glance doesn't benefit from the decimal places a table would; if the precise figure matters for a specific decision, it belongs in the Methodology/appendix material, not the headline number.

**State uncertainty and non-comparability plainly, on the slide, rather than forcing a conclusion the data doesn't support.** "Attribution definitions differ across platforms — a direct cross-channel comparison isn't shown" is a complete, honest slide when that's what the comparability rules actually find; it does not need to be dressed up as a finding to justify its own slide.

**A flat or unchanged KPI is a real finding, not a gap to explain away.** "Performance remained broadly stable" is a complete sentence and a legitimate slide when that's genuinely what happened — don't manufacture a narrative ("despite a challenging environment…") to make an unremarkable period sound eventful. The instinct to always be able to say something interesting is exactly how invented data-adjacent stories get into a deck without a single number being wrong.

**Don't hide the bad news next to the good news.** If Revenue is +18% and CAC is +27% in the same period, both numbers belong in the deck — an executive deck's job is decision support, not a highlight reel. Suppressing a real, material finding because it complicates a positive headline is a violation of the same discipline that bans cherry-picking a favorable comparison period.

**Executive Summary caps at 3–5 messages, stated as complete sentences, not a dashboard summarized into bullets.** If the analysis produced more than 5 CRITICAL/HIGH findings, the summary states the top 3–5 by the same priority ranking used everywhere else in this skill — it does not try to represent everything the deck covers.

**No message repeats verbatim across the deck.** The Executive Summary states a finding once; every later slide that touches it adds evidence, diagnosis, or implication — restating the same sentence on the Channel slide, the Insight slide, and the Recommendation slide is padding, not reinforcement.

**Banned language — these read as AI-generated regardless of the analysis underneath them:**
- Throat-clearing: *"It is important to note that…", "As we can see…", "It should be noted that…", "The data clearly shows…", "Interestingly, …"* — delete the preamble, state the finding.
- Manufactured drama: *"This is a very significant finding," "This indicates that…"* used as filler rather than a real inference step.
- Jargon reached for by default rather than because it's the precise word: *leverage, unlock, holistic, robust, transformative, optimize, ecosystem, synergy, paradigm, actionable insights, data-driven approach, *strategic opportunity*.
- Marketing voice: *"Our exceptional growth demonstrates the tremendous success of our strategy"* — a deck's job is neutral, credible decision support, not a highlight reel; write the plain sentence instead ("Revenue increased 18%, while acquisition efficiency declined").
- Over-academic phrasing in the other direction is equally wrong: *"The observed trajectory demonstrates a material deterioration in downstream conversion efficiency"* should be *"Checkout conversion declined materially."*

**Design for three reading speeds on every slide, and check all three hold:**
- **5 seconds** — does the headline alone state the finding?
- **30 seconds** — does the primary visual actually prove what the headline claims?
- **2 minutes** — does the supporting detail add real information, or just repeat the headline in smaller type?

**Slide count is set by how many findings clear the candidate engine, not a target.** Already stated under Deck composition above — restated here because it's a content discipline as much as a structural one: 10 slides that each earned their place beat 18 that pad toward a "complete-feeling" deck. A short deck from a data-thin request is the correct output, not an underperformance to compensate for.

**Final editorial test — run this against every slide before it ships, not as a formality:**

1. Does this slide have exactly one message?
2. Does the headline actually state that message — a conclusion, not just the topic?
3. What specific number or chart supports it?
4. Am I making a causal claim? If so, does the wording match its tier — unqualified only at E4/E5, conditional with its assumption at E3, co-occurrence below that?
5. If I removed any single word or number, would the meaning change? (If not, cut it.)
6. Could an executive understand this slide in 30 seconds?
7. After reading it, would they still need to ask "so what?" — if yes, the implication is missing, not just under-stated.

If any answer is no, rewrite the slide — don't ship it and hope the speaker notes cover the gap.

**Governing principles, in order:** Identify what matters — don't summarize everything. Explain what the chart means — don't describe what it shows. Be useful — don't perform intelligence. Let the evidence determine the story — don't manufacture one to fill a slide. A senior reader should never finish a slide still needing to ask "so what."

## Analytical State — the honest-gap slide, not a skip

When a topic the user explicitly asked about (e.g. "include retention") genuinely can't be evaluated from the supplied data, **build this slide instead of silently omitting the topic or, worse, forcing a chart from insufficient data.** A component that is merely on a template's default list and can't be evaluated does not get its own slide — it is named in Methodology's Data limitations row, so the deck isn't padded with slides about what's missing. Same skeleton as a spotlight slide, muted treatment (gray headline, not colored): states what can't be evaluated, the specific reason (a stated minimum vs. what was actually supplied — "60 days required, 42 supplied," not a vague "insufficient data"), and when to re-evaluate if that's knowable. This is the deck's version of the KPI card's "Insufficient history" state (`dashboard-blueprints.md` §KPI card rules — the "no prior period to compare" / "Not available in supplied data" states) — same discipline, different medium. Silently dropping the topic reads as if it was never considered; this slide proves it was.

## Recommended Actions slide

One slide, up to 3 actions (never more — a room reading a slide caps lower than a scrolled dashboard table). Same evidence bar as the dashboard's action cards (`dashboard-blueprints.md` Output mode 2 step 8): each action names its evidence inline, not just a headline claim, and carries a priority pill using the skill's own scale (Critical / High / Medium — `SKILL.md` §Label vocabulary), shown as a neutral text pill; color on this slide, as everywhere, means direction only. If a 4th action has real evidence behind it, it goes in the appendix/methodology material or gets cut — not compressed into the same slide at illegible size.

## Methodology slide

Closing, dark background (matching Cover, bookending the deck). A definition grid — Period, Comparison basis, primary metric's definition, Attribution model — plus a full-width **Data limitations** row. This is where the following are stated, every time they apply, not optionally:

- Any comparability hard block that affected what could be shown (e.g. "Meta revenue is attribution-based and is not additive with Shopify revenue")
- The Coverage integrity note — which supplied files/tables were used, which were set aside and why (`dashboard-blueprints.md` §Dashboard QA gate)
- Any source-identification or mapping-confidence caveat carried at less than HIGH/EXACT (`analysis-playbook.md` §Source identification, `kpi-framework.md` §1)

A deck without this slide has hidden its own uncertainty in a format that discourages the reader from asking. It closes the deck for a reason — it's the place a reader who wants to challenge a number goes to check where it came from.

## Rendering mechanism

**First confirm a PPTX toolkit actually exists in this environment** — a presentation skill such as `anthropic-skills:pptx`, or a library such as pptxgenjs. If none does, don't claim a deck: deliver the slide-by-slide content as text and say no `.pptx` was produced (`SKILL.md` §Environment fallbacks). The API names below are pptxgenjs's; another toolkit's equivalents apply. **When a toolkit exists, generate the actual `.pptx` with it** — native slide shapes and text boxes (pptxgenjs or equivalent), not an HTML-to-PPTX conversion and not a set of exported images pretending to be a deck. Canvas: 16:9 widescreen (13.333in × 7.5in, 1920×1080 proportions).

**Reuse the design system's exact tokens** — the design-token block in `dashboard-blueprints.md` §Rendering mechanism: same colors, same font, same spacing base. The spotlight-slide colors in the layout table above (Danger `#A11D1D`, Success `#156143`, Info/lilac `#8FA3FF`, dark ground `#0E1116`) are that token set's dark-ground variants, not a second palette. **Accessibility carries over unchanged too** (`dashboard-blueprints.md` §Accessibility): a delta is never color-alone — it carries its sign or arrow; a cohort-heatmap cell prints its value, not just a background color; any chart with ≥2 series gets a legend. Do not invent a separate visual language for the deck; a reader seeing both outputs from one request should recognize them as the same product.

**Font caveat, stated honestly, not assumed away:** an HTML dashboard embeds Plus Jakarta Sans directly (`dashboard-blueprints.md` §Rendering mechanism, design tokens), which a browser renders reliably. PPTX font handling is weaker — pptxgenjs does not embed fonts into the file by default, so a recipient without Plus Jakarta Sans installed will see PowerPoint's substitute font, which can shift line breaks and spacing away from the designed layout. State this limitation when delivering a deck rather than presenting the rendered result as pixel-identical to the HTML reference. If font-embedding is genuinely required, it needs direct manipulation of the PPTX's underlying XML/font-table — treat that as an explicit ask, not a default.

**Real charts are native chart objects, not hand-drawn shapes standing in for one.** A native PPTX chart carries an embedded data workbook — the same reason "the chart comes from Excel" reads as normal to anyone who's built a deck by hand — and stays editable (right-click → Edit Data) in a way a rectangle sized to look like a bar never does. Use the toolkit's native chart API (`addChart()` in pptxgenjs) for every layout that's actually charting a data series, not text-and-numbers:

| Layout / chart form | Native chart type | Note |
|---|---|---|
| A — trend | `line` or `area` | Directly supported |
| C — ranked comparison | `bar` (horizontal orientation) | Directly supported |
| Relationship / quadrant (per `dashboard-blueprints.md`'s scatter rows) | `scatter` | Directly supported |
| D — decomposition / waterfall | `bar`, **stacked**, with an invisible base series | PowerPoint has a native Waterfall chart type; the charting library doesn't expose it. The standard, correct workaround is a stacked bar chart with a transparent "riser" series holding each bar at its running-total height — a real native chart, not an approximation. Do not hand-draw floating rectangles to fake this |
| Funnel | `bar` (horizontal, descending widths) | PowerPoint's native Funnel type isn't exposed by the library either. A descending horizontal bar chart is the closest available native-chart equivalent — still a real, editable, Excel-backed object, just not literally PowerPoint's newer Funnel chart type |
| Cohort heatmap | A native PPTX **table**, cell background color per value | Not a chart — no chart type fits a colored grid. A table object, same as the dashboard's own heatmap rule (`dashboard-blueprints.md`'s accessibility note: build as an actual table, not a styled grid of shapes) |

**Shapes and text boxes are still correct for what isn't a chart** — KPI stat readouts, spotlight big-numbers, action cards, the Methodology definition grid. Those aren't data series being charted, they're single values with typographic treatment; forcing them through the chart API would be the opposite mistake. The dividing line: if the slide's content is "one number, styled," it's a text box; if it's "several data points forming a series," it's a native chart, not a shape sized to resemble one.

**Never hand-draw rectangles to approximate a chart the toolkit can actually build natively.** This was a real defect in this skill's first executed presentation build — a ranked-comparison slide used styled rectangles instead of a native `bar` chart, which the toolkit supported directly. Visually similar, but not an editable chart and not what "the deck has real charts in it" means to someone who opens the file in PowerPoint.

**Speaker notes carry the analytical trail, not restated content.** Per the design system's reference deck (the user's own, not shipped in this repo): each slide's speaker notes state which layout it uses and why that finding earned a slide (which candidate-engine criteria it cleared), not a spoken-word script of the slide's own text — the slide already says that. **Notes and embedded chart workbooks are part of the file the user will share:** they hold only the aggregated values the slide shows — no raw rows, no identifiers, no pasted source data (`data-quality-gate.md` §Handling PII).

**Verify before delivering** — same discipline as the dashboard's render-verification rule (`dashboard-blueprints.md` §Rendering mechanism): convert the generated `.pptx` to PDF and render each slide to an image for visual inspection (following the toolkit's own QA workflow where it has one). If no PDF or image renderer is available, run the structural checks that are and say the deck was not visually verified before calling it done — a shape-generation error or text overflow is as silent a failure in pptxgenjs as a missing charting-library reference is in HTML, and does not show up in a structural validator alone.

**The PDF conversion is a verification step, not a second deliverable.** The `.pptx` is the output this skill hands to the user by default — don't also hand over the intermediate PDF unless it's specifically asked for; producing one every time as a matter of course adds a file the user didn't request and implies a second supported output format that isn't one.
