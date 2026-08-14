# CRM / Lifecycle Metric Definitions — raw research

> All entries extracted from pages fetched live. Unverified items listed at the end of each section.

---

## 1. Braze

### 1.1 Core message metrics
Source unless noted: https://www.braze.com/docs/user_guide/analytics/reporting/report_metrics

| Metric | Definition | Formula | Gotcha |
|---|---|---|---|
| **Sends** | Total messages sent, regardless of delivery status. | count | Send ≠ accepted by receiving server. |
| **Deliveries** | Message requests accepted by the receiving server. | (Sends − Bounces) ÷ Sends | **Derived by subtraction**, not independently observed. |
| **Delivery rate** | Messages reaching recipient servers. | Deliveries ÷ **Sends** | — |
| **Unique opens** | Delivered messages opened by a single user at least once, over a **7-day** window. | Unique Opens ÷ Deliveries | 7-day attribution cutoff; deduped by `dispatch_id`. |
| **Total opens** | Total messages opened. | Opens ÷ Deliveries | Counts repeats; **can exceed 100%**. |
| **Unique clicks** | Distinct recipients clicking a link at least once (7-day window, by `dispatch_id`). | Unique Clicks ÷ Deliveries | Deduped per dispatch, not per user lifetime. |
| **Click rate (email)** | — | Unique Clicks ÷ **Deliveries** | Denominator is Deliveries, not sends. |
| **CTOR** | Opened emails clicked "by a single user **or machine** at least once." | Unique Clicks ÷ Unique Opens | Denominator **explicitly includes machine (MPP) opens** → CTOR structurally deflated on Apple-heavy lists. |
| **Hard bounce** | Permanent delivery error. | — | Braze marks the address invalid, stops future attempts. |
| **Soft bounce** | Temporary error on a valid address. | — | **Retried within 72 hours**, so early bounce-rate reads are unstable. |
| **Bounce rate** | — | Bounces ÷ **Sends** | Sends denominator while engagement rates use Deliveries. |
| **Unsubscribes** | Subscription changed to unsubscribed via a **Braze-handled** path. | Unsubscribes ÷ Deliveries | ESP-side or list-unsubscribe handled elsewhere is **not captured**. |
| **Spam rate** | Delivered emails marked spam by the recipient. | Marked as Spam ÷ **Sends** | **Not comparable to Google's 0.3% rule**, which uses inbox-delivered mail. |
| **Conversions (primary)** | Defined event occurring after interacting with or viewing a message. | Primary Conversions ÷ Unique Recipients | Per-channel conversion opportunity → **multichannel conversion rate can exceed 100%**. |
| **Revenue** | Revenue from campaign recipients **within the primary conversion window**. | count | Revenue is hostage to the conversion window length. |

### 1.2 Machine opens / MPP
Sources: braze.com/docs/user_guide/analytics/metrics_glossary · /channels/email/reporting · /channels/email/faq

- **Machine Opens** — "includes both non-human and human opens that indicate an open by an Apple MPP-enabled user." Tracked from Nov 2021 (SendGrid) / Dec 2021 (SparkPost). **Gotcha: not a clean subset** — Braze documents a case yielding **+1 Machine Open and +1 Other Open for the same user** across two devices, so you cannot simply subtract.
- **Other Opens** — human opens not impacted by MPP. Braze recommends focusing on **Other Opens + Unique Clicks**. Machine-open share drifts with Apple Mail adoption, so machine-open trendlines are **not period-comparable**.
- **Estimated Real Opens** — "the result of a proprietary Braze statistical model," inferred from click data. Requires ~**10,000 delivered emails**, first computed after 24h, recalculated every 72h — **unavailable for small sends**.
- **Currents raw events** — machine opens are **not emitted as a distinct event type**; open/click events fire per occurrence, so Currents counts will not reconcile with deduped dashboard uniques.

### 1.3 Conversions & conversion window
https://www.braze.com/docs/user_guide/messaging/messaging_fundamentals/conversion_events

