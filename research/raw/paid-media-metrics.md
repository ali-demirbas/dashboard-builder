# Paid-Media Metric Definitions — raw research

> All entries from pages actually fetched. Meta help pages are JavaScript-rendered, so they were retrieved with a rendering scraper; every URL returned HTTP 200.

---

## 1. Meta (Ads Manager / Business Help Center)

### Reach
- **Definition** — Meta Accounts that saw your ads at least once.
- **Gotcha** — Meta states plainly it "is calculated using sampled data" and is **estimated**, involving deduplication across devices and across Facebook and Instagram. **Reach is not a hard count** and should never be reconciled to the decimal against an MMP or GA4 user count.
- **Source** — facebook.com/business/help/710746785663278 · developers.facebook.com/docs/graph-api/reference/adaccount/insights/

### Impressions
- **Definition** — Times ads were on screen. Counted the first time an instance is on screen.
- **Gotcha** — Three traps in one metric. (1) Scroll-back does not re-count, but two separate on-screen occasions in a day count as 2. (2) **"This method of counting video impressions differs from industry standards for video ads"** — a video is not required to start playing for the impression to count. (3) Only impressions "from certain placements are accredited by the MRC" — the number as a whole is **not** an MRC viewable impression.
- **Source** — facebook.com/business/help/675615482516035

### Frequency
- **Formula** — Impressions ÷ reach (implied).
- **Gotcha** — Flagged **estimated** in the API reference because reach is sampled. **Frequency inherits all of reach's estimation error.**

### CPM
- **Formula** — Amount spent ÷ impressions × 1,000.
- **Gotcha** — Denominator is Meta's own served-impression count, not a viewable impression. Cross-platform CPM comparison is only valid if both sides count impressions the same way — and Meta's video impression counting explicitly departs from industry standards.
- **Source** — facebook.com/business/help/753932008002620

### Clicks (all) vs CTR (link) vs CTR (all)
- **Clicks (all)** — link clicks + clicks to the Page profile/picture + post reactions, comments, shares + clicks to expand media + clicks to take the objective action.
- **CTR (link)** = Link clicks ÷ impressions. **CTR (all)** = Clicks (all) ÷ impressions.
- **Gotcha** — **This is the headline CPC/CTR trap.** "Clicks (all)" includes likes, comments, shares and profile taps — interactions that never reached your site. CTR (all) is systematically higher than CTR (link) on the same ad, and the gap is engagement, not traffic. **Reporting "CTR" without specifying which one is the single most common Meta reporting error.** Both sit in the same column picker with near-identical names.
- **Source** — facebook.com/business/help/787506997938504 · /877711998984611 · /928745330472862

### Results / Cost per result
- **Gotcha** — Three stated traps. (1) **"Your results may not reflect how you're billed"** — results may count purchases while billing is on impressions. (2) The unit changes with the objective, so **Results is not summable across a mixed-objective account**. (3) "In some cases where results cannot be measured directly due to partial or missing data, **statistical modeling may be used**." For iOS 14+, Cost per result is spend ÷ results **reported by Apple's SKAdNetwork API** — two different measurement systems inside one column.
- **Source** — facebook.com/business/help/611432918970668 · /762109693832964

### Purchase ROAS
- **Formula** — Purchase conversion value ÷ amount spent.
- **Gotcha** — The word is **"approximate."** Where events cannot be counted directly, statistical modeling may be used "as well as for the **values** assigned to those events" — **both the count and its currency value can be modeled.** For iOS 14+ delivery the metric may not be calculated at all. On Meta's official estimated-metrics list.
- **Source** — facebook.com/business/help/274294333328345 · /metrics-labeling

### Attribution models (Standard / Incremental / Custom)
- **Gotcha** — Meta's own warning: **"Results cannot be compared in the Campaign Overview table across ad sets with different attribution models. Each attribution model uses different counting mechanisms, and comparing across different attribution models will lead to inaccurate conclusions."** A single account can now contain **three mutually incomparable counting systems in one table.**
- **Source** — facebook.com/business/help/460276478298895

