---
name: growthmax-imagery
description: Apply GrowthMax's visual identity to any image produced for the website — blog hero images, OG/social cards, page heros, anything else with the GrowthMax name on it. Use this skill ANY time a deliverable will be rendered as an image for growthmaxinc.com. Triggers include "blog hero," "header image," "OG image," "social card," "page hero," "regenerate the image," "make a graphic," "design an illustration." Do NOT use AI raster image generators or photographic stock — this skill defines the only acceptable production path: the flat-vector PIL renderer at `scripts/generate-hero-image.py`.
---

# GrowthMax Imagery — Creative Direction

This is the single source of truth for any image rendered for **growthmaxinc.com**. The auto-pipeline at `scripts/generate-post.py` reads this file on every run; humans regenerating images by hand follow the same rules. There is no second style, no fallback look, no "just for this one post" exception.

---

## The promise

A GrowthMax image looks like a one-page diagram from the inside of a calm, well-run consultancy. **It explains the post's argument in five seconds, without the headline.** The palette is cyan and sky. The composition is flat-vector geometry — cards, circles, lines — never painterly, never photographic, never 3D-rendered. The reader feels: *clear, modern, considered, and on the same team as me.* It earns the brand promise — Partnership. Not Replacement. — by being legible and respectful, not loud.

---

## Two non-negotiables

1. **Single style, single renderer.** Every image is produced by `scripts/generate-hero-image.py`. Output is a 1200×630 JPG. No raster AI illustrators (Midjourney, Imagen, Sora, DALL·E, Ideogram), no stock photography, no hand-drawn one-offs, no 3D renders. If the topic genuinely cannot be rendered by the three layouts in the renderer, the answer is to tighten the angle of the post — not to swap in a different image style.

2. **Content match before composition.** The image must encode the post's actual argument. A reader who has read the post should see the image and recognize their own takeaway. A reader who hasn't read it should be able to predict the headline within ±20% accuracy. Generic frames ("AI Project Outcomes," "Stalled vs Scaled") that could fit five different posts are a failure mode — see §Header copy.

---

## Brand principles → imagery rules

The site's four messaging pillars (per `CLAUDE.md`) translate directly into visual rules:

**1. Partnership, not replacement.** AI augments human expertise.
→ When a person and an AI element appear together, the person leads — larger, foreground, or labelled with the action verb. The AI element is a tool the person operates, not a replacement standing where the person used to stand. The `person` icon (with its small star/spark glyph) is GrowthMax's protagonist; reach for it when the post is about people doing the work.

**2. Clarity over hype.** Speak plainly about what AI can and can't do.
→ No abstract glow effects, no sparkles, no "magical" gradients in the central composition. The faint sky-50 → cyan-50 background gradient is the only gradient. No "exploding" trajectory lines, no neural-net mesh patterns, no constellation backgrounds.

**3. Outcomes-focused.** Real results, not technology for technology's sake.
→ When labels reference time or results, prefer concrete units (weeks, signals, steps, stages) over abstractions (transformation, evolution, journey). The footer subtitle is the place to land the outcome — make it earn its line.

**4. Empathy for the human side.** Adoption creates anxiety; meet people where they are.
→ Avoid imagery that visualizes failure as a person (e.g., a crossed-out figure, a worried face). When the post is about a hard moment, the visual should diagnose the *situation*, not blame the *people*. Use `question`, `gear`, `clock`, `cycle` icons for the friction state — not `person` with a negative cue.

---

## Style spec (frozen)

These values are baked into the renderer and are not up for debate. They're listed here so anyone editing the renderer or reviewing output knows what's locked.

