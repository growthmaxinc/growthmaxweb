---
name: growthmax-imagery
description: Apply GrowthMax's editorial illustration style to any image rendered for the website — blog hero images, OG/social cards, page heros. Use this skill ANY time a deliverable will be rendered as an image for growthmaxinc.com. Triggers include "blog hero," "header image," "OG image," "social card," "page hero," "regenerate the image," "design an illustration." The skill defines a single locked illustration aesthetic but allows four composition types (metaphor, tableau, person, group) chosen per post to match its argument shape. Generated via Gemini Imagen 4.
---

# GrowthMax Imagery — Creative Direction (v3)

This is the single source of truth for any image rendered for **growthmaxinc.com**. The auto-pipeline at `scripts/generate-post.py` reads this file on every run; humans regenerating images by hand follow the same rules.

What's locked: the *style, palette, and rendering quality* — every image is a painterly editorial illustration in the same hand. What varies per post: the *composition* (people vs. metaphor vs. objects), the *setting*, the *protagonist*, and the *symbolic content* — picked from each post's argument shape, not formulaic.

---

## The promise

A GrowthMax image looks like an editorial illustration on the cover of a thoughtful business publication — *Harvard Business Review*, *The Atlantic*, *Stripe Press*. **Some posts are best served by a person mid-thought. Others by a visual metaphor with no people in it. Others by a tabletop of carefully arranged objects.** The image always *illustrates the post's argument*, not just "shows a person at a desk."

---

## The single style — locked

These five rules are non-negotiable across every composition type:

1. **Style — flat modern editorial illustration, painterly.** Vector-shape construction with soft painterly textures — flat fills with gentle gradients and subtle grain. Not photorealistic. Not 3D-rendered. Not cartoon. Not line-art. Think *Tom Haugomat*, *Owen Davey*, *Mark Smith*, *Olimpia Zagnoli*.

2. **Lighting — soft, single source, varied.** Always one directional light source with gentle highlights and ambient shadows. **The light source must vary per post** — overcast morning, overhead lamp, ambient diffuse, blue-hour dusk, midday outdoor shade, candlelight, screen glow, etc. The "warm late-afternoon light spilling through a window" cliché is forbidden as a default — use it only when a specific post genuinely calls for it (no more than ~15% of images).

3. **Palette — cyan/sky dominant + one warm accent.** Blues, cyans, sky-blues, cool whites for the dominant tones. **One** warm accent — peach (`#FB923C`), amber (`#FCD34D`), or coral (`#F87171`) — sparingly, never the largest element.

4. **Mood — considered, calm, intentional.** No frenetic energy. No theatrical drama. No literal "AI = brain + circuit" clichés.

5. **No text, no UI.** Imagen sometimes hallucinates garbled letters on screens, signs, books. The prompt must explicitly forbid all visible text.

---

## Composition types — pick one per post

The composition type is chosen from the post's argument shape. Most posts (~50%) are best served *without* a person.

### Type A — Metaphor-led (no people)

A single visual metaphor that encodes the post's argument. No human figures.

**Use when** the post is a diagnosis, a framework, a process, a decision, or a phenomenon. The metaphor *is* the argument compressed into a single image.

**Examples:**
- *Hidden costs* → an iceberg, with the visible peak labelled "Technology" and the deeper mass implying the unseen
- *90-day timeline* → a winding road with three milestone markers receding into golden-hour distance
- *Build vs. buy* → a fork in a country road, two paths diverging, signposts at the split
- *Why implementations fail* → a half-built bridge stopping mid-span over a chasm, scaffolding still up
- *Stalled project* → a stopped gear in machinery, dust motes catching afternoon light
- *Scaling adoption* → a sapling and a mature tree side-by-side, same species, time elapsed
- *Training vs. implementation* → two stone pillars with a delicate arch connecting them above

### Type B — Tableau (objects, no people)

An overhead or three-quarter view of a desk surface with arranged objects that tell the story. Hands may appear at the edge of the frame, but no full figures.

**Use when** the post is about tools, methods, or evidence — when the *materials* are the story.

**Examples:**
- *Measure ROI* → a notebook open to a hand-sketched chart, a ruler beside it, a peach mug, a fountain pen, papers with annotations
- *Signs your team is ready* → 5 small distinct objects (a sprouting seedling, a key, a compass, a candle, a clock) arranged like a still life
- *Your first AI agent* → a single small sapling in a peach pot, surrounded by empty space — the rest of the desk implied

### Type C — Person-led (single character)

A single human character in their environment. Use the rich character variety described below — gender, ethnicity, age, setting all vary per post.

**Use when** the post is *about a personal experience* — anxiety, identity, individual learning, a moment of decision. The character is the argument.

**Examples:**
- *Where do I fit?* → a person sitting at a window, hands not on the keyboard, looking out — the question mid-air
- *People-first AI strategy* → a person leading a small workshop, mid-gesture (could become a group composition)

