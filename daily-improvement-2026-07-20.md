# Daily Improvement Report — 2026-07-20

## Finding 1 (Urgent): Blog Pipeline Idle Since June 1 — Keyword Calendar Exhausted

**What's happening:** No new blog posts have been published in 7 weeks. The "Generate Blog Post" workflow (running Mon/Wed/Fri on schedule) is completing successfully but doing nothing — the script prints "keyword program is fully published. Nothing to do." and exits.

**Root cause:** All 23 rows in the Calendar (90-day) tab of `GrowthMax-Keyword-Program.xlsx` have been published. The auto-generator has no remaining "Not started" rows to process.

**Impact:** The site has been dark on content since June 1. At 3 posts/week, this gap represents roughly 21 posts that could have been published. Search visibility compounds over time — every week without new content is a missed opportunity.

**Fix:** Open `GrowthMax-Keyword-Program.xlsx` and add new rows to the Calendar tab with status "Not started" and target publish dates. The next scheduled workflow run will immediately pick up the first eligible row and resume generation. The `scripts/topics.yml` file also confirms the workbook is now the sole source of truth for topics.

Suggested approach: plan a new 90-day batch (roughly 36 posts at 3/week through mid-October) using the keyword strategy file already in the repo (`GrowthMax-Keyword-Program-Strategy.md`) as the source.

---

## Finding 2: Internal Sales Files Are Publicly Visible on GitHub

**What's happening:** The public repo contains `prospect-emails-agent-dev.md` in the root — a file with 4 cold email sales templates, including targeting rationale and a note that replies route to `hi@growthmaxinc.com`. Also present: `FIX_AND_PUSH.command` and `COMMIT_AND_PUSH_2026-06-04.command` (macOS shell scripts exposing internal workflow details).

**Root cause:** These files were added to the repo for convenience and never moved out. The `_config.yml` excludes them from the Jekyll build, but they are fully readable by anyone browsing `github.com/growthmaxinc/growthmaxweb`.

**Impact:** Prospecting strategy and email templates are visible to competitors, prospects, and the general public. The `.command` scripts reveal internal tooling patterns.

**Fix:** Remove these files from the repo and add a `.gitignore` entry for `*.command` and `prospect-*.md` to prevent future recurrence. If the content needs to live somewhere, move it to a private repo or a local-only folder not tracked by git.

Files to remove:
- `prospect-emails-agent-dev.md`
- `FIX_AND_PUSH.command`
- `COMMIT_AND_PUSH_2026-06-04.command`

Consider also whether the `daily-improvement-*.md` files (7 of them, accumulating) should remain in the public repo long-term — they expose the site's internal development audit trail.

---

*Status check: The June 29 issues (missing `image_alt` in frontmatter, broken `/about/claude-partnership/` links) appear resolved — `generate-post.py` now emits `image_alt` on every post, and `about/claude-partnership.html` exists with the correct permalink.*

*Automated review via scheduled task — 2026-07-20*