| Property | Value |
|---|---|
| Canvas | 1200 × 630 px landscape, JPG @ quality 88 |
| Background | Vertical gradient from `#F0F9FF` (sky-50) → `#ECFEFF` (cyan-50) |
| Grid lines | `#BAE6FD` @ 27% opacity, horizontal only, ~5 lines |
| Card surface | White `#FFFFFF`, border `#67E8F9` (cyan-300), 18px radius |
| Highlighted card | Solid `#155E75` (cyan-800) fill, `#0E7490` (cyan-700) border |
| Primary stroke | `#0E7490` (cyan-700) |
| Deep accent | `#1E40AF` (blue-800) — used only for spark glyphs and small punctuation, never for fill on a primary shape |
| Footer band | `#164E63` (cyan-900) fill, white title, `#A5F3FC` (cyan-200) subtitle |
| Type | Liberation Sans (Inter substitute on the runner). Header tracks +space, footer title is light weight |

If you find yourself wanting to introduce a new colour — orange, pink, purple, neon green, deep navy, gold — stop. The post needs a different layout, not a different palette.

---

## Layout selection — decision tree

Three layouts. Each one has a clear shape of post it serves. Pick the layout from the *post's argument*, not the post's title.

### `timeline` — when the post is a sequence

Use when the post answers "what's the order of operations?" — a roadmap, a set of phases, a chronology, a how-to that has clearly numbered steps.

Tells: the post has 3–5 named phases, and the order matters. If you reordered the phases, the post would break.

Examples in our archive that should have used (and did use) timeline:
- "How to scale AI adoption after first success" → 4 steps: Pilot Success → Team Selection → Governance → Human Amplification
- "Post-launch AI agent management" → 5 steps: Launch → Support → Capture → Iterate → Scale
- "How to train your team on AI without overwhelm" → 4 steps

Counter-examples (do NOT use timeline):
- A post about *one* topic with three angles → use cards
- A post comparing two paths → use split

### `split` — when the post is a decision

Use when the post answers "given two options, when do I pick which?" — build vs buy, in-house vs consultant, training vs implementation.

Tells: there are exactly two named alternatives, and the post earns its keep by helping the reader decide. The center "decision" circle should hold the *axis* of the decision, not a generic word like "CHOOSE."

Examples that should have used (and did use) split:
- "When to hire AI consultant vs building in-house" → CONSULTANT ↔ IN-HOUSE, center: "DECIDE / 3 factors" *(could be tighter — see §Footer subtitle)*
- "AI training vs implementation" → TRAINING ↔ IMPLEMENTATION, center: "BOTH / essential"

Counter-examples:
- Post compares three or more options → cards
- Post is "X is wrong, here's the alternative" — that's one path, not two. Use cards or timeline.
- Post is "before vs after" of the same thing — use timeline.

### `cards` — when the post is a list of distinct ideas

Use when the post answers "what are the [N] [things] for [topic]?" — signs, signals, principles, pillars, mistakes, tactics, factors.

Tells: the post has 3–5 discrete bullet-points-of-equal-weight, and you could reorder them without losing meaning.

Examples that should have used (and did use) cards:
- "5 signs your team is ready for AI" → 5 cards, one highlighted as the central one
- "Building trust in AI" → 5 cards: Be Transparent, Communicate Early, Set Expectations, Amplify Humans, Show Value

Highlight rule: at most **one** card may be highlighted (solid teal). It should be the central or pivotal idea — the one the post hangs on. If every card matters equally, highlight nothing.

### Tie-breakers

If two layouts could fit:

- **timeline beats cards** when the order matters
- **cards beats split** when there are 3+ options
- **split beats anything** when the post's whole purpose is to pick between A and B
- When in doubt → **cards**. It is the most flexible and the least likely to over-promise.

---

## Header copy — top label

The header is the spaced-out uppercase word(s) at the top of the image. It names the **conceptual frame** of the post, like a section title in a textbook.

**Rules:**
- 2–5 words, ideally 3.
- Maximum **24 characters** including spaces. (The renderer spaces letters with `   `, so 24 chars becomes ~95 visual chars wide. More than that and the header touches the canvas edge.)
- Title case in the spec; the renderer uppercases.
- Concrete and specific to *this post*, not a category that fits five posts.

