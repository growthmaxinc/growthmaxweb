# SEO + AEO Standards

This is the single source of truth for what "compliant" means on growthmaxinc.com. Every published page must pass `scripts/seo_aeo_audit.py` (CI enforces this on every push to `main`).

If you're a contributor, a subagent, or future-me — read this before editing or generating any page.

---

## What "AEO" means here

**Answer Engine Optimization** is what makes a page citable by ChatGPT, Perplexity, Google AI Overviews, and Featured Snippets. The mechanism is simple: those engines preferentially quote *short, declarative chunks* that directly answer a search-shaped question. If your chunk is too long, you either get truncated mid-sentence or get skipped in favor of a competitor's tighter answer.

The whole AEO discipline reduces to one rule: **every question H2 must be followed by a 40–60 word direct answer**.

---

## Hard rules (CI fails the build if any of these are violated)

### 1. AEO answer length
Every H2 phrased as a question (ends with `?`) must be immediately followed by a paragraph of **40–60 words**. The first sentence resolves the question; the remaining 1–2 sentences add color or specificity. Any further elaboration goes in the *second* paragraph of that section.

This applies to:
- Markdown posts: the first paragraph after `## Question?` (excluding markdown formatting)
- Pillar/HTML pages: the first `<p>` element after `<h2>Question?</h2>`

CTA-style H2s ("Ready to...?") are exempt.

### 2. H2 hygiene
H2 headings never end with a period. Question H2s end with `?`; topical H2s end with no terminal punctuation. Sentence-style H2s ("The path forward.") are not allowed.

### 3. Meta description length
Front-matter `description:` field must be **≤ 160 characters**. Google truncates SERP descriptions around 155–160 chars; longer descriptions render with `…` mid-word.

### 4. TLDR length
Front-matter `tldr:` field must be **≤ 220 characters**. The TLDR renders in a callout box at the top of every post; longer TLDRs visually overwhelm the hero.

### 5. Posts: required front-matter fields
Every file in `_posts/` must have these fields:
- `title`, `subtitle`, `description`, `category`, `read_time`, `tags`, `keywords`
- `slug`, `image`, `image_alt`
- `tldr`, `faq` (FAQPage schema renders from this)
- `pillar`, `pillar_page`, `primary_keyword` (the keyword program uses these for sibling discovery)

### 6. Pillar/HTML pages: required front-matter fields
Every Jekyll-processed HTML page must have:
- `layout` (usually `default`) OR an inline `{% include nav.html %}`
- `title`, `description`, `permalink`

### 7. No `<h1>` in post bodies
The post layout (`_layouts/post.html`) emits `<h1>{{ page.title }}</h1>`. A second H1 in the markdown body creates a duplicate-H1 SEO problem. Use `##` and below in post markdown.

### 8. Internal link integrity
Every internal link of the form `/blog/<slug>/`, `/resources/<page>/`, `/solutions/<page>/`, `/partnership/`, or `/ai-agents-for-business/` must resolve to a real file in the repo. Broken internal links waste crawl budget and frustrate users.

### 9. FAQPage JSON-LD validity
Any `<script type="application/ld+json">` containing `"@type": "FAQPage"` must parse as valid JSON.

---

## Soft rules (warnings, not failures)

- **Title length**: aim for ≤ 60 chars (Google truncates titles around 60). Not enforced because brand titles often run a bit longer.
- **Question H2 count per post**: the keyword program recommends ≥ 3 question-format H2s per spoke post. Enforced by the audit as a warning.
- **Sibling link count**: the program recommends 2–3 inline links to sibling spokes. Audit reports the count but doesn't fail.

---

## Workflow

### When you (or a subagent) write or edit a page

1. **Before starting**, read this doc.
2. **While writing**, count words on each question-H2 paragraph as you go. Aim for 50 words (middle of the 40–60 range = safety margin).
3. **Before declaring done**, run:
   ```
   python scripts/seo_aeo_audit.py
   ```
4. If the script reports any errors, fix them. Do not ship until it's clean.

### When the auto-generation pipeline runs

`scripts/generate-post.py` runs the same audit logic on its own output before saving. If the generated post fails AEO validation, the script regenerates (up to 3 attempts) with feedback like "previous attempt had paragraph X at 87 words; tighten to 40–60." If 3 attempts all fail, the script exits non-zero, the GitHub Action fails, and the Calendar row stays `Not started` — the bad post never gets committed.

### When CI runs on a PR or push to main

The `.github/workflows/seo-audit.yml` workflow runs `python scripts/seo_aeo_audit.py` and fails the check if exit code is non-zero. Required-status-check on `main` blocks merges that introduce regressions.

---

## Anti-patterns (don't do these)

- **Don't compress prose with regex.** This was tried in May 2026, dropped junk filler text into 11 files, and broke things worse than the original problem. Prose rewriting requires the Edit tool, one paragraph at a time.
- **Don't trust subagent self-reports without verification.** Always run the audit yourself after a subagent declares done.
- **Don't add filler to hit word counts.** If a paragraph is short, add a concrete example, a specific number, or one more dimension of the answer. Don't pad with synonyms or repeat the same idea.
- **Don't bury AEO answers under throat-clearing preamble.** "There are several reasons why AI implementations may not deliver expected outcomes…" wastes the chunk. The first sentence under a question H2 should resolve the question.
- **Don't put H1s in post markdown.** The layout adds them.

---

## Why this exists

In May 2026 we shipped 20 blog posts with question-format H2s but 92% of the answer paragraphs were too long (~100 words instead of 40–60). The mistake wasn't bad writing — it was the absence of a binding test. Every check in this doc has a corresponding line in `scripts/seo_aeo_audit.py`. If a check isn't enforced by the script, it isn't really a standard.
