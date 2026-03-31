# GrowthMax Website — Daily Improvement Review
**Date:** March 30, 2026
**Repo:** https://github.com/growthmaxinc/growthmaxweb
**Latest commit:** `fedaa45` — Fix stray g> character in Solutions nav button

---

## Improvement 1: Add missing SEO meta tags and Open Graph data to the homepage

**What's missing:** The homepage (`index.html`) has no `<meta name="description">`, no Open Graph tags (`og:title`, `og:description`, `og:image`), and no Twitter Card meta tags. Meanwhile, the solutions pages and resource pages already have all of these — so the homepage is the odd one out.

**Why it matters:** The homepage is the most shared and linked-to page on the site. Without a meta description, Google will auto-generate a snippet (often poorly). Without OG tags, any link shared on LinkedIn, Slack, or Twitter will show a blank preview card — a missed branding opportunity for a company whose target audience lives on LinkedIn. The solutions pages already have structured data and OG tags, so this is likely an oversight rather than a deliberate choice.

**Suggested fix:** Add the following to the `<head>` of `index.html`, right after the existing `<title>` tag:

```html
<meta name="description" content="GrowthMax builds custom AI agents that augment your expertise and amplify your judgment. Partnership, not replacement." />
<meta property="og:title" content="GrowthMax Inc — Custom AI Agents for Your Role" />
<meta property="og:description" content="Custom AI agents designed to augment your expertise, amplify your judgment, and help you achieve outcomes neither of you could alone." />
<meta property="og:url" content="https://www.growthmaxinc.com/" />
<meta property="og:type" content="website" />
<meta property="og:image" content="https://www.growthmaxinc.com/growthMAX.PNG" />
<meta name="twitter:card" content="summary_large_image" />
```

**Effort:** ~5 minutes. Copy the pattern already used on the solutions pages.

---

## Improvement 2: Replace CDN Tailwind with a production build (or at minimum, add a favicon)

**What's happening:** Every page loads Tailwind CSS via `<script src="https://cdn.tailwindcss.com">`. This is the Tailwind Play CDN, which is explicitly documented as "not for production." It ships the entire Tailwind framework (~300KB+ of JS that generates CSS on the fly in the browser), adding unnecessary page weight and a render-blocking dependency on a third-party CDN.

Additionally, no page defines a `<link rel="icon">` favicon. Browsers will request `/favicon.ico` on every page load and get a 404, which shows a broken icon in browser tabs and bookmarks.

**Why it matters:** Page speed directly affects SEO rankings and user experience. The Tailwind Play CDN adds latency on every page load (especially on mobile/slower connections). A missing favicon looks unprofessional in browser tabs and bookmark lists — small detail, big perception impact for a consultancy selling to enterprise buyers.

**Suggested fix (quick win — favicon):** Generate a simple favicon from the GrowthMax logo and add to all pages:
```html
<link rel="icon" type="image/png" href="/favicon.png" />
```

**Suggested fix (higher effort — Tailwind production build):** Set up a simple build step (even just the Tailwind CLI) to generate a minified CSS file with only the classes actually used. This could reduce the CSS payload from ~300KB to ~10-15KB. This is a bigger project but would meaningfully improve load times.

**Effort:** Favicon — 10 minutes. Tailwind production build — 1-2 hours for initial setup.

---

*Next review: March 31, 2026*