**Strong examples:**
- "5 Signs of Readiness" (specific, numbered, post-shaped)
- "Confidence-First AI Training" (names the editorial angle)
- "Post-Launch Success Framework"
- "Consultant vs. In-House"

**Weak examples — do not reuse these:**
- "AI Project Outcomes" (used on *two* unrelated posts already — generic)
- "AI Strategy" (a category, not a frame)
- "How to Adopt AI" (matches half the blog)
- "The Future of Work" (vague, hype-adjacent)

If the strongest header you can write also fits another post on the site, the header is too generic. Get more specific.

---

## Footer title — the big editorial line

The footer title is the large white line in the dark cyan-900 footer band. It is the **plain-English benefit** of reading the post — the single sentence the reader will quote when they recommend the post to a colleague.

**Rules:**
- 3–7 words.
- Maximum **40 characters**, hard cap. Anything longer wraps awkwardly or clips at the edges given the 36pt light weight.
- Active voice, sentence case (the renderer renders it as written, not uppercase).
- Names a benefit, an action, or a reframing. Not the post's title verbatim.
- May echo the header's frame, but should reward the reader for moving their eye down — give them the *takeaway*, not a restatement.

**Strong examples:**
- "Is Your Team Ready for AI?" *(question form — works when the post is a self-assessment)*
- "Turn Skeptics Into Advocates" *(verb-led, transformation framed without hype)*
- "Scale Smart, Not Fast" *(opinion, position-taking)*
- "Build AI Skills Without Fear" *(addresses the anxiety directly — pillar 4)*
- "When to Hire vs. Build"

**Weak examples:**
- "AI Project Outcomes" (header, not footer — too abstract for the editorial line)
- "Learn About AI Adoption" (filler verb, no specificity)
- "Maximize Your AI ROI" (hype vocab — "maximize," "ROI" without a number, generic)
- The post's literal title (the layout already gets you to the post; don't echo)

---

## Footer subtitle — the supporting line

The footer subtitle is the smaller cyan-200 line under the footer title. It earns its place by adding **the single piece of context** that makes the footer title land.

