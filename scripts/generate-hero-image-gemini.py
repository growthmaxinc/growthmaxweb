#!/usr/bin/env python3
"""
Generate a hero image for a GrowthMax blog post using Gemini Imagen 4.

Two-stage pipeline:
  Stage 1: Pre-sample composition type, gender, ethnicity per slug
           (deterministic via slug hash + quotas). Then Claude fills in the
           per-post variables for the chosen composition type's template.
  Stage 2: Gemini Imagen 4 renders the assembled prompt; we resize the
           output to the canonical 1200×630 site dimensions.

Creative direction lives in scripts/skills/growthmax-imagery/SKILL.md.
The skill defines four composition types (metaphor / tableau / person /
group); each has its own prompt template and Claude instruction.

Environment:
    ANTHROPIC_API_KEY  required for stage 1
    GEMINI_API_KEY     required for stage 2
    IMAGE_MODEL_TIER   "paid" (default for backfill/auto) → Imagen 4
                       "free" → Nano Banana via generateContent
"""
import argparse
import hashlib
import io
import json
import os
import random
import sys
from pathlib import Path

from anthropic import Anthropic
from google import genai
from google.genai import types as genai_types
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO / "scripts" / "skills" / "growthmax-imagery" / "SKILL.md"
TARGET_W, TARGET_H = 1200, 630


# ---------------------------------------------------------------------
# Quota distributions — see SKILL.md for rationale
# ---------------------------------------------------------------------

COMPOSITION_DISTRIBUTION = [
    ("metaphor", 0.50),  # iceberg, road, bridge, fork — no people
    ("tableau",  0.15),  # arranged objects, no full figures
    ("person",   0.25),  # single character, personal-experience posts
    ("group",    0.10),  # two characters, collaboration posts
]

ETHNICITY_DISTRIBUTION = [
    ("Caucasian",       0.85),
    ("Black",           0.04),
    ("East Asian",      0.03),
    ("South Asian",     0.03),
    ("Hispanic/Latino", 0.03),
    ("Middle Eastern",  0.02),
]

# Gender split is 50/50 across person + group posts only
GENDERS = ["man", "woman"]


def _seed_for(slug, salt=""):
    return int(hashlib.sha256((salt + slug).encode()).hexdigest()[:8], 16)


def pick_ethnicity_for_slug(slug):
    seed = _seed_for(slug, "ethnicity:")
    rng = random.Random(seed)
    r = rng.random()
    cum = 0.0
    for label, w in ETHNICITY_DISTRIBUTION:
        cum += w
        if r < cum:
            return label
    return "Caucasian"


def pick_gender_for_slug(slug):
    seed = _seed_for(slug, "gender:")
    rng = random.Random(seed)
    return rng.choice(GENDERS)


def pick_composition_for_slug(slug):
    seed = _seed_for(slug, "composition:")
    rng = random.Random(seed)
    r = rng.random()
    cum = 0.0
    for label, w in COMPOSITION_DISTRIBUTION:
        cum += w
        if r < cum:
            return label
    return "metaphor"


def assign_ethnicities_quota(slugs, compositions=None):
    """Exact 85/15 ethnicity quota across slugs that will actually display
    a character (person + group compositions). Slugs that get metaphor or
    tableau compositions get 'Caucasian' assigned but it's never used.

    If compositions is None, applies the quota to all slugs (legacy behavior).
    """
    if not slugs:
        return {}
    if compositions is None:
        slugs_for_quota = list(slugs)
    else:
        slugs_for_quota = [s for s in slugs if compositions.get(s) in ("person", "group")]
    n = len(slugs_for_quota)
    n_other = max(round(n * 0.15), 0)
    ranked = sorted(slugs_for_quota, key=lambda s: hashlib.sha256(("ethnicity:" + s).encode()).hexdigest())
    other_slugs = set(ranked[:n_other])
    pool = ["Black", "East Asian", "South Asian", "Hispanic/Latino", "Middle Eastern"]
    out = {}
    for i, slug in enumerate(sorted(other_slugs)):
        out[slug] = pool[i % len(pool)]
    for slug in slugs:
        if slug not in out:
            out[slug] = "Caucasian"
    return out