### Attribution setting (standard model)
- **Current options** — **Click-through:** 1-day or 7-day after a **link click**. **View-through:** 1-day after an impression. **Engage-through:** 1-day after a non-link click action — any click excluding link clicks; for video also a play of 5 seconds (or 97% if shorter).
- **Gotcha** — Two structural changes visible on the current page. (1) **Click-through now requires a *link* click** — other clicks moved into the separate engage-through bucket, so "click-through conversions" is a **narrower population than it used to be**. (2) The page **no longer lists any 28-day window**. Meta notes "some accounts may still use prior versions… while this feature is rolling out" — **two accounts can be on different definitions simultaneously.**
- **Default** — "Meta uses a default attribution setting of **7-day click, 1-day view and 1-day engagement conversion**." **The default silently includes both view-through and engage-through credit.** Any Meta "conversions" number quoted without its attribution setting includes conversions from people who **never clicked the ad** — the primary reason Meta's count exceeds GA4's.
- **Source** — facebook.com/business/help/460276478298895 · /611432918970668

### How actions are attributed
- **Gotcha** — **Conversions are reported on the date of the impression or click, not the date of the conversion.** This alone guarantees Meta and any conversion-dated system (GA4, most BI warehouses) will disagree on any given day, and that **yesterday's Meta numbers keep changing for days afterward.**
- **Source** — facebook.com/business/help/458681590974355

### Estimated metrics
- **Published list** — **Reach**, Purchase ROAS, Leads, App installs, Website landing page views, Unique link clicks, Results ROAS, Estimated spend. API additionally flags `frequency`, **`spend`**, `cpp` and all `cost_per_unique_*`.
- **Gotcha** — **`spend` itself is flagged estimated.** Meta's guidance permits estimated metrics for directional guidance but **not for billing and not for historical comparison** — which excludes most of what these columns are actually used for in reporting decks.
- **Source** — facebook.com/business/help/metrics-labeling

### In development metrics
- **Published list** — **6-second video plays**, **Video plays at 100%**, Cost per ThruPlay, `video_play_actions`, Qualified lead rate, Billable amount spent, Ad recall lift.
- **Gotcha** — Explicitly **not** for historical comparison or strategic planning. **Core video KPIs sit on this list** — a year-over-year video completion comparison is comparing two different methodologies.

### Conversions API / Aggregated Event Measurement
- **CAPI gotcha** — CAPI raises **matched events**, which raises attributed conversions — **a CAPI deployment causes a step-change in reported conversions with no change in real demand. Any pre/post CAPI performance comparison is invalid.**
- **AEM** — limits each primary domain to **8 prioritized conversion events**; statistical modeling accounts for unobservable events. Reporting delayed up to **72 hours**; **breakdowns by age, gender, region and placement are unavailable** for AEM-reported conversions.
- **Source** — facebook.com/business/help/2041148702652965 · /387440828988900

### ThruPlay / 3-second video plays
- **ThruPlay** — plays to completion for videos under 15s; ≥15s for longer videos. **"Completion" means 97%, not 100%.** Asymmetry: on a 14-second video ThruPlay requires near-full completion, but on a 60-second video only 25% of runtime. **Not a constant standard of attention across creative lengths.**
- **3-second plays** — counts **how much of a video was played, not elapsed time**, and **replays are excluded**. Meta's example: 2 seconds, rewind, same first 2 seconds again = **no** 3-second view. Combined with the impression rule (a video need not play at all for an impression), **a low 3-sec-play/impression ratio can reflect counting mechanics rather than weak creative.**
- **Source** — facebook.com/business/help/2051461368219124 · /743427195703387

### Ad relevance diagnostics
- **Gotcha** — All three rankings are **relative percentile rankings against competitors, not absolute performance** — your ad can improve in absolute terms and fall a band because the auction got more competitive. Not shown below **500 impressions**. Critically: **"Ad relevance diagnostics aren't inputs into the ad auction"** — optimizing to raise a ranking is optimizing a readout, not a lever.
- **Source** — facebook.com/business/help/403110480493160

### Auction overlap
- **Gotcha** — Only one of your ads enters the auction. The damage compounds: overlap "can prevent an ad set from spending its full budget or achieving enough results to **exit the learning phase**." **Account fragmentation therefore shows up as a learning-phase problem, not as an overlap problem.**
- **Source** — facebook.com/business/help/537699989762051

