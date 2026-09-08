# Daily Improvement Review, 2026-08-31

Repo: `growthmaxinc/growthmaxweb` (main @ `f4a98b5`, 178 commits)
Reviewed: commit history, blog auto-generation pipeline, keyword workbook, llms.txt, sitemap config, open issues and PRs.

---

## 1. CRITICAL: the blog auto-generation pipeline has been silently dead for 12 days

**Symptom.** The last auto-generated post landed 2026-08-19 (`f4a98b5`). Since then five scheduled runs have come and gone (Aug 21, 24, 26, 28, 31) with zero commits. That is roughly five missing posts, and the cadence gap is now visible to crawlers.

**Root cause (confirmed from the workbook, not inferred).** `scripts/generate-post.py` only selects Calendar rows where `Type` contains "spoke". The Calendar (90-day) tab now has exactly three `Not started` rows left, and none of them qualify:

| Row | Date | Type | Title |
|---|---|---|---|
| 5 | 2026-04-20 | Pillar update | Expand /ai-agents-for-business/ into full pillar |
| 6 | 2026-04-23 | New pillar | The AI Adoption Playbook: A People-First Framework |
| 9 | 2026-05-04 | New pillar | AI Partnership, Not Replacement: The Operating Model |

All 44 Spoke rows are `Published` or `Backfilled`. The runner correctly skips pillar work as human-authored, finds no eligible row, exits clean, and commits nothing. The keyword program is exhausted.

**Why nobody noticed.** The workflow has a `Notify on stale pipeline` step that opens a tracking issue when a scheduled run produces no post. GitHub reports **"Issue creation is restricted in this repository"** and the repo has **zero open issues**. The safety net cannot fire. The one control designed to catch exactly this failure is itself non-functional.

**Recommended fix, in order:**

1. **Refill the Calendar with Spoke rows.** 19 Master Keywords are still `Not started` and unmapped to any live URL. High-value, on-strategy candidates:
   - Pillar 2: `custom AI agents for enterprise` (K014), `enterprise AI agent development` (K015), `AI agent integration` (K019), `AI agents for HR` (K022), `AI agent evaluation` (K024), `AI agent observability` (K025)
   - Pillar 4: `enterprise AI training` (K039), `AI literacy program` (K040), `AI bootcamp for engineers` (K042), `AI skills for employees` (K043), `custom AI training for companies` (K047)
   - Pillar 5: `human AI collaboration` (K049), `responsible AI enterprise` (K054)
   - Pillar 1: `AI maturity model` (K005), `AI investment prioritization` (K013)
   - Pillar 3: `AI implementation timeline` (K036), `AI adoption metrics KPIs` (K038)

   That is roughly 9 weeks of runway at 2 posts per week. Add them as `Spoke` rows with forward publish dates and status `Not started`.

2. **Make the alert work without issue creation.** Since issues are restricted, the notify step should instead fail the job (`exit 1`) so the run shows red in the Actions tab and triggers GitHub's default workflow-failure email. Keep the diagnostic text as the failure message. Wrap the existing `issues.create` call in a try/catch so a 403 degrades to a hard failure rather than a swallowed error.

3. **Add a runway guard.** Have `generate-post.py` print a warning and fail the run when fewer than 4 eligible Spoke rows remain, so the calendar gets refilled two weeks before it empties rather than after.

**First-principles note:** the pipeline was designed with two guards against publishing the wrong thing (early and late slug collision) but only one against publishing nothing, and that one depends on a repo permission nobody verified. Silence is the failure mode that costs the most and signals the least. Alerting should never depend on a capability the workflow does not test.

---

## 2. HIGH (AEO): `llms.txt` covers 10 of 43 posts and has not been updated since June

`llms.txt` is the machine-readable map answer engines read first. It currently lists 10 blog posts. 33 are missing, including every post published after 2026-06-01 and the entire enterprise-buyer cluster that is the strongest commercial content on the site:

- `ai-governance-framework-enterprise`
- `enterprise-ai-agent-security-buyers-checklist`
- `how-to-evaluate-ai-vendors-scorecard`
- `ai-business-case-template`
- `what-a-custom-ai-agent-costs-and-why`
- `12-month-ai-transformation-roadmap`
- `ai-readiness-assessment`
- `ai-center-of-excellence-playbook`
- `human-in-the-loop-ai-enterprise`
- `measuring-roi-on-enterprise-ai-training`
- plus 23 others

The high-intent, bottom-of-funnel content is precisely what is invisible to LLM crawlers. `jekyll-sitemap` keeps `sitemap.xml` current automatically; `llms.txt` is hand-maintained and has drifted, which is the predictable outcome of a manual step inside an automated pipeline.

**Recommended fix.** Generate `llms.txt` from `_posts/` as a build step. Keep the hand-written `Core`, `Solutions`, and `More` sections in a template; generate the `Key Writing` section from post front matter (title, permalink, description), newest first, capped at 25 to 30 entries. Add it to the `git add` line in `generate-post.yml` so it updates on every publish and cannot drift again.

**Minor, same file:** `llms.txt` contains 2 em dashes, which violates the punctuation rule in CLAUDE.md. Worth cleaning when the file is regenerated.

---

## Also noted, not urgent

- One open PR on the repo, not reviewed here.
- `scripts/topics.yml` is deprecated and empty. Safe to delete once nothing references it, to remove a misleading second source of truth for topic selection.
- I could not read the Actions run logs directly (fetch blocked), so the run-level confirmation of "no eligible Calendar rows" comes from the workbook state rather than the log line. The workbook evidence is unambiguous.

---

## Suggested order of work

1. Refill Calendar with 15 to 19 Spoke rows from unused Master Keywords, and trigger a manual `workflow_dispatch` run to confirm the pipeline recovers.
2. Change the stale-pipeline notifier to fail the job instead of relying on issue creation.
3. Automate `llms.txt` generation and backfill the 33 missing posts.
