# Google Stack Metric Definitions — raw research

> Every entry below was verified against a Google-hosted page that was actually fetched. Nothing from memory.
> Omitted deliberately (no Google page confirmed them): a 28-day active-users definition (`active28DayUsers` appears only in third-party write-ups; Google's UI documents 1/7/**30**-day).

---

## Google Analytics 4

### Active users
- **Definition** — Unique users who engaged with the site or app in the date range. The default/primary user metric in GA4 reports.
- **Formula** — None stated. A user qualifies via an engaged session, or by triggering `first_visit`/`first_open`, or by sending `engagement_time_msec`. On iOS, `first_open` or `user_engagement` is required.
- **Used in** — Nearly every standard report; the headline "Users" number is Active users.
- **Gotcha** — Not the same population as Universal Analytics "Total Users". Not all new users are active, so **New users can exceed Active users** — looks like a data error, is definitional. Google Ads exports include active *and* inactive users, so the same property yields different user counts per export surface.
- **Source** — https://support.google.com/analytics/answer/12253918?hl=en

### Total users
- **Definition** — Unique users who triggered any event in the date range.
- **Used in** — Explorations; available as a secondary metric in reports.
- **Gotcha** — Closest analogue to UA "Users", but **not** what GA4 reports show by default. Google's migration guidance says Total Users in Explorations is more comparable to UA than the Users metric in reports.
- **Source** — https://support.google.com/analytics/answer/12253918?hl=en

### New users
- **Definition** — New unique users who logged `first_open` or `first_visit` in the range.
- **Gotcha** — Anchored to the analytics client identifier: a cookie clear, reinstall, or new device manufactures a new user. Does not match Play Console user acquisitions, which are Google-account-scoped across devices.
- **Source** — https://support.google.com/analytics/answer/12253918?hl=en

### Returning users
- **Definition** — Unique users who initiated at least one previous session, regardless of whether that session was engaged.
- **Gotcha** — New + Returning does **not** reconcile to Active users; the qualifying conditions differ (previous session vs engagement in this range).
- **Source** — https://support.google.com/analytics/answer/12253918?hl=en

### 1-day / 7-day / 30-day active users
- **Definition** — People who used the site/app in the past 30, 7, and 1 days. Only users who engaged while the site was in focus or the app in the foreground count.
- **Formula** — Overlapping rolling windows anchored on the end of the report range, **not** disjoint buckets.
- **Used in** — Engagement overview, "User activity over time" card.
- **Gotcha** — GA4's long window is **30 days, not 28**. Play Console MAU is a rolling 28 days, so GA4 MAU and Play MAU differ by construction before any identity difference.
- **Source** — https://support.google.com/analytics/answer/12995458?hl=en

### User stickiness (DAU/MAU, DAU/WAU, WAU/MAU)
- **Definition** — Compares engagement over a narrower time frame with a broader one. DAU = last 24h, WAU = last 7d, MAU = last 30d.
- **Formula** — DAU/MAU, DAU/WAU, WAU/MAU.
- **Gotcha** — MAU is a rolling 30 days, not a calendar month and not Play's 28. Any DAU/MAU benchmark from product-analytics literature will silently mismatch.
- **Source** — https://support.google.com/analytics/answer/12993725?hl=en

### Active users in last 30 minutes
- **Definition** — All users on the site/app in the last 30 minutes (also a 5-minute variant).
- **Used in** — Realtime report.
- **Gotcha** — Raw time-window count with no stated engagement qualification, so it will not reconcile with Active users in standard reports for the same period.
- **Source** — https://support.google.com/analytics/answer/9271392?hl=en

### Sessions
- **Definition** — A period during which a user interacts with the site/app; begins when the app opens in the foreground or a page/screen is viewed and no session is active.
- **Formula** — Counted by **estimating** unique session IDs using HyperLogLog++ (since Oct 2021).
- **Gotcha** — Three compounding traps. (1) Sessions end only after 30 min inactivity with no maximum duration; unlike UA they do **not** restart at midnight and do **not** restart on campaign-parameter change, so GA4 systematically reports fewer sessions than UA for the same traffic. (2) The count is a statistical estimate, so it will not tie to `COUNT(DISTINCT ga_session_id)` in BigQuery. (3) `ga_session_id` is a start timestamp in seconds, not a globally unique ID.
- **Source** — https://support.google.com/analytics/answer/9191807?hl=en · https://support.google.com/analytics/answer/11986666?hl=en

### Engaged sessions
- **Definition** — A session that lasts longer than 10 seconds, **or** has a key event, **or** has 2+ screen/page views. Any one condition suffices.
- **Gotcha** — The key-event leg means this metric moves whenever you re-designate which events are key events, with zero traffic change. The 10-second threshold is configurable per property, so the metric is **not portable between two GA4 properties**.
- **Source** — https://support.google.com/analytics/answer/12195621?hl=en

### Engagement rate / Bounce rate
- **Formula** — Engagement rate = Engaged sessions ÷ Sessions. Bounce rate = 1 − engagement rate (exact inverse).
- **Gotcha** — Not comparable to an inverted UA bounce rate. UA bounce = "single-page session with no interaction"; GA4 bounce = "session that was not engaged". **A 15-second single-page read is a bounce in UA and an engaged session in GA4.** Historic bounce-rate benchmarks are unusable against GA4.
- **Source** — https://support.google.com/analytics/answer/12195621?hl=en · https://support.google.com/analytics/answer/11986666?hl=en

### Average engagement time
- **Definition** — Average time the website was in focus in the browser, or the app in the foreground.
- **Formula** — Denominator is **active users**, not sessions. Input is `engagement_time_msec`, sent when the page loses focus, the app is backgrounded, or the user navigates away.
- **Gotcha** — This is **not** "average session duration". Accrues only while in focus/foreground, so background audio, downloads, and offline usage register zero. Not comparable to UA's Avg. Session Duration, which included idle open-tab time.
- **Source** — https://support.google.com/analytics/answer/13391283?hl=en · https://support.google.com/analytics/answer/11109416?hl=en

### Average engagement time per session
- **Gotcha** — Sits next to "Average engagement time" in the same card with a **different denominator** (sessions vs active users). Picking the wrong one silently changes the number by the sessions-per-user factor.
- **Source** — https://support.google.com/analytics/answer/13391283?hl=en

### Engaged sessions per active user
- **Formula** — Engaged sessions ÷ Active users.
- **Gotcha** — Inherits every active-user qualification rule; it is **not** "engaged sessions ÷ total users".
- **Source** — https://support.google.com/analytics/answer/13391283?hl=en

### Views
- **Definition** — Number of app screens or web pages users saw. Repeated views of a single screen/page count separately.
- **Gotcha** — Merges web pageviews and app screenviews into one metric, and GA4 has **no "unique pageviews" equivalent at all**. Enhanced measurement detects page changes from browser history events, so SPAs generate views UA never recorded. Google states pageview discrepancies up to 10% between UA and GA4 are expected.
- **Source** — https://support.google.com/analytics/answer/13391283?hl=en

### Views per active user
- **Formula** — Views ÷ Active users.
- **Gotcha** — Denominator is active users, not sessions — this is **not** UA's "pages per session".
- **Source** — https://support.google.com/analytics/answer/12926732?hl=en

### Event count
- **Definition** — Number of times an event was collected.
- **Gotcha** — GA4 has no Category/Action/Label hierarchy; event names are reused with varying parameters, so UA "Total Events" and GA4 "Event count" count differently structured objects. Every interaction is an event including `page_view`, so account-level event totals are far larger than UA's.
- **Source** — https://support.google.com/analytics/answer/13391283?hl=en

### Key events (2024 replacement for "Conversions")
- **Definition** — An event measuring an action important to the business; any collected event can be marked as a key event. "Conversion" now specifically means the **Google Ads-side** action used to measure campaign performance and optimize bidding.
- **Gotcha** — Google split one word into two objects that do not reconcile. **Google Ads conversions do not appear in standard Analytics reports at all.** Conversions created from GA4 key events carry no historical data, so a newly created conversion shows zero history in Ads while Analytics shows a full backfill. Separately: **renaming an event that is already a key event silently removes its key-event status.**
- **Source** — https://support.google.com/analytics/answer/9267568 · https://support.google.com/analytics/answer/13965727?hl=en

### Modeled key events
- **Definition** — Google models online key events that cannot be observed directly, preserving attribution while protecting privacy.
- **Gotcha** — Attributed conversion data for a channel can keep updating for **up to 12 days** after the conversion is recorded, so recent-period channel numbers are provisional. Modeling applies only above a confidence threshold; below it, traffic falls to **"Direct"** instead — which reads as a channel-mix shift rather than a modeling gap. Triggers: missing third-party cookies, consent refusal, Apple ATT, cross-device paths.
- **Source** — https://support.google.com/analytics/answer/10710245?hl=en

### Behavioral modeling for consent mode
- **Definition** — ML estimates behavior of users who do not grant consent, based on similar users who do.
- **Eligibility** — ≥1,000 events/day with `analytics_storage='denied'` for ≥7 days, and ≥1,000 daily users with `analytics_storage='granted'` on ≥7 of the previous 28 days.
- **Gotcha** — Applies to **user-level** metrics (DAU, new users, journeys, geo, device) but **not** to event counts such as page views or session starts — so users and events drift apart. Modeled data is **not available in BigQuery export**, nor in audiences, retention reports, or sequence segments: the UI and the warehouse will never agree. A data-quality icon is the only signal estimation is in play.
- **Source** — https://support.google.com/analytics/answer/11161109?hl=en

### Reporting identity (Blended / Observed / Device-based)
- **Definition** — Blended = User-ID → device ID → modeling. Observed = User-ID → device ID. Device-based = device ID only.
- **Gotcha** — Switching is **fully retroactive**: every historical user count in the property changes the moment someone flips this setting, with no annotation in reports. Blended and Observed also subject reports to data thresholds. **Any user-count benchmark must record which identity produced it.**
- **Source** — https://support.google.com/analytics/answer/10976610?hl=en

### User acquisition vs Traffic acquisition
- **Definition** — User acquisition is scoped to **new users** with user-scoped dimensions (First user source/medium/campaign); Traffic acquisition is scoped to **new sessions** with session-scoped dimensions (Session source/medium/campaign).
- **Gotcha** — Google explicitly warns **not** to compare metric values across the two reports. Worked example: a user arrives once from Google then returns 10 times directly → all 11 sessions under "Google" in User acquisition, but 1 under Google and 10 under "(direct)" in Traffic acquisition. Both reports show identically named metrics, which is exactly why the mistake is so common.
- **Source** — https://support.google.com/analytics/answer/14731736?hl=en

### Reporting attribution model
- **Definition** — Data-driven uses your account's own data and ML to weight click interactions; paid-and-organic last click ignores direct traffic and gives 100% credit to the last channel clicked (or engaged-view for YouTube).
- **Applies to** — Only **event-scoped** traffic dimensions (Source, Medium, Campaign, Default channel group) and the metrics Key events, Total revenue, Purchase revenue, Total ad revenue.
- **Gotcha** — Does **not** affect user- or session-scoped traffic dimensions (Session source, First user medium), so two reports in the same property can attribute the same revenue differently and both be "correct". Changing the model applies to **historical and future** data, silently restating past reports. First click, linear, time decay, and position-based were removed in Nov 2023, so any pre-2024 model comparison cannot be reproduced.
- **Source** — https://support.google.com/analytics/answer/10597962?hl=en

### Session key event rate / User key event rate
- **Definition** — `sessionKeyEventRate`: percentage of sessions in which any key event was triggered. `userKeyEventRate`: percentage of users who triggered any key event.
- **Gotcha** — Both are "any key event" rates, not per-event-type — a session/user counts once regardless of how many distinct key events it triggered, so this rate cannot be decomposed into per-key-event contributions without pulling per-event data separately.
- **Source** — https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema (GA4 Data API metrics reference)

### Purchase revenue family — purchaseRevenue vs grossPurchaseRevenue vs totalRevenue vs refundAmount
- **Definition** — `purchaseRevenue`: sum of purchase revenue, **net of refunds**. `grossPurchaseRevenue`: sum of purchase revenue, explicitly **not** net of refunds. `totalRevenue`: purchase + subscription + ad revenue, net of refunds. `refundAmount`: refunds as their own separate metric.
- **Gotcha** — A UI-exported column headed "Purchase revenue" can trace to either `purchaseRevenue` (net) or `grossPurchaseRevenue` (gross) — the label alone does not disambiguate which API metric produced it, and the two differ by exactly the refund amount.
- **Source** — https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema (GA4 Data API metrics reference)

### returnOnAdSpend
- **Definition** — `returnOnAdSpend = totalRevenue ÷ advertiserAdCost`.
- **Gotcha** — Because `totalRevenue` (above) already folds in the app's own ad revenue alongside purchase/subscription revenue, GA4's native ROAS inherits the same ad-revenue-in-the-numerator conflation already documented for Adjust's ROAS elsewhere in this research set — not a pure e-commerce ROAS, and not comparable to AppsFlyer/Meta/Google Ads/Triple Whale ROAS without checking whether ad revenue is present.
- **Source** — https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema (GA4 Data API metrics reference)

### Default Channel Group — Direct
- **Definition** — Source exactly matches `(direct)` AND Medium is one of `(not set)`/`(none)`. Described as traffic arriving "via a saved link or by entering your URL."
- **Gotcha** — This page states the technical classification rule only. It does **not** enumerate *why* a session's referrer ends up empty (HTTPS→HTTP stripping, in-app browsers, incomplete UTM tagging are common practitioner explanations, not confirmed here). Don't cite those specific causes as GA4-documented — only the classification rule itself is confirmed.
- **Source** — https://support.google.com/analytics/answer/9756891

### Key event lookback window
- **Formula** — Acquisition key events (`first_open`, `first_visit`): default **30 days**, alternative 7. All other key events: default **90 days**, alternatives 30 or 60. Engaged-view: default 3 days.
- **Gotcha** — GA4's 90-day default is longer than Google Ads' 30-day click default and far longer than Meta's 7-day-click/1-day-view, so identical campaigns **can never reconcile without normalizing windows first**. Unlike the attribution model, lookback changes apply **going forward only**, creating an invisible discontinuity mid-flight.
- **Source** — https://support.google.com/analytics/answer/16291704?hl=en

### Data thresholds
- **Definition** — Applied to prevent inferring the identity or sensitive information of individual users. System-defined, not disclosed, not adjustable.
- **Gotcha** — Rows **silently vanish rather than showing zero**, so totals do not sum and the same query over a wider date range returns *more* data — reads as a traffic increase. Enabling Google Signals or a Blended/Observed identity increases exposure. BigQuery export avoids thresholds but excludes Google Signals data, so **neither surface is complete**.
- **Source** — https://support.google.com/analytics/answer/9383630?hl=en

### The (other) row / cardinality
- **Definition** — Appears when rows exceed the table's row limit; less common dimension values are condensed into it. Any dimension with >500 values is high-cardinality. Google's example: 100k row limit, 150k unique pages → last 50k under (other).
- **Gotcha** — Limits differ between standard and 360, differ per report, and shrink when you add secondary dimensions, filters, or comparisons. The same underlying data returns different long-tail detail depending on how the query was built, and **a metric summed from a table with an (other) row is not the property total.**
- **Source** — https://support.google.com/analytics/answer/9309767?hl=en

### (not set)
- **Definition** — Placeholder used when Analytics received no information for a dimension.
- **Gotcha** — **The cause differs per dimension**, so one "(not set)" bucket is really several unrelated failures: unlinked Ads account or auto-tagging off; incomplete/incorrect UTMs; missing `session_start` (often a GTM trigger misconfiguration) for Session source/medium; missing `page_view` for Landing page; the first 24 hours after registering a custom parameter; consent-mode misconfiguration blocking `user_engagement`. **Treating (not set) as one traffic category is always wrong.**
- **Source** — https://support.google.com/analytics/answer/13504892?hl=en

### Reports vs Explorations differences
- **Gotcha** — Google documents the same query returning different numbers: unsupported dimensions/metrics silently dropped in Explorations; Explorations use case-**sensitive** filters while reports are case-insensitive; comparisons convert to segments and drop unsupported fields; Explorations are capped by the property's data-retention setting while reports are not; thresholding bites differently; behavioral modeling differs; last 48 hours differ due to processing.
- **Source** — https://support.google.com/analytics/answer/9371379

### GA4 vs Universal Analytics tolerance bands
- **Formula** — Google's own acceptance criteria: pageview discrepancies up to **10%**, user/session discrepancies up to **20%** are expected.
- **Gotcha** — Any historical trendline spanning the migration has a built-in step change of up to 20% on user and session metrics that is **not a real business change**.
- **Source** — https://support.google.com/analytics/answer/11986666?hl=en

---

## Google Ads

### Impressions
- **Definition** — How often the ad is shown; one impression each time it appears. **Partial displays still count.**
- **Gotcha** — A served-impression count, not viewability. Comparing to Meta's or a DSP's viewable impressions (or to Active View, reported separately) overstates inventory quality.
- **Source** — https://support.google.com/google-ads/answer/6320?hl=en

### Clicks
- **Definition** — Counted when someone clicks the ad. Invalid clicks (accidental, automated, bots) are filtered and not charged.
- **Gotcha** — **A click is recorded even when the user never reaches the site** due to a technical issue, so Ads clicks structurally exceed GA4 sessions. Invalid-click filtering happens on Google's schedule, so clicks are not a stable joinable key with any external log.
- **Source** — https://support.google.com/google-ads/answer/31799?hl=en

### CTR
- **Formula** — Clicks ÷ Impressions.
- **Gotcha** — Denominator is served impressions, numerator includes clicks that never landed. Search and Display/Video CTR share one column name but describe different behavior, so **account-level blended CTR is meaningless** and cannot be benchmarked against Meta.
- **Source** — https://support.google.com/google-ads/answer/2615875?hl=en

### Avg. CPC
- **Formula** — Total cost of clicks ÷ total clicks.
- **Gotcha** — Backward-looking average of actual charges, not your bid. For Hotel ads, Avg. CPC can legitimately exceed max. CPC because the bid is multiplied by nights.
- **Source** — https://support.google.com/google-ads/answer/14074?hl=en

### Cost
- **Gotcha** — The billable event varies by format **inside one column** (clicks, views, calls), so dividing account-level Cost by account-level Clicks silently folds in video spend that produced no clicks.
- **Source** — https://support.google.com/google-ads/answer/2454071?hl=en

### Conversions
- **Definition** — Conversions across primary conversion actions; may include modeled conversions including predicted cross-device.
- **Gotcha** — **The single biggest cross-platform trap: primary conversion columns are dated by the time of the CLICK, not the time of the conversion.** Google's own example puts both the click and a following-week conversion in last week. GA4 and virtually every other platform date on the conversion day, so recent Google Ads days under-report and backfill for weeks. A separate **"Conversions (by conv. time)"** column exists specifically for third-party comparison.
- **Source** — https://support.google.com/google-ads/answer/6270625?hl=en

### Conv. rate
- **Formula** — Conversions ÷ total eligible ad interactions.
- **Gotcha** — Can legitimately **exceed 100%** with multiple conversion actions or "Every" counting. The denominator is *interactions* (clicks, swipes, video views, calls by format), not sessions or users — not the same construct as a GA4 session key event rate.
- **Source** — https://support.google.com/google-ads/answer/2684489?hl=en

### Cost/conv.
- **Formula** — Total cost ÷ the "Conversions" column.
- **Gotcha** — Numerator is real spend in the period; denominator is back-dated to the click. On recent ranges CPA looks inflated then falls for weeks. Also blended across all primary conversion actions, so **adding a soft action to primaries "improves" CPA with no business change.**
- **Source** — https://support.google.com/google-ads/answer/6270625?hl=en

### Conv. value / Value/conv. / All conv. value
- **Formula** — Value/conv. = total conversion value ÷ conversions.
- **Gotcha** — "Conversions" and "All conversions" are different populations, so their value columns are not interchangeable. Values are whatever you passed in — tax, shipping, currency handling are your configuration, not a Google standard — so it will not tie to GA4 or backend revenue by default.
- **Source** — https://support.google.com/google-ads/answer/6270625?hl=en

### Conv. value/cost (Google's ROAS column)
- **Formula** — Conv. value ÷ Cost. ×100 for Target ROAS percentage.
- **Gotcha** — Google reports ROAS as a **ratio** (4.0) while the Target ROAS setting is a **percentage** (400%). Numerator inherits click-date dating and modeling; denominator is same-day spend — so the ratio is depressed on recent dates and rises retroactively.
- **Source** — https://support.google.com/google-ads/answer/13405059?hl=en

### Impression share / Search lost IS (budget) / (rank)
- **Formula** — Impressions received ÷ **estimated** eligible impressions. Updates within 1-2 days.
- **Gotcha** — The denominator is an estimate by Google's own wording, based on targeting, approval status, quality, and bids — not an observed market total. **"Lost IS (budget) = 40%" does not mean uncapping budget yields 40% more impressions.** The budget variant exists only at campaign level, so ad-group and keyword-level gaps get attributed to rank even when budget was the real constraint. No other platform publishes an equivalent, so it cannot serve as cross-platform share of voice.
- **Source** — https://support.google.com/google-ads/answer/7103314?hl=en

### Quality Score
- **Definition** — 1-10 estimate of ad/keyword/landing-page quality. Components (expected CTR, ad relevance, landing page experience) each rated below/average/above average against advertisers whose ads showed for the **exact same search over the last 90 days**.
- **Gotcha** — Google explicitly states QS is **not used at auction time** to determine Ad Rank, is based on historical exact-search impressions, and **"is not a key performance indicator and should not be optimized or aggregated with the rest of your data."** Averaging it across keywords contradicts the documentation.
- **Source** — https://support.google.com/google-ads/answer/140351?hl=en · https://support.google.com/google-ads/answer/2454010?hl=en

### Views and View rate (Video)
- **Definition** — Skippable in-stream: 30 seconds or to the end (whichever first), or click on an interactive element. In-feed: thumbnail click, or inline autoplay ≥10 seconds. Shorts: 10 seconds or to the end, or CTA engagement. **Bumper and non-skippable in-stream ads generate no views.**
- **Formula** — View rate = Views ÷ Impressions.
- **Gotcha** — Google's 30s/10s bars are completely different from Meta's 3-second video view or ThruPlay. Formats generating zero views by definition still contribute impressions, so **any account-level view rate including them is mathematically depressed.**
- **Source** — https://support.google.com/google-ads/answer/2375431?hl=en

### Avg. CPV
- **Gotcha** — Includes only cost that was **eligible for views**, excluding bumper and non-skippable spend. Reconstructing video spend as Avg. CPV × Views under-counts real cost in any mixed-format campaign.
- **Source** — https://support.google.com/google-ads/answer/2382888?hl=en

### Video played to 25/50/75/100%
- **Definition** — Percentage of people who watched each quartile, **out of viewers who initiated the player**.
- **Gotcha** — The denominator is **player initiations**, not impressions and not views, and the initiation point differs by format (in-stream autoplays; in-feed and Masthead initiate only after a thumbnail click). Google says use directionally. **Cannot** be divided into impressions to build a completion rate, nor compared with Meta's impression-based watch percentages.
- **Source** — https://support.google.com/google-ads/answer/2375431?hl=en

### Conversion counting: "One" vs "Every"
- **Definition** — "Every" counts every conversion after an ad interaction; "One" counts one per ad click. **Every** is default for website actions, in-app actions, Analytics transactions, imported conversions; **One** is default for call conversions, Analytics goals, app installs.
- **Gotcha** — **The default differs by conversion source inside the same account**, so a website purchase and a call from one campaign are counted on different rules. "Every" makes Conv. rate exceed 100% legitimately. Not retroactive, so a mid-period switch creates an invisible step change.
- **Source** — https://support.google.com/google-ads/answer/3438531?hl=en

### Conversion window
- **Formula** — Click-through default 30 days (configurable 1-90 by campaign type). View-through default 1 day (up to 30). Engaged-view default 3 days (1-30). Changes apply to future conversions only.
- **Gotcha** — A 30-day click window plus click-date reporting means **the most recent 30 days are permanently incomplete and keep filling in** — the same past date returns different numbers when re-pulled weeks later. GA4's 90-day default and Meta's 7-day-click/1-day-view are different windows entirely.
- **Source** — https://support.google.com/google-ads/answer/3123169?hl=en

### Attribution model
- **Gotcha** — Data-driven is a per-account, per-conversion-action model whose weights are **undisclosed and not reproducible outside Google**, and it produces fractional conversions. First click, linear, time decay, and position-based are no longer supported and were auto-upgraded. GA4 and Meta apply their own models, so **summing platform-reported conversions across vendors always over-counts.**
- **Source** — https://support.google.com/google-ads/answer/6259715?hl=en

---

## Google Play Console

### User acquisitions (installs by user)
- **Definition** — Users who installed the app and did not already have it on any of their other devices at the time.
- **Gotcha** — Counted **per Google account across all devices**, not per device or per launch. One person installing on phone and tablet is a single acquisition — structurally lower than device-level installs, never matches an MMP's or Firebase's device-based count.
- **Source** — https://support.google.com/googleplay/android-developer/answer/139628?hl=en

### Install events
- **Definition** — Times the app was installed, **including** on devices where it had been installed previously.
- **Gotcha** — The only truly gross count. "Install events", "store listing acquisitions", and Firebase `first_open` are three different counting units.
- **Source** — https://support.google.com/googleplay/android-developer/answer/139628?hl=en

### Events vs Uniques vs Actives
- **Definition** — Event = every occurrence; uniques = users/devices that experienced an event; actives = active devices the app is installed on, or users with ≥1 such device.
- **Gotcha** — **Play ships the same nominal metric in three incompatible units, and the chosen variant is not visible in the chart title.** Most common source of Play-vs-analytics discrepancies.
- **Source** — https://support.google.com/googleplay/android-developer/answer/9419939?hl=en

### Active devices / install base
- **Definition** — Devices that checked in with Google at least once in the past 30 days; install base = active devices the app is installed on.
- **Gotcha** — "Active" means the **device checked in with Google**, not that the app was ever opened. An installed-footprint metric, not engagement.
- **Source** — https://support.google.com/googleplay/android-developer/answer/9419939?hl=en

### Active users (DAU / MAU) in Play statistics
- **Definition** — DAU = users who opened the app that day; MAU = users who opened it in a rolling **28-day** period.
- **Gotcha** — Play MAU = 28 days; GA4/Firebase MAU = 30 days. **The two dashboards disagree by construction** before any identity difference. Play counts accounts; Firebase counts app instances.
- **Source** — https://support.google.com/googleplay/android-developer/answer/139628?hl=en

### User loss (uninstalls by user)
- **Definition** — Users who uninstalled from all their devices, **or who stopped using every device the app is installed on for over 30 days.**
- **Gotcha** — A user counts as lost merely by going device-inactive for 30 days without uninstalling, so Play "uninstalls" bundle true churn with dormancy and lag reality by up to 30 days. Firebase `app_remove` fires on actual package removal (Android only) — the two series can never be reconciled.
- **Source** — https://support.google.com/googleplay/android-developer/answer/139628?hl=en

### Store listing visitors
- **Definition** — Users who visited the store listing and did not already have the app on any device.
- **Gotcha** — Deduplication is per day **and per dimension**, not per user, so one person arriving via Play search and again via a direct link the same day **counts twice**. Over-the-air and play.google.com web impressions are not tracked.
- **Source** — https://support.google.com/googleplay/android-developer/answer/9859173?hl=en

### Store listing acquisitions
- **Gotcha** — Runs lower than total installs because multi-device installs collapse into one acquisition. Excludes acquisitions from other Play surfaces (Promotional Content) and from backup-and-restore. **Store listing acquisitions ≠ Play installs ≠ MMP installs.**
- **Source** — https://support.google.com/googleplay/android-developer/answer/9859173?hl=en

### Store listing click-through rate (replaces legacy "Conversion rate")
- **Definition** — Percentage of store listing visitors who clicked a button (Install, Open, Pre-register). Play states this **replaces** the legacy "Conversion rate" metric.
- **Gotcha** — Measures the **click, not the completed install** — so the number people still call "store listing conversion rate" stops at button tap and reads higher than any install-based conversion rate from an MMP or Firebase `first_open`.
- **Source** — https://support.google.com/googleplay/android-developer/answer/9859173?hl=en

### First-time installers (acquisition reports)
- **Definition** — Unique users who installed X days after visiting the store listing in the Play Store app.
- **Gotcha** — Acquisition reports attribute the install back to the **visit** date and keep counting activity after the selected range ends — a Jan 11 visit with a Jan 15 install lands in a range ending Jan 12. This is why acquisition reports show higher installs than the Statistics page for the same dates.
- **Source** — https://support.google.com/googleplay/android-developer/answer/6263332?hl=en

### Retained installers
- **Definition** — Installers who kept the app on at least one device for the number of days shown. **Play states explicitly this does not mean the app was opened.**
- **Gotcha** — This is **installation** retention, not usage retention. A user who installed and never opened again counts as fully retained — Play can read ~70% Day-30 where Firebase/GA4 reads ~20% for the same app, and **both are correct**.
- **Source** — https://support.google.com/googleplay/android-developer/answer/6263332?hl=en

### Store listing visitors vs Google Ads clicks
- **Gotcha** — Play notes its visitor data will differ from Ads clicks because an ad click does not always result in a Play Store visit. The top of the Play funnel is systematically smaller than ad-platform clicks; using Ads clicks as the denominator for a Play conversion rate mixes two measurement points.
- **Source** — https://support.google.com/googleplay/android-developer/answer/9859173?hl=en

---

## Firebase / Google Analytics for Firebase

### Session / `session_start`
- **Gotcha** — Foreground-driven and client-generated: background work, silent pushes, and headless SDK activity never create a session. Not comparable to server-side sessions or Play's device check-in activity.
- **Source** — https://support.google.com/firebase/answer/9191807

### `ga_session_id` and the 30-minute timeout
- **Definition** — Session ID is the **timestamp in seconds** at session start; sessions time out after 30 min inactivity (configurable up to 7h55m), no upper length limit.
- **Gotcha** — Standard-report session counts are a HyperLogLog++ approximation, so Firebase session totals will not tie to a BigQuery `COUNT(DISTINCT ga_session_id)`.
- **Source** — https://support.google.com/firebase/answer/9191807

### `user_engagement`
- **Definition** — Logged when the app is in the foreground (or page in focus) for ≥1 second; `engagement_time_msec` carries active duration.
- **Gotcha** — Accrues only in the foreground. **An app whose value is delivered in the background looks dead in Firebase engagement reporting.**
- **Source** — https://support.google.com/firebase/answer/9234069?hl=en

### `first_open`
- **Definition** — Triggered the first time a user launches the app after installing or reinstalling — **at first use, not at download**.
- **Gotcha** — The biggest app-analytics reconciliation trap: a Play install with no first launch produces **zero** `first_open`, and a reinstall produces a **new** `first_open`. Store installs and analytics first-opens are different events on different days.
- **Source** — https://support.google.com/firebase/answer/9234069?hl=en

### `app_remove` / `app_clear_data`
- **Gotcha** — **Android only**, and counts package removals from any source, while Play "user loss" counts accounts losing the app across all devices or going 30 days inactive. Neither validates the other, and **iOS has no equivalent event**.
- **Source** — https://support.google.com/firebase/answer/9234069?hl=en

### Engaged sessions per active user (Firebase)
- **Formula** — Engaged sessions ÷ total users. Engaged = ≥10 seconds, or ≥1 key event, or ≥2 page/screen views.
- **Source** — https://support.google.com/firebase/answer/6317517?hl=en

### Average engagement time (Firebase)
- **Formula** — Total foreground time across all sessions ÷ total **active users**.
- **Gotcha** — Denominator is active users, not sessions — this is not average session length and will not match an MMP's session duration.
- **Source** — https://support.google.com/firebase/answer/6317517?hl=en

### Active users over time (1/7/30-day)
- **Gotcha** — Firebase monthly window is 30 days; Play Console MAU is 28. Counting unit is the **SDK-identified app instance**, not a Google account. **Same word, three different numbers across Play, Firebase, and any MMP.**
- **Source** — https://support.google.com/firebase/answer/6317517?hl=en

### Cohorts (Firebase console)
- **Definition** — Users who started using the app in the same period; retention shows percentage returning each day within their first **42 days**.
- **Gotcha** — Capped at a 42-day observation window — annual retention or subscription-renewal horizons **do not exist in this surface**.
- **Source** — https://support.google.com/firebase/answer/6317510?hl=en

### User retention by cohort / Day-N retention
- **Formula** — Day-N retention = (users returning N days after acquisition ÷ total users acquired that day) × 100. Vendor example: 4 users acquired Oct 1, 3 return by Oct 2 → Day 1 = 75%; 2 by Oct 8 → Day 7 = 50%; 1 by Oct 31 → Day 30 = 25%.
- **Gotcha** — Requires an actual **return visit**, whereas Play's retained installers only requires the app to still be installed. Putting the two side by side badly distorts retention in either direction.
- **Source** — https://support.google.com/analytics/answer/11004084?hl=en

### Crash-free users (Crashlytics)
- **Formula** — Crash-free users % = 1 − (crashed users ÷ all users). Crash-free sessions = 1 − (crashed sessions ÷ all sessions). A "user" = an individual installation on a device.
- **Gotcha** — Firebase states the value **should not be compared across different time periods**: it is an aggregation over the window, not an average, so a longer window mechanically lowers it. Only fatal events count, and the Crashlytics session (cold start, or foregrounding after 30+ min backgrounded) is defined separately from the Analytics session.
- **Source** — https://firebase.google.com/docs/crashlytics/crash-free-metrics

---

## Google Search Console

### Impressions
- **Definition** — How often someone saw a link to your site on Google; generally counted when the item appears on the current results page **whether or not the user scrolled to it**. Inside independently scrolling containers (carousels, expandable blocks) and infinite scroll, the item must actually be scrolled or expanded into view.
- **Gotcha** — A "present on the page" metric, not "seen on screen": a link at rank 40 earns an impression even if the user never scrolled past rank 3, **systematically inflating GSC impressions versus any viewability-based ad impression**. The rule then flips inside carousels, Images, News, and Discover — so impression volume is not defined consistently across search types *inside the same report*. Image results log one impression per host page URL even when several images appear; repeat views in one session collapse to one impression.
- **Source** — https://support.google.com/webmasters/answer/7042828?hl=en

### Clicks
- **Definition** — Counted when the user clicks a link taking them **outside** Google Search, Discover, or News. Re-clicking the same link after returning counts once.
- **Gotcha** — Query-refinement links, expanding an image thumbnail, and expanding a "People also ask" or FAQ entry are all **excluded**; only the link click inside the expanded element counts. GSC clicks are strictly "exits to your site" — a narrower event than a paid ad click and much narrower than a session or landing-page count.
- **Source** — https://support.google.com/webmasters/answer/7042828?hl=en

### CTR
- **Formula** — Clicks ÷ Impressions.
- **Gotcha** — **Not comparable to Google Ads CTR despite identical arithmetic.** The organic denominator includes results present on the page with no scroll or viewability requirement — including results the user demonstrably never looked at — pushing organic CTR structurally downward. The numerator is narrower. Ads occupy no positions in GSC's position model, so "CTR at position 3" means different slots in the two products. GSC CTR is generally **higher when aggregated by property than by page** whenever several of your pages rank for one query, so the same traffic yields two different CTRs depending on grouping.
- **Source** — https://support.google.com/webmasters/answer/7042828?hl=en · https://support.google.com/webmasters/answer/17011364

### Average position
- **Definition** — Position is the relative slot top-to-bottom, primary side then secondary; each result element occupies a single position shared by its links. Average position takes the **topmost** position your link occupied for each query and averages across queries that produced an impression.
- **Formula** — Google's worked example: query 1 shows positions 2, 4, 6 → records 2; query 2 shows 3, 5, 9 → records 3; average = 2.5.
- **Gotcha** — **Not a ranking.** Google states the value depends on context (mobile vs desktop, image layout, screen width) and should be watched for change over time rather than read as absolute rank. Only the best position per query enters the average, so extra deeper listings never drag it down. Ads occupy no positions, so an organic "position 1" can sit well below the fold. Comparing it to a rank tracker or Ads auction position metrics is invalid.
- **Source** — https://support.google.com/webmasters/answer/7042828?hl=en

### Data aggregation type (by property / by page)
- **Definition** — By property: all results for the same query pointing to the same property count once. By page: each unique URL counts separately. Grouping by Pages or Search Appearance **forces page aggregation**, while graph data is always aggregated by property.
- **Gotcha** — **The biggest source of "the numbers don't match" inside GSC itself**: the chart is always property-aggregated while the table silently switches to page aggregation when you pick Pages or Search Appearance. CTR and average position are generally higher under property aggregation. Discover never aggregates by property — a third rule. Any cross-platform benchmark must state which aggregation produced it.
- **Source** — https://support.google.com/webmasters/answer/17011364 · https://support.google.com/webmasters/answer/17011259

### Anonymized queries / data limits
- **Definition** — Queries made a very small number of times, or containing personal/sensitive information, may not be tracked or shown. Only top data rows are stored; tables display max 1,000 rows.
- **Gotcha** — **Table rows will not sum to the chart total, by design.** Applying a query filter drops anonymized queries out of the totals too, so the same date range yields a smaller total once filtered — an artifact, not a traffic change. GSC tracks daily data in **Pacific time**, not your account time zone, and data takes 2-3 days to appear with the newest days preliminary.
- **Source** — https://support.google.com/webmasters/answer/96568?hl=en · https://support.google.com/webmasters/answer/17011364

### Search appearance
- **Gotcha** — Clicks attach to URLs, not URL-plus-feature pairs, so Google warns it is **not guaranteed** that all clicks under a filtered appearance type were on the link carrying that feature. Selecting this dimension also forces page aggregation, shifting CTR and position at the same time you change the filter. Feature-level CTR is directional at best.
- **Source** — https://support.google.com/webmasters/answer/17011259 · https://support.google.com/webmasters/answer/6211453?hl=en

### Discover metrics
- **Definition** — An impression is counted when the item is **scrolled into view**, one impression per result per session. A click counts only on the item click; sharing does not.
- **Gotcha** — **There is no position metric in Discover at all**, so no average-position trend exists to explain volume swings. Discover impressions are never aggregated by property, so Discover cannot be blended with property-aggregated Search totals.
- **Source** — https://support.google.com/webmasters/answer/9216516?hl=en

### Google News metrics
- **Gotcha** — The News tab **inside Google Search is not in this report**; it lives in the Search results report under the News search type — so the same editorial content is split across two reports with two different impression rules (scroll-required here, present-on-page there). In-article swipes and notifications are excluded, attribution uses canonical URLs rather than the landing page, app data exists only from Nov 2020, and there is no position metric.
- **Source** — https://support.google.com/webmasters/answer/10083653?hl=en
