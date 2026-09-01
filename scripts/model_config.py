"""
Single source of truth for the Anthropic model used across the pipeline.

Why this file exists
--------------------
`claude-sonnet-4-20250514` was deprecated on 2026-06-15. generate-post.py was
updated to `claude-sonnet-4-6`, but the identical string in
generate-hero-image-gemini.py was missed. From the first run after the
deprecation took effect, every hero image render raised inside
claude_fill_variables(), got swallowed by the broad `except Exception` in
generate_hero_image(), and the post silently shipped with the
/growthMAX.PNG placeholder instead. 19 consecutive posts went out with the
generic logo as their OG image before anyone noticed.

One constant, imported everywhere, so the next model migration is a
one-line change that cannot half-apply.
"""

# Text model for post generation and hero-image variable filling.
TEXT_MODEL = "claude-sonnet-4-6"
