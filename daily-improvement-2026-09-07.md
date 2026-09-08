# Daily Improvement Review, 2026-09-07

Repo: `growthmaxinc/growthmaxweb` (main, 178 commits, unchanged since 2026-08-19)
Reviewed: commit count, `_posts/`, Actions run history, `.github/workflows/generate-post.yml`, `scripts/generate-post.py`, `scripts/seo_aeo_audit.py`, `llms.txt`, `BRAND-GUIDELINES.md`, `SEO-STANDARDS.md`, open issues and PRs.

---

## 1. CRITICAL, now escalating: the blog pipeline is 19 days dead and the 2026-08-31 review shipped nothing

**Current state.** Last published post is `2026-08-19-measuring-roi-on-enterprise-ai-training.md`. `_posts/` holds 43 files. The repo is still at 178 commits, the same count recorded in the 2026-08-31 review seven days ago. That means zero commits in 19 days and roughly 8 missed Mon/Wed/Fri publishing slots.

**Correction added after first draft: the fixes exist, they were never applied.** The repo root contains `.pending-fix-2026-08-31/growthmax-fixes.patch` (702 KB, authored 2026-09-01) and `APPLY_AND_PUSH_2026-08-31.command`. That patch already contains the Calendar refill (17 Spoke rows), the notifier change, the runway guard, generated `llms.txt`, a hero image model-string fix, and the em dash cleanup described in section 2 below. Nobody ran the script. The single highest-value action in this repo right now is running it.

**Nothing from the last review was implemented.** I diffed the current files against the three recommendations made on 2026-08-31:

| Recommendation | Status today |
|---|---|
| Refill Calendar with Spoke rows | Not done. Workbook untouched (no commits). |
| Make the stale alert work without issue creation | Not done. `generate-post.yml` lines 106 to 140 still call `issues.create`. |
| Add a runway guard to `generate-post.py` | Not done. `find_next_calendar_row()` returns `(None, None)` silently on exhaustion. |

**The alert is still structurally unable to alert.** The repo shows "Issue creation is restricted in this repository" and zero open issues. The notify step's only output path is `github.rest.issues.create`. Either the call 403s and the step throws, or it silently no-ops. Either way the intended signal, an issue titled "Auto-pipeline produced no post", cannot appear. Seven scheduled runs have now fired into a void.

**What I could not verify.** The Actions listing renders run status client-side, so I could read run numbers and durations but not pass/fail conclusions. Runs #71, #72 and #73 lasted 1m31s, 1m34s and 3m3s, which is longer than the 19 to 30 second no-op runs of #66 through #70. That is worth a human eyeball: a 3-minute run that produces no commit looks less like "no eligible row" and more like generation succeeding and then failing at audit, hero-image validation, or push. Open run #73 and read the "Generate blog post" and "Commit and push" step logs before assuming the diagnosis from 2026-08-31 is still the whole story.

**Recommended order of work, unchanged and now overdue:**

1. Open run #73 and confirm which of the five documented failure modes actually fired.
2. Replace the issue-based notifier with `exit 1` on the job. A red run in the Actions tab is a signal the repo permissions cannot suppress. Keep the diagnostic text as the failure message and wrap `issues.create` in try/catch so a 403 degrades to a hard failure rather than a swallowed one.
3. Refill the Calendar tab with 15 to 19 Spoke rows drawn from the 19 unstarted Master Keywords, then trigger a manual `workflow_dispatch` to confirm recovery.
4. Add a runway guard: fail the run when fewer than 4 eligible Spoke rows remain, so the calendar gets refilled two weeks before it empties.

**First-principles note.** The deeper failure is not the empty calendar, it is that this review loop produces diagnoses that nobody converts into commits. A finding written on 2026-08-31 and still open on 2026-09-07 has the same practical value as a finding never written. The cheapest structural fix is item 2: make the machine escalate to a channel that reaches a human inbox, rather than relying on a weekly report someone has to read and act on. Detection that depends on human diligence is not detection.

---

## 2. The post generator's own prompt tells Claude to use em dashes, and nothing downstream catches them

**Status: already fixed in the unapplied patch.** Everything below describes the state of `main` today. The 2026-08-31 patch corrects the prompt, strips 882 dashes across 43 posts and 10 pages, and adds `scripts/normalize_dashes.py --check` as a blocking audit. It is accurate as a description of live production and moot the moment the patch is applied.

**The defect.** `scripts/generate-post.py` line 89, inside the `BRAND_VOICE` prompt block sent with every generation request:

```
- Use em dashes (---) sparingly for emphasis
```

House style is no em dashes in web or product copy. The generator instructs the exact opposite, on every run, in the prompt that shapes every published post.

