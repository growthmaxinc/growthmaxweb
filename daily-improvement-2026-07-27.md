# Daily Improvement Report — 2026-07-27

## Finding 1 (Ongoing — Critical): Blog Pipeline Still Idle at 56 Days

**Status:** Unresolved since first flagged July 20, 2026.

The automated blog generator (runs Mon/Wed/Fri at 9am UTC) continues to exit with "Nothing to do" — all 23 rows in the Calendar tab of `GrowthMax-Keyword-Program.xlsx` have been published. The most recent post is `2026-06-01-ai-adoption-metrics-that-actually-matter.md`. No new content has shipped in 56 days.

Looking at the GitHub Actions log, "Generate Blog Post" runs #22, #23, and #24 all completed recently in under 3 minutes, consistent with an early exit rather than actual post generation.

**Impact:** The homepage blog teaser and the `/resources/blog.html` index are both Jekyll-driven and will continue showing the June 1 post as "latest" until new posts are added. For a site selling AI expertise, 8 weeks of silence on content undercuts credibility with any visitor who checks the blog.

**Fix:** Open `GrowthMax-Keyword-Program.xlsx` and add new rows to the Calendar tab with status "Not started." The next scheduled workflow run will immediately pick up the first eligible row. `GrowthMax-Keyword-Program-Strategy.md` in the repo root has the keyword framework to draw from. Aim for a new 90-day batch (roughly 36 posts at 3/week through late October).

---

## Finding 2 (New): 8 Daily Improvement Reports Are Publicly Readable on GitHub

**What's happening:** The repo root now contains 8 `daily-improvement-*.md` files (March through July 2026). These files are excluded from the Jekyll build via `_config.yml`, so they don't appear on the live site, but they are fully readable by anyone browsing the public GitHub repo at `github.com/growthmaxinc/growthmaxweb`.

The reports contain internal development notes including: a list of files considered sensitive (`prospect-emails-agent-dev.md`, `.command` scripts), analysis of broken internal links, audit trail of imagery pipeline changes, and details of how the automated blog generation works. The July 20 report mentions the sensitive sales files by name, which draws further attention to them.

This creates a compounding exposure: the sensitive files are public, and so is the audit that describes why they're sensitive.

**Fix (two steps):**

1. Move the `daily-improvement-*.md` files out of the repo root into a private location (a local folder not tracked by git, or a separate private repo). Add `daily-improvement-*.md` to `.gitignore` so future reports don't accumulate in the public repo.

2. While in `.gitignore`, also add `*.command`, `prospect-*.md`, and `FIX_AND_PUSH.command` to prevent the sensitive files that were flagged July 20 from continuing to accumulate. Those files should also be removed from git history if the content is genuinely confidential (requires `git filter-branch` or BFG Repo Cleaner).

---

*Note: The July 20 report's secondary finding (sensitive sales files publicly visible: `prospect-emails-agent-dev.md`, `FIX_AND_PUSH.command`, `COMMIT_AND_PUSH_2026-06-04.command`) also remains unresolved. Finding 2 above addresses the systemic fix for both.*

*Automated review via scheduled task — 2026-07-27*