### Type D — Group / pair (two characters)

Two characters in a contained interaction — across a table, side by side at a screen, or in conversation.

**Use when** the post is about *collaboration, alignment, conflict, or interpersonal change*.

**Examples:**
- *Executive buy-in* → an executive across a table from a project lead, both leaning in over a shared document
- *Change management playbook* → two people on a low couch, one explaining, the other listening
- *Building trust* → two people side by side at a window, looking out together — quiet shared moment

### Composition assignment (the 20 published posts)

Pre-assigned per post by the generator using the post slug. The full mapping is in `assign_composition_for_slug()` in `scripts/generate-hero-image-gemini.py`. Distribution target across 20 posts:
- ~50% metaphor (10 posts)
- ~15% tableau (3 posts)
- ~25% person (5 posts)
- ~10% group (2 posts)

---

## Setting variety (when people appear)

For Type C and Type D posts, the setting must vary. **No two consecutive person-led posts may share the same setting.** Pick from:

- Home office (warm, lived-in)
- Library / reading nook
- Café table (window seat or terrace)
- Co-working space corner
- Conference room (modern, plants, daylight)
- Studio / workshop with paper everywhere
- Kitchen counter (laptop on the counter, morning light)
- Outdoor — park bench, terrace, balcony
- Train carriage (window seat, countryside passing)
- Hotel lobby (soft chair, low table)

Avoid the SaaS-default "white desk, plant, laptop, window with city skyline" repeated everywhere. Mix it up.

---

## Character variety (when people appear)

**Gender** — quota-balanced 50/50 across the person-led + group posts. Pre-sampled per slug to maintain the ratio.

**Ethnicity** — 85% Caucasian / 15% non-Caucasian across the published archive. The 15% is spread across Black, East Asian, South Asian, Hispanic/Latino, and Middle Eastern (rotating) so no single non-Caucasian group dominates the minority share. Pre-sampled per slug deterministically.

**Age range** — 30s, 40s, 50s, occasional 60s. Never under 25 (B2B audience).

**Body type / hair / attire** — vary widely. Not all "white shirt and laptop." Sweaters, button-downs, t-shirts under blazers, sometimes a scarf or hat. Glasses sometimes, not always.

The same character may appear in two posts only when the posts are explicitly part of a series.

---

## Per-post conceptual accent (always include)

Every image — regardless of composition type — has one symbolic element that ties the visual to the post's specific topic. Mug-sized. Integrated naturally:

| Topic | Accent |
|---|---|
| AI presence / partnership | Faint sparkles in the air (max 3-5, very subtle) — *only when AI itself is the topic* |
| Time / phasing | Hourglass, wall calendar, clock, sundial |
| Growth / measurement | Hand-sketched line graph, balance scale, a sprouting plant |
| Decision / weighing | Old-fashioned balance, two open books, a coin mid-flip |
| Conversation / culture | A second mug, a phone face-up, two chairs |
| Beginning / kickoff | A sealed envelope, a kit, an unopened notebook, a key |
| Iteration | Marked-up paper, sticky notes, drafts pinned to a board |
| Hidden / unseen | Water surface, an iceberg, a closed door slightly ajar |
| Path / journey | A road, footsteps, a map, a compass |
| Loss / failure | A toppled object, a snuffed candle, an empty chair |

---

## Imagen prompt templates

The auto-pipeline picks one of four templates based on the assigned composition type. Each template fills in per-post variables.

### Metaphor template
```
A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. {METAPHOR_DESCRIPTION}. {SCENE_CONTEXT}.

No people in the image. The composition is symbolic — a single visual metaphor that encodes the post's argument.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. Avoid harsh shadows. The warm-window-spilling-afternoon-light cliché is forbidden — vary the lighting per post (overcast morning, single overhead lamp, ambient indoor diffuse, blue-hour dusk, midday outdoor shade, candlelight, etc.).

Color palette: cyan and sky-blue dominant (#38BDF8, #0EA5E9, #0E7490, #ECFEFF, #A5F3FC), with one warm accent of {WARM_ACCENT_COLOR_NAME} ({WARM_ACCENT_HEX}) on {WARM_ACCENT_OBJECT}. No other warm colors.

Composition: {COMPOSITION_NOTES}. Generous breathing room, ~15% quiet space.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli — confident shape language, considered, slightly nostalgic editorial illustration. Not photorealistic. Not 3D-rendered. Not cartoon. Vector shapes with soft painterly textures.

Mood: {MOOD_REGISTER}.

Strictly forbidden: any visible text, words, numbers, letters, logos. No legible signs, no readable book titles. No sparkles unless explicitly described.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner.
```

