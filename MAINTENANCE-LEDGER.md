# Maintenance Ledger

Not part of the skill's runtime — a bakım/audit tracking dosyası. Amaç token azaltmak değil, bir sonraki audit turunda "neresi değişti, neresi zaten denetlendi" sorusunu saniyeler içinde cevaplamak.

**Operasyonel kural (2026-08-14'ten itibaren):** `dashboard-builder-consolidated.md` artık her modül düzenlemesinden sonra otomatik yeniden üretilmiyor. Sadece Ali paylaşım/snapshot için istediğinde build edilir. Günlük geliştirme akışı: modül düzenle → test/audit et → tekrarla → **sadece release anında** "consolidated üret."

```yaml
current_pass: 21

modules:
  SKILL.md:
    last_changed_pass: 17
    last_audited_pass: 17
    status: PASS
  data-quality-gate.md:
    last_changed_pass: 21
    last_audited_pass: 21
    status: PASS. Pass 21: added Cohort grain sufficiency check to
      §5 Distributional — a cohort partitioned finer than its N supports
      (daily cohorts on low daily volume) reads as a flat/non-improving
      retention curve when it's actually per-cohort sampling noise;
      distinct from the existing cohort-maturity check. Sourced from an
      external kpi-dashboard-design skill's troubleshooting-pattern
      section, cross-checked against our own framework before adding
      (not applied blindly).
  comparability-rules.md:
    last_changed_pass: 17
    last_audited_pass: 17
    status: PASS
  kpi-framework.md:
    last_changed_pass: 17
    last_audited_pass: 17
    status: PASS
  analysis-playbook.md:
    last_changed_pass: 17
    last_audited_pass: 17
    status: PASS
  dashboard-blueprints.md:
    last_changed_pass: 21
    last_audited_pass: 21
    status: PASS. Pass 21: added a Responsive layout paragraph to
      §Rendering mechanism — SVG viewBox/scaling requirement + a stated
      ~768px reflow breakpoint (KPI strip to 2 cols, chart row to 1 col,
      detail table horizontal-scroll-in-container). Previously
      unaddressed anywhere in this file. Sourced + cross-checked the
      same way as the data-quality-gate.md Pass 21 change. A paired
      "data-volume rendering strategy" finding was reviewed and
      deliberately not applied — Ali's call, not a rejection on merits.
  presentation-blueprints.md:
    last_changed_pass: 20
    last_audited_pass: 20
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

decisions_deferred_not_findings:
  - id: auto-mode
    note: >
      A zero-selection "upload -> automatic dashboard" mode was proposed.
      This is a product/UX decision (Ali's call), not an audit defect —
      not tracked as an open finding, just noted here so it isn't
      rediscovered as if new.

last_consolidated_build:
  pass: 21
  date: 2026-08-14
  word_count: 22825
  note: >
    Regenerated directly (no subagent) to keep cost low. Pass-by-pass
    changelog intentionally dropped from this build per Ali's request —
    word count is lower than the prior 34,543 mostly because of that, not
    because content was cut. Re-add the changelog only if asked.
```

**Nasıl okunur:** `last_changed_pass > last_audited_pass` olan bir modül, son değişiklikten sonra tam denetlenmemiş demektir — sıradaki audit'in önceliği odur. `last_consolidated_build.pass`'ten büyük `last_changed_pass`'i olan herhangi bir modül varsa, consolidated dosya güncel değildir — release öncesi yeniden üretilmeli.