### Learning phase / ~50 events rule
- **Definition** — Exit "usually occurs after about **50 results in the week after the ad set's last significant edit**."
- **Gotcha** — Meta's explicit warning: **"During the learning phase, ad sets are less stable and usually have a higher CPA"** and "results aren't necessarily indicative of future performance." **Reading CPA off a learning-phase ad set and acting on it triggers a significant edit, which resets the phase** — the diagnostic loop that keeps accounts permanently in learning. The threshold is ~50 results **in a week**, so the constraint is a **rate, not a total**.
- **Source** — facebook.com/business/help/112167992830700

---

## 2. TikTok Ads Manager

### Impressions / Gross Impressions
- **Gross Impressions** = times your ads were shown, **including invalid impressions**.
- **Gotcha** — Third-party dashboards sometimes pull `gross_impressions` instead of `impressions`, **inflating every impression-based rate and cost metric downstream**.

### Frequency vs Average 7 day frequency
- **Gotcha** — Average 7 day frequency is **fixed to 7 days regardless of your report date range**, while plain Frequency floats with the range. Mixing them produces non-comparable numbers.

### CPM
- **Gotcha** — TikTok separately reports **Cost per 1,000 people reached**, a reach-based cost. The two are routinely confused; **CPM is always the lower number.**

### Clicks (all) vs Clicks (destination) / CTR (destination)
- **Gotcha** — TikTok's default CPC uses **destination** clicks. A CPC from Clicks (all) looks far cheaper than TikTok's own column — the same all-vs-link trap as Meta, with different naming. Likes, comments, profile taps and sound clicks are in Clicks (all) but **excluded** from the CTR numerator.

### CVR vs CVR (clicks)
- **Definition** — CVR = conversions ÷ **impressions**. CVR (clicks) = conversions ÷ **destination clicks**.
- **Gotcha** — The API field `conversion_rate` is the **click**-based version; TikTok tells integrators to migrate to `conversion_rate_v2`, the impression-based metric matching the UI column of the same name. **Legacy pipelines silently report a different metric than the UI.**

### Results / Cost per result / Result rate
- **Gotcha** — TikTok's own docs warn that `result`, `cost_per_result` and `result_rate` **at campaign level are meaningless** when ad groups underneath use different optimization goals. **Never roll Results up across mixed-goal campaigns.**

### ROAS fields
- **Gotcha** — Many ROAS columns: Purchase ROAS (website / app / TikTok-onsite / Shop / offline) and **VTA purchase ROAS** (`vta_complete_payment_roas`, purchases attributed to someone **only viewing** the ad). **They are not additive** and are frequently mixed in exports.

### Attribution: CTA / VTA / EVTA
- **Definition** — **CTA** = click then convert. **VTA** = view without click, then convert. **EVTA** = view for **6 seconds or more**, then convert.
- **Gotcha** — EVTA is a *third* credit path, so **CTA + VTA ≠ total conversions**. And **VTA conversions are dated to the impression time**, not the conversion day — historical VTA figures keep changing.

### Attribution window
- **Options (ad group level)** — Click-through **1 / 7 / 14 / 28 day**; view-through **Off / 1 day / 7 day**; Event count **Every** or **Once**.
- **Gotcha** — Two hard ones. (1) **"Attribution settings cannot be changed once the ad group has been published"** — you must build a new ad group. (2) The setting **"doesn't impact your MMP reporting. It controls your TikTok Ads Manager conversion reporting"** — TikTok and your MMP **diverge by design** unless aligned manually. TikTok's own pages are inconsistent: treat the ad-group-level page as authoritative.
- **Source** — ads.tiktok.com/help/article/attribution-settings-at-the-ad-group-level