def assign_compositions_quota(slugs):
    """Composition assignment per slug. For known posts uses the
    hand-curated KNOWN_COMPOSITIONS map (picked from each post's actual
    argument shape). For unknown posts falls back to hash-based pick
    weighted by COMPOSITION_DISTRIBUTION."""
    out = {}
    for slug in slugs:
        if slug in KNOWN_COMPOSITIONS:
            out[slug] = KNOWN_COMPOSITIONS[slug]
        else:
            out[slug] = pick_composition_for_slug(slug)
    return out


def assign_genders_quota(slugs, compositions):
    """50/50 gender split across the slugs that need a gender (person + group).
    Pre-sampled deterministically from the slug list."""
    needing_gender = [s for s in slugs if compositions.get(s) in ("person", "group")]
    if not needing_gender:
        return {}
    ranked = sorted(needing_gender, key=lambda s: hashlib.sha256(("gender:" + s).encode()).hexdigest())
    half = len(ranked) // 2
    out = {}
    for i, slug in enumerate(ranked):
        out[slug] = "woman" if i < half else "man"
    return out


# ---------------------------------------------------------------------
# Prompt templates per composition type
# ---------------------------------------------------------------------

METAPHOR_TEMPLATE = """A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. {METAPHOR_DESCRIPTION}. {SCENE_CONTEXT}.

No people in the image. The composition is symbolic — a single visual metaphor that encodes the post's argument.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. Avoid harsh shadows. The warm-window-spilling-afternoon-light cliché is forbidden.

Color palette: cool tones dominate — deep cyan, soft sky-blue, ice-blue, cool whites. Exactly ONE warm accent of muted {WARM_ACCENT_COLOR_NAME} appears on {WARM_ACCENT_OBJECT} only. No other warm colors anywhere in the image.

Composition: {COMPOSITION_NOTES}. Generous breathing room.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli — confident shape language, considered editorial illustration. Not photorealistic. Not 3D-rendered. Not cartoon. Vector shapes with soft painterly textures.

Mood: {MOOD_REGISTER}.

CRITICAL — NO TEXT WHATSOEVER: the image must contain ZERO letters, numbers, words, labels, captions, hex codes, color codes, signs, logos, brand marks, book titles, notebook writing, sticky-note text, screen text, watermarks, or any character glyphs of any kind. Every surface (book covers, paper, notebooks, signs, screens, posters) must be blank or filled with abstract shapes only. If you would normally letter or label anything, leave it blank. This rule is absolute and overrides any other instruction.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner."""


TABLEAU_TEMPLATE = """A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. An overhead or three-quarter view of a {SURFACE_TYPE} arranged with {OBJECT_LIST}. {SCENE_CONTEXT}.

No full human figures — at most a hand or arm at the edge of the frame.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. The warm-window-spilling-afternoon-light cliché is forbidden.

Color palette: cool tones dominate — deep cyan, soft sky-blue, ice-blue, cool whites. Exactly ONE warm accent of muted {WARM_ACCENT_COLOR_NAME} appears on {WARM_ACCENT_OBJECT} only. No other warm colors anywhere in the image.

Composition: {COMPOSITION_NOTES}.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli.

Mood: {MOOD_REGISTER}.

CRITICAL — NO TEXT WHATSOEVER: the image must contain ZERO letters, numbers, words, labels, captions, hex codes, color codes, signs, logos, brand marks, book titles, notebook writing, sticky-note text, screen text, watermarks, or any character glyphs of any kind. Every surface must be blank or filled with abstract shapes only. This rule is absolute and overrides any other instruction.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner."""


