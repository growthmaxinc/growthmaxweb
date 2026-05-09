#!/usr/bin/env python3
"""
Render hero image samples for visual review.

Triggered by .github/workflows/sample-heroes.yml. Reads a comma-separated
list of post slugs from the SLUGS env var, looks up each post's front
matter in _posts/, and generates the hero image into samples/blog-{slug}.jpg.

The samples/ directory is not referenced by any layout — these images are
purely for human review. Once the aesthetic is approved, the backfill
script regenerates all 20 posts and moves them to the repo root.

Run locally:
    SLUGS="where-do-i-fit-crisis,measure-roi-first-ai-agent" \\
    ANTHROPIC_API_KEY=... GEMINI_API_KEY=... \\
    python scripts/render_samples.py
"""
import os
import re
import sys
from pathlib import Path

# Local modules
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "gemini_hero", str(Path(__file__).parent / "generate-hero-image-gemini.py")
)
gemini_hero = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gemini_hero)

import yaml

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"
SAMPLES_DIR = REPO / "samples"


def find_post_file(slug):
    """Find the _posts/*.md file whose filename ends with {slug}.md."""
    for f in POSTS_DIR.glob(f"*-{slug}.md"):
        return f
    raise FileNotFoundError(
        f"No _posts file found for slug {slug!r}. "
        f"Looked for *-{slug}.md in {POSTS_DIR}"
    )


def parse_frontmatter(post_path):
    """Extract title/subtitle/tldr from a Jekyll markdown post."""
    text = post_path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        raise ValueError(f"No front matter in {post_path}")
    fm = yaml.safe_load(m.group(1))
    return {
        "title": fm.get("title", ""),
        "subtitle": fm.get("subtitle", ""),
        "tldr": fm.get("tldr", ""),
    }


def main():
    slugs_raw = os.environ.get("SLUGS", "").strip()
    if not slugs_raw:
        print("ERROR: SLUGS env var is empty", file=sys.stderr)
        sys.exit(1)
    slugs = [s.strip() for s in slugs_raw.split(",") if s.strip()]
    print(f"Rendering {len(slugs)} sample(s): {', '.join(slugs)}")

    SAMPLES_DIR.mkdir(exist_ok=True)
    gen = gemini_hero.HeroImageGenerator()

    # For multi-post sample renders, force-pin the ethnicity per slug using
    # quota assignment so the demographic ratio matches SKILL.md exactly
    # (single-slug sampling has too much variance at small N).
    if len(slugs) > 1:
        assignments = gemini_hero.assign_ethnicities_quota(slugs)
        gen._ethnicity_overrides = assignments
        print(f"  Ethnicity assignments (quota): {assignments}")
    else:
        gen._ethnicity_overrides = {}

    failures = []
    for slug in slugs:
        try:
            post_file = find_post_file(slug)
            fm = parse_frontmatter(post_file)
            print(f"\n=== {slug} ===")
            print(f"  Title: {fm['title']}")
            out_path = SAMPLES_DIR / f"blog-{slug}.jpg"
            gen.render_post(fm["title"], fm["subtitle"], fm["tldr"], out_path)
            print(f"  ✓ {out_path}")
        except Exception as e:
            print(f"  ✗ {slug} failed: {e}", file=sys.stderr)
            failures.append((slug, str(e)))

    if failures:
        print(f"\n{len(failures)} sample(s) failed:")
        for slug, err in failures:
            print(f"  - {slug}: {err}")
        sys.exit(1)
    print(f"\n✓ All {len(slugs)} samples rendered to {SAMPLES_DIR}/")


if __name__ == "__main__":
    main()