### Video views (the trap)
- **Definition** — Times your video **started to play**. Counted per impression; replays excluded.
- **Gotcha** — **A TikTok video view is a play start with no minimum watch duration.** On autoplay in-feed placements, views and impressions can be near-identical, making "view rate" look extraordinary. **It is a play-start rate, not an attention metric.**
- **6-second views** — "played at least 6 seconds in an impression session, **played in full if under 6 seconds, or received at least 1 engagement within the first 6 seconds**." **The biggest counting trap on TikTok: a 6-second view does not require 6 seconds of watching.** TikTok even splits the field, with `paid_engagement_engaged_view` defined as receiving a positive interaction "**without being viewed for 6 seconds**."
- **Quartiles vs average play time** — a direct internal contradiction: quartile and view counts **exclude** replays, but average play time **includes** them. **On short looping creative, average play time can exceed the video's own duration while the 100% view count stays flat.**
- **Source** — ads.tiktok.com/help/article/video-play

---

## 3. LinkedIn Campaign Manager

### Impressions (viewability standard)
- **Definition** — For Sponsored Content, an impression records only when the ad is "at least 50% in view… for at least one second on desktop or **300 milliseconds on mobile**."
- **Gotcha** — **LinkedIn is the outlier that applies a viewability gate to its own impression count — but only on Sponsored Content.** On the LinkedIn Audience Network "an impression counts when the ad renders on the partner's page," with no gate. **LAN-heavy campaigns carry structurally cheaper, lower-quality impressions inside the same CPM column.** The mobile threshold (300ms) is *below* the MRC 1-second standard.
- **Source** — linkedin.com/help/lms/answer/a445476 · /a424623

### Reach (member accounts)
- **Gotcha** — LinkedIn counts logged-in **member accounts**, not devices or cookies — genuinely deduplicated across devices in a way Meta/TikTok cookie-and-device blends are not. **LinkedIn reach and Meta reach are not the same kind of number.**

### Clicks (chargeable clicks)
- **Gotcha** — **LinkedIn's biggest counting trap.** The headline Clicks column is **chargeable-only**, and what counts as chargeable **changes with the objective**. For the **video views objective there are no chargeable clicks at all** — clicks display but none are charged, so **CTR reads near-zero**. Comparing CPC or CTR across LinkedIn objectives compares different definitions.
- **Source** — linkedin.com/help/lms/answer/a426672

### Engagement Rate vs Average CTR
- **Formula** — Engagement Rate = (paid + free clicks) ÷ impressions. Average CTR = **chargeable** clicks ÷ impressions.
- **Gotcha** — Different numerators over the **same** denominator. Engagement rate always exceeds CTR on the same ad, and **the gap is a definitional artifact, not a performance signal.**

### Video views
- **Definition** — "Two or more continuous seconds of playback while the video is at least 50% on screen."
- **Gotcha** — Stricter than TikTok's play-start and different from Meta's 3-second rule. LinkedIn reports **Plays** (play starts) separately. **Cross-platform "video views" comparison without stating the threshold is meaningless.**
- **Quartiles** — "including watches that **skipped to this point**"; Completions = **97–100%**, including skips. **Skip-ahead counts** — the exact opposite of TikTok's replay-excluded quartiles, so completion rates are **not comparable between the two platforms in either direction.**
- **Source** — linkedin.com/help/lms/answer/a426666

### Conversions and Conversion Rate
- **Gotcha** — View conversions are **inside the headline total by default**. Worse, Conversion Rate has a **mismatched numerator and denominator** — the numerator includes view-through conversions while the denominator is chargeable clicks, so **LinkedIn conversion rate can exceed 100%** on view-heavy campaigns.
- **Source** — linkedin.com/help/lms/answer/a420212 · /a422513

### Conversion window
- **Options** — **1, 7, 30 or 90 days**, set separately for click and view. **365-day** available for some categories via CAPI or CSV upload.
- **Gotcha** — **LinkedIn recommends 90-day click / 90-day view** to maximize captured conversions. That is a **90× longer view window than Meta's 1-day default** and 13× longer than TikTok's 7-day maximum. **Any cross-platform ROAS table built on each platform's recommended settings is comparing wildly different counting universes.**
- **Source** — linkedin.com/help/lms/answer/a426359

### Lead Form Opens
- **Gotcha** — A pre-submit click on Sponsored Content is counted **twice, in two columns**: "as a click **and** a lead form open."

---

## 4. Industry standards — IAB / MRC