PERSON_TEMPLATE = """A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. {CHARACTER} in a {SETTING_TYPE}. The character is in {POSE_DESCRIPTION}, {ACTIVITY_DESCRIPTION}. {CONCEPTUAL_ACCENT_DESCRIPTION}.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. The warm-window-spilling-afternoon-light cliché is forbidden — use a different light source for this image.

Color palette: cool tones dominate — deep cyan, soft sky-blue, ice-blue, cool whites. Exactly ONE warm accent of muted {WARM_ACCENT_COLOR_NAME} appears on {WARM_ACCENT_OBJECT} only. No other warm colors anywhere in the image.

Composition: character offset to the {LEFT_OR_RIGHT} third of the frame, side profile or three-quarter angle, occupying about 35% of frame width. The opposite side shows {OPPOSITE_SIDE_DESCRIPTION}. Generous breathing room.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli.

Mood: {MOOD_REGISTER}. {CHARACTER_EXPRESSION}.

CRITICAL — NO TEXT WHATSOEVER: the image must contain ZERO letters, numbers, words, labels, captions, hex codes, color codes, signs, logos, brand marks, book titles, notebook writing, sticky-note text, screen text, watermarks, or any character glyphs of any kind. Every surface (books, paper, notebooks, signs, screens, posters, wall art) must be blank or filled with abstract shapes only. This rule is absolute and overrides any other instruction. Also forbidden: hands-on-keyboard close-ups, multiple warm colors.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner."""


GROUP_TEMPLATE = """A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. Two characters in {SETTING_TYPE}: {CHARACTER_A_DESCRIPTION} and {CHARACTER_B_DESCRIPTION}. They are {INTERACTION_DESCRIPTION}. {CONCEPTUAL_ACCENT_DESCRIPTION}.

Lighting: {LIGHT_DESCRIPTION}. Soft, considered, single source. The warm-window-spilling-afternoon-light cliché is forbidden.

Color palette: cool tones dominate — deep cyan, soft sky-blue, ice-blue, cool whites. Exactly ONE warm accent of muted {WARM_ACCENT_COLOR_NAME} appears on {WARM_ACCENT_OBJECT} only. No other warm colors anywhere in the image.

Composition: both characters in the lower two-thirds, with breathing space above. {COMPOSITION_NOTES}.

Style references: Tom Haugomat, Owen Davey, Olimpia Zagnoli.

Mood: {MOOD_REGISTER}.

CRITICAL — NO TEXT WHATSOEVER: the image must contain ZERO letters, numbers, words, labels, captions, hex codes, color codes, signs, logos, brand marks, book titles, notebook writing, sticky-note text, screen text, watermarks, or any character glyphs of any kind. Every surface must be blank or filled with abstract shapes only. This rule is absolute and overrides any other instruction. Also forbidden: multiple warm colors.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner."""


PROMPT_TEMPLATES = {
    "metaphor": METAPHOR_TEMPLATE,
    "tableau":  TABLEAU_TEMPLATE,
    "person":   PERSON_TEMPLATE,
    "group":    GROUP_TEMPLATE,
}


# Required JSON keys per composition type — Claude must return exactly these
TEMPLATE_VARIABLES = {
    "metaphor": [
        "METAPHOR_DESCRIPTION", "SCENE_CONTEXT", "LIGHT_DESCRIPTION",
        "WARM_ACCENT_COLOR_NAME", "WARM_ACCENT_OBJECT",
        "COMPOSITION_NOTES", "MOOD_REGISTER",
    ],
    "tableau": [
        "SURFACE_TYPE", "OBJECT_LIST", "SCENE_CONTEXT", "LIGHT_DESCRIPTION",
        "WARM_ACCENT_COLOR_NAME", "WARM_ACCENT_OBJECT",
        "COMPOSITION_NOTES", "MOOD_REGISTER",
    ],
    "person": [
        "CHARACTER", "SETTING_TYPE", "POSE_DESCRIPTION", "ACTIVITY_DESCRIPTION",
        "CONCEPTUAL_ACCENT_DESCRIPTION", "LIGHT_DESCRIPTION",
        "WARM_ACCENT_COLOR_NAME", "WARM_ACCENT_OBJECT",
        "LEFT_OR_RIGHT", "OPPOSITE_SIDE_DESCRIPTION",
        "MOOD_REGISTER", "CHARACTER_EXPRESSION",
    ],
    "group": [
        "SETTING_TYPE", "CHARACTER_A_DESCRIPTION", "CHARACTER_B_DESCRIPTION",
        "INTERACTION_DESCRIPTION", "CONCEPTUAL_ACCENT_DESCRIPTION",
        "LIGHT_DESCRIPTION",
        "WARM_ACCENT_COLOR_NAME", "WARM_ACCENT_OBJECT",
        "COMPOSITION_NOTES", "MOOD_REGISTER",
    ],
}


