# MMP / Attribution Metric Definitions — raw research

> Every entry verified against a vendor page that was actually fetched.
> Not verified, deliberately omitted: Adjust's "Limited" attribution status; a standalone AppsFlyer Retention article (retention formula taken from the Cohort & Retention dashboard page instead); Adjust's `/en/article/fraud-prevention` page (404 — definitions taken from the Datascape glossary and Protection Dashboard).

---

## 1. Adjust

### Installs
- **Definition** — Adjust counts an install only after a user downloads the app **and opens it for the first time**. A download without a first open is not an install.
- **Used in** — Datascape, Campaign Lab; denominator of eCPI/CCR/ICR.
- **Gotcha** — Apple Ads and app stores report *downloads* at store level; Adjust counts only the first open — a permanent structural gap on iOS. Adjust counts per device, not per store account.
- **Source** — https://help.adjust.com/en/article/datascape-metrics-glossary · https://help.adjust.com/en/article/apple-ads-reporting

### Reattributions
- **Definition** — A previously inactive user engages with a retargeting campaign, returns, and is assigned a new attribution source. Requires: prior install on device, engagement with an Adjust link using a **different token** than the original, an in-app session within the reattribution window, and prior inactivity for the configured period.
- **Gotcha** — A *separate* metric from installs. The network running the retargeting campaign usually counts the same event as a **fresh install** in its dashboard, so MMP installs < network installs by exactly the reattribution volume.
- **Source** — https://help.adjust.com/en/article/reattribution

### Reattribution vs Reinstall (redownload)
- **Definition** — A reinstall is a device recorded as uninstalled that later shows as installed again. A reattribution updates the source of a returning user; a redownload creates a **new install record** and re-runs attribution from scratch.
- **Gotcha** — Uninstalls are measured via daily silent push tokens, and Adjust dates the uninstall to the **last active session**, not the detection day (which can lag up to a week). On iOS 15+, Adjust only receives push updates from apps recently run in the foreground, so uninstall/reinstall counts **under-report dormant users**.
- **Source** — https://help.adjust.com/en/article/uninstalls-reinstalls

### Sessions
- **Definition** — App opens recorded by the SDK; a new session after **30 minutes** of inactivity.
- **Formula** — `sessions = base_sessions + installs + reattributions`
- **Gotcha** — The 30-minute rule is an Adjust convention. AppsFlyer counts every foreground return; GA4 counts differently again. **"Sessions" is one of the least comparable metrics across tools.**
- **Source** — https://help.adjust.com/en/article/datascape-metrics-glossary

### Clicks / Impressions
- **Definition** — For self-attributing networks (SANs), the counts *received from the network*; for non-SANs, what Adjust measures directly on its links.
- **Gotcha** — **Two different data-collection mechanisms behind one metric name.** SAN numbers are the network's own definition (Adjust relays them); non-SAN numbers are Adjust's. Never compare CTR across SAN and non-SAN sources.
- **Source** — https://help.adjust.com/en/article/datascape-metrics-glossary

### Attribution methods
- **Definition** — Matching a user to the source that drove the install; click-based and impression-based (view-through) engagement, matched deterministically on advertising/device IDs (IDFA, GPS ADID, IDFV, Android ID, OAID, Play Store referrer) with probabilistic modeling as fallback.
- **Gotcha** — Deterministic and probabilistic matching carry **different window lengths**, so the same campaign can win or lose attribution purely on which method fired. On iOS 14.5+, probabilistic modeling is restricted to owned media, cross-promo, and consented web-to-app.
- **Source** — https://help.adjust.com/en/article/attribution-overview · https://help.adjust.com/en/article/attribution-methods

### Attribution windows (defaults and ranges)
| Window | Range | Default |
|---|---|---|
| Click, device matching | 1–30 days | **7 days** |
| Click, probabilistic | 1–24 hours | **6 hours** |
| Impression, device matching | 1–24 hours | **24 hours** |
| Impression, probabilistic | 1–24 hours | **6 hours** |
| Temporary attribution | 1–90 days | **7 days** |
| Inactivity (reattribution eligibility) | 0–365 days | **7 days** |
| Reattribution, clicks/device matching | 1–30 days | **7 days** |
| Reattribution, impressions | 1–24 hours | **24 hours** |
| Cross-device probabilistic inactivity | 1–72 hours | **24 hours** |