### Tableau template
```
A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. An overhead or three-quarter view of a {SURFACE_TYPE} arranged with {OBJECT_LIST}. {SCENE_CONTEXT}.

No full human figures — at most a hand or arm at the edge of the frame.

Lighting: soft directional warmth from {LIGHT_SOURCE}, late afternoon golden-hour atmosphere, ambient soft shadows on the surface.

Color palette: cyan and sky-blue dominant (#38BDF8, #0EA5E9, #0E7490, #ECFEFF, #A5F3FC), with one warm accent of {WARM_ACCENT_COLOR_NAME} ({WARM_ACCENT_HEX}) on {WARM_ACCENT_OBJECT}. No other warm colors.

Composition: {COMPOSITION_NOTES}.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli.

Mood: {MOOD_REGISTER}.

Strictly forbidden: any visible text, words, numbers, letters, logos. No readable book titles or notebook contents.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner.
```

### Person template
```
A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. {CHARACTER} in a {SETTING_TYPE}. The character is in {POSE_DESCRIPTION}, {ACTIVITY_DESCRIPTION}. {CONCEPTUAL_ACCENT_DESCRIPTION}.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. Avoid harsh shadows. The warm-window-spilling-afternoon-light cliché is forbidden — vary the lighting per post (overcast morning, single overhead lamp, ambient indoor diffuse, blue-hour dusk, midday outdoor shade, candlelight, etc.).

Color palette: cyan and sky-blue dominant (#38BDF8, #0EA5E9, #0E7490, #ECFEFF, #A5F3FC), with one warm accent of {WARM_ACCENT_COLOR_NAME} ({WARM_ACCENT_HEX}) on {WARM_ACCENT_OBJECT}. No other warm colors.

Composition: character offset to the {LEFT_OR_RIGHT} third of the frame, side profile or three-quarter angle, occupying about 35% of frame width. The opposite side shows {OPPOSITE_SIDE_DESCRIPTION}. Generous breathing room.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli.

Mood: {MOOD_REGISTER}. {CHARACTER_EXPRESSION}.

Strictly forbidden: any visible text, words, numbers, letters, logos. No hands-on-keyboard close-ups. No multiple warm colors.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner.
```

### Group template
```
A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. Two characters in {SETTING_TYPE}: {CHARACTER_A_DESCRIPTION} and {CHARACTER_B_DESCRIPTION}. They are {INTERACTION_DESCRIPTION}. {CONCEPTUAL_ACCENT_DESCRIPTION}.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. Avoid harsh shadows. The warm-window-spilling-afternoon-light cliché is forbidden — vary the lighting per post (overcast morning, single overhead lamp, ambient indoor diffuse, blue-hour dusk, midday outdoor shade, candlelight, etc.).

Color palette: cyan and sky-blue dominant (#38BDF8, #0EA5E9, #0E7490, #ECFEFF, #A5F3FC), with one warm accent of {WARM_ACCENT_COLOR_NAME} ({WARM_ACCENT_HEX}) on {WARM_ACCENT_OBJECT}. No other warm colors.

Composition: both characters in the lower two-thirds, with breathing space above. {COMPOSITION_NOTES}.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli.

Mood: {MOOD_REGISTER}.

Strictly forbidden: any visible text, words, numbers, letters, logos. No multiple warm colors.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner.
```

---

## Hard image specs (frozen)

| Property | Value |
|---|---|
| Dimensions | 1200 × 630 px |
| Aspect ratio | 16:9 landscape |
| Format | JPG, quality 88, optimized |
| File size | ≤ 200 KB |
| File naming | `blog-{slug}.jpg` at repo root |
| Generator | Gemini Imagen 4 via `scripts/generate-hero-image-gemini.py` |

---

## Pre-publish validation checklist

Before any image goes live, all 10 must pass:

1. **Style** — flat modern editorial illustration. Not photorealistic, not 3D, not cartoon.
2. **Composition match** — the chosen composition type fits the post's argument shape (don't put a person on a hidden-costs post; don't put an iceberg on a "where do I fit?" post).
3. **Palette** — cyan/sky dominant; exactly one warm accent. No second warm color.
4. **Lighting** — single soft directional source.
5. **Setting variety** — for person-led posts, the setting differs from neighboring person-led posts in the archive.
6. **Conceptual accent** — present and tied to the post's specific topic.
7. **Text-free** — no legible words, letters, numbers anywhere.
8. **Mood match** — image reads at the post's emotional weight.
9. **Composition** — has breathing room, not crowded edge-to-edge.
10. **Dimensions** — exactly 1200 × 630 JPG.

---

## How this skill is applied

**Auto-pipeline:** `scripts/generate-post.py` reads this file on every Mon/Wed/Fri run. The generator pre-samples composition type, gender, ethnicity per slug; Claude fills the variables for the chosen template; Imagen renders. Result is validated and committed.

**Manual regeneration:** open this file, hand-write per-post variables, call `scripts/generate-hero-image-gemini.py`, validate, commit.

---

## Out of scope

- Logo, favicon, team avatars (`*_gemini_cartoon.png`).
- Charts and data-viz inside post body content (Plotly, Recharts).