# Hand-curated composition assignments for the 20 published posts.
# Picked from each post's actual argument shape, not random hash.
# For new (unknown) posts the auto-pipeline falls back to hash-based pick.
KNOWN_COMPOSITIONS = {
    "partnership-not-replacement": "metaphor",         # two hands reaching for the same task
    "where-do-i-fit-crisis": "person",                  # personal/emotional
    "why-ai-implementations-fail": "metaphor",          # broken bridge / scattered pieces
    "your-first-ai-agent": "metaphor",                  # single sapling / focused beam
    "measure-roi-first-ai-agent": "tableau",            # notebook + chart + ruler
    "custom-ai-agents-vs-off-shelf": "metaphor",        # fork in road, two paths
    "people-first-ai-strategy": "group",                # collaboration
    "90-day-ai-adoption-timeline": "metaphor",          # winding road / path with milestones
    "hidden-costs-ai-implementation": "metaphor",       # iceberg
    "change-management-playbook": "group",              # leading people through change
    "stalled-ai-project": "metaphor",                   # stopped gear / blocked road
    "ai-training-vs-implementation": "metaphor",        # two pillars with bridge
    "signs-team-ready-ai": "tableau",                   # 5 small symbolic objects
    "post-launch-ai-agent-management": "metaphor",      # tending a young plant
    "when-to-hire-ai-consultant-vs-building-in-house": "metaphor",  # fork
    "how-to-scale-ai-adoption-after-first-success": "metaphor",     # sapling to tree
    "why-your-second-ai-project-matters-more-than-your-first": "metaphor",  # second seed
    "executive-buy-in-ai-projects-leadership-alignment": "group",   # exec + lead at table
    "how-to-train-team-ai-without-overwhelm": "person",             # learner reading
    "building-trust-ai-address-team-resistance": "group",           # two people in conversation
}


# ---------------------------------------------------------------------
# Claude instruction templates per composition type
# ---------------------------------------------------------------------

CLAUDE_BASE_INSTRUCTION = """You are art-directing a single hero illustration for a GrowthMax blog post.

The complete creative direction is in the system prompt above (SKILL.md). Read it carefully — every rule is binding.

Post title:    {title}
Post subtitle: {subtitle}
TL;DR:         {tldr}

PRE-ASSIGNED FOR THIS POST:
- Composition type: {composition}
- Lighting brief (one of these, vary across posts): NOT a window in late afternoon. Pick from: overcast morning indoor diffuse, single overhead lamp glow, ambient diffuse studio light, blue-hour dusk through skylight, midday outdoor shade, candlelight, screen-glow blue light, warm tungsten interior, cool fluorescent ceiling, side rim from a doorway.{character_constraints}

Output a JSON object with exactly these keys, no others:

{json_schema}

WORK ORDER:
1. Read the post and identify its argument shape and emotional weight.
2. Build the per-post variables to encode that argument visually using the {composition} composition type per SKILL.md.
3. Make sure every choice ties back to THIS post's specific topic — don't be generic.
4. The lighting must NOT be "warm window in late afternoon" — pick something different.
5. Output ONLY the JSON object, no surrounding prose, no code fences.
"""


