# Daily Improvement Review — May 25, 2026

**Repo:** https://github.com/growthmaxinc/growthmaxweb
**Live site checked:** https://growthmaxinc.com (homepage + Calendar/Master Keywords workbook state)

---

## What landed since last review (May 18)

Both prior recommendations shipped. Confirmed in repo:

- ✅ **Duplicate blog posts fixed.** The May 11 and May 13 `_posts/*augmentation-vs-automation*.md` files were deleted (commit `0fc8013`). `scripts/generate-post.py` now has both an early-guard (`_slugify(working_title)` checked against `_posts/*.md`) and a late-guard (LLM-produced slug rechecked after generation). The homepage's "Latest 3" loop now renders Augmentation (May 15), Building Trust (May 4), How to Train Your Team (May 1) — three distinct posts, three distinct URLs. Confirmed live.
- ✅ **Social link previews fixed.** `_config.yml` `twitter:` block removed, site-wide default `image: /growthMAX.PNG` added under the `defaults` block (commit `1973a4e`). Confirmed live — page source now emits `<meta name="twitter:card" content="summary_large_image">`, `<meta property="og:image" content="https://growthmaxinc.com/growthMAX.PNG">`, and no more `@` or `@GrowthMax Inc` broken handles.
- ✅ **Bonus follow-up shipped.** Commit `3a40a0c` deleted the duplicate `<link rel="canonical">` on `index.html` (jekyll-seo-tag is now the single source) and removed the dead `/index.php` file Google had been indexing as a duplicate of `/`. Search Console "Alternate page with proper canonical tag" issue should now be re-validatable.

Two new candidates below — both from comparing the live blog state to the keyword program's Calendar tab.

---

## Improvement 1 — CRITICAL: The blog auto-pipeline has been silent for 10 days. Four scheduled runs have produced nothing.

**What:** The auto-generator's last published post was May 15 (*"Augmentation vs. Automation: Why the Distinction Matters"*). The cron schedule in `.github/workflows/generate-post.yml` is `0 9 * * 1,3,5` — every Monday, Wednesday, and Friday at 9am UTC. Since May 15:

- Mon May 18 — no post
- Wed May 20 — no post
- Fri May 22 — no post
- Mon May 25 (today) — no post

Four consecutive missed scheduled runs. `_posts/` ends at `2026-05-15-augmentation-vs-automation-why-the-distinction-matters.md`. `git log` since May 19 shows only the three hand-authored fix commits (`0fc8013`, `1973a4e`, `3a40a0c`) — zero auto-generated commits from `github-actions[bot]`.

**Confirmed live:**

