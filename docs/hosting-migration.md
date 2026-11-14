# Moving VI Fieldnotes to business-appropriate hosting
Last reviewed 14 November 2026. The existing editorial GitHub Pages site remains live. No external hosting account, custom domain or paid subscription has been created through this project.

## Why this matters
GitHub Pages is intended to showcase personal or organizational projects, not to run a site primarily directed at commercial transactions. See https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits .
Google AdSense requires a site URL without a path, and generally doesn't accept arbitrary subdomains as new sites (except eligible host partners). See https://support.google.com/adsense/answer/2784438?hl=en . The current GitHub Pages project lives under `/vi-fieldnotes/`. **Do not assume AdSense will approve it.** Commercial rollout should use hosting and an origin under the publisher's control and applicable platform terms.

## Recommended low-cost future path
Keep GitHub as the source repository, move production hosting to a dedicated Cloudflare Pages site using Git integration, and optionally connect a custom domain only once traffic or commercial eligibility justifies it. Cloudflare Pages documents GitHub builds and a free tier with build limits; these are not guaranteed indefinitely. Source: https://developers.cloudflare.com/pages/configuration/git-integration/ and https://developers.cloudflare.com/pages/platform/limits/ .

### One-time owner actions (cannot be automated without Cloudflare authorization)
1. Sign in to Cloudflare Dashboard with your own account; open Workers & Pages → Create → Pages → Import an existing Git repository. Grant access to **trustNOpeps/vi-fieldnotes** only, if available.
2. Create a Pages project (for example `vi-fieldnotes`) and confirm its final assigned `*.pages.dev` URL; do not guess whether the name is available.
3. Build command: `python3 scripts/build-for-root.py`.
4. Build output directory: `dist`.
5. Environment variable `SITE_ORIGIN`: your **exact** HTTPS project origin, e.g. `https://vi-fieldnotes.pages.dev` ONLY if that is the actual assigned URL. No trailing slash or path. Add variable for production and, when appropriate, previews.
6. Deploy the `main` branch. Verify home, guide index, articles, `/tools/`, /sitemap.xml, and consent banner, then check for browser console issues.
7. If purchasing a custom domain later, add it to Cloudflare Pages and update `SITE_ORIGIN` to the exact new domain. Rebuild to update canonical, OG URLs, sitemap and robots. Verify DNS/HTTPS and redirects.

### SEO + analytics migration checklist
- In Google Search Console, add and verify the NEW URL-prefix/domain property; submit the NEW sitemap. Do not assume the old property transfers.
- Update the GA4 web stream's primary URL and inspect Realtime again. The same public measurement ID may remain if appropriate to the analytics property, but verify in the UI.
- Preserve existing editorial timestamps and sources. Avoid showing two domains with conflicting canonical URLs for a prolonged time.
- Set appropriate site redirects or a visible migration announcement on the previous GitHub Pages site after the replacement site is tested. Redirect capability depends on the chosen hosting.
- Re-check privacy text and consent after changing the site origin; browser-local consent is domain-specific.

### Before enabling affiliate revenue
- Obtain actual affiliate-program approval and register the exact production URL as an approved promotional channel where required.
- Confirm product eligibility, current merchant links, disclosure near every compensated placement, and the site's terms of service.
- Track eligible clicks, confirmed sales, and settled commissions separately; revenue is zero until program evidence exists.
- For advertising, separately apply and wait for site review; no guarantee of acceptance.

## Local build smoke test
Run:
```bash
SITE_ORIGIN=https://your-actual-site.pages.dev python3 scripts/build-for-root.py
```
Upload the generated `dist/` only after using a real origin. CI tests with a placeholder domain purely to validate generated links; this does not publish anything.
