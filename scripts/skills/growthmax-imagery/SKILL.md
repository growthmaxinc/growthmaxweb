---
name: growthmax-imagery
description: Apply GrowthMax's editorial illustration style to any image rendered for the website — blog hero images, OG/social cards, page heros. Use this skill ANY time a deliverable will be rendered as an image for growthmaxinc.com. Triggers include "blog hero," "header image," "OG image," "social card," "page hero," "regenerate the image," "design an illustration." The skill defines a single locked aesthetic (painterly editorial illustration of a single character at work) and a prompt template that the auto-pipeline feeds to Gemini Imagen on every run. Do NOT use the legacy flat-vector PIL renderer for new heros — it is retained only for fallback.
---

# GrowthMax Imagery — Creative Direction

This is the single source of truth for any image rendered for **growthmaxinc.com**. The auto-pipeline at `scripts/generate-post.py` reads this file on every run; humans regenerating images by hand follow the same rules. There is one aesthetic, one palette, one composition pattern. Variation lives inside that frame, never outside it.

---

## The promise

A GrowthMax image looks like an editorial illustration on the cover of a thoughtful business publication — the kind of art you see leading a *Harvard Business Review* feature or an *Atlantic* essay on the future of work. **A single person, captured in a moment of focused thinking, in a warm and human workspace.** The viewer feels: someone like me, doing real work, with care. The image earns the brand promise — Partnership. Not Replacement. — by centering the human, never the technology.

The reference image for this aesthetic is the existing `blog-partnership-not-replacement.jpg`: a woman at a wooden desk, headphones on, side profile, soft cool light from an open window, peach lamp glowing, plant on the desk, hanging pendants, faint sparkles in the air. Calm. Focused. Considered. That image is the north star.

---

## The single style — locked

Every hero image must have these properties. They are not aesthetic suggestions; they are the brand.

**1. Subject — one person at a workspace.**
A single human character (rarely two, only when the post is explicitly about partnership/collaboration) engaged in real work — reading, writing, thinking, listening, drawing, reviewing. The character is offset to one side of the frame, never centered head-on. Side profile or three-quarter angle. Never staring directly at the viewer.

**2. Workspace — warm, lived-in, human.**
A real desk with real things on it: a laptop, a notebook, a coffee mug, a small plant, papers, a lamp. Wooden surfaces, not glass. A window or natural light source nearby. The space feels like someone's home office or a cozy corner of a creative agency — never sterile, never minimal, never a "tech bro" co-working space with neon.

**3. Style — flat modern editorial illustration, painterly.**
Vector-shape construction with soft painterly textures — flat fills with gentle gradients and subtle grain. Not photorealistic. Not 3D-rendered. Not cartoon (no big eyes, no exaggerated proportions). Not line-art (shapes have form, not just outlines). Think *Tom Haugomat*, *Owen Davey*, *Mark Smith* — illustration that feels considered and slightly nostalgic, with confident shape language.

**4. Lighting — soft directional warmth.**
Light comes from one source — a window, a lamp, an overhead pendant — and the character is illuminated from that one direction with gentle highlights and ambient shadows. The room has atmosphere; it isn't flat. Time of day reads as late afternoon or early evening — golden hour, not midday harshness, not nighttime gloom.

**5. Palette — cyan/sky dominant with one warm accent.**
The dominant tones are blues, cyans, sky-blues, and cool whites. **One** warm accent color appears per image — a peach lamp, an amber coffee, a coral plant pot, a yellow notebook. The warm accent is never the largest element; it's a punctuation mark that gives the cool palette life.

**6. Mood — contemplative, calm, grounded.**
The character is mid-thought, mid-task, mid-pause. They are present and considered, never frantic, never bored, never theatrical. Their face shows thought, not emotion-as-performance. The whole image breathes.

---

## Palette spec

These are the colors Imagen prompts should reach for. Do not invent new ones.

| Role | Hex | Use |
|---|---|---|
| Sky / cool dominant | `#38BDF8` | Walls, sky behind window, large background fields |
| Cyan / mid-tone | `#0EA5E9` | Mid-shadow on cool surfaces |
| Deep cyan | `#0E7490` | Dark accents, character clothing, lamp shadow |
| Cool off-white | `#ECFEFF` | Highlights, paper, light spill |
| Cyan-200 / soft fill | `#A5F3FC` | Soft mid-tones on light surfaces |
| **Warm accent — peach** | `#FB923C` | Lamp glow, coffee, sunset light |
| **Warm accent — amber** | `#FCD34D` | Notebook, sticky notes, plant pot |
| **Warm accent — coral** | `#F87171` | Sparingly — flower, pillow, accent textile |
| Skin tones | natural range | Diverse — vary across posts (see §Character variety) |

The warm accent is *one per image*, not all three. Pick the one that fits the post's mood.

---

## Composition rules

