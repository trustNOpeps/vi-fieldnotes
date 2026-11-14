# Growth metrics dictionary — VI Fieldnotes

## Tracking (consent-first GA4)
GA4 Measurement ID `G-R2X4W14SCX` is already installed by explicit consent. The site does **not** load GA4 until "Allow analytics" is chosen.

| Event | Trigger | Meaning | Limits |
|---|---|---|---|
| `page_view` | GA4 page loaded after consent | Consented page view | Not unique visitors or revenue |
| `select_content` | User clicks a guide card | Reader's interest in a guide | Internal navigation only |
| `vi_tool_open` | User navigates to tool | Interest in storage calculator | Not proof it was used |
| `vi_storage_calculation` | Check space button clicked | Tool use; anonymized status: meets_guidance / below_guidance / invalid_input | Does not send entered GB |
| `vi_checklist_open` | Launch checklist CTA link clicked | Interest in launch prep | Doesn't mean completion |
| `vi_checklist_updated` | User toggles checkbox | Anonymized number of completed steps | Not a purchase or identity |
| `vi_primary_source_open` | Click Rockstar or PlayStation source | Evidence-seeking engagement | Count only with consent |
| `vi_affiliate_outbound` | Click a future explicitly marked approved affiliate link | Commercial outbound intent | **No such link is active yet**; never treat as sales |

**Note:** Google's default Enhanced Measurement may also track outbound link clicks. Do not double-add both GA4 events into one 'total clicks' KPI without deduplication.

## Campaign attribution
Use real UTM labels in content links:
- `utm_source`: `youtube`, `x`, `instagram`, `tiktok`.
- `utm_medium`: `social`.
- `utm_campaign`: `launch2026`.
- `utm_content`: e.g., `storage_02`.

Campaign URL query strings must not be inserted as canonical URLs. Avoid putting personal data or secrets into query parameters.

## Weekly report
Measure (a) Search Console indexed URLs (independently verified), organic impressions, clicks; (b) consented GA4 sessions, engagement, landing pages; (c) each campaign's real views and click metrics; (d) approved affiliate portal paid transactions, not assumed conversion; (e) actual expenses.

Decision signals at day 30 should be assessed in context, not used as guarantees. Look for useful repeat intent and confirmed orders if a program is approved.

A sample CSV in `operations/growth_scorecard.csv` intentionally leaves actual metrics empty until observed.
