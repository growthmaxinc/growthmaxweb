#!/usr/bin/env python3
"""
Validate that every blog-*.jpg in the repo root is on-brand.

The canonical hero-image renderer (scripts/generate-hero-image.py) always
emits 1200x630 JPGs. The growthmax-imagery skill (scripts/skills/growthmax-imagery/SKILL.md)
declares the renderer the only acceptable production path — no AI-raster
portrait illustrations from Gemini/Midjourney/DALL·E, no bespoke one-off
infographics.

This script enforces that gate. It checks every blog-*.jpg in the repo
root and fails (exit 1) if any image is not exactly 1200x630, which is the
fingerprint of the canonical renderer. Off-brand drift typically introduces
portrait-orientation files (e.g., 1024x1536 from Gemini ImageFX) — those
get caught here before they reach main.

Run from CI (.github/workflows/) or by hand:
    python scripts/validate_hero_images.py
"""
import sys
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED = (1200, 630)


def main():
    failures = []
    images = sorted(REPO_ROOT.glob("blog-*.jpg"))
    if not images:
        print("no blog-*.jpg files found at repo root — skipping validation")
        return 0
    for img_path in images:
        try:
            with Image.open(img_path) as im:
                size = im.size
        except Exception as e:
            failures.append((img_path.name, f"could not open: {e}"))
            continue
        if size != EXPECTED:
            failures.append((
                img_path.name,
                f"dimensions {size[0]}x{size[1]} != expected {EXPECTED[0]}x{EXPECTED[1]} "
                "(only the canonical PIL renderer is allowed — see "
                "scripts/skills/growthmax-imagery/SKILL.md)"
            ))

    if failures:
        print(f"\n✗ Hero image validation FAILED — {len(failures)} off-brand file(s):\n")
        for name, reason in failures:
            print(f"  {name}")
            print(f"    {reason}")
        print(
            "\nFix: regenerate the failing image(s) using "
            "scripts/generate-hero-image.py with a spec that follows "
            "scripts/skills/growthmax-imagery/SKILL.md.\n"
        )
        return 1

    print(f"✓ Hero image validation passed — {len(images)} files, all 1200x630.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
