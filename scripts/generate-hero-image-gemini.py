#!/usr/bin/env python3
"""
Generate a hero image for a GrowthMax blog post using Gemini Imagen 3.

Two-stage pipeline:
  Stage 1: Claude reads the post (title + subtitle + tldr) and writes a JSON
           object filling in the per-post variables of the imagery skill's
           prompt template — character, workspace, lighting, mood, etc.
  Stage 2: We assemble the prompt and call Gemini Imagen 3, then resize the
           output to the canonical 1200×630 site dimensions.

Creative direction lives in scripts/skills/growthmax-imagery/SKILL.md and is
loaded fresh on every call. Edits to the skill take effect on the next run
without code changes here.

Usage:
    # CLI — render a single post by passing its content
    python generate-hero-image-gemini.py \\
        --title "Why AI Implementations Fail" \\
        --subtitle "Organizational disorientation, not technology" \\
        --tldr "Roughly 70% of AI implementations fail..." \\
        --out blog-why-ai-implementations-fail.jpg

    # Programmatic — import HeroImageGenerator and call .render_post(...)

Environment:
    ANTHROPIC_API_KEY  required for stage 1 (per-post variables)
    GEMINI_API_KEY     required for stage 2 (image generation)
"""
import argparse
import io
import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from google import genai
from google.genai import types as genai_types
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO / "scripts" / "skills" / "growthmax-imagery" / "SKILL.md"

# Imagen 3 native 16:9 output is 1408x768. We crop+resize to the canonical
# 1200x630 site dimensions, which match the blog layout's object-cover band.
TARGET_W, TARGET_H = 1200, 630

# The 13 per-post variables Claude fills in. Keys must match the bracketed
# placeholders in SKILL.md §Imagen prompt template.
PROMPT_VARIABLES = [
    "CHARACTER",
    "WORKSPACE_TYPE",
    "POSE_DESCRIPTION",
    "ACTIVITY_DESCRIPTION",
    "CONCEPTUAL_ACCENT_DESCRIPTION",
    "LIGHT_SOURCE",
    "WARM_ACCENT_COLOR_NAME",
    "WARM_ACCENT_HEX",
    "WARM_ACCENT_OBJECT",
    "LEFT_OR_RIGHT",
    "OPPOSITE_SIDE_DESCRIPTION",
    "MOOD_REGISTER",
    "CHARACTER_EXPRESSION",
]


PROMPT_TEMPLATE = """A flat modern editorial illustration, painterly style with soft gradients and subtle grain texture. {CHARACTER} in a warm, lived-in {WORKSPACE_TYPE}. The character is in {POSE_DESCRIPTION}, {ACTIVITY_DESCRIPTION}. {CONCEPTUAL_ACCENT_DESCRIPTION}.

Lighting: soft directional warmth from {LIGHT_SOURCE}, late afternoon golden-hour atmosphere, ambient soft shadows.

Color palette: cyan and sky-blue dominant (#38BDF8, #0EA5E9, #0E7490, #ECFEFF, #A5F3FC), with one warm accent of {WARM_ACCENT_COLOR_NAME} ({WARM_ACCENT_HEX}) on {WARM_ACCENT_OBJECT}. No other warm colors.

Composition: character offset to the {LEFT_OR_RIGHT} third of the frame, side profile or three-quarter angle, occupying about 35% of frame width. The opposite side shows {OPPOSITE_SIDE_DESCRIPTION}. Generous breathing room, approximately 15% quiet space.

Style references: Tom Haugomat, Owen Davey, Mark Smith — confident shape language, considered, slightly nostalgic editorial illustration. Not photorealistic. Not 3D-rendered. Not cartoon. Not line-art. Vector shapes with soft painterly textures.

Mood: {MOOD_REGISTER}. {CHARACTER_EXPRESSION}.

Strictly forbidden: any visible text, words, numbers, letters, logos, or UI elements. No legible signs, no readable book titles, no laptop screens with text, no notebook writing — keep all surfaces blank or abstract. No hands-on-keyboard close-ups. No multiple warm colors. No neon, no glow effects, no sparkles unless explicitly described in the conceptual accent.

Aspect ratio: 16:9 landscape, designed for a 1200x630 hero banner."""


