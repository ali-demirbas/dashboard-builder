# Maintenance Ledger

Not part of the skill's runtime — a bakım/audit tracking dosyası. Amaç token azaltmak değil, bir sonraki audit turunda "neresi değişti, neresi zaten denetlendi" sorusunu saniyeler içinde cevaplamak.

**Operasyonel kural (2026-08-14'ten itibaren):** `dashboard-builder-consolidated.md` artık her modül düzenlemesinden sonra otomatik yeniden üretilmiyor. Sadece Ali paylaşım/snapshot için istediğinde build edilir. Günlük geliştirme akışı: modül düzenle → test/audit et → tekrarla → **sadece release anında** "consolidated üret."

```yaml
current_pass: 25

modules:
  SKILL.md:
    last_changed_pass: 22
    last_audited_pass: 22
    status: PASS. Pass 22: tightened step 6's template/format question —
      explicitly states these are two INDEPENDENT questions, and that a
      partial answer gets a re-ask for only the unanswered one, never
      re-bundled into one combined question. Real field-test finding: a
      live tester's session bundled both into one question, got a partial
      answer, needed a second round-trip to get the format too.
  data-quality-gate.md:
    last_changed_pass: 25
    last_audited_pass: 25
    status: PASS. Pass 21: added Cohort grain sufficiency check to
      §5 Distributional — a cohort partitioned finer than its N supports
      (daily cohorts on low daily volume) reads as a flat/non-improving
      retention curve when it's actually per-cohort sampling noise;
      distinct from the existing cohort-maturity check. Came out of a comparative
      review, cross-checked against our own framework before adding
      (not applied blindly).
  comparability-rules.md:
    last_changed_pass: 25
    last_audited_pass: 25
    status: PASS. Pass 23: added one clarifying paragraph after the
      "unknown is a mismatch" reporting requirement — an unknown checklist
      item rules out DIRECT specifically, it does not by itself force
      NOT_COMPARABLE (which requires a named §2 hard block). Real
      external-review finding: the existing wording read as if any unknown
      metadata field forces a hard refusal, which would make most
      real-world exports NOT_COMPARABLE by default. The 4-state
      architecture already resolved this correctly (unknown → CONDITIONAL
      by default, not NOT_COMPARABLE) — this was a communication gap, not
      an architecture gap, so no new taxonomy was added.
  kpi-framework.md:
    last_changed_pass: 25
    last_audited_pass: 25
    status: PASS
  analysis-playbook.md:
    last_changed_pass: 25
    last_audited_pass: 25
    status: PASS. Pass 23: two fixes from an external adversarial review,
      both verified against source before applying. (a) REAL BUG: Insight
      Candidate Engine question 6 was logically inverted — the table's own
      "If no" convention combined with "Is there a plausible alternative
      explanation not yet ruled out?" fired the downgrade on the wrong
      answer (NO instead of YES). Reworded to "Have all plausible
      alternative explanations been ruled out?" so "If no" now correctly
      triggers the downgrade — matches the CRITICAL/HIGH definitions
      immediately below, which already used the correct logic. (b) Added
      deterministic guidance to Statistical sufficiency: a rate change now
      requires an actual two-proportion z-test/CI (via Operating Principle
      11's compute-don't-estimate rule) rather than an eyeballed judgment
      of "enough volume"; a correlation requires n + a computed p-value/CI,
      not R alone; with no compute tool available, cap the claim at
      "directional, untested" rather than substituting intuition — ties the
      SUPPRESS/downgrade decision to an actual test result whenever one can
      run. Addresses part of the standing insight-ranking-consistency open
      finding (still not fully closed — see open_findings below).
  dashboard-blueprints.md:
    last_changed_pass: 25
    last_audited_pass: 25
    status: PASS. Pass 21: added a Responsive layout paragraph to
      §Rendering mechanism — SVG viewBox/scaling requirement + a stated
      ~768px reflow breakpoint (KPI strip to 2 cols, chart row to 1 col,
      detail table horizontal-scroll-in-container). Previously
      unaddressed anywhere in this file. Sourced + cross-checked the
      same way as the data-quality-gate.md Pass 21 change. A paired
      "data-volume rendering strategy" finding was reviewed and
      deliberately not applied — Ali's call, not a rejection on merits.
      Pass 22: added an explicit UTF-8 charset requirement to §Rendering
      mechanism (`<meta charset="utf-8">` first in `<head>`, HTML-entity
      fallback) — a real bug from a live field test: ₺/em-dash/middle-dot
      rendered as mojibake on first publish because nothing required a
      charset declaration, despite the skill's own visual language
      depending on non-ASCII glyphs throughout.
      Pass 23: two small fixes from the same external review. (a) Dashboard
      QA gate said "Run all seven" over an 8-row table — editorial
      off-by-one, fixed to "eight". (b) Unit integrity's currency clause
      said "currency figures use one currency," reading as a blanket ban
      on multi-currency data — tightened to match data-quality-gate.md §3's
      actual (more nuanced) rule exactly: per-currency reporting or a
      stated-FX-method conversion are both fine, blending at face value
      is not. The two files now say the same thing instead of the QA gate
      being stricter than the rule it's supposed to enforce.
  presentation-blueprints.md:
    last_changed_pass: 25
    last_audited_pass: 25
    status: PASS. Pass 19 carried 1 open correction (real 8-slide deck
      built for Numerspace.com via anthropic-skills:pptx/pptxgenjs;
      structural validation passed, content QA clean, visual QA caught
      2 layout defects both fixed; a 3rd — ranked-comparison slide used
      hand-drawn rectangles instead of a native `bar` chart — fixed at
      spec level only, delivered file not rebuilt, still offer-if-asked.
      LibreOffice installed on host to enable PDF-based visual QA).
      Pass 20: reviewed external critique (unattributed per policy) of
      Deck composition — 2 real findings, 1 pushed back on. Applied:
      (a) explicit user-override mechanism — MEDIUM findings, specific
      dashboard sections/KPIs can be added to a deck on request, placed
      in the fitting layout or an Appendix, keeping their own
      evidence/caveat framing rather than inheriting CRITICAL/HIGH
      visual weight. (b) Methodology slide reclassified from a bare
      "fixed, always present" item to explicitly mandatory-but-scalable
      — content can compress for a small deck, but the disclosure
      itself (Coverage integrity note, data-quality WARNINGs, mapping-
      confidence caveats) may not be dropped. Rejected the paired
      suggestion to make Methodology fully conditional/removable — that
      would contradict non-negotiable rule 1 (disclose every gap).

open_findings:
  - id: insight-ranking-consistency
    area: analysis-playbook.md — Insight Candidate Engine
    note: >
      Rule-based gate exists (Pass 16), but individual materiality/broadness
      judgments still rest on LLM reasoning per case. Not a rule gap — a
      measurement gap. Needs: run the same dataset 3-5x, diff the resulting
      priority labels, see how much they actually vary. Not yet run.
  - id: test-suite-coverage
    area: TEST-SUITE-regression-benchmark.md
    note: >
      4 of 50 cases actually executed against real subagents (T-X03, T-M07,
      T-M08, T-D04 — all passed, cross-verified by hand). Remaining 46 are
      still a manual checklist only, never run. Priority if resumed: the
      other P0/P1-adjacent cases first (EC-08 duplicate rows, EC-19 large
      dataset, EC-24 malformed CSV).

pass_18_notes: >
  Real-world catch, not a supplied audit: a live Numerspace.com dashboard
  build silently dropped available data (an organic-query table) and ranked
  channels by volume alone despite the skill's own "never declare a channel
  best on one metric" rule already existing in prose. Root cause: no
  mechanism forced accounting for supplied-but-unused data, and the
  volume-ranking chart form wasn't wired to the quality-pairing rule.
  Fixed: Coverage integrity added as an 8th Dashboard QA gate check +
  Output mode 2 structure item 9 (data-quality-gate.md had no equivalent
  gap — this was dashboard-blueprints.md only); channel-ranking chart-form
  row now requires pairing a volume metric with an available quality metric;
  anomaly-triage's "check configuration before business explanation" rule
  extended from movements to disproportionate static compositions, gated
  strictly to named+sourced mechanisms (no license to speculate). One GA4
  fact (Direct channel definition) added to comparability-rules.md /
  data-quality-gate.md — WebFetch-verified against Google's own page
  first; an initial draft over-claimed unconfirmed causal detail
  (HTTPS-stripping, in-app browsers) and was scaled back to only what the
  fetched source actually states.

pass_24_notes: >
  Adversarial audit before a usage-limit reset: 3 parallel auditors
  (cross-file / analysis+data-quality logic / comparability+kpi logic /
  dashboard+presentation specs; a 4th cross-file pass died to the rate
  limit — its ground was largely covered by the other three). ~35 verified
  defects fixed, several of them introduced by Passes 20-23 themselves.
  REAL BUGS: candidate-engine Q4 ("broad or concentrated?") fired its
  consequence on the wrong answer, same class as the Q6 bug fixed in P23 —
  reworded to "Is it broad-based?"; Q2 had no UNTESTED branch although the
  P23 Statistical-sufficiency text required one (criterion, consequence and
  missing branch all disagreed) — Q2 now = test/CI excludes zero? NO →
  SUPPRESS, UNTESTED (no compute tool) → cap MEDIUM; "first failure decides"
  contradicted the non-terminal rows 4/6/7 — now "1-3 terminal, 4-8 jointly
  read"; label block re-derived (HIGH needs Q5; Q7 never stays open; Q3
  fail = SUPPRESS, not "LOW at most"); GRR formula column stated the
  aggregate-min form its own variance column calls wrong — now per-customer
  Σmin; KF spam-rate action trigger instructed exactly the ESP-vs-Postmaster
  comparison CR §2.2 hard-blocks; CR line 30 ("both go in the refusal")
  contradicted P23's own "unknown → CONDITIONAL" paragraph; CONDITIONAL's
  example (Adjust installs vs GA4 new users) was simultaneously a §2.1 hard
  block — §2.1 now blocks ranking/netting/summing, not side-by-side
  reconciliation; PB cited design tokens DB never defined — token block
  added to DB §Rendering mechanism; PB cited a DB "§04 Insufficient
  history" state that doesn't exist; DB QA gate cited a nonexistent
  analysis-playbook "multi-table-export check" — the check (used live in
  P18) is now actually written into §Ingestion. INCONSISTENCIES: "5–8
  cards" x3 vs "up to 8, no floor"; pie "≤4-category" exception vs Template
  E's own ban; Methodology "fold into Exec Summary" (P20) vs 3 rules needing
  it as a closing slide; Appendix "after Methodology" (P20) vs "Methodology
  closes"; "Key Takeaways" card label was on the banned-phrase list;
  Exec-Summary 1–2 vs 3–5 sentences; python-pptx named in 3 places while
  the chart API text is pptxgenjs; deck-only High/Medium pills vs the
  skill's 🔴/🟠/🟡 scale; DQ clicks>impressions BLOCKER (table) vs WARNING
  (§3); "entire date range missing" BLOCKER vs §2's paused-campaign WARNING
  — now scoped to "across all dimensions"; cohort-immature WARNING said
  "compute, but label" (can't compute) — now "Not available"; same-weekday
  "3-4 prior instances, same as 21-day floor" (4 instances = 28 days);
  confidence table rated a causal diagnosis High on E1/E2 and had an
  unreachable "BLOCKER → Low" row and an example reason not in the table —
  High = E4/E5 only, Low = material WARNING, 4th row Alternative
  explanations; E3 row credited eBay's +4,100% (the uncontrolled E2 figure)
  — now the controlled +1,400%; E1 example was a single-period move (E0 per
  the trend gate); Google ROAS/tROAS filed as hard block but NORMALIZABLE;
  MER "~5.0+" benchmark had no source under a "never quote unsourced" rule;
  GRR trigger (<90%) tripped half the §7 median band; ARPDAU "ARPU is
  cohorted" overstated; CAC identity silently picked a spend scope; CTOR
  "three vendors" named two; residue ("archetype", changelog prose in the
  sparkline rule, "(Pass 19 test run)", duplicated Actions/Findings bullets,
  wrong above/below pointers, "rule 9" ambiguity). DELIBERATELY NOT APPLIED
  (unverifiable without research, or over-literal): CR §2.1 "Facebook 60"
  click window (likely stale — Meta's current max click window is 7 days;
  verify against source before changing); a16z LTV margin basis stated two
  ways (net profit vs contribution margin — needs the source); GRR/NRR
  cohort-vs-formula attribution split across the two files; soft-flag rows
  that are "valid for use A, blocked for use B" — kept as soft flags, that
  is what a caveat is; null-rate severity axis gap; layout letters A/B/C/E
  (skips D — matches the user's own reference deck, left alone). PROCESS
  CHANGE: dashboard-builder-consolidated.md is now built by verbatim
  concatenation of the 7 source files (scripts/build_consolidated.sh),
  not hand-condensed — P23 found two of my own edits had never been
  mirrored, and hand-mirroring ~35 edits here would have been worse.

pass_25_notes: >
  Closed out everything Pass 24 had deliberately left open, each one checked
  against research/raw/ first rather than rewritten from memory.
  comparability-rules.md: the "Facebook 60-day" click window turned out to
  be sourced (it is Adjust's own discrepancy doc's example) but conflicts
  with Meta's current 7-day default and with AppsFlyer's SRN table — now
  attributed and recorded as a vendor-doc conflict, not silently resolved;
  the header's "every rule is vendor-doc or peer-reviewed" claim now admits
  the few labeled heuristics/vendor simulations (trend-gate cadence
  figures, the Recast simulation, the illustrative Play/Firebase ~70%/~20%
  pair); three unsourced "single most common" frequency claims softened
  (plus one each in analysis-playbook.md and dashboard-blueprints.md);
  §2.2 now says up front that its two NORMALIZABLE entries (MER,
  ROAS/tROAS) are look-alikes, not blocks; §3 soft flags gained a "scoped
  to a use" rule and five rows are tagged [blocked use: …] (Meta estimated
  metrics, Meta in-development metrics, Braze variant-vs-step, relative
  lift across studies, PSA holdout on optimized delivery) — they stay in
  §3 because the figure is valid for its other uses; cohort-vs-formula
  method now named for both NRR and GRR in both files; the PSA
  "two-thirds" figure attributed to its study. kpi-framework.md: a16z LTV
  basis reconciled per the source (defines net profit, worked chain uses
  contribution margin); the eight source facts vs the seven comparability
  checks explained as complementary lists; NRR trigger's "GRR < 85%"
  aligned to the §7 band; two wrong cross-references fixed.
  data-quality-gate.md: zero-denominator ratios moved out of the WARNING
  row into their own "display rule, not a severity" paragraph (the WARNING
  consequence is "compute, but label"; this case must not be computed);
  null-rate severities now cover every cell (analysis vs unused column).
  dashboard-blueprints.md: remaining above/below pointers and the last
  "5–8 cards" phrase. presentation-blueprints.md: layout E renamed D (the
  catalog ran A, B, C, E); "six layouts" now names the four additional
  skeletons; duplicated conditional-section bullets merged. The
  rate-limited cross-file auditor from Pass 24 was replaced by a
  mechanical count check (checklist 7, join gate 9, engine 8, QA gate 8,
  templates 11, rules 15, principles 11, layouts 6, facts 8, refs 6) —
  all match.

decisions_deferred_not_findings:
  - id: auto-mode
    note: >
      A zero-selection "upload -> automatic dashboard" mode was proposed.
      This is a product/UX decision (Ali's call), not an audit defect —
      not tracked as an open finding, just noted here so it isn't
      rediscovered as if new.

last_consolidated_build:
  pass: 25
  date: 2026-10-10
  word_count: 36470
  note: >
    Built by scripts/build_consolidated.sh — verbatim concatenation of
    SKILL.md + the 6 reference files, Part headers added. No hand-condensed
    sections anymore, so nothing to mirror by hand. Changelog still omitted.
```

**Nasıl okunur:** `last_changed_pass > last_audited_pass` olan bir modül, son değişiklikten sonra tam denetlenmemiş demektir — sıradaki audit'in önceliği odur. `last_consolidated_build.pass`'ten büyük `last_changed_pass`'i olan herhangi bir modül varsa, consolidated dosya güncel değildir — release öncesi yeniden üretilmeli.