- **Primary conversion event** — the first event added at setup. Determines the multivariate winner, **the window in which revenue is calculated**, and Intelligent Selection's optimization target.
- **Conversion window** — max **30 days**; **default 3 days** if none selected.
- **Gotchas** — Conversion events **cannot be added or removed after launch**. Single-channel = one conversion per user per send; **multichannel = one conversion opportunity per channel**. In Canvas, conversions attribute to the **last Canvas Message step received**, not to each step's own timestamp.
- **Conversions Dashboard** — six attribution bases (Upon Receipt / Send / Open / Click / Impression / Last-Touch). **Multi-channel analysis auto-forces Last-Touch**; a user who entered before the report's date range is excluded even if the conversion falls inside it.

### 1.4 Canvas step analytics
https://www.braze.com/docs/user_guide/messaging/canvas/testing_canvases/measuring_and_testing_with_canvas_analytics

- **Conversions** — one per conversion event per Canvas entry, "assigned to the most recent message received by the user for that entry."
- **Gotcha (the big one)** — **variant conversions count from the moment of entry; step conversions count only after the step's message is sent.** A user converting before receiving any message counts toward the variant but toward no step — **variant and step totals will never reconcile.** Conversion window runs from **Canvas entry**, not per message.
- **Funnel Reports** — first step is always message receipt; completion window 1–30 days; max one conversion per user even with re-eligibility; orphaned users (post-`changeUser()`) excluded.

### 1.5 Engagement / Retention / Active users

- **Engagement reports** — recurring emailed CSV per campaign/Canvas. Aggregated at **campaign/Canvas level, not variant/step level**; not saved in the dashboard, CSV links expire after 1 hour.
- **Retention reports** — "the rate at which any user who has received this specific campaign has performed a retention event over the 30 days from the time they received the campaign." Two modes: **Rolling** (cumulative, on or after day N) and **Range** (bounded window). **Rolling retention can exceed 100%**; multi-cohort rows are weighted averages; cannot re-run the same retention event for 24h; **API-triggered campaigns cannot generate retention reports**.
- **DAU** = unique users with ≥1 session that day. **MAU** = users with a session in the last **30 days**, computed nightly on a rolling window. **Stickiness = DAU ÷ MAU.** Daily Sessions per MAU = Daily Sessions ÷ MAU.
- **Active user** — "anyone who has a session in that period (**users updated via the API also count** for that period)."
- **Gotcha** — **API-only profile updates inflate active-user counts without any real app usage**; offline sessions sync late so DAU changes retroactively; merged/orphaned profiles excluded from MAU.

### 1.6 Intelligence Suite
- **Intelligent Selection** — analyzes twice a day, reallocates variant traffic via multi-armed bandit with a "regret" metric. Stops "when it has **95% confidence** that continuing won't improve the conversion rate by more than **1%** of its present rate." **Gotcha: during training, variants receive roughly equal sends regardless of your configured split** — a 99/1 target may send 50/50 early, corrupting naive per-variant rate comparisons.
- **Intelligent Timing** — computed from session times, push direct opens, push influenced opens, email clicks, and **email opens excluding machine opens**. Fallbacks: most popular app time → custom time → **5 PM local**. Must launch **≥48 hours** ahead; optimal times computed at midnight Samoa time (UTC+13), so users may receive on a different calendar date.

### 1.7 Push / SMS

| Metric | Definition | Formula | Gotcha |
|---|---|---|---|
| **Push Direct Opens** | Users who opened by directly pressing the notification. | ÷ Deliveries | The only true click signal. |
| **Push Influenced Opens** | Users who opened the app after the push was sent, **without opening the push**. | ÷ Deliveries | **Correlational, not causal** — inflates "push open rate" if summed with direct opens. |
| **SMS Sent** | Campaign launched and SMS sent from Braze. | count | **Payload handed to the provider**, not the handset. |
| **SMS Confirmed Delivery** | "carrier has confirmed the message was delivered to the target phone number." | ÷ Sends | Asynchronous carrier DLR. **Some carriers never return receipts.** Braze charges for both. |
| **SMS Rejections** | Rejected by carrier (content filtering, invalid number). | ÷ Sends | **Billed** even though undelivered. |
| **SMS Opt-Out** | Replied with an opt-out keyword. | count | Inbound-keyword only — app/preference-center opt-outs land elsewhere. |
| **Uninstalls** | Flagged via passive push errors or **nightly background push** to users with no session/push in 24h. | count | Braze "increments the uninstall count for **every campaign that the user successfully received in the past 24 hours** by one" → **one uninstall attributed to multiple campaigns**. Apple deliberately delays token invalidation. |
| **Push subscription states** | `Subscribed` (default at profile creation), `Opted-In` (explicit OS acceptance), `Unsubscribed` (explicit rejection). | — | **Braze does not auto-set `Unsubscribed` when a user disables OS notifications** — you must update via SDK/REST, so reachability is overstated by default. |

