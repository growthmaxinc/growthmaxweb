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

It ALSO checks that the newest post actually references a real hero
rather than the /growthMAX.PNG placeholder.

That second check is the one that was missing. Validating only the
dimensions of blog-*.jpg files that happen to exist says nothing about
whether the post just generated got an image at all. Between 2026-07-01
and 2026-08-19, hero rendering failed on every run (a deprecated Claude
model string), generate_hero_image() swallowed the exception, 19 posts
shipped with the generic logo as their OG image, and this validator
passed green every single time. A guard has to test the thing that fails.

Run from CI (.github/workflows/generate-post.yml) or by hand:
    python scripts/validate_hero_images.py
"""
import re
import sys
from pathlib import Path

import yaml
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED = (1200, 630)


PLACEHOLDER = "/growthMAX.PNG"
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _post_image(path):
    """Return the `image:` value from a post's front matter, or None."""
    m = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None
    return fm.get("image")


def check_dimensions():
    """Every blog-*.jpg at the repo root must be exactly 1200x630."""
    images = sorted(REPO_ROOT.glob("blog-*.jpg"))
    if not images:
        print("no blog-*.jpg files found at repo root - skipping dimension check")
        return []

    failures = []
    for img_path in images:
        try:
            with Image.open(img_path) as im:
                size = im.size
        except Exception as e:
            failures.append((img_path.name, "could not open: %s" % e))
            continue
        if size != EXPECTED:
            failures.append((
                img_path.name,
                "dimensions %dx%d != expected %dx%d (canonical pipeline always "
                "emits %dx%d)" % (size[0], size[1], EXPECTED[0], EXPECTED[1],
                                  EXPECTED[0], EXPECTED[1]),
            ))
    print("checked %d hero image(s) for canonical dimensions" % len(images))
    return failures


def check_newest_post_has_hero():
    """The most recent post must reference a real hero, not the placeholder.

    Older posts are reported as warnings so the existing backlog is visible
    without blocking CI. Clear them with the Backfill All Hero Images
    workflow, then they stop appearing.
    """
    posts = sorted((REPO_ROOT / "_posts").glob("*.md"))
    if not posts:
        print("no posts found - skipping hero reference check")
        return []

    stale = [p for p in posts if _post_image(p) == PLACEHOLDER]
    newest = posts[-1]

    if stale:
        older = [p.name for p in stale if p != newest]
        if older:
            print("\nWARNING: %d older post(s) still on the placeholder hero. "
                  "Run the 'Backfill All Hero Images' workflow to clear them:"
                  % len(older))
            for name in older:
                print("  - %s" % name)

    if _post_image(newest) == PLACEHOLDER:
        return [(
            newest.name,
            "references the %s placeholder instead of a generated hero. "
            "Hero rendering failed for this post; check the 'Generate blog "
            "post' step for 'Hero image generation failed'." % PLACEHOLDER,
        )]

    print("newest post (%s) has a real hero image" % newest.name)
    return []


def main():
    failures = check_dimensions() + check_newest_post_has_hero()

    if failures:
        print("\nHERO IMAGE VALIDATION FAILED:")
        for name, why in failures:
            print("  %s: %s" % (name, why))
        return 1

    print("\nHero image validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