- **Homepage** ([growthmaxinc.com](https://growthmaxinc.com/)) — "Thoughts on AI & Partnership" section's lead card has been the Augmentation post for 10 straight days. A return visitor on the Mon/Wed/Fri rhythm sees the same headline four visits in a row.
- **Blog index** ([growthmaxinc.com/resources/blog.html](https://growthmaxinc.com/resources/blog.html)) — top of feed unchanged since May 15.
- **Calendar (90-day) tab** of `GrowthMax-Keyword-Program.xlsx` — at least six "Not started" Spoke rows are already overdue and would have been picked up by `find_next_calendar_row()` on any of the four missed runs:

  | Row | Publish date | Working title |
  |---|---|---|
  | 8 | 2026-04-30 | AI Agent vs. AI Assistant vs. Chatbot |
  | 10 | 2026-05-07 | AI Adoption Metrics That Actually Matter |
  | 11 | 2026-05-11 | AI Agent Architecture Explained (for Non-Engineers) |
  | 13 | 2026-05-18 | What a Custom AI Agent Costs (and Why) |
  | 14 | 2026-05-21 | AI Agents for Operations Teams |
  | 15 | 2026-05-25 | Is Your Organization AI-Ready? A Self-Assessment |

  None of those slugs collide with any file in `_posts/`, so the slug-collision guard added on May 18 is **not** what's killing the runs. The pipeline should pick row 8, generate it, and move on.

**Why it matters:**

1. **Stale-blog signal is the worst it's been.** Two reviews in a row have flagged blog-index quality. Last time it was three duplicate cards. This time it's one card that hasn't moved in 10 days. The blog is the consultancy's most direct "we ship" demonstration for prospects landing from search or LinkedIn; "newest post is 10 days old" reads roughly the same as "we don't ship much."
2. **AEO/SEO momentum is paused.** Six overdue spoke posts means six missing internal links into pillar pages, six missing fresh dates for sitemap freshness signals, and six missing chances to rank on the long-tail keywords already mapped in the Master Keywords sheet. Each delayed week compounds.
3. **Failure mode is silent.** GitHub Actions runs that exit non-zero produce no commit, no notification, and no visible artifact in the repo — the only way to detect a broken pipeline today is to notice that no auto-generate commit landed. There's no canary, no Slack ping, no dashboard. After 10 days of silence I had to reverse-engineer the state from `git log` and the workbook.

**Most likely root causes** — in descending order of probability:

a. **Secret expired or rotated.** The workflow reads `ANTHROPIC_API_KEY: ${{ secrets.WEBSITE }}` and `GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}`. If either secret was rotated (or the GitHub Action's permissions to read it changed), the very first API call fails and the script exits non-zero before any commit. Worth checking first because it's the cheapest diagnosis and the most common cause of "silent CI" symptoms.

b. **AEO validation failing 3× in a row.** `generate_post_with_validation()` retries up to `MAX_GENERATION_RETRIES = 3` and then raises `RuntimeError`, which `main()` catches and exits 1 on. If a particular row (e.g., row 8's "AI Agent vs. AI Assistant vs. Chatbot") consistently produces a post that fails one of the AEO checks (likely culprits: too few question-style H2s, meta description >160 chars, AEO answer outside the 40–60-word band), every run on that row will fail. The Calendar row stays "Not started," so the next scheduled run picks the *same* row, fails again, and the pipeline is permanently stuck.

c. **Imagen 4 / paid-tier billing issue.** `IMAGE_MODEL_TIER=paid` is hardcoded in the workflow. If Google AI Studio billing lapsed or the project's Imagen 4 quota tripped, `generate_hero_image()` raises before `save_post()`, and the post never lands. Cheap to check — Google Cloud billing console will show it immediately.

d. **GitHub Actions billing.** Less likely on a public repo, but worth glancing at the Actions tab.

**Suggested change** — three parts, in order:

1. **Diagnose first** (~5 minutes). Open the GitHub Actions tab → "Generate Blog Post" workflow. The failed runs since May 18 are there; the failing step name tells you which root cause is right. (Anthropic API call failing → secret. Audit step failing → AEO. `generate_hero_image` failing → Imagen.) **Do this before changing anything.**

2. **Apply the right fix** based on what step 1 surfaces:
   - **Secret expired:** rotate `secrets.WEBSITE` (Anthropic key) or `secrets.GEMINI_API_KEY`, re-run the latest failed workflow with "Re-run failed jobs."
   - **AEO retry exhaustion:** open the workflow log, find the "Last errors: [...]" line at the bottom of the failing run. If the same error repeats across attempts, either fix the prompt (e.g., add a system instruction forcing meta description ≤160 chars) or relax the validator for the specific check that's failing.
   - **Imagen billing:** re-enable billing on Google AI Studio, or temporarily set `IMAGE_MODEL_TIER=free` in the workflow env so the free Nano Banana tier picks up the slack until billing is restored.

3. **Add a 10-minute canary so this never goes silent again** — append to the existing `Commit and push` step in `.github/workflows/generate-post.yml`:

   ```yaml
   - name: Notify on stale pipeline
     # If no new post was committed (could be the slug guard, could be a
     # silent failure earlier in the workflow), open or update a tracking
     # issue so silent-CI doesn't go undetected for another 10 days.
     if: steps.commit.outputs.has_new_post != 'true'
     uses: actions/github-script@v7
     with:
       script: |
         const title = "Auto-pipeline produced no post today";
         const issues = await github.rest.issues.listForRepo({
           owner: context.repo.owner, repo: context.repo.repo,
           state: "open", labels: "auto-pipeline-stale"
         });
         const body = `Run ${context.runId} produced no commit. Likely causes: expired secret, AEO retry exhaustion, Imagen billing, or all eligible Calendar rows skipped. See run log.`;
         if (issues.data.length === 0) {
           await github.rest.issues.create({
             owner: context.repo.owner, repo: context.repo.repo,
             title, body, labels: ["auto-pipeline-stale"]
           });
         } else {
           await github.rest.issues.createComment({
             owner: context.repo.owner, repo: context.repo.repo,
             issue_number: issues.data[0].number, body
           });
         }
   ```

   This converts "silently broken" into "an open issue in the repo." Same signal a human would otherwise have to detect by noticing no commit landed.

**Effort:** ~15 minutes to diagnose + fix the immediate cause. Another 10 minutes to add the canary. The canary is the more valuable investment — the next failure mode is unlikely to be the same as this one.

**Expected impact:** Blog index resumes shipping fresh content on Mon/Wed/Fri. Six overdue spokes get picked up in the next ~2 weeks. The next silent failure surfaces as a GitHub issue within hours instead of within 10 days.

---

## Improvement 2 — `GrowthMax-Keyword-Program.xlsx` Calendar/Master Keywords is dramatically out of sync with `_posts/`. The reporting tab is lying.

**What:** The Calendar (90-day) tab is supposed to be the source of truth for "what's published vs. what's queued." Right now it shows **1 row marked Published** and **25 rows marked "Not started."** The actual `_posts/` directory contains **20 published posts**.

**Confirmed via the workbook:**

```
Status counts in Calendar (90-day):
  'Not started':            25
  'Published 2026-05-15':    1
```

The only row marked Published is row 7 (Augmentation vs. Automation). The other 19 live posts — *Where Do I Fit, Why AI Implementations Fail, Your First AI Agent, Measure ROI, Custom vs. Off-Shelf, People-First Strategy, 90-Day Timeline, Hidden Costs, Change Management, Stalled Project, Training vs. Implementation, Signs Team Ready, Post-Launch Management, When to Hire Consultant, Scale After First Success, Second Project, Executive Buy-In, How to Train Team, Building Trust* — are not represented in the Calendar at all. Master Keywords almost certainly has the matching gap (the writeback path updates both).

**Why this happened:** The auto-pipeline only writes back the Calendar row it generated *from*. Posts that pre-date the keyword program were never backfilled into the workbook. The Calendar's earliest dated row is April 20, but `_posts/` reaches back to March 19. Everything before April 20 is invisible to the program.

**Why it matters:**

1. **The workbook is becoming useless as a reporting artifact.** Any "how many posts have we published against the keyword program" question gives the wrong answer by 19. If anyone is using this sheet to brief stakeholders, plan budget, or decide what to cover next, the data is misleading.
2. **Sibling-link quality is silently degrading.** `sibling_spokes()` in `generate-post.py` reads "published URLs in this pillar" from the Master Keywords tab. If 19 published posts are missing from Master Keywords, every new post's prompt is told there are far fewer sibling posts to link to than actually exist. The result is fewer internal links and worse pillar coherence — a quiet AEO/SEO regression baked into every future post.
3. **It blocks any future "what's the next eligible spoke" reasoning.** Today the script just walks the Calendar top-down. A smarter scheduler — "fill the pillar that's underrepresented next" — needs accurate counts of what's been published per pillar. Right now those counts are wrong.

**Suggested change** — one small backfill script + one workflow follow-up:

1. **Backfill the workbook** (~30 minutes, one-time). Add `scripts/backfill_workbook.py` that:
   - Walks `_posts/*.md`
   - Reads each post's `slug`, `pillar`, `primary_keyword`, `image`, and the file's date
   - For each post that doesn't already have a matching "Published" row in Calendar, either:
     - Updates the matching "Not started" row (matched by `_slugify(working_title) == post.slug`), OR
     - Appends a new "Published" row at the bottom of Calendar with a `Backfilled YYYY-MM-DD` note
   - Calls the existing `writeback_publish()` helper so Master Keywords gets the same treatment via the canonical code path.

   Run it locally once, commit the updated `.xlsx`, push.

2. **Add a CI assertion so it never drifts again** (10 minutes). Append a step to `.github/workflows/generate-post.yml` (or a new lightweight workflow on `pull_request`):

   ```yaml
   - name: Workbook must match _posts/
     run: python scripts/assert_workbook_in_sync.py
   ```

   The script counts `_posts/*.md` vs. Calendar `Published *` rows and exits non-zero if they diverge. Cheap, prevents the same drift from recurring.

**Effort:** ~40 minutes for the one-time backfill plus the guardrail. The script is straightforward — most of the logic already exists in `writeback_publish()` and `_slugify()`.

**Expected impact:** The keyword program becomes an accurate reporting artifact again. Sibling-link quality on future auto-generated posts improves (more linked siblings per pillar = better topical authority signals). Future stakeholder questions about coverage get correct answers.

---

## Backlog (still open from prior reviews — for awareness, not re-recommending)

- **Email-subscribe path.** Still no low-friction conversion between "read the blog" and "book a sales conversation." Flagged April 27, deferred again May 8 and May 18.
- **Untracked-file clutter at repo root.** `daily-improvement-*.md`, `chris_gemini_cartoon.jpg`-style stray files. Already excluded from Jekyll build via `_config.yml`. A `.gitignore` for `daily-improvement-*.md` would clean `git status`. Cosmetic.
- **CI canary / failure notification.** Now upgraded from "nice-to-have" to part of Improvement 1 above — included as the third sub-step there.

---

*Generated automatically by the `review-growthmax-website` scheduled task.*