**Rules:**
- ≤ 10 words.
- Maximum **65 characters**, hard cap.
- Should answer "for whom?" or "why now?" or "what's the unit?" — never restate the title.
- Sentence case, no terminal period (it's a tagline).

**Strong examples:**
- "A practical readiness checklist" (says what the image is, who it's for)
- "Proactive communication builds lasting team confidence" (mechanism — *why* it works)
- "Transform your organization without losing momentum" (caveat — *what to avoid*)
- "Why AI adoption needs both, not either-or" (resolves the dichotomy the image set up)

**Weak examples:**
- "A guide to AI" (zero specificity)
- "Read more on the blog" (CTA, not subtitle)
- "Modern teams use AI" (truism)

---

## Icon strategy

The renderer ships with 13 icons: `check, person, question, target, clock, book, rocket, gear, chart, cycle, flag, scale, chat`. Use them deliberately.

**Pairing rules** (use these to fight the "lazy `?` for everything" pattern):

| Concept | Preferred icon | Avoid |
|---|---|---|
| Audit / current state | `gear` or `chart` | `?` (overused) |
| The diagnostic question | `question` | (this is the one place `?` belongs) |
| Goal / outcome | `target` | `flag` (reserve for kickoff) |
| Beginning / kickoff | `flag` or `rocket` | `target` (that's the end) |
| Iteration / feedback loop | `cycle` | `chart` |
| Growth / measurement | `chart` | `target` |
| Capability / training | `book` | `person` (person is the doer, not the topic) |
| Person doing work | `person` | (no substitute — this is the protagonist) |
| Conversation / culture | `chat` | `person` |
| Time / phasing | `clock` | (no substitute) |
| Tradeoff / governance | `scale` | `gear` |
| Ship-it / launch | `rocket` | `flag` |
| Validation / trust | `check` | `target` |

**Variety rule:** within a 5-card composition, no icon may appear more than once. Within a published archive, no two posts on the homepage may have the same lead icon — vary the protagonist.

**Person-led rule (pillar 1):** if the post is about people doing AI work (training, change management, trust, adoption), at least one slot in the composition should use `person`, and a `person` slot in `cards` is a strong candidate for the highlight position.

---

## Hard renderer constraints (math)

These are derived from `scripts/generate-hero-image.py`. Violating them produces the cut-edge / overflow defects we already see in the archive.

| Field | Hard cap | Why |
|---|---|---|
| `header` | 24 chars (post-spacing it spans <1100px at 20pt Medium) | More clips the canvas edge |
| `footer_title` | 40 chars at 36pt Light | Wraps and looks broken past this |
| `footer_subtitle` | 65 chars at 18pt Light | Wraps at ~70 chars; 65 is the safety margin |
| Card `label` | 26 chars (≈ two lines of 14 wrapped chars) | Renderer hard-truncates after 2 lines |
| Timeline step `label` | 26 chars (same wrap) | Same |
| Split column `label` | **14 chars** at 32pt SemiBold (UPPERCASE) | "EXECUTIVE BUY-IN" = 16 chars and clips. Hard cap 14. Reword if longer. |
| Split column `sub` | 60 chars (3 lines of 22 wrapped) | More truncates |
| Split center `label` | 7 chars (UPPERCASE inside 124px circle) | "DECIDE" = 6 chars fits; "CONSIDER" = 8 chars overruns |
| Split center `sub` | 18 chars at 14pt Light | More wraps inside circle |
| Cards count | 3–5 | <3 looks lonely; >5 won't fit |
| Timeline steps | 3–5 | Same |

**If you cannot fit the spec inside these caps, the answer is to tighten the spec — not to ask the renderer to bend.** The constraint is part of the brand: GrowthMax doesn't write headlines that need a runway.

---

## Pre-publish validation checklist

Before any image goes live (auto-pipeline or manual), verify all 10:

1. **Style** — output is a 1200×630 JPG produced by `generate-hero-image.py`. Not a raster AI illustration. Not a one-off custom layout.
2. **Palette** — only the colours in §Style spec appear. No orange, pink, purple, gold, or photographic skin tones.
3. **Layout match** — chosen layout matches the post's argument shape per §Layout selection.
4. **Content match** — a reader who hasn't read the post can predict the headline ±20% from the image alone.
5. **Header** — ≤24 chars, specific to this post, doesn't fit any other post on the site.
6. **Footer title** — ≤40 chars, names a benefit/action/reframe, doesn't echo the post title verbatim.
7. **Footer subtitle** — ≤65 chars, adds context the title doesn't already give.
8. **Icon variety** — no icon used more than once in the composition; lead icon hasn't been used as the lead on a recent (last 5) post.
9. **No clipping** — split labels ≤14 chars; all card/step labels fit two wrapped lines.
10. **Pillar fit** — visual respects the empathy rule (no person-as-failure imagery) and the clarity rule (no glow / sparkle / mesh).

A "yes" to all 10 is required. If any is "no," regenerate the spec — don't ship the image.

---

## How this skill is applied

**Auto-pipeline (`scripts/generate-post.py`):** the `HERO_IMAGE_SPEC_PROMPT` reads this file from disk and uses it as the system prompt for the spec-generation call. Every blog post the pipeline ships goes through these rules.

**Manual regeneration (Cowork, by hand):** open this file and the renderer code, write the spec by hand or have Claude write it, run the renderer locally, run the §Pre-publish validation checklist before committing.

**OG / social cards / page heros:** the same rules apply. The renderer is the only acceptable path; if a layout for a non-blog use case doesn't yet exist, extend the renderer rather than swapping in a different style.

---

## Out of scope for this skill

- Logo placement, favicon design — those are owned by the site shell.
- Chart and data-viz output (Plotly, Recharts) inside blog *body* content — those follow the Tailwind cyan/sky palette but aren't governed here.
- Avatars and team photos — those are photographic stock approved separately and live as `*_gemini_cartoon.png` at the repo root.
