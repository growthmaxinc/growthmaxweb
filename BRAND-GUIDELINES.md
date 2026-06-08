# GrowthMax Brand Guidelines

The single source of truth for the GrowthMax visual and verbal identity. If you are designing, writing, or building anything with the GrowthMax name on it — a page, a deck, a social post, a blog hero — this document governs it. The live, shareable version of this lives at **[growthmaxinc.com/brand](https://growthmaxinc.com/brand/)**, where the logo files and asset bundle can be downloaded.

> Related references in this repo: visual/layout patterns in `CLAUDE.md`, imagery creative direction in `scripts/skills/growthmax-imagery/SKILL.md`, and SEO/AEO rules in `SEO-STANDARDS.md`.

---

## 1. Brand at a glance

GrowthMax Inc is an AI consultancy that builds custom AI agents and runs AI training bootcamps. The whole brand rests on one idea:

> **Partnership. Not Replacement.**
> AI augments human expertise — it doesn't replace people.

Everything we make should feel calm, confident, and human. We speak plainly about what AI can and can't do, we focus on outcomes over hype, and we meet people where they are in the anxiety and disorientation that AI adoption creates.

---

## 2. Logo

### The logo
The primary logo is an upward-climbing bar-chart mark — deep-slate bars with a cyan gradient and a rising arrow — set above the **GROWTHMAX** wordmark in deep slate. It reads instantly as growth, momentum, and measurement.

### Variants and when to use them

| File | Use |
|---|---|
| `growthmax-logo.png` | Primary full-color logo on white or very light (`sky-50`) backgrounds. |
| `growthmax-logo-transparent.png` | Same logo with a transparent background, for placing over light imagery or tinted panels. |
| `growthmax-mark.svg` | The standalone "G" mark (cyan rounded square) — for avatars, favicons, app icons, and tight spaces where the full wordmark won't fit. |
| `growthmax-favicon.svg` | The favicon as shipped site-wide (`/favicon.svg`). |

Download all of these as a bundle from `growthmaxinc.com/brand` or `/assets/brand/growthmax-brand-assets.zip`.

### Logo do's and don'ts
- **Do** keep clear space around the logo equal to at least the height of one chart bar.
- **Do** place the full-color logo on white, `sky-50`, or `cyan-50` backgrounds.
- **Don't** recolor, rotate, skew, add shadows/gradients, or outline the logo.
- **Don't** place the full-color logo on busy photography or low-contrast color — use the transparent or mark version instead.
- **Don't** rebuild the wordmark in a different typeface.

---

## 3. Color

The palette is the Tailwind **cyan / sky / blue** family, cool and clean, with a deep-slate ink for the logo and one warm accent reserved for illustration only.

### Core palette

| Role | Token | Hex |
|---|---|---|
| Page background (primary) | `sky-50` | `#F0F9FF` |
| Page background (alt sections) | `cyan-50` | `#ECFEFF` |
| Nav surface | `cyan-100` | `#CFFAFE` |
| Card / component borders | `cyan-200` | `#A5F3FC` |
| Headings | `cyan-900` | `#164E63` |
| Body text | `cyan-800` | `#155E75` |
| Secondary text / links | `cyan-700` | `#0E7490` |
| Icons / link hover | `cyan-600` | `#0891B2` |
| Bright cyan (logo bars, highlights) | `cyan-400` | `#22D3EE` |

### Accent & CTA

| Role | Token | Hex |
|---|---|---|
| Category / eyebrow labels | `blue-600` | `#2563EB` |
| Primary CTA gradient — start | `blue-600` | `#2563EB` |
| Primary CTA gradient — end | `indigo-600` | `#4F46E5` |
| Sky highlight | `sky-500` | `#0EA5E9` |

Primary buttons use the `blue-600 → indigo-600` gradient, white text, fully rounded. Secondary buttons are outlined in `cyan-700` and fill `cyan-700` with white text on hover.

### Warm accent — illustration only

| Token | Hex |
|---|---|
| Peach | `#FB923C` |
| Amber | `#FCD34D` |
| Coral | `#F87171` |

Exactly **one** warm accent appears in any illustration, used sparingly and never as the largest element. Warm tones do **not** appear in UI, type, or buttons — they live only inside editorial imagery.

---

## 4. Typography

**Inter** is the only typeface, everywhere. Weights in use: 300 (light), 400 (regular), 500 (medium), 600 (semibold).

The voice of the type is airy and considered — large headings in **light** weight with tight tracking, never heavy or shouty.

| Style | Spec |
|---|---|
| Hero heading | `text-6xl md:text-7xl`, `font-light`, `tracking-tight`, `cyan-900` |
| Section heading | `text-3xl md:text-5xl`, `font-light`, `tracking-tight`, `cyan-900` |
| Body | `font-light`, `leading-relaxed`, `cyan-800` |
| Eyebrow / category label | `text-xs`, `font-medium`, `uppercase`, `tracking-wide`, `blue-600` |
| Links | `cyan-700`, hover `cyan-900` |

Rule of thumb: headings are **light**, labels are **medium uppercase**, body is **light and roomy**. Avoid bold walls of text.

---

## 5. Layout & components

- **Content width:** `max-w-6xl mx-auto px-6` general; `max-w-4xl` for text-heavy sections.
- **Section padding:** `py-12 md:py-20 px-6`.
- **Cards:** `bg-white`, `border border-cyan-200`, `rounded-2xl`, `shadow-md`; hover `hover:shadow-lg`.
- **Corners:** `rounded-2xl` for cards, `rounded-full` for buttons and avatars.
- **Grids:** `grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8`.
- **Nav & footer:** identical on every page (cyan nav with Solutions/Resources dropdowns + mobile accordion; three-column footer). Copy from an existing page — never reinvent.

---

## 6. Voice & messaging

### Messaging pillars
1. **Partnership, not replacement** — AI augments human expertise; it doesn't replace people.
2. **Clarity over hype** — speak plainly about what AI can and can't do; no buzzword overload.
3. **Outcomes-focused** — emphasize real results, not technology for its own sake.
4. **Empathy for the human side** — AI adoption creates anxiety and disorientation; meet people where they are.

### Writing style
Warm, confident, direct — a knowledgeable colleague, not a sales brochure. Short paragraphs, clear structure.

- **Preferred vocabulary:** augment, amplify, partner, judgment, expertise, outcomes, coherence.
- **Avoid:** jargon soup, fear-mongering, over-promising, and the words *revolutionize*, *disrupt*, *game-changer*.
- **Contact:** `hi@growthmaxinc.com`

---

## 7. Imagery

GrowthMax images look like editorial illustrations on the cover of a thoughtful business publication — *HBR*, *The Atlantic*, *Stripe Press*.

**Locked across every image:**
1. **Style** — flat modern editorial illustration, painterly; vector shapes with soft gradients and subtle grain. Not photoreal, not 3D, not cartoon, not line-art.
2. **Lighting** — soft, single source, varied per image (the warm-window-afternoon cliché is forbidden as a default).
3. **Palette** — cyan/sky dominant + cool whites, with one sparing warm accent.
4. **Mood** — considered, calm, intentional. No frenetic energy, no "brain + circuit" AI clichés.
5. **No text, no UI** in the artwork.

**Composition varies per piece** — a visual metaphor (no people), a tableau of objects, a single person, or a pair — chosen to fit the argument, not a formula. Full creative direction, prompt templates, and the auto-pipeline rules live in `scripts/skills/growthmax-imagery/SKILL.md`.

---

## 8. Asset downloads

All brand assets are downloadable from **[growthmaxinc.com/brand](https://growthmaxinc.com/brand/)**:

- Full-color logo (PNG) — `assets/brand/growthmax-logo.png`
- Transparent logo (PNG) — `assets/brand/growthmax-logo-transparent.png`
- Logo mark (SVG) — `assets/brand/growthmax-mark.svg`
- Favicon (SVG) — `assets/brand/growthmax-favicon.svg`
- Everything, zipped — `assets/brand/growthmax-brand-assets.zip`

For brand or press inquiries, contact **hi@growthmaxinc.com**.

---

*Last updated: June 8, 2026.*