**Aspect ratio: 1200×630 landscape.** Always. The site's blog index and post layouts use `object-cover` to fit images into a fixed-height band; portrait images get cropped to a sliver. 1200×630 is also the OG/Twitter card standard, so social shares work without a second asset.

**Character placement: offset, not centered.** The character occupies roughly 30–40% of the frame width, positioned in the left or right third. The opposite side holds the workspace context — a window, a wall with a plant, a desk with papers — or a subtle conceptual element (a softly drawn chart, a stack of books, a pendant lamp). Centered head-on shots feel like portraits, not editorial illustration.

**Breathing room.** ~15% of the frame is "quiet space" — the character does not crowd the edge, the workspace doesn't pack every pixel. The image rewards a long look.

**No text, no UI.** Imagen sometimes hallucinates garbled text on laptop screens or signs. The prompt must explicitly forbid this. The character's screen, books, and notebook should be blank or show only abstract shapes.

**No hands on the laptop trackpad close-up.** Avoid the cliché "hands on keyboard" stock-photo crop. The character is a whole person, not a body part.

---

## Character variety

Across the 20+ posts on the blog, the cast should feel like a small team you'd meet at a real company — not the same model repeating. Vary deliberately:

- **Gender** — alternate (and include nonbinary presentation) across posts
- **Ethnicity** — approximately 85% Caucasian / 15% non-Caucasian across the published archive, sampled independently per post. The 15% should itself vary (Black, East Asian, South Asian, Hispanic/Latino, Middle Eastern). Per-post: pick one ethnicity at random with this weighting; do not cluster non-Caucasian posts together. Goal is a team that reads as predominantly white but not exclusively so.
- **Age range** — include 30s, 40s, 50s, occasional 60s. Never under 25 (this is a B2B audience)
- **Body type** — vary
- **Hair** — short, long, curly, straight, locs, bald — mix it up
- **Attire** — casual professional. Sweaters, button-downs, t-shirts under blazers, sometimes a scarf. Never "corporate suit." Never "techbro hoodie."