- **Gotcha** — **The single largest source of MMP-vs-network install gaps.** Adjust's own docs note partners run their own windows (Google 30 days, Facebook 60 days), so any install landing between Adjust's 7-day default and the network's window is **Organic in Adjust and paid in the network dashboard**.
- **Source** — https://help.adjust.com/en/article/attribution-windows · https://help.adjust.com/en/article/data-discrepancies

### Organic / unattributed
- **Gotcha** — **"Organic" in an MMP is a residual bucket, not a channel.** Anything that fell outside a window, failed device matching, or was rejected by fraud filters lands here — so Organic inflates exactly when paid measurement degrades.
- **Source** — https://help.adjust.com/en/article/attribution-overview

### Cohort metrics
- **Formula** — Retention Rate = `Retained users N days / Cohort size N days` · Revenue Per User = `Revenue N days / Cohort size N days` · ARPU = `All revenue total N days / Cohort size N days` · **ARPDAU = `All Revenue Total / Total DAU in date range`**
- **Gotcha** — **ARPDAU is not cohorted** (it's a date-range activity metric) while **ARPU is cohorted** — mixing them in one deck produces numbers that can never reconcile. Cohort size includes reattributions where enabled, changing the denominator versus install-only cohorts elsewhere.
- **Source** — https://help.adjust.com/en/article/datascape-metrics-glossary

### eCPI / ROAS / ROI
- **Formula** — eCPI (all installs) = `Ad Spend / Installs` · ROAS = `(Cohort revenue + Cohort ad revenue) / Ad Spend` · ROI = `Cohort gross profit / Ad Spend`
- **Gotcha** — **Adjust's ROAS is a ratio, AppsFlyer's is a percentage** (`Revenue / cost * 100`) — the same campaign reads 0.8 in one tool and 80 in the other. Adjust's ROAS also folds in **ad revenue**; ad-network dashboards generally only see IAP revenue you post back.
- **Source** — https://help.adjust.com/en/article/datascape-metrics-glossary

### SKAdNetwork metrics (Adjust)
- **Formula** — Installs (SKAN) = valid SKAN postbacks where `redownload = false` · Valid Conversions = `Installs + Reinstalls − Conversion Value Null` · eCPI (SKAN) = `Ad Spend (SKAN) / Installs (SKAN)` · ROAS (SKAN avg) = Revenue (SKAN avg) × Installs ÷ (Ad Spend × Valid Conversions)
- **Gotcha** — SKAN installs and Adjust-attributed installs describe **the same users through two pipelines and must never be summed**. SKAN is never real-time: SKAN 3 enforces 24–48h minimum; SKAN 4 postbacks arrive across ~3–41 days post-install.
- **Source** — https://help.adjust.com/en/article/skadnetwork · https://help.adjust.com/en/article/skadnetworking-reporting

### Conversion Value / Conversion Value Null
- **Definition** — A 6-bit integer (0–63) mapped to in-app events. A **null** value means the install happened but Apple withheld detail because the campaign missed Apple's daily privacy threshold.
- **Gotcha** — **Null rate is a function of spend concentration, not user behavior** — low-budget or fragmented campaigns get nulled and therefore look like they produce zero-value users. Adjust's own guidance: the fix is more spend per campaign, not better mapping.
- **Source** — https://help.adjust.com/en/article/what-is-a-conversion-value

### Fraud prevention metrics
- **Definition** — Rejected Installs split by filter: Click Injection (falsified clicks between download start and install), Distribution Outlier, Anonymous IP (data centers, VPNs, Tor, cloud), SDK Signature failures. Rejected Install Rate excludes Organic and Untrusted Device installs from the total.
- **Gotcha** — Click injection is **Android-only**. Because rejected installs are removed from attributed traffic, **turning fraud prevention on mechanically lowers paid installs and raises Organic** versus the network's invoice.
- **Source** — https://help.adjust.com/en/article/fraud-prevention-dashboard · https://help.adjust.com/en/article/click-injection-filtering · https://help.adjust.com/en/article/anonymous-ip-filtering

### Assists
- **Definition** — An install where multiple ad engagements competed; the non-winning clicks/impressions inside the window are the assists. Organic users cannot be assists.
- **Gotcha** — Assists are **additive on top of** last-touch installs — an install with 3 assists produces 1 install and 3 assist records. **Summing installs + assists double-counts users.**
- **Source** — https://help.adjust.com/en/article/assists

---

## 2. AppsFlyer

### Install
- **Definition** — Recorded when a user downloads, installs, **and launches** the app.
- **Gotcha** — Aggregated dashboards are **LTV** (grouped by install date); raw data reports are **activity** (grouped by event date). Comparing the two without neutralizing both differences produces guaranteed mismatches.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/115005600889

### Organic vs Non-organic install
- **Formula** — Organic installs = `Total installs − All non-organic installs`
- **Gotcha** — Installs occurring **after** a lookback window expires are re-classified as Organic — so **shortening a lookback window moves paid installs into Organic with no change in user behavior**. Abnormal organic spikes can also be failed-attribution fraud (click flooding whose last click landed beyond the window).
- **Source** — https://www.appsflyer.com/glossary/non-organic-install/ · https://support.appsflyer.com/hc/en-us/articles/218254203

### Loyal user
- **Definition** — By default, a user who after first open launches the app a further **3 times**. Replaceable per app with any in-app event.
- **Gotcha** — AppsFlyer explicitly warns **fraudsters know the 3-launch default and fake it**; the metric is only meaningful once redefined against a real quality event. Non-comparable across accounts.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/207447003

### Retention
- **Formula** — `Retention = (On-day unique users who opened the app / conversions) * 100`
- **Gotcha** — Cohort periods are **calendar-based** (hours rounded down; days/weeks/months on calendar boundaries), **not** rolling 24h from install timestamp — AppsFlyer itself names this as a cause of mismatch with networks that cohort by install timestamp. Post-reinstall events treated as unattributed organic are excluded from retention counts.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/207040496

### Cohort
- **Formula** — Max horizons: 72 hours / 180 days / 156 weeks / 36 months.
- **Gotcha** — **Three view types give three different install universes**: User acquisition (reinstalls excluded unless specially enabled), Retargeting (re-attributions/re-engagements only), Unified (retargeting takes precedence, `is_primary_attribution=true`). **Cost is only included where an attribution exists**, so click/impression spend with no installs silently vanishes from cohort cost.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/207040496

### LTV vs Activity
- **Definition** — LTV = post-install event data **grouped by user acquisition date**. Activity = the same data **grouped by event date**. Installs are neither.
- **Gotcha** — **AppsFlyer's stated #1 cause of internal discrepancies.** Activity data includes events from installs *before* the range; LTV data includes events *after* the range. Most external platforms (Google, Apple) report Activity — Meta offers partial LTV limited to 28 days post-install — so external comparisons must use AppsFlyer raw/activity data.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/115005600889

### ROI / ROAS / eCPI / ARPU / eCPA
- **Formula** — ROI = `(Revenue − cost) / cost * 100` · ROAS = `Revenue / cost * 100` · Average eCPI = `Cost / attributions` (attributions = installs + re-engagements + re-attributions) · ARPU = `Revenue / unique users` · eCPA = `Cost / cumulative unique users performing the event`
- **Gotcha** — **eCPI divides by attributions, not installs** — retargeting conversions dilute it, and it will not match a CPI computed as spend÷installs. ROI/ROAS/cost are unavailable in Retargeting view and at hourly granularity.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/207040496

### Re-engagement vs Re-attribution
- **Definition** — **Re-engagement** = app is on the device and a retargeting source gets credit for the open. **Re-attribution** = app was deleted, user reinstalls via a retargeting campaign within the window, retargeting source is credited.
- **Windows** — View-through default 1 day (1–23h / 1–7d); click lookback default 7 days (1–23h / 1–30d); re-engagement window default 30 days (1–23h / 1–90d / lifetime); minimum inactivity 0–30 days (default none).
- **Gotcha** — During the re-engagement window, in-app events are **double attributed** — to the retargeting source (primary) and the original UA source (secondary). **Aggregating raw data without filtering `is_primary_attribution = TRUE` inflates event totals.** Re-attributions mint a **new AppsFlyer ID**; re-engagements keep the existing one — which is why GA4 (keyed on user ID) sees one user where AppsFlyer sees two.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/207033786 · https://support.appsflyer.com/hc/en-us/articles/4413026674833

### Assisted installs / Multi-touch / Contributor
- **Definition** — Installs where a source touched the user before the install and within the window but did not win last touch. **Up to 3 contributors** recorded per install, exposed as Contributor 1–3 with media source, campaign, engagement time/type, agency, match type.
- **Gotcha** — Networks that restrict user-level data **cannot appear as contributors at all**, so their real assist volume is structurally invisible. `total_candidates` counts engagements seen at install time, but many are ineligible — **a non-zero `total_candidates` with an Organic attribution is normal, not a bug.**
- **Source** — https://support.appsflyer.com/hc/en-us/articles/207040506

### Lookback windows
- **Formula** — Click-through: 1–30 days or 1–23 hours, **default 7 days**. View-through: **1–24 hours, default 24h**. Engaged click/view (selected non-SRNs): 1–7 days or 1–23 hours, **default 2 days**. Probabilistic modeling: **adaptive, up to 24 hours, ignores any window set on the link.** Link with no window parameter: 7 days click / 1 day impression. **SRN defaults: Google 30d click, Meta 7d, Snapchat 28d, X Ads 14d, Apple Search Ads 30d; all 24h view-through.**
- **Gotcha** — AppsFlyer explicitly instructs matching your window to the SRN's own default; the mismatch is **asymmetric** — a shorter AppsFlyer window pushes installs into Organic while the SRN still self-reports them. AppsFlyer's own distribution data: **~62% of installs happen within 15 minutes of engagement, ~72% within 1 hour, ~97% within 7 days** — so window length beyond 7 days moves only ~2–3% of volume but can move a lot of *credit*.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/208338403

### Self-reporting networks (SRN/SAN)
- **Definition** — Super-publisher platforms that attribute their own traffic without third-party input (Meta ads, Google Ads, X Ads).
- **Gotcha** — For SRNs, `engaged_click`/`engaged_view` cannot have their own lookback windows — they inherit the click-through window. AppsFlyer never sees the underlying engagements, only the network's claim, so **an SRN discrepancy can never be resolved by inspecting AppsFlyer's own click log.**
- **Source** — https://support.appsflyer.com/hc/en-us/articles/208338403

### Protect360 fraud metrics
- **Definition** — Blocks fraudulent attribution in real time (**before** attribution) and flags post-attribution fraud detected up to 7 days after install (8 days total). Blocked installs/events are **never attributed** and are absent from dashboards; post-attribution fraud is **marked but not erased**. Types: install hijacking (very short CTIT + Play Server-Side API), click hijacking, click flooding (low CVR + long CTIT), device ID reset fraud, behavioral anomalies, IP denylists, SDK authentication, store validation.
- **Benchmarks (AppsFlyer's own)** — Normal conversion rates 0.5–35% (suspect sources below 25% of your app average); CTIT >60 min should be ~30% of installs (suspect >50%); CTIT >5 hours ~20% (suspect >40%).
- **Gotcha** — **Two different reporting regimes for one word "fraud":** blocked traffic silently disappears from install counts, while post-attribution fraud stays inside them and must be manually subtracted. For fraudulent UA reinstalls, attribution is reassigned to **Organic**, moving spend-driven volume into your baseline.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/218254203

### SKAN + Single Source of Truth (SSOT)
- **Formula** — Non-organic AppsFlyer installs (A) + SKAN unique installs where `af_attribution_flag=false` (B) = **All non-organic installs (C)**. Organic installs = `Total installs − C`. Campaign eCPI = `Cost / C`.
- **Gotcha** — **The SKAN dashboard ignores the flag and does not deduplicate** — only the SSOT view and flag-aware raw queries do. Timezones split inside one view: AppsFlyer data uses app-local/UTC, SKAN data uses UTC **except Meta and Google SKAN**, which follow those accounts' own timezone settings. Google SKAN installs can arrive **up to 45 days late**; changing Conversion Studio config causes ~96h of inaccuracy while old- and new-schema postbacks overlap.
- **Source** — https://support.appsflyer.com/hc/en-us/articles/4410634145425

---

## 3. Branch and Singular

### Branch — Click / Impression / Install / Open
- **Windows** — click-to-install **7 days**, click-to-open **1 day**, click-to-event **30 days**, impression-to-conversion **1 day**, re-engagement inactivity **90 days**. Configurable at org, app, ad-partner level. Priority: deterministic (Install Referrer API, consented device IDs, SKAN/AdAttributionKit, Apple Ads, preload, direct deep links) → probabilistic fallback.
- **Gotcha** — Click-to-**open** (1 day) is far shorter than click-to-install (7 days), so **engagement and acquisition campaigns are judged on different clocks by default**. Branch's 90-day re-engagement inactivity default is an order of magnitude longer than Adjust's 7-day default — **the identical retargeting campaign yields wildly different re-engagement counts across the two MMPs with no config change.**
- **Source** — https://help.branch.io/marketer-hub/docs/branch-methodology-overview

### Branch — Last-touch vs install-touch attribution
- **Definition** — **Install-touch (ITA)** gives 100% credit for *all* downstream conversions to the last touch before the install. **Last-touch (LTA)** gives 100% credit for each conversion to the last click/impression before *that* conversion.
- **Gotcha** — Branch states ITA has a systemic bias toward install ads at the expense of engagement, owned, and earned activity. **This is the deepest definitional split between vendors:** install-touch credits the install source for a purchase 60 days later; last-touch credits whichever channel drove that purchase. Same raw data, entirely different channel P&L.
- **Source** — https://www.branch.io/resources/blog/whats-the-difference-last-touch-vs-install-touch-attribution/

### Branch — Deepview (web-to-app) metrics
- **Gotcha** — If a user without the app clicks a Branch link with an active Deepview but does **not** click the Deepview CTA, downstream installs and purchases are **not attributed back** to the original link click. **Web-to-app funnels leak attribution at the interstitial, and the leak shows up as Organic.**
- **Source** — https://help.branch.io/marketer-hub/docs/deepview-analytics

### Singular — MTA Installs, Assisted Installs, SAI, CAI
- **Definition** — Tracks up to four touchpoints (T-1…T-4) preceding the last attributing touchpoint (T0). **Assisted Installs** = a source had a touchpoint in T1–T4 but did not win last touch. **SAI** = last touchpoint had no other source touchpoints. **CAI** = last touchpoint had at least one other source touchpoint.
- **Formula** — Default model: `MTA Installs = (SAI × 1.0) + (CAI × 0.3) + (Applicable Assisted Installs at T-1 × 0.7)`. MTA eCPI = `total cost / total MTA Installs`. Constraint: total last-touch attributed installs must equal total modeled installs.
- **Gotcha** — **MTA Installs is a modeled, configurable number** — the 1.0/0.3/0.7 weights are per-organization business rules, so it is **not comparable between two Singular accounts**, let alone against another MMP. Singular dedupes per source (one click + one impression from the same source in T1–T4 count once) specifically to stop sources assisting their own installs. A longer CTV view window **mechanically manufactures more assists**.
- **Source** — https://support.singular.net/hc/en-us/articles/43108170707739

---

## 4. Apple — SKAdNetwork and AdAttributionKit

### Attribution eligibility time-windows
- **Formula** — StoreKit-rendered ad → **30 days** to install. View-through ad → **24 hours** to install. Attributable web ad tap → **30 days** to install. After install → **60 days** to launch. After install → **60 days** to send the first conversion value update.
- **Gotcha** — **Apple's view-through window is fixed at 24 hours and cannot be lengthened**, while MMP/network VTA windows are configurable — iOS view-through credit is capped by the OS regardless of your settings. StoreKit records a maximum of **15 view-through impressions per source app**, discarding the oldest, so high-frequency publishers lose impressions before attribution is even evaluated.
- **Source** — https://developer.apple.com/documentation/storekit/receiving-ad-attributions-and-postbacks

### Winning vs nonwinning postbacks (fidelity-type)
- **Definition** — From v2.2, attribution goes to the most recent impression with the **highest `fidelity-type`** — StoreKit-rendered ads are `1`, view-through ads are `0`. From iOS 14.6 (v3+), one winning postback (`did-win: true`) plus up to five nonwinning postbacks, one per ad network.
- **Gotcha** — **This is not last-touch.** A StoreKit-rendered ad always beats a more recent view-through ad, so SKAN's winner can differ from the MMP's last-touch winner for the same user. Nonwinning postbacks carry no `conversion-value` and no `source-app-id`.
- **Source** — https://developer.apple.com/documentation/storekit/receiving-ad-attributions-and-postbacks

### Conversion values (fine and coarse)
- **Formula** — Fine = 6-bit integer, 0–63. Coarse = low/medium/high tier.
- **Gotcha** — **The fine value is available only in the first postback**; postbacks 2 and 3 carry coarse values only. **Any SKAN "D7/D30 revenue" figure is modeled from a 3-bucket signal, not measured.**
- **Source** — https://developer.apple.com/documentation/adattributionkit/receiving-postbacks-in-multiple-conversion-windows

### Conversion windows and postback delays
- **Formula** — Three windows from first launch: **days 0–2**, **days 3–7**, **days 8–35**. Random delay **24–48 hours** for postback 1; **24–144 hours** for postbacks 2 and 3. Minimum impression-to-postback 24–48 hours. Tier 0 apps receive only the first postback.
- **Gotcha** — Randomized delay is deliberate anti-fingerprinting noise, so **postback arrival date ≠ install date**. Any daily SKAN install curve is a **delivery** curve, not a conversion curve, and late postbacks retroactively change "closed" days — which is why **SKAN D7 can appear lower than D2 before backfill completes**.
- **Source** — https://developer.apple.com/documentation/adattributionkit/receiving-postbacks-in-multiple-conversion-windows

### Crowd anonymity / postback data tiers
- **Formula** — Tier 3 → source-identifier (2/3/4 digits) + fine conversion value + publisher-item-identifier + country-code. Tier 2 → source-identifier + fine value. Tier 1 → **2-digit** source-identifier + coarse value only. Tier 0 → 2-digit source-identifier only, **and no second or third postback**. Postbacks 2 and 3 carry only a 2-digit source-identifier + coarse value at every tier.
- **Gotcha** — **Campaign granularity is granted by Apple, not chosen by you:** at Tier 1 or 0 the system falls back to the 2-digit source identifier, **collapsing your ad-set/creative structure into ~100 buckets**. Country-code only appears if that country's crowd is Tier 3.
- **Source** — https://developer.apple.com/documentation/adattributionkit/receiving-postbacks-in-multiple-conversion-windows

### AdAttributionKit reengagement postbacks
- **Gotcha** — For **reengagement** conversions a single ad network may receive winning postbacks across multiple windows and the framework generates **no runner-up postbacks** at all — so there is no OS-level way to see which other networks touched the user. **Assist/MTA analysis is structurally impossible for iOS reengagement.**
- **Source** — https://developer.apple.com/documentation/adattributionkit

---

## Why platforms disagree — 25 mechanical reasons

1. **Attribution window length mismatch.** Adjust default click window 7 days; partners run their own (Google 30d, Facebook 60d). AppsFlyer SRN defaults differ per network (Google 30d, Meta 7d, Snapchat 28d, X Ads 14d, Apple Search Ads 30d). Installs outside the MMP's shorter window become Organic while the network still bills them. — help.adjust.com/en/article/data-discrepancies · support.appsflyer.com/hc/en-us/articles/208338403
2. **Different attribution method, different window** within one MMP (Adjust click device-match 7d vs probabilistic 6h; AppsFlyer probabilistic adaptive ≤24h and *ignores* link-level windows). — help.adjust.com/en/article/attribution-windows
3. **Date-of-click vs date-of-event.** SANs attribute events to the click date, not the event date. — help.adjust.com/en/article/data-discrepancies
4. **LTV vs activity grouping.** AppsFlyer dashboards group by install date; raw data and most external platforms group by event date. Meta offers only partial LTV, capped at 28 days post-install. — support.appsflyer.com/hc/en-us/articles/115005600889
5. **Download vs first open.** Stores and Apple Ads count the download; MMPs count only the first launch. — help.adjust.com/en/article/apple-ads-reporting
6. **Device-based vs account-based counting.** Adjust counts per device; stores count per account. — help.adjust.com/en/article/data-discrepancies
7. **Timezone offset.** Adjust uses UTC; stores use configurable timezones. AppsFlyer app timezone vs GA4 property timezone shifts data by a full day. In SSOT, AppsFlyer data is app-local/UTC while SKAN is UTC — except Meta and Google SKAN. — help.adjust.com/en/article/data-discrepancies · support.appsflyer.com/hc/en-us/articles/4410634145425
8. **Identity model: device vs user.** GA4 associates by Customer User ID; AppsFlyer mints a **new AppsFlyer ID** on re-attribution — GA4 sees one user, AppsFlyer sees two. — support.appsflyer.com/hc/en-us/articles/4413026674833
9. **Session counting rules.** AppsFlyer counts a session on every foreground return; GA4 counts by CID and activity. AppsFlyer's own example: **5 launches 5 minutes apart = 5 AppsFlyer sessions, 1 GA4 session.** Adjust opens a new session after 30 min inactivity. — support.appsflyer.com/hc/en-us/articles/4413026674833
10. **Event deduplication logic differs.** AppsFlyer and GA4 drop near-simultaneous duplicates by different mechanisms; Adjust duplicates events sent via both SDK and S2S. — help.adjust.com/en/article/data-discrepancies
11. **Retargeting reclassification.** Reinstalls inside the re-attribution window are re-attributions in the MMP but new installs to the network. — support.appsflyer.com/hc/en-us/articles/207033786
12. **Fraud filtering asymmetry.** MMP-blocked installs never enter attribution; post-attribution fraud stays but flagged. Fraudulent AppsFlyer UA reinstalls are **reassigned to Organic**. — support.appsflyer.com/hc/en-us/articles/218254203
13. **SKAN is a parallel, non-deduplicated pipeline.** Without SSOT's `af_attribution_flag` the same user is counted twice; the SKAN dashboard never deduplicates. — support.appsflyer.com/hc/en-us/articles/4410634145425
14. **SKAN delay and randomized postback timing.** 24–48h minimum; 24–48h (first) and 24–144h (second/third) random delays; Google SKAN can lag **up to 45 days**. — developer.apple.com/documentation/adattributionkit/receiving-postbacks-in-multiple-conversion-windows
15. **Privacy thresholds null out data.** Below crowd anonymity, conversion values arrive null and granularity collapses to 2 digits; Tier 0 receives no second/third postback. — help.adjust.com/en/article/what-is-a-conversion-value
16. **SKAN's winner rule isn't last-touch** — highest fidelity-type wins. — developer.apple.com/documentation/storekit/receiving-ad-attributions-and-postbacks
17. **Cohort period boundaries.** AppsFlyer cohorts are calendar-based with hours rounded down, not rolling from install timestamp. — support.appsflyer.com/hc/en-us/articles/207040496
18. **Same metric name, different formula.** ROAS is a ratio in Adjust and a percentage in AppsFlyer; eCPI divides by installs in Adjust and by **attributions** in AppsFlyer.
19. **Multi-touch numbers are modeled, not measured.** Singular's MTA uses configurable per-org weights; AppsFlyer caps contributors at 3 and excludes networks that restrict user-level data.
20. **Install-touch vs last-touch credit for post-install events** — same data, different channel P&L. — branch.io/resources/blog/whats-the-difference-last-touch-vs-install-touch-attribution/
21. **Dual SDK implementations.** Running both MMP and network/analytics SDKs causes event discrepancies; platforms don't de-duplicate across SDKs.
22. **Privacy-mode postback suppression.** With AppsFlyer Aggregated Advanced Privacy on, no postbacks go to GA4 for non-consenting iOS 14.5+ users — GA4 is structurally short by that volume.
23. **Cost only counts where an attribution exists.** In AppsFlyer Cohort, a campaign spending with no attributions contributes **zero** cost, understating spend versus billing.
24. **Web-to-app interstitial leakage** (Branch Deepviews).
25. **Different default re-engagement clocks across MMPs** — Branch 90 days, Adjust 7 days, AppsFlyer none by default.
