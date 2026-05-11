#!/usr/bin/env python3
"""
Validate that every blog-*.jpg at the repo root is at the canonical
hero dimensions (1200x630).

The canonical hero pipeline is the two-stage renderer in
generate-hero-image-gemini.py: Gemini Imagen renders an image, which is
then resized to 1200x630 (TARGET_W x TARGET_H in that module). Anything
in the repo root that doesn't match that fingerprint is off-brand and
should not be published.

Behaviour:
  * No blog-*.jpg files at all -> exit 0 (no-op). The blog generator
    falls back to the default placeholder hero when image rendering
    fails, so a publish-text-only run is allowed and validation
    skips silently.
  * Any blog-*.jpg with non-1200x630 dimensions -> exit 1, listing
    each offender. CI then refuses to commit/deploy until the file is
    re-rendered through the canonical pipeline.

Run from CI (.github/workflows/generate-post.yml) or by hand:
    python scripts/validate_hero_images.py
"""
import sys
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED = (1200, 630)


def main():
    images = sorted(REPO_ROOT.glob("blog-*.jpg"))
    if not images:
        print("no blog-*.jpg files found at repo root - skipping validation")
        return 0

    failures = []
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
                f"dimensions {size[0]}x{size[1]} != expected "
                f"{EXPECTED[0]}x{EXPECTED[1]} (canonical pipeline always "
                "emits this size; see scripts/generate-hero-image-gemini.py "
                "TARGET_W/TARGET_H)"
            ))

    if failures:
        print(f"\nHero image validation FAILED - {len(failures)} off-brand file(s):\n")
        for name, reason in failures:
            print(f"  {name}")
            print(f"    {reason}")
        print(
            "\nFix: regenerate the failing image(s) via the backfill workflow "
            "(.github/workflows/backfill-heroes.yml) or by running "
            "scripts/render_samples.py with OUTPUT_DIR=. for the affected slugs.\n"
        )
        return 1

    print(f"Hero image validation passed - {len(images)} files, all 1200x630.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
