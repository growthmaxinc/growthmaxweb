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

# Image models and the call shape used to reach them.
#
# IMAGE_TIER selects between two incompatible Gemini APIs:
#   "free" -> models.generate_content(). Works with a Gemini Developer API
#             key, which is what GEMINI_API_KEY holds.
#   "paid" -> models.generate_images(). Vertex only. Raises "This method is
#             only supported in Gemini Enterprise Agent Platform mode" under
#             a Developer API key. Every hero render failed this way from
#             2026-09-02 until 53c8997.
#
# Same reasoning as TEXT_MODEL above: the identifiers live in one place so a
# migration cannot half-apply. Do not inline these strings at the call site.
IMAGE_TIER = "free"
IMAGE_MODELS_FREE = ("gemini-3.1-flash-image-preview", "gemini-2.5-flash-image")
IMAGE_MODEL_PAID = "imagen-4.0-generate-001"