CLAUDE_INSTRUCTION = """You are art-directing a single hero illustration for a GrowthMax blog post.

The complete creative direction is in the system prompt above (SKILL.md). Read it carefully — every rule there is binding. Your job is to fill in the per-post variation: the character, the workspace, the activity, the mood, and the conceptual accent that tie this image to THIS post's argument.

Post title:    {title}
Post subtitle: {subtitle}
TL;DR:         {tldr}

Output a JSON object with exactly these keys, no others, no surrounding prose, no code fences:

{{
  "CHARACTER": "<1 sentence — gender, approximate age, ethnicity, hair, attire. Vary across posts; avoid the SaaS-default 'white woman in plaid shirt'>",
  "WORKSPACE_TYPE": "<2-4 words — e.g., 'home office', 'cozy corner office', 'shared studio space'>",
  "POSE_DESCRIPTION": "<short phrase — e.g., 'side profile, seated', 'three-quarter angle, leaning slightly forward'>",
  "ACTIVITY_DESCRIPTION": "<short phrase describing what they're doing right now — match the post's argument>",
  "CONCEPTUAL_ACCENT_DESCRIPTION": "<1 sentence — the one symbolic object on the desk or in the air. Mug-sized. Integrated naturally. See SKILL.md §Per-post variation.>",
  "LIGHT_SOURCE": "<short phrase — e.g., 'a tall window to the left', 'a peach-shaded desk lamp', 'an overhead pendant'>",
  "WARM_ACCENT_COLOR_NAME": "<one of: peach, amber, coral>",
  "WARM_ACCENT_HEX": "<corresponding hex: peach #FB923C, amber #FCD34D, coral #F87171>",
  "WARM_ACCENT_OBJECT": "<short phrase — what specifically holds the warm color. e.g., 'a peach lamp shade', 'an amber notebook', 'a coral plant pot'>",
  "LEFT_OR_RIGHT": "<one of: 'left' or 'right' — which third holds the character>",
  "OPPOSITE_SIDE_DESCRIPTION": "<short phrase — what fills the opposite side. e.g., 'an open window with afternoon light and a small monstera plant', 'a wall with framed prints and a tall bookshelf'>",
  "MOOD_REGISTER": "<short phrase per SKILL.md §Mood register table — e.g., 'engaged, focused, mid-morning warmth', 'quiet, slightly melancholy, late afternoon'>",
  "CHARACTER_EXPRESSION": "<short phrase describing facial expression and gaze — e.g., 'looking down at the notebook with thoughtful concentration', 'gazing toward the window, mid-thought'>"
}}

WORK ORDER:
1. Read the post and identify the emotional weight (diagnostic, tactical, strategic, people, decision per SKILL.md §Mood register).
2. Pick a character that fits the post — vary deliberately across posts so the cast feels like a real team.
3. Pick an activity that visually represents the post's argument (writing, reading, conversing, paused-thinking, etc.).
4. Pick a conceptual accent from SKILL.md §Per-post variation that maps to the post's topic.
5. Pick the warm accent color that fits the mood (peach for warm tactical, amber for grounded strategic, coral sparingly for people-focused).
6. Output ONLY the JSON object."""


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
                f"Imagery skill not found at {SKILL_PATH}. "
                "This file is the source of truth for hero image creative "
                "direction and must be present."
            )
        self.skill_text = SKILL_PATH.read_text()

    # -----------------------------------------------------------------
    # Stage 1 — Claude writes the per-post variables
    # -----------------------------------------------------------------
    def claude_fill_variables(self, title, subtitle, tldr):
        instruction = CLAUDE_INSTRUCTION.format(
            title=title, subtitle=subtitle, tldr=tldr
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
        missing = [v for v in PROMPT_VARIABLES if v not in variables]
        if missing:
            raise ValueError(
                f"Claude returned variables missing required keys: {missing}. "
                f"Got: {sorted(variables.keys())}"
            )
        return variables

    def assemble_prompt(self, variables):
        return PROMPT_TEMPLATE.format(**variables)

    # -----------------------------------------------------------------
    # Stage 2 — Gemini renders the image
    # -----------------------------------------------------------------
    # Two paths:
    #   1. Imagen 4 via generate_images (paid Google AI plan only) — best
    #      quality, dedicated image model. Used if IMAGE_MODEL_TIER=paid.
    #   2. Nano Banana via generate_content (gemini-X-flash-image, available
    #      on free tier) — multimodal model that can output images. Used by
    #      default to keep the pipeline running on the free tier.
    # If Nano Banana ever produces visibly worse output than Imagen, switch
    # the env var or hardcode the tier.

    def imagen_generate(self, prompt):
        """Render the prompt to image bytes via the configured Gemini path."""
        tier = os.environ.get("IMAGE_MODEL_TIER", "free").lower()
        if tier == "paid":
            return self._generate_via_imagen(prompt)
        return self._generate_via_nano_banana(prompt)

    def _generate_via_imagen(self, prompt):
        """Paid path — Imagen 4 dedicated image model."""
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
        """Free-tier path — Nano Banana (gemini-X-flash-image) multimodal.
        Output aspect ratio is not user-controllable on this path; we resize
        whatever it produces to the canonical 1200x630."""
        # Nano Banana 2 (gemini-3.1-flash-image-preview) is the newest as of
        # May 2026 — preview but free. Falls back to 2.5 if 3.1 errors.
        for model_name in (
            "gemini-3.1-flash-image-preview",
            "gemini-2.5-flash-image",
        ):
            try:
                response = self.gemini.models.generate_content(
                    model=model_name,
                    contents=[prompt],
                )
                # Pull the first image part out of the response
                for cand in response.candidates or []:
                    for part in (cand.content.parts if cand.content else []):
                        inline = getattr(part, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            return inline.data
                # No image part — try next model
                print(
                    f"  (no image part in {model_name} response — trying fallback)",
                    flush=True,
                )
            except Exception as e:
                print(f"  ({model_name} errored: {e} — trying fallback)", flush=True)
        raise RuntimeError(
            "All Nano Banana models failed to return an image. "
            "Set IMAGE_MODEL_TIER=paid and ensure billing is enabled "
            "on Google AI Studio to use Imagen 4 instead."
        )

    # -----------------------------------------------------------------
    # Resize Imagen 16:9 output (1408×768) to canonical 1200×630
    # -----------------------------------------------------------------
    def resize_to_canonical(self, image_bytes):
        """Imagen's 16:9 output is ~1408×768 (aspect 1.833). Site target is
        1200×630 (aspect 1.905). We center-crop a tiny strip from top/bottom
        before downscaling to keep the character framing intact."""
        im = Image.open(io.BytesIO(image_bytes))
        if im.mode != "RGB":
            im = im.convert("RGB")

        src_w, src_h = im.size
        # Scale to fit width=TARGET_W, then center-crop height
        scale = TARGET_W / src_w
        scaled_h = int(src_h * scale)
        im = im.resize((TARGET_W, scaled_h), Image.LANCZOS)
        if scaled_h > TARGET_H:
            top = (scaled_h - TARGET_H) // 2
            im = im.crop((0, top, TARGET_W, top + TARGET_H))
        elif scaled_h < TARGET_H:
            # Imagen output was wider than 16:9 — pad rather than crop
            new = Image.new("RGB", (TARGET_W, TARGET_H), (236, 254, 255))
            new.paste(im, (0, (TARGET_H - scaled_h) // 2))
            im = new

        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=88, optimize=True)
        return buf.getvalue()

    # -----------------------------------------------------------------
    # Top-level entry — the only public method most callers need
    # -----------------------------------------------------------------
    def render_post(self, title, subtitle, tldr, out_path):
        out_path = Path(out_path)
        print(f"  [1/3] Claude filling per-post variables...", flush=True)
        variables = self.claude_fill_variables(title, subtitle, tldr)
        prompt = self.assemble_prompt(variables)

        print(f"  [2/3] Imagen rendering (this takes ~10-20s)...", flush=True)
        raw_bytes = self.imagen_generate(prompt)

        print(f"  [3/3] Resizing to {TARGET_W}x{TARGET_H} and saving...", flush=True)
        canonical_bytes = self.resize_to_canonical(raw_bytes)
        out_path.write_bytes(canonical_bytes)

        # Validate dimensions before returning
        with Image.open(out_path) as check:
            if check.size != (TARGET_W, TARGET_H):
                raise RuntimeError(
                    f"Output dimensions {check.size} != expected ({TARGET_W}, {TARGET_H})"
                )

        # Build alt text from the variables — concrete and accessible
        alt = (
            f"Editorial illustration: {variables['CHARACTER'].lower()} "
            f"{variables['ACTIVITY_DESCRIPTION'].lower()} in a {variables['WORKSPACE_TYPE']}, "
            f"with {variables['CONCEPTUAL_ACCENT_DESCRIPTION'].lower()}"
        )
        return out_path, alt, variables


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--tldr", default="")
    parser.add_argument("--out", required=True, help="output JPG path")
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Also write the assembled Imagen prompt to <out>.prompt.txt",
    )
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
        prompt_file = Path(args.out).with_suffix(".prompt.txt")
        prompt_file.write_text(gen.assemble_prompt(variables))
        print(f"  Prompt written to {prompt_file}")


if __name__ == "__main__":
    main()