Primary standards documents (fetched as PDFs):
- **S1** MRC *Viewable Ad Impression Measurement Guidelines* v2.0 (Aug 2015)
- **S2** IAB Tech Lab + MRC *Desktop Display Impression Measurement Guidelines* v7.1 (Oct 2017)
- **S3** IAB Tech Lab + MRC *Digital Video Impression Measurement Guidelines* v1.1 (Jun 2018)

### Ad Impression (begin-to-render)
- **Definition** — Responses from an ad delivery system to an ad request, filtered for invalid traffic, recorded as late as possible. **"The ad must be loaded and at minimum begin to render in order to count it as a valid ad impression."**
- **Gotcha** — **Begin-to-render does not mean visible.** The guideline states: **"It does not require any portion of the ad to be visible or displayed on screen."** A served impression can be a DOM insertion the user never had any chance to see. — S2

### Client-initiated counting (Count on Decision prohibited)
- **Gotcha** — Server-initiated counting ("count on decision"/"count on insertion") is **not acceptable**. MRC **excludes** Count-on-Decision impressions from the Rendered Served Impression base, noting "many ads served under a Count on Decision approach never actually render to the browser." **The single largest source of impression discrepancies between two systems.** — S2

### Tracked Ads
- **Definition** — Counted when the measurement vendor's assets have downloaded and initiated, **but prior to ad content loading and rendering**. "This metric should not be labeled as an Ad Impression, without qualification."
- **Gotcha** — **The standards-sanctioned home for the number many tools loosely call "impressions."** If a platform reports one undifferentiated figure, you cannot tell whether it is Ad Impressions or Tracked Ads — and the difference is exactly the inventory that never rendered. — S2

### Viewable Impression — Display (50% / 1 continuous second)
- **Definition** — ≥50% of pixels on an in-focus browser tab in viewable space, **and** held for **≥1 continuous second, post ad render**.
- **Gotcha** — Three traps. (1) **Order matters** — "the clock starts… only when the ad is determined to have met the 50% pixel threshold." Vendors running the tests concurrently inflate counts. (2) **Strong user interaction is a back door** — a legitimate click can count the impression viewable **even if 50%/1s is never met**; these must be segregated, and often are not. (3) **Container vs ad measurement** — some vendors measure the iframe container rather than the ad, silently breaking the pixel math. — S1

### Viewable Impression — Video (50% / 2 continuous seconds)
- **Definition** — 50%-pixel criterion held for **2 continuous seconds**; "not necessarily the first 2 seconds… any unduplicated content of the ad comprising 2 continuous seconds qualifies."
- **Gotcha** — (a) **In-stream only** — banner ads with embedded video are measured under the **display 1-second rule**, so a "video" line item in a social or native feed may legitimately be reported on the display standard. (b) **Ad pixels vs player pixels** — if viewability is based on 50% of the *player's* pixels rather than the ad's, **a small ad in a large player passes when it should fail.** — S1

### Large-format display (30% / 1 second, ≥242,500 pixels)
- **Gotcha** — The concession is **binary at 242,500 pixels** — a 970×90 or 728×250 gets no relief. **Format-level viewability rankings across a mixed buy compare two different standards**, with billboards scored on a materially easier test. — S1

### Measured Rate and Viewable Rate — the two that matter most
- **Measured Rate** = **(Viewable + Non-Viewable) ÷ Total Rendered Served Impressions.** MRC's example: (300 + 200) ÷ 1000 = **50%**.
- **Viewable Rate** = **Viewable ÷ (Viewable + Non-Viewable).** Example: 300 ÷ 500 = **60%**.
- **Gotcha** — **The denominator is measured, not served** — undetermined inventory is **excluded rather than counted as failure**. In MRC's own example **half the campaign was undetermined**. **A 70% viewable rate at a 40% measured rate describes 28% of the buy. A viewable rate quoted without its measured rate is uninterpretable.** MRC explicitly blocks the conservative alternative, calling it "overly conservative" — **the standard mandates the more flattering of the two available calculations.** — S1

### Impression Distribution
- **Gotcha** — Disclosure required only **at campaign level**; placement- or domain-level breakouts are outside the guarantee. Desktop browser, mobile browser and mobile in-app statistics must be reported **separately** — **a single blended viewability number across environments is non-compliant.** — S1

