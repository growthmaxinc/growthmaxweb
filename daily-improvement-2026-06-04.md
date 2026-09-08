# Daily Improvement Review — June 4, 2026

**Repo:** https://github.com/growthmaxinc/growthmaxweb
**Branch checked:** `main` (latest commit `f673715` via Generate Blog Post run #24, scheduled)
**Live site:** confirmed indirectly via `_posts/` and `.github/workflows/`

---

## What landed since last review (May 25)

The May 25 critical recommendation (silent auto-pipeline) shipped in full:

- ✅ **Auto-pipeline back online.** First post since May 15 landed May 25 — `2026-05-25-ai-agent-vs-ai-assistant-vs-chatbot.md` — and the GitHub Actions log shows scheduled runs #20, #23, and #24 all completed. The diagnosis trail in repo commits (`d630415` "Fix blog auto-generator: skip header row + add missing validate_hero_...", `9215a1d` "Auto-generator: upgrade to claude-sonnet-4-6 + only process Spoke rows") confirms two distinct root causes were found and fixed.
- ✅ **Stale-pipeline canary shipped.** `.github/workflows/generate-post.yml` lines 81–140 now have a `Notify on stale pipeline` step that opens (or comments on) an issue labeled `auto-pipeline-stale` whenever a scheduled run finishes without producing a commit, with a five-cause diagnosis checklist baked into the issue body. This is the exact mechanism May 25 recommended — converts "silently broken" into "open issue in repo."
- ✅ **Hero-image validator added.** `Validate hero image is on-brand` step now runs `scripts/validate_hero_images.py` after generation, guarding the 1200×630 brand-correct output before commit.
- ✅ **Imagery v3 / v3.1 shipped.** `67d22f2` and `59ff884` added composition variety, gender quota, lighting variety, and stripped hex codes from the prompt — addresses the May 18 imagery audit's "fragmented across 3 styles" finding.

May 25's Improvement 2 (workbook backfill) does **not** appear to have shipped yet — `scripts/backfill_workbook.py` is not in the repo, and no commit message mentions a one-time backfill. That carries forward below as Improvement 2.

Two new candidates this week, both driven by what showed up in run #24's annotation panel.

---

## Improvement 1 — CRITICAL: Node.js 20 forced-deprecation already happened (June 2). All six workflows are now running with a soft warning that becomes a hard failure on September 16.

**What:** Every scheduled run since June 2 shows the same four warnings in the Actions annotation panel. From the most recent successful run (#24, today's scheduled run):

> Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/configure-pages@v5`, `actions/upload-artifact@v4`, `actions/deploy-pages@v4`. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026. Node.js 20 will be removed from the runner on September 16th, 2026.

Plus a second standing warning on the build step:

> The github-pages gem can't satisfy your Gemfile's dependencies. If you want to use a different Jekyll version or need additional dependencies, consider building Jekyll site with GitHub Actions.

**Confirmed in repo:**

`.github/workflows/generate-post.yml` pins `actions/checkout@v4` (line 31, 148), `actions/setup-python@v5` (line 34), `actions/github-script@v7` (line 88), `actions/configure-pages@v5` (line 153), `actions/upload-pages-artifact@v3` (line 162), `actions/deploy-pages@v4` (line 173).

`.github/workflows/deploy.yml` pins `actions/checkout@v4` (line 34), `actions/configure-pages@v5` (line 37), `actions/upload-pages-artifact@v3` (line 46), `actions/deploy-pages@v4` (line 57).

The other workflows (`backfill-heroes.yml`, `sample-heroes.yml`, `seo-audit.yml`, `list-imagen-models.yml`) almost certainly use the same major-version pins.

**Why it matters:**

1. **The clock is real.** June 2 was the forced-runtime cutover (warnings only — workflows still pass because Microsoft re-issued v4/v5 with Node 24-compatible code under the same tag). **September 16 is the hard removal date.** On that day, any workflow still pinned to `@v4` of these actions stops running. The auto-pipeline goes silent again — same failure mode that consumed two weeks of debugging in May. Worth fixing now while it's a one-line bump in each workflow, not in mid-September when it surfaces as broken CI.
2. **Warning noise is masking real signal.** Every workflow run now has four-to-five Node 20 deprecation annotations plus the Gemfile warning. The next genuine warning (a real bug) gets harder to spot because the run page is already painted yellow on every run. Annotation hygiene matters more once you have a canary in place — the canary doesn't help if the surrounding warnings have desensitized you.
3. **Cheapest possible CI hygiene win.** Bumping action versions is a five-minute change with near-zero risk: these actions are designed to be major-version-stable, and `v5`/`v6` releases of each have been out for months.

**Suggested change** — two small commits:

1. **Bump action major versions across all workflows** (5 minutes). In `.github/workflows/generate-post.yml`, `.github/workflows/deploy.yml`, and the other four workflow files:

   ```
   actions/checkout@v4              →  actions/checkout@v5
   actions/setup-python@v5          →  actions/setup-python@v6
   actions/configure-pages@v5       →  actions/configure-pages@v6   (if released; otherwise leave on v5 with an explicit Node 24 opt-in)
   actions/upload-pages-artifact@v3 →  actions/upload-pages-artifact@v4
   actions/upload-artifact@v4       →  actions/upload-artifact@v5
   actions/deploy-pages@v4          →  actions/deploy-pages@v5
   actions/github-script@v7         →  actions/github-script@v8
   actions/jekyll-build-pages@v1    →  (leave — v1 is the canonical pin)
   ```

   Run any one workflow manually (`workflow_dispatch`) after the bump to confirm green. If a specific action's v-bump introduces an input rename, revert just that one and follow the action's release notes.

2. **Fix the github-pages Gemfile warning** (5 minutes). The current `Gemfile` is pinning a `github-pages` gem version that's behind what the runner expects. Either run `bundle update github-pages` locally and commit the new `Gemfile.lock`, OR (the cleaner fix the warning itself suggests) drop `github-pages` and use `actions/jekyll-build-pages@v1` directly, which is already what the workflows do. The `github-pages` gem is only needed for local Jekyll serve, not for CI build — pruning it from `Gemfile` removes the warning entirely.

**Effort:** ~10 minutes for the action bumps + 5 minutes for the Gemfile. Both can land in a single PR.

**Expected impact:** Annotation panel returns to clean (only real warnings show). The auto-pipeline survives the September 16 Node 20 removal without intervention. Zero behavior change to the site.

---

## Improvement 2 — Carryover: keyword workbook backfill is still open, and the gap is now wider.

**What:** Last review flagged that `GrowthMax-Keyword-Program.xlsx`'s Calendar tab showed **1 Published row vs. 20 actual posts** in `_posts/`. No `scripts/backfill_workbook.py` commit has landed since. One additional post has been auto-generated (May 25's "AI Agent vs. AI Assistant vs. Chatbot"), so the workbook now has approximately **2 Published rows vs. 21 actual posts** — the gap moved from 19 to 19, but the *proportion* of misreporting just got worse.

The reason this hasn't shipped is understandable — the May 25 → June 4 window was correctly spent stabilizing the pipeline itself. Reporting accuracy is the obvious next priority now that the pipeline is healthy.

**Why it matters** (compressed from the May 25 writeup, which is still accurate):

1. **Sibling-link quality is silently capped.** `sibling_spokes()` reads "published URLs in this pillar" from Master Keywords. Every new auto-generated post is told there are ~1/10th as many siblings as actually exist, which directly throttles internal linking and pillar coherence. This compounds with every new post.
2. **The workbook can't answer "what should we cover next?".** With 19 published posts invisible to the program, "fill the underrepresented pillar next" reasoning is impossible. Recent commit `9215a1d` ("only process Spoke rows") tightens how the script consumes the workbook — making workbook accuracy a more load-bearing dependency than it was a week ago.
3. **It's a 30-minute one-time fix.** Most of the logic already exists in `writeback_publish()` and `_slugify()` in `scripts/generate-post.py`. The backfill is a wrapper that walks `_posts/*.md` and calls the canonical writeback helper for each post that has no matching Published row.

**Suggested change** — unchanged from May 25:

1. Add `scripts/backfill_workbook.py` that walks `_posts/*.md`, matches against Calendar rows by `_slugify(working_title) == post.slug`, and either updates the matching "Not started" row to "Published YYYY-MM-DD" or appends a "Backfilled YYYY-MM-DD" row. Call `writeback_publish()` so Master Keywords gets the same treatment via the canonical code path.
2. Run it locally once, commit the updated `.xlsx`, push.
3. (Optional, deferrable) Add `scripts/assert_workbook_in_sync.py` as a CI step on `pull_request` so the gap can't reopen — exits non-zero if `len(_posts/*.md) != len(Calendar Published rows)`.

**Effort:** ~30 minutes for the one-time backfill. The assert script is a separate ~10 minutes.

**Expected impact:** `sibling_spokes()` returns real numbers, every new auto-generated post links to the full ~21-post sibling set instead of ~2. Future stakeholder questions about coverage get correct answers from the workbook.

---

## Backlog (still open from prior reviews — for awareness, not re-recommending)

- **Email-subscribe path.** Still no low-friction conversion between "read the blog" and "book a sales conversation." Flagged April 27, deferred again May 8, May 18, May 25.
- **`.gitignore` for `daily-improvement-*.md`.** Cosmetic; deferred again.
- **CI canary for blog auto-pipeline.** ✅ Shipped — closing this entry.

---

*Generated automatically by the `review-growthmax-website` scheduled task.*