**Measured impact.** 229 em dashes across 17 of 43 published posts. The distribution shows the problem worsening, not decaying:

| Post | Em dashes |
|---|---|
| 2026-08-12 growthmax-ai-adoption-framework | 25 |
| 2026-06-01 ai-adoption-metrics-that-actually-matter | 24 |
| 2026-08-10 how-to-upskill-your-workforce-on-ai | 24 |
| 2026-05-25 ai-agent-vs-ai-assistant-vs-chatbot | 21 |
| 2026-07-08 ai-readiness-assessment | 20 |
| 2026-08-05 ai-business-case-template | 19 |
| 2026-07-17 enterprise-ai-agent-security-buyers-checklist | 19 |
| 2026-08-17 ai-rollout-plan-your-team-will-actually-follow | 16 |
| ...9 more | 1 to 17 |

Early posts average 3 to 9. Every August post is in the high teens or twenties. `llms.txt` carries 2 more.

**Root cause, and it is not the prompt line.** The rule is documented nowhere the pipeline can read it:

- `CLAUDE.md` does not state it.
- `BRAND-GUIDELINES.md` does not state it (zero matches for "dash").
- `SEO-STANDARDS.md` does not state it (zero matches for "dash").
- `scripts/seo_aeo_audit.py` has no check for it. The only "dash" hits in that file are em dashes in its own log strings.

Commit `5b98308` is titled "Fix hero image pipeline and enforce the no-dash punctuation rule," so someone intended to close this. The enforcement did not reach the generator prompt, the standards docs, or the audit. The rule currently lives only in one operator's assistant settings, which means it applies when a human is in the loop and evaporates when the automation runs. That is precisely backwards: an automated publishing pipeline needs its style rules encoded in the repo, because the pipeline never reads anyone's preferences.

**Recommended fix, three lines of defense:**

1. **Prompt.** Change `generate-post.py` line 89 to a prohibition: `- Never use em dashes or en dashes. Use commas, colons, or separate sentences.` One line, effective on the next run.
2. **Standards.** Add the punctuation rule to `BRAND-GUIDELINES.md` under writing style and mirror it in `CLAUDE.md`, so it is discoverable by any human or agent working in the repo.
3. **Audit.** Add an em-dash and en-dash check to `seo_aeo_audit.py` as an error, not a warning. The workflow already runs the audit as a pre-commit gate at line 52, so this alone prevents recurrence without any workflow change.

**Backfill.** The 229 existing occurrences are a separate, low-risk cleanup: a scripted replace across `_posts/` and `llms.txt`, reviewed as one commit. Worth doing after the gate is in place, so the fix cannot regress.

---

## Still open from 2026-08-31, not re-argued here

`llms.txt` still lists 10 of 43 posts and has not changed since June. The entire enterprise-buyer cluster, which is the highest commercial-intent content on the site, remains invisible to answer engines. The recommendation stands: generate the `Key Writing` section from `_posts/` front matter as a build step and add `llms.txt` to the `git add` line in `generate-post.yml`.

---

## How to ship this

Everything above is already written and staged. There is nothing to author, only something to run.

**Option A, double-click.** In Finder, open the `growthmaxweb` folder and double-click `APPLY_AND_PUSH_2026-08-31.command`. If macOS blocks it, right-click, choose Open, then confirm.

**Option B, Terminal.** Preferred, because you see the output if a step fails:

```
cd ~/Documents/growthmaxweb
./APPLY_AND_PUSH_2026-08-31.command
```

If it is not executable: `chmod +x APPLY_AND_PUSH_2026-08-31.command` first.

The script syncs local `main` to `origin/main` (discarding anything uncommitted in that folder, which is intentional), applies the patch as one commit, runs three gates (SEO/AEO audit, dash check, llms.txt freshness), pushes only if all three pass, then deletes itself and the pending folder. It is safe to run twice.

If the push prompts for credentials, use your GitHub username and a personal access token as the password, not your account password.

**Then, in the Actions tab:**

1. Run "Backfill All Hero Images" to fix the 19 posts still shipping the generic logo as their OG image.
2. Run "Generate Blog Post" via Run workflow. Expect a new post, a real `blog-*.jpg` hero, and a log line reading `RUNWAY: 16 eligible Spoke rows remaining in Calendar`.

**One thing this session's report cannot resolve.** Runs #71 to #73 took 1m31s to 3m3s, which is too long for a clean "no eligible row" exit. If the manual dispatch above still produces no post, open that run's "Generate blog post" and "Commit and push" step logs. The failure is downstream of calendar selection.

---

## Suggested sequence

1. Run the apply-and-push script. Everything else depends on it.
2. Backfill hero images, then dispatch a manual post run to confirm recovery.
3. If the manual run still produces nothing, read run logs before changing more code.