METAPHOR_SCHEMA = """{
  "METAPHOR_DESCRIPTION": "<1-2 sentences: the central visual metaphor for this post. Be specific and vivid (not 'a road' but 'a quiet country road forking at a wooden signpost'). See SKILL.md §Type A examples.>",
  "SCENE_CONTEXT": "<1 sentence: surrounding context for the metaphor — what's around it, what background>",
  "LIGHT_DESCRIPTION": "<short phrase per the lighting brief above — pick something OTHER than warm afternoon window light>",
  "WARM_ACCENT_COLOR_NAME": "<one of: muted peach, soft amber, dusty coral>",
  "WARM_ACCENT_OBJECT": "<short phrase — what specifically holds the warm color>",
  "COMPOSITION_NOTES": "<1 sentence: how the metaphor is positioned in the frame — central, offset, foreground/background>",
  "MOOD_REGISTER": "<short phrase — quiet & contemplative, urgent & focused, hopeful, melancholy, etc>"
}"""


TABLEAU_SCHEMA = """{
  "SURFACE_TYPE": "<2-4 words: e.g., 'wooden desk', 'marble countertop', 'paper-strewn drafting table'>",
  "OBJECT_LIST": "<1-2 sentences listing the specific objects arranged on the surface — they should encode the post's argument>",
  "SCENE_CONTEXT": "<short phrase: what surrounds the surface (a chair edge, a wall, an open window edge, etc.)>",
  "LIGHT_DESCRIPTION": "<short phrase per the lighting brief — NOT warm afternoon window light>",
  "WARM_ACCENT_COLOR_NAME": "<one of: muted peach, soft amber, dusty coral>",
  "WARM_ACCENT_OBJECT": "<which object holds the warm color>",
  "COMPOSITION_NOTES": "<1 sentence: angle (overhead, three-quarter, side), how objects are arranged in the frame>",
  "MOOD_REGISTER": "<short phrase>"
}"""


PERSON_SCHEMA = """{
  "CHARACTER": "<1 sentence — gender (use the assigned gender), approximate age, hair, attire. Use the assigned ethnicity. Avoid SaaS-default 'white woman in plaid shirt'>",
  "SETTING_TYPE": "<2-4 words from SKILL.md §Setting variety — NOT 'home office with window'. Try library, café, train, kitchen counter, conference room, studio, outdoor terrace, etc.>",
  "POSE_DESCRIPTION": "<short phrase>",
  "ACTIVITY_DESCRIPTION": "<short phrase tied to the post's argument>",
  "CONCEPTUAL_ACCENT_DESCRIPTION": "<1 sentence: the symbolic object per SKILL.md §Per-post conceptual accent>",
  "LIGHT_DESCRIPTION": "<short phrase per lighting brief — NOT warm afternoon window light>",
  "WARM_ACCENT_COLOR_NAME": "<one of: muted peach, soft amber, dusty coral>",
  "WARM_ACCENT_OBJECT": "<short phrase>",
  "LEFT_OR_RIGHT": "<'left' or 'right'>",
  "OPPOSITE_SIDE_DESCRIPTION": "<short phrase: what fills the opposite side of the frame>",
  "MOOD_REGISTER": "<short phrase>",
  "CHARACTER_EXPRESSION": "<short phrase: face/gaze>"
}"""


GROUP_SCHEMA = """{
  "SETTING_TYPE": "<2-4 words — NOT 'home office with window'. Where this conversation happens: a café, a low couch in a lounge, an outdoor bench, a conference room corner, etc.>",
  "CHARACTER_A_DESCRIPTION": "<1 sentence — first character, use the assigned gender for them>",
  "CHARACTER_B_DESCRIPTION": "<1 sentence — second character, opposite gender from A by default unless the post specifically calls for same-gender>",
  "INTERACTION_DESCRIPTION": "<short phrase: what they're doing — leaning over a shared document, in conversation across a table, listening side-by-side, etc.>",
  "CONCEPTUAL_ACCENT_DESCRIPTION": "<1 sentence: symbolic object>",
  "LIGHT_DESCRIPTION": "<short phrase — NOT warm afternoon window light>",
  "WARM_ACCENT_COLOR_NAME": "<one of: muted peach, soft amber, dusty coral>",
  "WARM_ACCENT_OBJECT": "<short phrase>",
  "COMPOSITION_NOTES": "<1 sentence>",
  "MOOD_REGISTER": "<short phrase>"
}"""


