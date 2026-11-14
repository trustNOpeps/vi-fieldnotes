# VI Fieldnotes — indexing audit and Search Console handoff (14 Nov 2026)

## What is confirmed
- The site is public at https://trustnopeps.github.io/vi-fieldnotes/
- Repository branch `main` publishes its static HTML through GitHub Pages.
- 23 indexable URLs are listed in `sitemap.xml` including 15 guide pages.
- `robots.txt` permits crawling and declares the sitemap.
- Each static page has a canonical URL; build/QA checks validate internal links and sitemap membership.
- The site owner reports Search Console property verification, sitemap submission and GA4 setup completed.

## What cannot be measured through the available browser session
The available Google Search Console browser session is **signed out** and redirected to https://search.google.com/search-console/about . Therefore:
- Verified indexed URL count: **unknown**.
- Not-indexed count/reasons: **unknown**.
- Search impressions/clicks: **unknown**.
- Sitemap processing/last read status: **not independently retrieved**.

Do not equate "23 URLs included in sitemap" with "23 Google-indexed pages".
A `site:` search is a rough, incomplete spot check and is not a substitute for the property report.

## Exact owner-side actions
1. Open https://search.google.com/search-console and select the `URL prefix` property `https://trustnopeps.github.io/vi-fieldnotes/`.
2. **Indexing → Pages**: record *Indexed*, *Not indexed*, and top exclusion reasons, plus their screenshot/date.
3. **Sitemaps**: confirm `https://trustnopeps.github.io/vi-fieldnotes/sitemap.xml` has status Success and a valid last-read date.
4. **URL Inspection** on homepage, `/guides/`, `/tools/`, `/guides/indonesia-buying-guide/`, `/guides/ps5-storage-explained/`, and `/guides/release-date-2026/`. Record Google's "URL is on Google" or precise reason.
5. If a *valuable, canonical, publicly accessible page* is not indexed, use the URL Inspection interface's Request indexing judiciously. Do not submit unchanged pages daily. Address actual errors first.
6. **Performance → Search results**: after data exists, export impressions, clicks, CTR and query/page breakdown. Keep dates and geography explicit.
7. Review weekly in the owner account. Indexing is Google's independent decision; no tool can guarantee a ranking or deadline.

## SEO issue fixes already in code
- Consistent guides-index OG description for 15 articles (not the obsolete "12" statement).
- `lastmod` on homepage and guide index reflecting this publishing batch.
- Source-cited user-oriented content, descriptive nav labels, original site art, mobile-first CSS.
- The site contains no instant-indexing, link-farm, click-fraud or bot submission mechanism.

## Source of methodology
- Google Search Essentials: https://developers.google.com/search/docs/essentials
- Search indexing FAQ: https://developers.google.com/search/help/crawling-index-faq
- Google crawling troubleshooting: https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors

Prepared 2026-11-14 — actual indexing statistics should be filled only after authenticated access.