The same character may appear in two posts only when the posts are explicitly part of a series (e.g., "Building Trust pt. 1" and "Building Trust pt. 2" — we don't have these, but if we did, consistency would be a feature).

---

## Per-post variation — what changes

While the style and palette are locked, **two things change per post**:

**1. The character + activity.** Picked to fit the post's argument:
- A post about *executive buy-in* → a senior leader at a desk, mid-conversation pose, looking at a notebook
- A post about *training* → a person reading, leaning into an open laptop, clearly in learning mode
- A post about *measuring ROI* → a person with a notebook open to handwritten figures, contemplating
- A post about *scaling adoption* → two people in light conversation across a shared desk
- A post about *anxiety / "where do I fit?"* → a person paused at the desk, hands not on the keyboard, looking out the window
- A post about *partnership / augmentation* → person at the desk with a faint sparkle/shape in the air beside them representing the AI presence (subtle, not dominant)

**2. The conceptual accent.** One small symbolic element appears in the workspace — never literally, always integrated:
- AI presence → faint sparkles in the air (max 3–5, very subtle)
- Time / phasing → an hourglass, a wall calendar, a clock on the desk
- Growth / measurement → a small notebook chart, a hand-sketched line graph
- Decision / weighing → a balance, two open books
- Conversation / culture → a half-empty second coffee cup (someone just left), a phone face-up
- Beginning → a sealed envelope, a kit, an unopened notebook
- Iteration → marked-up paper, sticky notes, drafts pinned to a wall

This accent is *on the desk or in the air*, the size of a coffee mug. Never the focus.

---

## Mood register per post type

The post's emotional weight tunes the mood:

| Post type | Mood register | Example posts |
|---|---|---|
| Diagnostic ("what's wrong with...") | Quiet, slightly melancholy, late-afternoon | "Why AI Implementations Fail," "Where Do I Fit?" |
| Practical / tactical | Engaged, focused, mid-morning warmth | "How to Measure ROI," "Your First AI Agent" |
| Strategic / framework | Considered, broader light, more workspace visible | "90-Day Adoption Timeline," "Partnership Model" |
| People & culture | Warmer, slightly more ambient color, two figures OK | "Change Management," "Building Trust" |
| Decision / tradeoff | Tense but not anxious, single character with two objects in frame | "Build vs. Buy," "Consultant vs. In-House" |

The character's *expression* and the *light direction* do most of the mood work. Don't try to telegraph mood with palette deviation — the palette is locked.

---

## Imagen prompt template

This is the literal structure the auto-pipeline assembles. The brand DNA is constant. The per-post fields are filled in by Claude based on the post's title/subtitle/tldr and the variation rules above.

```
A flat modern editorial illustration, painterly style with soft 
gradients and subtle grain texture. {CHARACTER} in a warm, lived-in
{WORKSPACE_TYPE}. The character is in {POSE_DESCRIPTION},
{ACTIVITY_DESCRIPTION}. {CONCEPTUAL_ACCENT_DESCRIPTION}.

Lighting: soft directional warmth from {LIGHT_SOURCE}, late afternoon
golden-hour atmosphere, ambient soft shadows.

Color palette: cyan and sky-blue dominant (#38BDF8, #0EA5E9, #0E7490, 
#ECFEFF, #A5F3FC), with one warm accent of {WARM_ACCENT_COLOR_NAME}
({WARM_ACCENT_HEX}) on {WARM_ACCENT_OBJECT}. No other warm colors.

Composition: character offset to the {LEFT_OR_RIGHT} third of the frame,
side profile or three-quarter angle, occupying about 35% of frame width.
The opposite side shows {OPPOSITE_SIDE_DESCRIPTION}. Generous breathing
room, ~15% quiet space.

Style references: Tom Haugomat, Owen Davey, Mark Smith — confident shape
language, considered, slightly nostalgic editorial illustration. Not
photorealistic. Not 3D-rendered. Not cartoon. Not line-art. Vector
shapes with soft painterly textures.

Mood: {MOOD_REGISTER}. {CHARACTER_EXPRESSION}.

Strictly forbidden: any visible text, words, numbers, letters, logos,
or UI elements. No legible signs, no readable book titles, no laptop
screens with text, no notebook writing — keep all surfaces blank or
abstract. No hands-on-keyboard close-ups. No multiple warm colors.
No neon, no glow effects, no sparkles unless the post is specifically
about AI partnership (then maximum 3-5 small sparkles, very subtle).

Aspect ratio: 16:9 landscape, designed for a 1200×630 hero banner.
```

The auto-pipeline pre-pends this prompt with the post title and tldr in a system prompt to Claude, asks Claude to fill in the bracketed fields, then sends the assembled prompt to Imagen.

---

## Hard image specs (frozen)

| Property | Value |
|---|---|
| Dimensions | 1200 × 630 px |
| Aspect ratio | 16:9 landscape |
| Format | JPG, quality 88, optimized |
| File size | ≤ 200 KB |
| File naming | `blog-{slug}.jpg` at repo root |
| Color space | sRGB |
| Generator | Gemini Imagen 3 via `scripts/generate-hero-image-gemini.py` |

---

## Pre-publish validation checklist

Before any image goes live, all 10 must pass:

1. **Style** — flat modern editorial illustration. Not photorealistic, not 3D, not cartoon.
2. **Subject** — exactly one person at a workspace (or two, if the post is about partnership). Side profile or 3/4 angle.
3. **Palette** — cyan/sky dominant; exactly one warm accent. No second warm color, no off-palette colors.
4. **Lighting** — single soft directional source, late-afternoon warmth.
5. **Composition** — character in left or right third (not centered head-on), ~35% width, with breathing room.
6. **Workspace** — warm, human, lived-in (wood, plant, mug, lamp, books). Not sterile, not minimalist white.
7. **Text-free** — no legible words, letters, numbers, or UI on screens, books, notebooks, or signs.
8. **Mood match** — character's expression and light tone fit the post's emotional weight.
9. **Conceptual accent** — one symbolic object on the desk or in the air, mug-sized, integrated naturally.
10. **Dimensions** — exactly 1200 × 630 JPG.

Any "no" → regenerate with a tightened prompt before shipping.

---

## How this skill is applied

**Auto-pipeline (`scripts/generate-post.py`):** the hero generation step (`generate_hero_image`) loads this file as the system prompt, asks Claude to fill in the per-post variables, and passes the assembled prompt to Gemini Imagen. The result is validated against the checklist before the post commits.

**Manual regeneration (Cowork, by hand):** open this file, hand-write the per-post variables (or have Claude write them), call `scripts/generate-hero-image-gemini.py`, run the §Pre-publish validation checklist before committing.

**OG / social cards / page heros:** the same skill applies. 1200×630 is already OG-standard, so the blog hero doubles as the social card.

---

## Out of scope for this skill

- Logo placement, favicon design — owned by the site shell.
- Charts and data-viz inside post body content (Plotly, Recharts) — those follow Tailwind cyan/sky but aren't governed here.
- Team avatars (`*_gemini_cartoon.png`) — generated once, separately, not under this skill's prompt template.

---

## Why this differs from v1 of this skill

v1 (commits 76cf916 → b13707d) locked all imagery into the flat-vector PIL renderer. After backfilling 12 posts under that direction and reviewing, the diagrams felt generic — closer to a SaaS dashboard than editorial illustration. The blog needs *images*, not info-graphics. v2 (this version) is a complete reset: a single locked illustration aesthetic, generated by Gemini Imagen, with the character at the center of every frame. The PIL renderer is retained at `scripts/generate-hero-image.py` only as a fallback if Imagen ever fails — it does not produce the canonical look.