### Audibility
- **Gotcha** — **A "viewable" video impression under MRC may have been fully muted.** Audio detection is "strongly encouraged but not currently required." Even vendor audibility metrics typically measure player volume only. **A known open gap, not a settled definition.** — S1 · S3

---

## 5. Incrementality

### Meta — Lift test / holdout
- **Gotcha** — Meta states a lift test is not the same as an A/B test **"because A/B tests do not include randomized holdout groups."** **Treating an A/B winner as an incrementality result is the core error.**
- **Source** — facebook.com/business/help/552097218528551

### Meta — Conversion Lift
- **Stated minimums** — a campaign in the past year with **≥$5,000 USD** spend; **≥500 conversions** on 1-day click, 7-day click or 1-day view; campaigns over 90 days prorated (180 days → $10,000 / 1,000 conversions); signal quality via CAPI with **Event Match Quality > 5**.
- **Gotcha** — Randomization is **intent-to-treat** — the test group includes an "Unexposed Audience" that never actually saw the ad. Meta keeps them in to avoid overstating impact, which means **self-serve lift reads lower than any exposed-only comparison you build yourself.** Meta offers but **does not recommend** the post-test conversion window.
- **Source** — facebook.com/business/help/221353413010930

### Meta — incremental metrics
- **Formula** — `conversions_incremental` = test − control, **adjusted for population-size difference** (scaled control), reported with a **90% credible interval**. `conversions_incremental_share` = incremental ÷ exposed conversions. `conversions_CPiC` = spend ÷ incremental conversions. `sales_ROAS` = **incremental** sales ÷ spend.
- **Gotcha** — **Incrementality share is the number that exposes attribution inflation** — at 0.3, seventy percent of the conversions credited to exposed users would have happened anyway. Note Meta's lift-study `sales_ROAS` is an **incremental** ROAS **sharing a name with the very different Ads Manager ROAS**.
- **Conversion lift percent** — incremental ÷ `conversions_baseline`, a **modeled counterfactual** — **a small baseline mechanically inflates the percent.**
- **Source** — facebook.com/business/help/1092662031214127 · /673450219767299

### Meta — Lift vs Ads Manager
- **Gotcha** — Meta states the two are **"not meant to be compared."** Incremental conversions are computed "after first scaling your holdout group to be equal in size to your test group," which "isn't the same as the total conversions attributed to your ads in Ads Manager." **You cannot compute a clean "incrementality factor" by dividing one by the other.**
- **Source** — facebook.com/business/help/365383970855344

### Meta — Incremental attribution (the delivery model)
- **Gotcha** — This is **modeled, not experimental** — prediction, not a holdout. **Must not be confused with a Conversion Lift test result.**
- **Source** — facebook.com/business/help/2366718460372682

### Google — Conversion Lift
- **Formulas (stated)** — Incremental conversions = **Treatment − Control**. Relative lift = **Incremental ÷ Control**. iCPA = **Total ad spend ÷ Incremental conversions**. iROAS = **Incremental conversion value ÷ Total ad spend**.
- **Gotcha** — Google warns relative lift "can theoretically scale between −1 and infinity" and is sensitive to control-group size, so **relative lift should not be compared across studies** — compare absolute incremental conversions or iCPA.
- **Attributed vs incremental** — **incremental conversions ignore your attribution settings entirely** and compare treatment against control over the full study duration. **Any ratio between the two is a rough directional adjustment, not an exact incrementality multiplier.**
- **Source** — support.google.com/google-ads/answer/12003020 · /14102450

### Google — user-based lift minimums
- Holdback **1%–50%**; **$5,000 USD** and **1,000 conversions** for directional lift; minimum **7 days** but "typically recommend more than 14 days"; power selectable **50%–95%**, 90%+ recommended.
- **Gotcha** — Google quantifies the short-test penalty: **up to a 17% drop in Absolute Lift** in studies under 14 days, because conversion lag is not fully captured. **A 7-day test is permitted and will understate your incrementality.** Higher power means a larger holdout — **rigor is bought with suppressed reach.**
- **Source** — support.google.com/google-ads/answer/12005564

