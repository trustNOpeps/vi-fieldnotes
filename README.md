# VI Fieldnotes / independent GTA VI launch guides

**Primary website (Cloudflare Pages):** https://vi-fieldnotes.pages.dev/
**GitHub Pages preview:** https://trustnopeps.github.io/vi-fieldnotes/
**Source branch:** `main`
**Research baseline:** 14 November 2026 (pre-release).
**Scheduled publisher launch:** 19 November 2026, PS5 and Xbox Series X|S — verify directly with [Rockstar Games](https://www.rockstargames.com/VI).

VI Fieldnotes is an **independent, unofficial, accessible editorial website**, not affiliated with Rockstar Games, Take-Two Interactive, PlayStation or Xbox. It is a small source-grounded publication/learning experiment; no guaranteed traffic, income or affiliated business relationship is claimed.

## Features

- 15 concise source-linked guides, including Indonesia purchase/region rules, storage guidance and rumor verification. Dated review notes separate confirmed claims from unresolved points.
- Working guide search, category filters and FAQ search.
- Free browser-only PS5 storage calculator comparing user-entered GB to PlayStation Indonesia's published 212 GB preparation advisory.
- Ten-step launch checklist saved locally in the reader's browser.
- Custom visual identity using original abstract art, semantic accessible markup, responsive layout, canonical metadata and 23-route sitemap.
- Optional Google Analytics 4 integration `G-R2X4W14SCX`; consent-first, visitor may decline. Review [privacy/editorial notes](https://vi-fieldnotes.pages.dev/about/). The owner previously verified Google Search Console for the GitHub Pages site; verification of the Cloudflare property is a separate step.
- GitHub Actions static QA checks HTML, links, metadata, sitemap, article sources and JavaScript syntax.

## Running and testing

This project intentionally uses static HTML, CSS and vanilla JavaScript; no dependencies or API keys are needed.

```bash
git clone https://github.com/trustNOpeps/vi-fieldnotes.git
cd vi-fieldnotes
python3 tests/check_site.py
node --check script.js
```

Local preview needs the repository served at the `/vi-fieldnotes/` path to match GitHub Pages routing. You may use a simple static server with a parent directory containing the repo under that name, or use GitHub Pages for the exact live structure.

**GitHub Pages preview:** deploy from `main`, folder `/(root)`. The `.nojekyll` file keeps the static site assets unchanged. Workflow: [Actions](https://github.com/trustNOpeps/vi-fieldnotes/actions).

## Cloudflare Pages hosting

GitHub Pages is excellent for an independent editorial project, but [GitHub's own policy](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) does not allow it to serve as the primary hosting for a website principally facilitating commercial transactions. Google's AdSense site registration [does not accept directory paths](https://support.google.com/adsense/answer/2784438?hl=en) such as `/vi-fieldnotes/`. **Do not assume the current Pages address qualifies for AdSense or a merchant program.**

The primary portfolio destination is the Cloudflare Pages URL supplied by the owner. Build its root-path version with:

```bash
SITE_ORIGIN=https://vi-fieldnotes.pages.dev python3 scripts/build-for-root.py
# Output directory: dist
```

The build is tested in CI. Source HTML retains the GitHub Pages path; the build rewrites paths and metadata for Cloudflare. A Cloudflare deployment does not imply advertising or affiliate approval. Read [hosting migration guide](docs/hosting-migration.md) for Git integration, domain, Search Console and GA4 checks.

## Portfolio-ready project documentation

- [VI Fieldnotes portfolio case study](docs/portfolio-case-study.md) — purpose, visual direction, architecture, tested features and limitations.

## Operating references

- [Editorial and source-checking playbook](docs/launch-playbook.md)
- [Distribution kit / content scripts](docs/distribution-kit.md)
- [Monetization eligibility and evidence ledger](docs/monetization-readiness.md)
- [Hosting and domain migration](docs/hosting-migration.md)

No affiliate, sponsor or AdSense approval is represented as active as of publication. Publisher must apply under their real identity, confirm channel eligibility, disclose commercial links and record actual payments, not projections. No automated posting or mass-produced gameplay claims.

## Source hierarchy

1. Rockstar official game and support articles.
2. PlayStation/Xbox first-party support for region, hardware and timing.
3. Independent reports can inform questions but do not override publisher facts.

Following the scheduled launch, guides need a manual, factual re-review. The website automatically displays a freshness reminder after November 19, but **does not invent a successful release or update review dates automatically**.

## License and affiliation

The original VI Fieldnotes layouts, writing and abstract graphics were prepared for this independent project. Product trademarks remain with their respective owners. Third-party content and official source pages are linked, not copied into this repository.

## Automated editorial studio (draft-only MVP)

[VI Fieldnotes Editorial Studio](studio/README.md) provides a seven-day editorial queue (16–22 Nov 2026), a primary-source and rights gate, English narration scripts, five-scene neon-coast storyboards, subtitles, captions, and watermarked MP4 previews. A [daily GitHub Actions draft job](.github/workflows/editorial-studio.yml) generates an **internal review artifact** at 08:17 WITA; it never publishes anything to social accounts. An editorial review and a licensed, natural voice track are required before any video is considered publication-ready. Expired stories and an empty queue fail closed rather than repeating or inventing news. This tool is not included in the Cloudflare Pages output.
