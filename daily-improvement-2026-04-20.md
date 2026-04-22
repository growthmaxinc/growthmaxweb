# Daily Improvement Review — April 20, 2026

**Repo:** https://github.com/growthmaxinc/growthmaxweb
**Latest commit:** `6f003ad` — Auto-generate blog post 2026-04-20

---

## Improvement 1: Optimize the three team photos — 4.75 MB of eager-loaded PNGs for 144px avatars

**What:** The homepage Team section loads three PNG files at full size:

| File | Actual file size | Rendered size (CSS) |
|---|---|---|
| `chris_gemini_cartoon.png` | **1.86 MB** | 144–192 px rounded avatar |
| `debamitro_gemini_cartoon.png` | **1.25 MB** | 144–192 px rounded avatar |
| `rajanish_gemini_cartoon.png` | **1.65 MB** | 144–192 px rounded avatar |
| **Total** | **~4.75 MB** | |

None of them have `loading="lazy"`, `decoding="async"`, or explicit `width`/`height` attributes. They sit far below the fold (after hero, about, process, solutions) but the browser still downloads them on every homepage visit — including from mobile and enterprise networks with aggressive throttling.

See `index.html` lines 388, 404, 420.

**Why it matters:**
- **Performance / Core Web Vitals.** 4.75 MB of below-the-fold images is a massive, unnecessary payload. It inflates total transfer size, slows LCP on mobile, and can meaningfully lower the PageSpeed Insights score Google uses as a ranking signal. For a consultancy selling to enterprise buyers who often first visit from a phone on a client site, this is a bad first impression.
- **Bandwidth cost to visitors.** Mobile visitors on metered plans pay real money for 5 MB of cartoon avatars they may never scroll to.
- **Zero visual upside.** The images render at a maximum of 192 × 192 CSS pixels (384 × 384 actual pixels on 2× retina). They're clipped to a circle and have a 4-pixel cyan border on top. Anything above ~400px on the long edge is invisible detail.

**Suggested actions (both are zero-dependency, static-site-friendly):**

1. **Lazy-load + async decode + explicit dimensions** — three-attribute change per `<img>` tag in `index.html`:
   ```html
   <img src="chris_gemini_cartoon.png"
        alt="Chris Angell"
        width="192" height="192"
        loading="lazy" decoding="async"
        class="w-36 h-36 md:w-48 md:h-48 mx-auto rounded-full object-cover border-4 border-cyan-300">
   ```
   This alone removes them from the critical path on page load and prevents layout shift.

2. **Re-encode to ~400px JPG or WebP** — compress the three PNGs to ~60–100 KB each (target 400 × 400, ~85% quality). Options that don't add a build step:
   - Use squoosh.app or a macOS Preview export once, commit the new files
   - Or let GitHub Pages serve them as-is but rename to `.jpg`/`.webp` variants

   The combined payload drops from 4.75 MB to ~250 KB — a **~95% reduction** on this asset group.

**Effort:** 20 minutes total. Step 1 is three one-line edits. Step 2 is three image conversions.

**Expected impact:** Noticeable improvement in Lighthouse performance score and likely a small but real bump in mobile Search Console "Good URLs" metric within 2–4 weeks.

---

## Improvement 2: Add BreadcrumbList schema + visible breadcrumbs to solution, FAQ, blog-index, and pillar pages

**What:** Blog posts get full `BreadcrumbList` JSON-LD and visible breadcrumbs via `_layouts/post.html` (lines 60–86 and 149–157). But these six important, ranking-eligible pages have **neither**:

- `/solutions/agent-development/`
- `/solutions/bootcamp/`
- `/solutions/foundations/`
- `/resources/blog.html`
- `/resources/faq.html`
- `/ai-agents-for-business/` (the enterprise AI strategy pillar)

No breadcrumbs in the DOM, no `BreadcrumbList` schema. These are precisely the pages targeted for "custom AI agents for enterprise," "enterprise AI strategy," and the FAQ hub — all explicit SEO/AEO targets per recent commit history.

**Why it matters:**
- **AEO-first (per user's saved preference).** Google Search and AI answer engines both use `BreadcrumbList` schema to render enhanced result snippets (the `Home > Solutions > AI Agent Development` trail in the blue URL line). Without it, the result shows a flat URL with no context — a less clickable, less trustworthy-looking listing compared to competitors that do include breadcrumbs.
- **Topical-authority signal.** Breadcrumb structure tells Google how pages relate hierarchically, which strengthens the pillar-plus-cluster model the keyword-program strategy is betting on. Right now the blog posts are the only pages sending that signal.
- **Usability / orientation.** Visible breadcrumbs help a visitor who lands on a solution page from a search result or LinkedIn link understand where they are and navigate up one level without hunting through the nav dropdowns.

**Suggested approach (no custom infrastructure — reuses the exact pattern already in `_layouts/post.html`):**

1. Create a small Jekyll include — `_includes/breadcrumbs.html` — that takes a `section` variable (`Solutions`, `Resources`) and a `section_url`, and outputs:
   - The `BreadcrumbList` JSON-LD block (3 items: Home → Section → Current page)
   - The visible breadcrumb `<nav aria-label="Breadcrumb">` block styled consistently with the blog layout

2. Include it at the top of each listed page:
   ```liquid
   {% include breadcrumbs.html section="Solutions" section_url="/#solutions" %}
   ```

3. For the pillar page (`/ai-agents-for-business/`), use `section="Resources"` and `section_url="/resources/blog.html"` (or create a dedicated `/resources/` landing).

**Effort:** ~45 minutes. One new include file, six one-line insertions, standard Jekyll — no build step, no new dependencies.

**Expected impact:** Richer SERP display for the six highest-intent pages on the site. Reinforces the topical authority plan already in motion (per commits `9c6dfcb`, `2b2b7e1`, `afcece2`).

---

## Notes on prior recommendations

Confirming what's landed since earlier reviews:
- ✅ Preconnect hints (4/13 rec #1) — live in `_includes/head.html` lines 6–11
- ✅ Formspree contact form (4/13 rec #2) — live in `index.html` lines 473–515 with GA4 `generate_lead` event
- ✅ Solution-page heading weight (4/6 rec #2) — all three now use `font-light tracking-tight`
- ✅ Homepage meta/OG tags (3/30 rec #1) — handled via `jekyll-seo-tag` + front matter
- ✅ Favicon (3/30 rec #2 quick win) — `/favicon.svg` in head
- ⏳ Tailwind production build (3/30 rec #2 higher-effort) — still CDN; not yet a bottleneck, fine to defer
- ⏳ Real AI Readiness Assessment (4/6 rec #1) — CTA section is currently commented out in `index.html` lines 437–452; worth revisiting once an assessment tool is chosen

---

*Next review: April 21, 2026*
