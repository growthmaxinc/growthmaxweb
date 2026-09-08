# Daily Improvement Review — June 8, 2026

**Repo:** https://github.com/growthmaxinc/growthmaxweb
**Reviewed:** repo structure, recent commits, `_config.yml`, `scripts/generate-post.py`, structured-data coverage, `robots.txt`, `CLAUDE.md`

---

## What landed since last review (May 18)

Both prior recommendations shipped. Confirmed in the repo:

- ✅ **Duplicate-post bug fixed.** `scripts/generate-post.py` now has a `slug_already_published()` guard that aborts a run *before* burning an LLM + Imagen call if the candidate slug already exists (checked at two points — lines ~718 and ~748). No duplicate slugs remain in `_posts/` — the three May Augmentation duplicates are gone.
- ✅ **Social/Twitter meta fixed.** `_config.yml` now removes the broken `twitter:` block entirely (documented inline: "GrowthMax has no X/Twitter account") and sets a site-wide `image: /growthMAX.PNG` default in the `defaults` block for both posts and all pages, so OG/LinkedIn shares now carry an image.

The site is in genuinely good shape: FAQPage + Organization + WebSite + BlogPosting + BreadcrumbList schema are all present, the post layout emits an FAQ answer block for AEO, and the strategy docs are excluded from the build. The two items below are the highest-leverage things left.

---

## Improvement 1 — HIGH: `CLAUDE.md` describes a site that no longer exists. Fix the drift before it causes a bad edit.

**What:** The project's instruction file still documents the **old static-HTML architecture**, but the repo migrated to **Jekyll** some time ago. Every future change — by me or anyone else following CLAUDE.md — is being guided by a false mental model.

**Concretely wrong sections:**

- **Tech Stack** says: *"Static HTML — no framework, no build step, no bundler."* Reality: Jekyll with `_config.yml`, `kramdown`, `permalink: /blog/:slug/`, and the `jekyll-seo-tag` / `jekyll-sitemap` / `jekyll-feed` plugins. There very much *is* a build step (GitHub Pages runs Jekyll).
- **File Structure** describes blog posts as `blog-[slug].html` at root and tells you to "copy the nav and footer from an existing page." Reality: posts are markdown in `_posts/*.md`, nav/footer/head/scripts live in `_includes/`, and pages use `_layouts/` (`default.html`, `post.html`, `tag.html`). The `blog-*.html` files at root are now just hero images (`.jpg`), not pages.
- **"When Creating New Pages"** and **Deployment** ("just push HTML files," "No build step required") both describe the old flow. Following them today produces a root-level HTML file that bypasses the layout/include system and the SEO-tag plugin entirely.

**Why it matters:** CLAUDE.md is the single source of truth that steers every future edit. Right now it would actively lead a contributor to (a) create a new blog post as a hand-built `blog-foo.html` at root instead of a `_posts/*.md` file — which would skip the `permalink`, the breadcrumb schema, the FAQ/AEO block, and the auto-generated hero pipeline — and (b) hand-copy nav/footer into the page instead of reusing the `_includes/`, guaranteeing drift the next time the nav changes. The cost of stale instructions compounds silently.

**Suggested change:** Rewrite the **Tech Stack**, **File Structure**, **When Creating New Pages**, and **Deployment** sections of `CLAUDE.md` to reflect Jekyll: document the `_config.yml` / `_layouts` / `_includes` / `_posts` model, the `permalink: /blog/:slug/` scheme, the plugin set, and the fact that new posts are markdown front-matter files (ideally generated via `scripts/generate-post.py`, not hand-authored). Keep the Design System and Brand Voice sections — those are still accurate and valuable.

**Effort:** ~30–40 minutes. Pure documentation; zero risk to the live site.

**Expected impact:** Future changes get made against the real architecture the first time, instead of being caught and reworked. Removes the biggest "trap" in the repo for any new contributor (human or agent).

---

## Improvement 2 — MEDIUM: Make the AEO investment legible to answer engines — add `/llms.txt` and explicit AI-crawler rules.

**What:** AEO is a standing priority, and the on-page work is strong (FAQPage schema, the AEO answer-trim step in the pipeline, per-post Q&A blocks). But two pieces of the *off-page* AEO surface are missing:

1. **No `/llms.txt`.** This is the emerging convention (think "robots.txt for LLMs / answer engines") — a curated, plain-markdown map that points answer engines straight at your canonical pages: the pillar page, the solution pages, the FAQ, and the highest-value posts. The site has 25+ posts and a clear pillar/solution structure, which is exactly the case `/llms.txt` is designed for.
2. **`robots.txt` has no AI-crawler directives.** It currently does a blanket `Allow: /` (fine), but never explicitly names the answer-engine crawlers. For a business that *wants* to be cited by AI answer engines, an explicit welcome to `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, and `Google-Extended` is the correct, low-risk signal — and it documents the intent so no one later adds a blanket AI block by reflex.

**Why it matters:** They've already paid the expensive part of the AEO bill (structured data, FAQ blocks, answer-length tuning). `/llms.txt` plus explicit crawler allows is the cheap part that tells the engines *where to look and that they're welcome* — it compounds the existing work rather than duplicating it. For an AI consultancy, being well-represented in AI answer engines is also on-brand proof of competence.

**Suggested change:**

- Add a root `llms.txt` (excluded from nothing — it must be served), e.g.:

  ```
  # GrowthMax Inc — AI agents & training. "Partnership. Not Replacement."
  > Custom AI agents and AI-adoption training that augment human expertise.

  ## Core
  - [Partnership, Not Replacement](https://growthmaxinc.com/partnership.html): Our thesis on AI augmenting people.
  - [AI Agents for Business](https://growthmaxinc.com/ai-agents-for-business.html): What we build and why.
  - [FAQ](https://growthmaxinc.com/resources/faq.html): Common questions about AI adoption.

  ## Solutions
  - [Agent Development](https://growthmaxinc.com/solutions/agent-development.html)
  - [Bootcamp](https://growthmaxinc.com/solutions/bootcamp.html)
  - [Foundations](https://growthmaxinc.com/solutions/foundations.html)

  ## Writing
  - [Blog](https://growthmaxinc.com/resources/blog.html): Essays on AI adoption, change management, and ROI.
  ```

- Append explicit AI-crawler welcomes to `robots.txt` (keep the existing blanket allow):

  ```
  User-agent: GPTBot
  Allow: /
  User-agent: OAI-SearchBot
  Allow: /
  User-agent: ClaudeBot
  Allow: /
  User-agent: PerplexityBot
  Allow: /
  User-agent: Google-Extended
  Allow: /
  ```

**Effort:** ~20 minutes. Both are static files; no template or pipeline changes.

**Expected impact:** Answer engines get a clean, curated entry point to the canonical pages and an explicit signal that crawling/citation is welcome — extending the AEO work already done into the off-page layer where it's currently silent.

---

## Backlog (carried from prior reviews — for awareness, not re-recommending)

- **Email-subscribe path.** Still no low-friction conversion step between "read the blog" and "book a sales call." Flagged repeatedly since April 27.
- **Repo-root clutter.** Daily-improvement reports and hero `.jpg`s sit at root. Cosmetic (excluded from the build); a tighter `.gitignore` / `_config` exclude would tidy `git status` and the GitHub file tree.

---

*Generated automatically by the `review-growthmax-website` scheduled task. This is a read-only review — no files in the live site were changed.*