**Not verified in Braze docs:** a published push opt-in rate formula; a stated uplift formula for Canvas Experiment Paths; a metric literally named "Currently Active Users."

---

## 2. Klaviyo

Glossary: https://help.klaviyo.com/hc/en-us/articles/360037957832

| Metric | Formula | Gotcha |
|---|---|---|
| **Open rate** | Unique opens ÷ **total recipients** | Denominator is **recipients, not delivered** — reads lower than Braze/Iterable for the same list. MPP-inflated. |
| **Click rate** | Unique clicks ÷ total recipients | Klaviyo explicitly warns this is **not** CTOR. |
| **CTOR** | Clicks ÷ opens (unique vs total unspecified) | MPP inflates the denominator → deflated CTOR. |
| **Delivery rate** | Deliveries ÷ total sent | The **only** major Klaviyo rate on a sent denominator. |
| **Bounce rate** | Bounced ÷ recipients | Hard + soft combined into one rate. |
| **Hard / soft bounce** | — | Hard → **immediate auto-suppression**. Soft → suppressed after **>7 consecutive** soft bounces (2-year lookback). **Suppression shrinks future recipient denominators.** |
| **Unsubscribe rate** | Unsubscribes ÷ total recipients | — |
| **Spam complaint rate** | Complaints ÷ total recipients | **Structurally lower than the Gmail/Yahoo 0.3% figure**, which uses inboxed mail. Do not compare directly. |
| **Placed Order rate** | Orders in the attribution window ÷ unique recipients | **Widening the attribution window mechanically raises this.** |
| **Revenue per recipient (RPR)** | Attributed revenue ÷ total recipients | Moves whenever the window or model changes. |

### 2.1 Klaviyo attribution model & window (load-bearing)
- **Model:** co-operative **last-touch** by default; **linear** on Advanced KDP / Marketing Analytics. Model changes take up to **36 hours** to apply.
- **Default windows:** email opened 5d · email clicked 5d · SMS opened 1d · SMS clicked 5d · SMS delivered 12h · push opened 24h · WhatsApp opened 12h · WhatsApp clicked 5d · Active on Site 1d. **Max 90 days.**
- **Rule:** one order credited to exactly one message — whichever was opened/clicked most recently, if the conversion falls inside that message's window.
- **Gotchas:** (1) Window changes are **retroactive** — "any changes to attribution will apply to both historical and future conversions", so **past reports restate**. (2) **"Conversions are tracked if someone opens or clicks, or if Apple MPP automatically opens the email"** — **an MPP phantom open can win last-touch credit for a message never read.** There is an MPP-exclusion toggle in Attribution settings. (3) Conversions attribute within ~3h and recalculate for up to 5 days.
- Source: help.klaviyo.com/hc/en-us/articles/36457929459227 · /11118357030555 · /115005248128

### 2.2 Klaviyo MPP & holdouts
- **Apple Privacy Open flag** — True/False per open event, only for opens **on or after 20 Nov 2021**. Klaviyo states plainly it has **no way to distinguish a true human open from an automated open when MPP is enabled** — `False` is cleaner, not proof of a human. Guidance: segment `Apple Privacy Open equals False`, trigger flows on clicks, expect "a higher threshold to reach statistical significance" in open-rate A/B tests.
- **Global holdout groups** — requires **≥400,000 profiles**; **only one active holdout at a time**; applies to **all channels** in a campaign/flow (cannot be per-channel); ~5% recommended.

---

## 3. Iterable

Metric reference: https://support.iterable.com/hc/en-us/articles/213805923-Metric-Definitions

