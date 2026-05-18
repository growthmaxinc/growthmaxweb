# Daily Improvement Review — May 18, 2026

**Repo:** https://github.com/growthmaxinc/growthmaxweb
**Live site checked:** https://growthmaxinc.com (homepage + `/resources/blog.html`)

---

## What landed since last review (May 8)

Both prior recommendations shipped. Confirmed in repo:

- ✅ **Internal strategy docs no longer published.** `_config.yml` `exclude:` block now lists `SEO-STANDARDS.md`, `GrowthMax-Keyword-Program-Strategy.md`, and `scripts/`. The two strategy URLs that were leaking competitive intel now 404. Sitemap will drop them on next crawl cycle.
- ✅ **`last_modified_at` added to all 9 conversion pages.** Spot-checked: `index.html` (2026-05-05), `partnership.html` (2026-05-05), `ai-agents-for-business.html` (2026-05-05), `solutions/agent-development.html` (2026-05-05), `solutions/foundations.html` (2026-04-22), etc. Sitemap freshness signals now fire for the commercially-valuable URLs, not just blog posts.

Two new candidates below — both flagged from inspecting the live homepage and `/resources/blog.html`.

---

## Improvement 1 — CRITICAL: The same blog post is published three times. Homepage and blog index look broken.

**What:** The auto-generator produced the post *"Augmentation vs. Automation: Why the Distinction Matters"* three separate times — on May 11, May 13, and May 15. All three `_posts/*.md` files render with the same `:slug`, so Jekyll's `permalink: /blog/:slug/` collapses them onto a single canonical URL — but each one still appears as its own card on the blog index and gets selected for the homepage's "Latest 3 posts" loop.

**Confirmed live:**