### Google — geo lift
- Randomization units are **Google Marketing Areas (GMAs)**, built by spectral clustering. iROAS = Incremental conversion value ÷ **Incremental Cost** (note: **incremental cost, not total spend**, unlike the user-based iROAS).
- **Gotcha** — The GMA design trades **contamination** against statistical validity, so geo tests **cannot resolve anything at user level** and cannot answer audience or creative questions. **The iROAS denominator differs between geo and user methodologies, so the two iROAS figures are not directly comparable.**
- **Source** — support.google.com/google-ads/answer/14097193

### Google — Search Lift
- **Minimum** — **$10,000 USD** in the US. Budgets are **not additive** when measuring Brand and Search Lift together.
- **Gotcha** — **A demand signal, not a conversion signal.** Treating a search-query lift as revenue impact **double counts** against a Conversion Lift study on the same media.

### Google — Custom experiments (not lift)
- **Gotcha** — A head-to-head of two configurations, **not ad-versus-no-ad**, so it cannot produce incremental conversions. **Search-based splits reach significance faster precisely because they leak the same user into both arms** — which is what invalidates them causally. Google states **you cannot pool multiple experiments after the fact to manufacture significance.**
- **Source** — support.google.com/google-ads/answer/6261395 · /9232676

**Not verified / omitted:** No Meta Business Help Center article on **geo lift** surfaced; Meta's Conversion Lift docs make no mention of a geo-split product. TikTok's Attribution Manager article returns "no longer exists."

---

## 6. Why the same campaign reports different numbers in Meta vs an MMP vs GA4

1. **Meta dates conversions to the impression/click; GA4 dates them to the conversion.** A conversion today from a click five days ago lands on Meta's five-days-ago row and GA4's today row. Meta's recent days keep changing after the fact. — facebook.com/business/help/458681590974355
2. **Meta's default includes view-through and engage-through credit; a click-based analytics tool has no equivalent.** GA4's non-data-driven models are last-click. **A Meta view-through or engage-through conversion has no representation in GA4 at all.**
3. **Click-through now requires a *link* click on Meta, and 28-day windows are gone** — and two accounts can be on different definitions simultaneously during rollout.
4. **Recommended defaults differ wildly.** LinkedIn **recommends 90-day click / 90-day view**; Meta's default view window is **1 day**; TikTok's max view window is 7 days. **A cross-platform ROAS table built on each platform's own recommendation compares a 90-day view-through number against a 1-day one.**
5. **The MMP is deliberately not governed by the platform's attribution setting.** TikTok states outright its window "doesn't impact your MMP reporting." The two diverge **by design**.
6. **Each platform dedupes only within itself; nothing dedupes across platforms.** One person reached by all three appears as three reached users when summed.
7. **A material share of platform conversions is modeled, not observed** — Purchase ROAS models the **assigned values** as well as the counts; AEM adds up to 72-hour delay and removes demographic breakdowns. **Modeled conversions have no row in a warehouse or an MMP to match against.**
8. **Core reach and spend figures are formally "estimated" and disclaimed for exactly this use** — Meta permits them for directional guidance but **not for billing and not for historical comparison**, which is precisely what a reconciliation attempts.
9. **"Impressions" is not one thing.** Meta's video impression counting "differs from industry standards"; LinkedIn gates Sponsored Content at 50%/1s desktop and **300ms** mobile but applies no gate on its Audience Network; TikTok exposes `gross_impressions` including invalid impressions. **Under IAB/MRC none of these is a viewable impression.**
10. **"Clicks" is not one thing either, and neither is a video view.** Meta counts 3 seconds (replays excluded), TikTok counts a **play start with no minimum duration**, LinkedIn requires **2 continuous seconds at ≥50% on screen**. **A blended cross-platform CTR or view rate is arithmetic over incompatible units.**
11. **GA4's own scope model splits the answer before attribution is even applied.** Session-scoped dimensions are unaffected by the attribution model while event-scoped key-event credit uses it — **two GA4 reports can disagree with each other about the same campaign** before any comparison to Meta.
12. **None of these numbers is incrementality, and the platforms say so.** Meta: lift results and Ads Manager conversions are "not meant to be compared." Google: incremental conversions ignore attribution settings entirely. **Reconciling Meta to an MMP to GA4 harmonizes three attribution systems; it does not move any of them closer to causal truth.**