| Metric | Formula | Gotcha |
|---|---|---|
| **Unique Email Sends** | — | Iterable itself calls the unique figure **approximate**. |
| **Emails Delivered** | Total Sends (by `messageId`) − Bounced | Derived by subtraction, like Braze. |
| **Unique Email Opens** | — | **Includes pre-fetched and proxied opens** — MPP is inside this metric. |
| **Unique Email Opens (filtered)** | — | Filtered and unfiltered sit **side by side in the UI**; reports silently mix them. |
| **Unique Email Opens or Clicks** | — | **A click from a user with images off registers as an open.** This is the numerator of Unique Email Open Rate → open rate is not purely pixel-based. |
| **Unique Email Open Rate** | Unique Opens or Clicks ÷ Unique Delivered | The filtered version uses a **different numerator** — the two are not comparable. |
| **Unique Email Click Rate** | Unique Clicks ÷ Unique **Delivered** | Delivered denominator (vs Klaviyo's recipients) → reads higher for the same list. |
| **CTOR** | Unique Clicks ÷ Unique Opens **or Clicks** | **Every clicker is in the denominator by construction** → CTOR cannot exceed 100% and is structurally deflated. Uses the **unfiltered** open metric. |
| **Bounce Rate** | Bounced ÷ Total **Sends** | Hard/soft not split; sends denominator vs delivered elsewhere. |
| **Unsubscribe Rate** | **Total** Unsubscribes ÷ Total Delivered | Total (not unique) numerator. |
| **Complaint Rate** | Total Complaints ÷ Total Delivered | An FBL complaint **auto-unsubscribes the user from all channels**. |
| **Custom Conversions** | — | **Purchases are system events and do not count as custom conversions** unless `iterable_purchase` is designated. |
| **Revenue / AOV / Revenue per mille** | AOV = Revenue ÷ Total Purchases; **Revenue/M = revenue per thousand emails sent** | Iterable's RPR analogue is **per 1,000 sent**, not per recipient. |

### 3.1 Iterable attribution
- Two models per campaign: **time-based (default)**, or **attribution by `campaignId`**. Last-touch: credit goes to the **most recently sent** campaign holding an open window.
- **Gotchas:** attribution keys off `documentCreatedAt` (when Iterable **received** the event), not your `createdAt` — **sync latency shifts attribution**. With `campaignId` attribution, omitting the id means **no attribution is assigned and the data cannot be recovered**. Passing `campaignId`/`templateId` **overrides** an open time-based window.
- **Not published:** a default attribution-period length.

### 3.2 Iterable MPP filtering
`isBot` field drives every "(filtered)" metric. Iterable states `isBot` **"is a heuristic, not confirmation that a request was automated."** Unique Email Opens (filtered) determines open-based experiment winners; Unique Email Clicks (unfiltered) determines click-based winners.

### 3.3 Iterable push / SMS
- **Total Pushes Sent** includes "pushes received by a device whose owner **disabled notifications**" → **push open rate systematically understated**.
- **Uninstall attribution:** attributed to a campaign sent in the prior **12 hours**, or via a "ghost" push sent 12 hours later. **Disabling notifications is not counted as an uninstall.**
- **SMS:** **no SMS open metric** — clicks are the only signal; link-preview/prefetch clicks removed only in "(filtered)" variants. **SMS bounces do not auto-unsubscribe.**

---

## 4. Insider

Docs at `academy.insiderone.com`. **English only — no Turkish metric naming found on any fetched page.**

### 4.1 Email — academy.insiderone.com/docs/email-metrics-1
| Metric | Formula | Gotcha |
|---|---|---|
| Open Rate | Unique Opens ÷ **Delivered** | Page explicitly warns MPP prefetch inflates it. |
| Click-Through Rate | Unique Clicks ÷ **Delivered** | Named "CTR" but computed on **unique** clicks. |
| CTOR | Unique Clicks ÷ Unique Opens | Deflated by MPP-inflated denominator. |
| Bounce Rate | Bounces ÷ **Sent** | Sent denominator while engagement rates use Delivered. |
| **Blocks** | — | This is Insider's **soft bounce**, reported separately from "Bounces" (hard). **Mapping required for cross-vendor comparison.** |
| Unsubscribes | — | **Global** unsubscribe; includes List-Unsubscribe. |
| **Drop Messages** | — | Where frequency-capped sends are accounted — **they never enter "Sent".** |

**Email conversion attribution:** default goal = purchase; model = **last click**; **default window 7 days**. **Critical: "Email does not track opens" for attribution — conversions attribute to clicks, never opens or deliveries**; view-through exists for Architect/Mobile App/OnSite but **not Email**. Accounts created before 1 Jul 2026 record revenue per campaign **without deduplication** → overall revenue can be double-counted.

### 4.2 App push
`Targeted = Sent + Dropped`; `Sent = Delivered + Undelivered`. **Sent = handed to FCM/APNs**, not the device. Open Rate = Opens ÷ Delivered. **Dropped** = blocked by frequency caps / silent hours *before* reaching the device. **Device Uninstalls exists only as a breakdown of Undelivered — there is no standalone uninstall-rate metric.**

### 4.3 Web push
**Click-through Rate = total Clicks ÷ Delivered × 100.** **Gotcha: web push reports Clicks while app push reports Opens** — not comparable; and web-push CTR uses **total** clicks while email CTR uses **unique**.
**Opt-in CTR = subscribers ÷ users who viewed the opt-in screens × 100** — denominator is **prompt views, not site visitors**.
**Attribution:** last-click only; session-based (30-min) or duration-based up to **90 days**. Single API Push fixed at 1 day.

### 4.4 SMS
Sent = handed to the provider. **CTR = total Clicks ÷ Delivered** — differs from Insider's own email CTR, which uses unique. Conversions counted "within the specified duration **after a user clicks the link**."

### 4.5 Architect (journey) attribution
Models: **Last Click** and **Last View**. A "view" is channel-specific: Opens (Email), Opens/Read (WhatsApp), **Delivered (SMS)**, Impressions (InApp/OnSite). **Defaults: click-through 14 days, view-through 3 days.** **Gotchas:** the Architect click default (14d) **differs from the Email product default (7d)**; and under Last View, **a merely delivered SMS can win credit** — material over-crediting risk for SMS-heavy journeys.

---

## 5. D·engage

Docs: `dev.dengage.com`. **English only — no Turkish metric naming verified.**

### 5.1 Email
Delivery Rate = Delivered ÷ Total Sent. Open Rate = Unique Opens ÷ Delivered. CTOR = Unique Clicks ÷ Unique Opens. **Gotcha: no bounce-rate formula is stated anywhere.** Non-send reason codes sit between audience and Total Sent: `Content Status Passive`, `Email Duplicate`, `Email Status Passive`, `Email Permission Passive`, `Has Error` — **permission suppressions are reported here rather than as bounces or unsubscribes**, so an audience-vs-sent comparison looks broken until you read them.

### 5.2 Push
Metrics: Total Sent Push, **Sent To** (recipients, distinct from message count), Delivered, Delivery Rate, Total/Unique Click, Click Rate, **Bounced** (D·engage calls undelivered push a "bounce"), Conversion, Revenue, Visit; Total Send split into **Contacts vs Anonymous**. **Gotcha: Delivery Rate and Click Rate have no documented formula or denominator.** The cross-channel comparison view defines "Engagement" on **total** clicks while the campaign table reports **Unique** Click — two different engagement measures in one product.

### 5.3 SMS
DLR state exposed as **five separate buckets** rather than one delivery rate: **Waiting Report**, **Not Reported**, **Timeout**, **Failed**, **Rejected**. **Gotcha: SMS delivery rate is unstable over time** — the same campaign reports different delivery rates depending on when you pull the report, because Waiting Report drains asynchronously and Not Reported never resolves. Insider collapses all of this into a single `Undelivered`. **No SMS rate formulas stated.**

### 5.4 Conversion & control group
- **Conversion tracking:** up to **two** conversion events per campaign. **Gotcha: no attribution window, deadline, default, or model is documented.**
- **Control group:** "users who have not shown any content… excluded from winner selection." Significance via **Z-test** on click-based conversion. **Gotcha: no uplift or lift formula is published** — lift must be computed externally. Membership exportable via Incremental Logs, but docs do not state how membership is selected or whether it is stable across campaigns.

---

## 6. Apple Mail Privacy Protection

- **Definition** — Turning it on "make[s] it harder for senders to learn about your Mail activity." It "hides your IP address… It also prevents senders from seeing if you've opened the email message they sent you." **Gotcha: it is a per-user toggle inside the Mail app**, not account- or OS-level. The same person reading the same mailbox in Gmail is unaffected — **MPP contamination varies by list composition, not by sender.** — https://support.apple.com/guide/iphone/use-mail-privacy-protection-iphf084865c7/ios
- **Remote-content preloading** — Mail "downloads remote content in the background by default — regardless of whether you engage with the email." **Gotcha: the fetch happens on receipt, not on read, so the recorded open timestamp is a proxy-fetch time. Send-time-optimization models trained on open timestamps are corrupted, not merely noisy.** — https://www.apple.com/legal/privacy/data/en/mail-privacy-protection/
- **Two-relay proxying** — content routed through two relays operated by different entities; the first knows your IP but not the content, the second knows the content but not your IP. **Gotcha: geo and device segments built off open data are actively wrong, not just missing.**
- **Scale (Litmus)** — "Over 50% of email opens happen on a device with Apple's MPP activated." **Gotcha: >50% is Litmus's panel aggregate, not your list.** Litmus's own workaround: segment out non-Apple-Mail subscribers and use **their** opens as a proxy for performance and A/B testing. — litmus.com/apple-mail-privacy-protection-resources

**Google's counterweight (kills a common workflow):** Google states flatly "Google doesn't track open rates," "Google can't verify the accuracy of open rates reported by third parties," and **"Low open rates aren't necessarily an accurate indicator of deliverability or spam classification issues."** Using an open-rate drop as an inbox-placement alarm is **not supported by Google** — use Postmaster spam rate and reputation instead. — https://support.google.com/mail/answer/81126

---

## 7. Deliverability standards

### Google — bulk sender definition
"close to **5,000 messages or more to personal Gmail accounts within a 24-hour period**", counted per **primary domain** (2,500 from `solarmora.com` + 2,500 from `promotions.solarmora.com` = bulk). **Gotchas: subdomain-splitting does not evade it**, and status is **permanent** — "Senders who meet the above criteria at least once are permanently considered bulk senders… Changes in email sending practices will not affect permanent bulk sender status." **One Black Friday spike classifies you forever.** Applies to **personal Gmail only**, not Workspace recipients. — https://support.google.com/a/answer/14229414

### Google — spam rate (the 0.3% rule)
- **Definition** — "The percent of your messages that are **delivered to engaged recipient's Inbox and then marked as spam** by the recipient."
- **Thresholds** — keep **below 0.10%**, never reach **0.30%**. Calculated daily.
- **Gotcha (critical)** — **the denominator is inbox-delivered mail only** — messages Gmail already routed to spam are excluded. **A sender in deep trouble can therefore show a deceptively low spam rate.** Exceeding 0.3% makes you "ineligible for mitigation," and eligibility returns only "when their spam rates remain below 0.3% for **7 consecutive days**."
- — https://support.google.com/a/answer/14668346

### Google — authentication
All senders: SPF **or** DKIM. Bulk senders: SPF, DKIM **and** DMARC (`p=none` min). DKIM ≥1024 bits. Alignment: the From: organizational domain "must be aligned with either the SPF organizational domain or the DKIM organizational domain" — **"only one of these needs to be aligned."** **Gotcha: both must be configured but only one must be aligned** — a distinction that trips audits. As of "November 2025, Gmail is ramping up its enforcement on non-compliant traffic… including temporary and permanent rejections."

### Google — one-click unsubscribe (RFC 8058)
Required for 5,000+/day marketing/subscribed mail; headers `List-Unsubscribe-Post: List-Unsubscribe=One-Click` plus `List-Unsubscribe: <https://…>`, **and** a visible body link. **Honor within 48 hours. Gotchas:** "mailto and URL unsubscribe links don't meet our one-click unsubscribe requirement"; a one-click link pointing to a **preferences landing page "doesn't comply with RFC 8058"**; if the header is missing Google does **not** fall back to scanning the body.

### Google — infrastructure
PTR must match the sending IP with matching forward lookup; TLS required; RFC 5322 format. Applies to **all** senders. **Gotcha:** "The IP address quota is **shared for all senders that use that IP address**. When the IP address hits its quota, all domains that send from that IP address stop sending" — **on a shared IP another tenant can halt you.**

### Google Postmaster Tools — metric definitions
- **Delivery errors** = "The percent of all **authenticated** messages (SPF or DKIM) that were rejected or that temporarily failed, compared to all authenticated messages."
- **Gotcha:** Domain reputation "only displays messages sent from the **exact domain used for DKIM and SPF authentication**" — if your From: domain differs from your DKIM `d=` domain **you are reading reputation for a domain you don't think you're sending from.**
- — https://support.google.com/a/answer/14668346

### Yahoo
All senders: SPF or DKIM, valid forward/reverse DNS, RFC compliance, **"Keep your spam rate below 0.3%."** Bulk: SPF **and** DKIM, DMARC `p=none` min, alignment, one-click List-Unsubscribe. **Unsubscribes honored within 2 days.** **Gotchas:** denominator matches Google's — "Spam rate is calculated… based on **mail delivered to the inbox**." Yahoo publishes **no numeric volume threshold** for "bulk sender" — do not assume Google's 5,000/day. — https://senders.yahooinc.com/best-practices/

### Microsoft / Outlook.com
Applies to domains sending **>5,000 emails/day** to consumer Outlook.com. SPF + DKIM must pass; DMARC `p=none` min. Effective **5 May 2025**. **Gotchas:** (1) The widely-repeated "routed to Junk first, rejected later" plan is **struck through on Microsoft's own page** and replaced — non-compliant mail is **rejected** (`550 5.7.515`). **Any secondhand source still saying "goes to Junk" is stale.** (2) Scope is **consumer Outlook.com only**, not M365/Exchange Online tenants. (3) SPF records exceeding 10 DNS lookups fail. — techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/…/4399730

---

## 8. SMS & push — cross-vendor

### Sends vs delivery receipts
| Vendor | "Sent" means | Delivery-confirmed metric | Key gotcha |
|---|---|---|---|
| Braze SMS | Handed to the SMS provider | **Confirmed Delivery** = carrier confirmed delivery to the phone number | **Some carriers never return receipts**; Braze bills sends, confirmed deliveries, and rejections. |
| Insider | Handed to the provider (`Sent = Delivered + Undelivered`) | Delivered ÷ Sent | `Dropped` sits *before* Sent (frequency caps, silent hours) and is **invisible in delivery rate**. |
| D·engage | Handed to the provider | Delivered, with 5 separate DLR buckets | **Delivery rate changes depending on when you pull the report.** |
| Iterable | Passed to the carrier | Delivered = Sent − Bounced | **No SMS open metric at all.** |
| OneSignal | Includes successful sends to carrier **and failures** | "successfully delivered **to the carrier**" | **OneSignal's "Delivered" stops at the carrier, not the handset** — a weaker claim than Braze's. |

### Push delivery confirmation
- **OneSignal:** *Delivered* = "successfully delivered to the **push services** (FCM, APNs)"; **Confirmed Receipt** = "confirmed as received by the **device**, verified by the OneSignal SDK." **Only Confirmed Receipt is device-level.**
- **Iterable:** "Delivered" includes pushes reaching devices whose owner **disabled notifications** → open rate systematically understated.
- **Braze:** Direct Opens (true click) vs Influenced Opens (app opened after send) — **do not sum them.**

### Push opt-in rate
**No vendor fetched publishes an audience-level push opt-in-rate formula.** Insider web push is the one documented opt-in metric, and its denominator is **prompt views, not visitors**. Braze defines states but publishes no opt-in rate, and **does not auto-set `Unsubscribed` when a user disables OS notifications** — reachability is overstated unless you push that update.

### Uninstall attribution
| Vendor | Mechanism | Gotcha |
|---|---|---|
| **Braze** | Passive push errors + optional nightly background push | **One uninstall is credited to every campaign received in the past 24h.** Apple deliberately delays token invalidation. |
| **Iterable** | Campaign sent in the prior **12 hours**, or a "ghost" push 12h later | **Disabling notifications is not an uninstall.** |
| **Insider** | Only a breakdown of `Undelivered` | **No standalone uninstall rate exists.** |
| **D·engage** | Not documented | — |

---

## 9. Incrementality in CRM

### Braze — Global Control Group
- **Definition** — a randomly selected **1–15%** of the total user base who "do not receive any campaigns or Canvases." Assignment uses **random bucket numbers** (0–9999, assigned at profile creation), so new users falling in those ranges join automatically.
- **Formulas** — Change from Control = `((Treatment CR − Control CR) ÷ Control CR) × 100`. **Incremental Uplift (number)** = difference in total events. **(percent)** = incremental uplift ÷ total treatment events — "the percentage of your treatment's total events that can be attributed to your treatment."
- **Gotchas** — **API-triggered campaigns still reach control users** (except API Content Cards) — **the holdout is not airtight.** You cannot remove individual users; you must disable and recreate the whole group. **Max one active control group per workspace.** Braze guidance: ≥1,000 users but ≤10% of audience; run ≥1 month; reshuffle no more than monthly.
- — braze.com/docs/user_guide/engagement_tools/testing/global_control_group

### Braze — campaign A/B and Canvas experiments
- **Control variant** = users who receive **no message**, enabling "send something vs send nothing."
- **Z Test** for confidence vs control; "95% or greater confidence… indicates the difference is statistically meaningful." Winner selection uses **Pearson's chi-squared** at p < 0.05.
- **Gotchas:** **confidence can decline as data accumulates** if rates converge. Canvas Experiment Paths support a control group but Braze **does not publish the statistical method or an uplift formula** for them.
- **Conversion Correlation** uses the Wilson confidence interval at 95%; Braze explicitly labels findings **correlation, not causation**.

### Klaviyo — Global holdout groups
Requires **≥400,000 profiles**; **only one active holdout at a time**; applies to **all channels** (no per-channel holdout); ~5% recommended. **Klaviyo publishes no explicit lift formula.**

### Iterable — Holdout groups
The campaign is not sent **but conversions are still tracked**. Held-out profiles get a Send Skip event with `reason = ExperimentHoldOut`. **Gotchas:** holdout is an **experiment variant, per campaign** — not a global account-level suppression. And **the denominators don't match**: the holdout rate divides by **skipped sends** while the treated rate divides by **unique delivered** — a send-level count against a user-level count. Lift is expressed in **percentage points**. *(Experiment Analytics page retrieved via search summary rather than direct fetch — lower confidence.)*

### Insider — incrementality metrics
- **Incremental Conversions** = `Unique Conversions × (Σ Incr. conversions ÷ Σ Var(conversions))` — **a re-scaled aggregate across campaigns, not a raw variant-minus-control subtraction.**
- **Conversion Rate Uplift** = `Incremental Conversions ÷ (Unique Conversions − Incremental Conversions)` — **denominator is the non-incremental baseline**, so this is lift over baseline, not over total.
- **On-site Incremental Revenue** = `Var(Rev) − ((Var(Imp) × CG(CR)) × CG(AOV))`.
- **Gotchas: incremental values cannot be negative — negatives display as 0** in monthly summaries, so **summary-level incrementality is systematically optimistic.** A campaign needs ≥10 impressions and ≥1 conversion to show control-group results. **Bayesian Probability (Likelihood to Win) is explicitly "mutually exclusive from incremental metrics."**

### Cross-vendor incrementality comparison
| | Braze | Klaviyo | Iterable | Insider | D·engage |
|---|---|---|---|---|---|
| Global holdout | Yes, 1–15% | Yes, ≥400k profiles, 1 active | No | Not documented | Not documented |
| Per-campaign holdout | A/B control variant, Canvas Experiment Path | — | Yes (experiment variant) | Yes | Yes |
| Published lift formula | **Yes** | No | Percentage points | **Yes — 3 formulas** | **No** |
| Significance method | Z test; chi-squared for winner | Not published | Confidence % | Bayesian Likelihood to Win | Z-test |
| Biggest trap | **API campaigns bypass the global control group** | 400k minimum; all-channel only | Mismatched denominators | **Negative incrementality floored at 0** | **No lift math at all** |

---

## Not verified — deliberately omitted
Braze push opt-in rate formula; Canvas Experiment Path uplift formula; a metric named "Currently Active Users." Klaviyo separate hard/soft bounce-rate formulas. Iterable default attribution-period length. Insider app-push opt-in rate and uninstall rate; in-app metrics; Turkish-language docs. D·engage attribution window/model, push and SMS rate formulas, uninstall tracking; `helpdesk.dengage.com` and `dengage.com/knowledge-base/` not fetched. Apple developer/WWDC MPP docs not reached. Yahoo numeric bulk-sender volume threshold (not published).