- **Homepage** ([growthmaxinc.com](https://growthmaxinc.com/)) — "Thoughts on AI & Partnership" section shows the same post listed three times, with three subtly different descriptions ("…how keep…" vs. "isn't just semantics—it determines…" vs. "isn't just semantics — it determines…"). All three cards link to `/blog/augmentation-vs-automation-why-the-distinction-matters/`.
- **Blog index** ([growthmaxinc.com/resources/blog.html](https://growthmaxinc.com/resources/blog.html)) — first three cards are all the same Augmentation post (May 15, May 13, May 11) with three different hero images and three different descriptions, all pointing to one URL.
- **`_posts/`** — locally I only see posts up through `2026-05-04-building-trust-ai-address-team-resistance.md`, but the production site has three May 11/13/15 augmentation files plus a stale auto-pipeline that has been firing on schedule (Generate Blog Post #20, #22, #23, #24 per `/actions`). My local clone is behind, but the live site confirms what's been published.

**Why it matters:**

1. **First-impression bug on the highest-traffic page.** The homepage's social-proof loop ("here's what we've been thinking about") visibly repeats the same headline three times. A prospect lands, scans the section, and concludes either "they don't ship much" or "the site is broken." Both are worse than zero blog cards.
2. **Wastes auto-pipeline spend.** Each duplicate run consumes a Claude API call, a Gemini Imagen call, an AEO audit pass, and a CI/deploy cycle — all to produce content that is then silently overwritten at the URL level. Per the Actions feed, at least four scheduled runs have produced redundant Augmentation content since May 6.
3. **The dedupe check in `generate-post.py` is fooled.** `get_existing_posts()` reads titles from `_posts/*.md`, but only sends `existing[-15:]` to the prompt and only checks against `title`, never against the URL `slug`. With 20+ posts in the directory, an older topic can fall out of the prompt window. Worse, even if a title varies slightly the slug can collide and overwrite the canonical URL silently.
4. **Most likely root cause is the workbook write-back.** The recent commit `9215a1d` ("only process Spoke rows") suggests the calendar tab is the source of truth for "what to generate next." If `mark_row_published()` is failing to write back the published status (or if the workbook is committed back in a way that's lost on the next CI run), every scheduled run picks the same first "Not started" row and generates the same topic. The pattern fits — May 11, 13, 15 are exactly Mon/Wed/Fri.

**Suggested change** — three parts, in order of urgency:

1. **Clean up the existing duplicates** (5 minutes). Delete two of the three `_posts/2026-05-1*-augmentation-vs-automation-*.md` files (keep the most recent, May 15). Delete the matching extra hero images. The homepage and blog index will immediately render correctly on next deploy.

2. **Add a slug-collision guard to `generate-post.py`** before the LLM call (10 minutes):

   ```python
   def slug_already_published(slug: str) -> bool:
       """Any existing _posts file ending in -{slug}.md means the URL is taken."""
       return any(p.name.endswith(f"-{slug}.md") for p in POSTS_DIR.glob("*.md"))

   # After post_data is parsed but BEFORE write_post / hero image generation:
   if slug_already_published(post_data["slug"]):
       print(f"ABORT: slug '{post_data['slug']}' already published — skipping run")
       sys.exit(0)  # exit clean; CI marks the run green, no commit happens
   ```

   This is a belt: even if the workbook write-back is broken, no second post on the same topic will ever ship.

3. **Verify the workbook write-back is actually persisting** (15 minutes — the suspenders). After `update_workbook_status()` runs locally in CI, the workflow needs to commit `GrowthMax-Keyword-Program.xlsx` back to `main` for the next scheduled run to see the new status. Check `.github/workflows/generate-post.yml` — if the workflow `git add`'s only the post file and not the workbook, every run resets to the same "Not started" row. The fix is one line in the workflow's commit step.

**Effort:** ~30 minutes end-to-end. Mostly mechanical.

**Expected impact:** Homepage and blog index stop visibly repeating themselves. Auto-pipeline stops burning API credits on duplicates. The next scheduled run produces a genuinely new spoke from the calendar instead of a fourth Augmentation post.

---

## Improvement 2 — Social link previews are degraded: invalid Twitter handles and no default share image.

**What:** Every page on the site emits this in `<head>`:

```html
<meta name="twitter:card" content="summary">
<meta name="twitter:creator" content="@GrowthMax Inc">
<meta name="twitter:site" content="@">
```

Two of those three values are broken, and there is no `<meta property="og:image">` on the homepage or any non-post page.

**Confirmed live:** I fetched the rendered HTML of `growthmaxinc.com` and `growthmaxinc.com/resources/blog.html`. Both have the same broken tags. The `jekyll-seo-tag` plugin is doing exactly what `_config.yml` told it to — the bug is in the config, not the plugin.

**What's actually wrong:**

- `twitter:creator: @GrowthMax Inc` — not a valid X/Twitter handle (handles can't contain spaces). `jekyll-seo-tag` is interpolating `social.name` from `_config.yml`, which is correctly *"GrowthMax Inc"* for display purposes but should not be used as a Twitter username.
- `twitter:site: @` — the `@` with no handle after it. The plugin emits this when `twitter.username` is unset in `_config.yml`. Currently only `twitter.card` is set; `twitter.username` is missing.
- `twitter:card: summary` (not `summary_large_image`) — `jekyll-seo-tag` upgrades to `summary_large_image` *only when an image is available*. The homepage has no `image:` in front-matter and there's no site-wide default. So even the company's flagship URL falls back to the small thumbnail card.
- **No `og:image`** on the homepage or blog index — meaning when someone shares those URLs on LinkedIn (where GrowthMax actually has a presence), Slack, iMessage, WhatsApp, or anywhere else that uses Open Graph, the preview has no image at all. Just a text card.

**Why it matters:**

- **LinkedIn is the active distribution channel.** The footer and team-member bios only link LinkedIn — no X handle anywhere. LinkedIn uses `og:image`, not Twitter tags, but the missing OG image still hurts. Right now every LinkedIn post that shares a GrowthMax URL gets a flat text preview competing with rich-image previews from every other consultancy in the feed.
- **The hero-image investment isn't paying off where it should.** A meaningful chunk of recent commits (`Imagery v3`, `Imagery v3.1`, "Backfill All Hero Images" runs) went into making per-post hero illustrations consistent. Those images render on the blog index but never appear in link previews because the OG image tag isn't being emitted for the pages people actually share.
- **The invalid Twitter handles are a tiny credibility leak.** Anyone who right-clicks → "View source" or runs the URL through a metadata checker sees `@GrowthMax Inc` (broken) and `@` (broken). It's small, but it suggests "no one is minding the meta tags."

**Suggested change** — `_config.yml`:

```yaml
# Existing block — fix and extend
twitter:
  card: summary_large_image
  username: growthmaxinc           # ADD — the org's X handle; or remove the twitter block
                                   #       entirely if there's no X account to point to
# Remove or correct social.name's role as a Twitter source:
social:
  name: GrowthMax Inc
  links:
    - https://www.linkedin.com/company/growthmaxinc/
# (jekyll-seo-tag uses social.name for Organization schema, which is correct;
#  the twitter:creator bug specifically comes from not having author.twitter set.)

# ADD — site-wide default social-share image
image: /growthMAX.PNG              # or a purpose-built 1200x630 share card if one exists
```

Then on each non-post page that should have its own share image (e.g., `partnership.html`, `solutions/*.html`, `ai-agents-for-business.html`), add to the front-matter:

```yaml
image: /blog-partnership-not-replacement.jpg  # or a page-specific image
```

If there is **no** X/Twitter account, the cleanest fix is to delete the `twitter:` block from `_config.yml` entirely and skip the Twitter tags — better to emit nothing than emit `@`. The `og:image` work still helps LinkedIn/Slack/iMessage regardless.

**Effort:** 10 minutes to fix config + add default image. Another 20 minutes if you also want page-specific share images on the four solution/resource pages.

**Expected impact:** LinkedIn, Slack, and iMessage shares of GrowthMax URLs start rendering with a logo or hero image instead of a blank preview. The broken Twitter handles disappear from page source. Compounds with the SEO/AEO work already done — site looks polished to the same crawlers and humans the rest of the meta-tag work is targeting.

---

## Backlog (mentioned in prior reviews, still open — for awareness, not re-recommending)

- **Email-subscribe path.** Still no low-friction conversion option between "read the blog" and "book a sales conversation." Flagged April 27, deferred again May 8.
- **Untracked-file clutter at repo root.** `PUSH_THIS.sh`, `PUSH_2026-05-08.sh`, `mockup-design-elements.html`, daily-improvement reports. Cosmetic — they're excluded from Jekyll builds, just clutter `git status` and the GitHub file tree. A `.gitignore` covering `daily-improvement-*.md` and `PUSH_*.sh` would clean it up.
- **`index.php` at repo root.** Single PHP file in a static Jekyll/GitHub Pages site. Likely a relic — worth confirming whether anything still references it before deleting.

---

*Generated automatically by the `review-growthmax-website` scheduled task.*