CLAUDE_SCHEMAS = {
    "metaphor": METAPHOR_SCHEMA,
    "tableau":  TABLEAU_SCHEMA,
    "person":   PERSON_SCHEMA,
    "group":    GROUP_SCHEMA,
}


# ---------------------------------------------------------------------
# HeroImageGenerator
# ---------------------------------------------------------------------
class HeroImageGenerator:
    def __init__(self, anthropic_client=None, gemini_api_key=None):
        self.anthropic = anthropic_client or Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"]
        )
        self.gemini = genai.Client(
            api_key=gemini_api_key or os.environ["GEMINI_API_KEY"]
        )
        if not SKILL_PATH.exists():
            raise FileNotFoundError(
                f"Imagery skill not found at {SKILL_PATH}."
            )
        self.skill_text = SKILL_PATH.read_text()
        # Override maps populated by render_samples for batch jobs
        self._composition_overrides = {}
        self._gender_overrides = {}
        self._ethnicity_overrides = {}

    def _resolve_assignments(self, slug):
        """Pick composition, gender, ethnicity for this slug — overrides win."""
        composition = self._composition_overrides.get(slug) or pick_composition_for_slug(slug)
        ethnicity = self._ethnicity_overrides.get(slug) or pick_ethnicity_for_slug(slug)
        gender = self._gender_overrides.get(slug) or pick_gender_for_slug(slug)
        return composition, gender, ethnicity

    # -----------------------------------------------------------------
    # Stage 1 — Claude writes the per-post variables
    # -----------------------------------------------------------------
    def claude_fill_variables(self, title, subtitle, tldr, slug):
        composition, gender, ethnicity = self._resolve_assignments(slug)

        # Build character constraints only for compositions that need them
        if composition == "person":
            character_constraints = (
                f"\n- Character: a {gender} of {ethnicity} ethnicity. "
                "Use this assignment exactly; the rest of the character is yours to build."
            )
        elif composition == "group":
            character_constraints = (
                f"\n- One of the two characters: a {gender} of {ethnicity} ethnicity. "
                "The second character should differ in gender (and may differ in ethnicity)."
            )
        else:
            character_constraints = ""

        instruction = CLAUDE_BASE_INSTRUCTION.format(
            title=title, subtitle=subtitle, tldr=tldr,
            composition=composition,
            character_constraints=character_constraints,
            json_schema=CLAUDE_SCHEMAS[composition],
        )
        resp = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=self.skill_text,
            messages=[{"role": "user", "content": instruction}],
        )
        text = resp.content[0].text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        variables = json.loads(text.strip())
        required = TEMPLATE_VARIABLES[composition]
        missing = [v for v in required if v not in variables]
        if missing:
            raise ValueError(
                f"Claude returned variables missing required keys for composition "
                f"'{composition}': {missing}. Got: {sorted(variables.keys())}"
            )
        return composition, variables

    def assemble_prompt(self, composition, variables):
        return PROMPT_TEMPLATES[composition].format(**variables)

    # -----------------------------------------------------------------
    # Stage 2 — Gemini renders
    # -----------------------------------------------------------------
    def imagen_generate(self, prompt):
        tier = os.environ.get("IMAGE_MODEL_TIER", "free").lower()
        if tier == "paid":
            return self._generate_via_imagen(prompt)
        return self._generate_via_nano_banana(prompt)

    def _generate_via_imagen(self, prompt):
        result = self.gemini.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=genai_types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            ),
        )
        if not result.generated_images:
            raise RuntimeError("Imagen returned no images")
        return result.generated_images[0].image.image_bytes

    def _generate_via_nano_banana(self, prompt):
        for model_name in ("gemini-3.1-flash-image-preview", "gemini-2.5-flash-image"):
            try:
                response = self.gemini.models.generate_content(
                    model=model_name,
                    contents=[prompt],
                )
                for cand in response.candidates or []:
                    for part in (cand.content.parts if cand.content else []):
                        inline = getattr(part, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            return inline.data
                print(f"  (no image part in {model_name}, trying fallback)", flush=True)
            except Exception as e:
                print(f"  ({model_name} errored: {e}, trying fallback)", flush=True)
        raise RuntimeError(
            "All Nano Banana models failed. Set IMAGE_MODEL_TIER=paid for Imagen 4."
        )

    def resize_to_canonical(self, image_bytes):
        im = Image.open(io.BytesIO(image_bytes))
        if im.mode != "RGB":
            im = im.convert("RGB")
        src_w, src_h = im.size
        scale = TARGET_W / src_w
        scaled_h = int(src_h * scale)
        im = im.resize((TARGET_W, scaled_h), Image.LANCZOS)
        if scaled_h > TARGET_H:
            top = (scaled_h - TARGET_H) // 2
            im = im.crop((0, top, TARGET_W, top + TARGET_H))
        elif scaled_h < TARGET_H:
            new = Image.new("RGB", (TARGET_W, TARGET_H), (236, 254, 255))
            new.paste(im, (0, (TARGET_H - scaled_h) // 2))
            im = new
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=88, optimize=True)
        return buf.getvalue()

    # -----------------------------------------------------------------
    # Top-level entry
    # -----------------------------------------------------------------
    def render_post(self, title, subtitle, tldr, out_path):
        out_path = Path(out_path)
        slug = out_path.stem.removeprefix("blog-")

        composition, _, _ = self._resolve_assignments(slug)
        print(f"  [1/3] Composition={composition}; Claude filling variables...", flush=True)
        composition, variables = self.claude_fill_variables(title, subtitle, tldr, slug=slug)
        prompt = self.assemble_prompt(composition, variables)

        print(f"  [2/3] Imagen rendering (~10-20s)...", flush=True)
        raw_bytes = self.imagen_generate(prompt)

        print(f"  [3/3] Resizing to {TARGET_W}x{TARGET_H} and saving...", flush=True)
        canonical_bytes = self.resize_to_canonical(raw_bytes)
        out_path.write_bytes(canonical_bytes)

        with Image.open(out_path) as check:
            if check.size != (TARGET_W, TARGET_H):
                raise RuntimeError(
                    f"Output dimensions {check.size} != ({TARGET_W}, {TARGET_H})"
                )

        # Build alt text from whatever variables we have
        if composition == "metaphor":
            alt = f"Editorial illustration: {variables['METAPHOR_DESCRIPTION'].lower()}"
        elif composition == "tableau":
            alt = f"Editorial illustration: arranged objects on a {variables['SURFACE_TYPE']} including {variables['OBJECT_LIST'].lower()}"
        elif composition == "person":
            alt = (f"Editorial illustration: {variables['CHARACTER'].lower()} "
                   f"{variables['ACTIVITY_DESCRIPTION'].lower()} in a {variables['SETTING_TYPE']}")
        else:  # group
            alt = (f"Editorial illustration: two people in a {variables['SETTING_TYPE']} "
                   f"{variables['INTERACTION_DESCRIPTION'].lower()}")
        return out_path, alt, variables


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--tldr", default="")
    parser.add_argument("--out", required=True)
    parser.add_argument("--print-prompt", action="store_true")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    gen = HeroImageGenerator()
    print(f"Rendering: {args.title}")
    out_path, alt, variables = gen.render_post(
        args.title, args.subtitle, args.tldr, args.out
    )
    print(f"\n✓ Wrote {out_path}")
    print(f"  Alt: {alt}")
    if args.print_prompt:
        composition = pick_composition_for_slug(out_path.stem.removeprefix("blog-"))
        Path(args.out).with_suffix(".prompt.txt").write_text(
            gen.assemble_prompt(composition, variables)
        )


if __name__ == "__main__":
    main()
