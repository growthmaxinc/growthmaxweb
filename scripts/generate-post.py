"""
Blog post generator for GrowthMax Inc.
Generates SEO/AEO-optimized blog posts using Claude API.
Called by GitHub Actions on a schedule (Mon/Wed/Fri).
"""

import os
import sys
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic

# Local module — programmatic flat-vector hero image renderer.
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "hero_image", str(Path(__file__).parent / "generate-hero-image.py")
)
hero_image = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hero_image)

# --- Configuration ---

POSTS_DIR = Path("_posts")
TOPICS_FILE = Path("scripts/topics.yml")

BRAND_VOICE = """
You are writing for GrowthMax Inc, an AI consultancy that builds custom AI agents
and offers AI training bootcamps. The core brand message is "Partnership. Not Replacement."

Writing style:
- Warm, confident, direct — like a knowledgeable colleague, not a sales brochure
- Short paragraphs, clear structure
- Avoid: jargon soup, fear-mongering, over-promising, "revolutionize," "disrupt," "game-changer"
- Preferred vocabulary: augment, amplify, partner, judgment, expertise, outcomes, coherence
- Use em dashes (---) sparingly for emphasis
- Always frame AI as augmenting human expertise, never replacing it

Core messaging pillars:
1. Partnership, not replacement — AI augments human expertise
2. Clarity over hype — speak plainly about what AI can and can't do
3. Outcomes-focused — emphasize real results
4. Empathy for the human side — acknowledge AI adoption anxiety
"""

CATEGORIES = [
    "AI Strategy",
    "People & Culture",
    "Getting Started",
    "Implementation",
    "Partnership Model",
    "Employee Experience",
    "Leadership",
]

def get_existing_posts():
    """Read existing post titles to avoid duplicates."""
    posts = []
    for f in POSTS_DIR.glob("*.md"):
        with open(f) as fh:
            content = fh.read()
            # Extract title from front matter
            match = re.search(r'^title:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
            if match:
                posts.append(match.group(1))
    return posts

def get_topic_queue():
    """Load topic queue if it exists."""
    if TOPICS_FILE.exists():
        with open(TOPICS_FILE) as f:
            data = yaml.safe_load(f)
            return data.get("topics", []) if data else []
    return []

def generate_post(client, topic=None):
    """Generate a blog post using Claude."""
    existing = get_existing_posts()
    existing_list = "\n".join(f"- {t}" for t in existing)

    topic_instruction = ""
    if topic:
        topic_instruction = f"\nWrite about this specific topic: {topic}\n"
    else:
        topic_queue = get_topic_queue()
        if topic_queue:
            topic_instruction = f"\nChoose one of these suggested topics:\n"
            topic_instruction += "\n".join(f"- {t}" for t in topic_queue[:5])
            topic_instruction += "\n\nOr generate a related topic if none of these feel right.\n"

    prompt = f"""
{BRAND_VOICE}

Generate a complete blog post for the GrowthMax Inc website, optimized for both
search engines (SEO) and answer engines / AI assistants (AEO).

{topic_instruction}

EXISTING POSTS (do not duplicate these topics):
{existing_list}

CONTENT STRUCTURE REQUIREMENTS:
1. The post should be 1000-1500 words
2. Use 4-6 H2 sections (## headers in markdown) — each H2 should be a clear,
   question-like or keyword-rich phrase that someone might search for
3. Use H3 subheadings (###) within sections where it adds clarity
4. Open with a compelling hook paragraph (no heading) that includes the primary keyword
5. The first paragraph should directly answer the core question of the article
   (this helps AI assistants and featured snippets)
6. Use short paragraphs (2-4 sentences max)
7. Include bold text (**keyword phrases**) for key concepts
8. End with a forward-looking conclusion paragraph

SEO/AEO REQUIREMENTS:
9. Pick a category from: {', '.join(CATEGORIES)}
10. Generate 3-5 relevant tags from: ai-strategy, implementation, organizational-change,
    people-culture, adoption, employee-experience, partnership, getting-started, leadership,
    training, agents, productivity, change-management
11. Write a meta description under 160 characters that includes the primary keyword
    and a clear value proposition
12. Write a subtitle (one compelling line)
13. Generate a URL slug (lowercase, hyphens, no special chars, include primary keyword)
14. Write a one-sentence "tldr" that captures the single most important takeaway —
    this will appear as a highlighted callout box at the top of the article
15. Write 2-3 FAQ items (question + answer pairs) that are closely related to the
    article topic. Answers should be 1-2 sentences. These become FAQ schema markup
    which helps the article appear in Google's "People Also Ask" and AI assistant responses.

Respond in this exact JSON format:
{{
    "title": "The Post Title",
    "subtitle": "A compelling subtitle",
    "description": "Meta description under 160 chars with primary keyword",
    "category": "Category Name",
    "tags": ["tag1", "tag2", "tag3"],
    "keywords": "comma, separated, seo, keywords",
    "slug": "the-post-slug",
    "read_time": 7,
    "tldr": "One sentence key takeaway for the callout box",
    "faq": [
        {{"q": "A question someone might ask?", "a": "A direct, concise answer."}},
        {{"q": "Another related question?", "a": "Another direct answer."}}
    ],
    "content": "The full markdown content of the post (H2 headers, H3 subheaders, paragraphs, bold text). Do NOT include the title as an H1 — the layout handles that."
}}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract JSON from response
    text = response.content[0].text
    # Handle possible markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text.strip())

HERO_IMAGE_SPEC_PROMPT = """
You are designing a flat-vector hero illustration for a GrowthMax blog post.
The renderer supports three layouts. Pick whichever best matches the post's
structure and produce a JSON spec.

Post title:    {title}
Post subtitle: {subtitle}
TL;DR:         {tldr}

LAYOUTS

1) "timeline" — 3 to 5 sequential stages in a horizontal flow.
   Use when the post describes a process, roadmap, phases, or steps over time.
   Each step: {{ "icon": "<icon>", "label": "<2-3 words>" }}.

2) "split" — two contrasting options joined by a center "decision" circle.
   Use when the post compares two approaches (A vs B, build vs buy, etc.).
   left/right: {{ "icon": "<icon>", "label": "<1-2 words>", "sub": "<short phrase>" }}.
   center: {{ "label": "<1 word verb>", "sub": "<2-3 words>" }}.

3) "cards" — 3 to 5 cards in a row, each with icon and label.
   Use when the post lists discrete signals, principles, pillars, or categories.
   Each card: {{ "icon": "<icon>", "label": "<2-3 words>", "highlight": <bool> }}.
   Mark at most one card "highlight": true (for the most central idea).

ALLOWED ICONS:
check, person, question, target, clock, book, rocket, gear, chart, cycle, flag, scale, chat

COMMON FIELDS (always include):
- "header": 2-5 uppercase-ish words, the concept label across the top.
- "footer_title": A short benefit-oriented title (3-6 words), NOT the post title verbatim.
- "footer_subtitle": A one-line supporting phrase (<= 10 words).

Also return "alt": a single-sentence alt-text description of the illustration.

Respond with ONLY a JSON object (no prose, no code fences) of the form:
{{
  "layout": "timeline" | "split" | "cards",
  "header": "...",
  "footer_title": "...",
  "footer_subtitle": "...",
  "alt": "...",
  ...layout-specific fields...
}}
"""

def generate_hero_image(client, post_data, out_dir=Path(".")):
    """Ask Claude for a hero-image spec, then render it with the local renderer.

    Returns (image_path, alt_text) or (None, None) if generation fails — callers
    should fall back to the default /growthMAX.PNG.
    """
    prompt = HERO_IMAGE_SPEC_PROMPT.format(
        title=post_data.get("title", ""),
        subtitle=post_data.get("subtitle", ""),
        tldr=post_data.get("tldr", ""),
    )
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        cfg = json.loads(text.strip())
        alt = cfg.pop("alt", "Flat vector hero illustration for the blog post")
        slug = post_data["slug"]
        out_path = out_dir / f"blog-{slug}.jpg"
        hero_image.render(cfg, str(out_path))
        print(f"Generated hero image: {out_path}")
        return out_path, alt
    except Exception as e:
        print(f"Hero image generation failed, falling back to default: {e}", file=sys.stderr)
        return None, None

def save_post(post_data, image_path=None, image_alt=None):
    """Save the generated post as a Jekyll markdown file."""
    today = datetime.now().strftime("%Y-%m-%d")
    slug = post_data["slug"]
    filename = POSTS_DIR / f"{today}-{slug}.md"

    front_matter = {
        "title": post_data["title"],
        "subtitle": post_data["subtitle"],
        "description": post_data["description"],
        "category": post_data["category"],
        "read_time": post_data["read_time"],
        "tags": post_data["tags"],
        "keywords": post_data["keywords"],
        "image": f"/{image_path.name}" if image_path else "/growthMAX.PNG",
        "slug": slug,
    }
    if image_alt:
        front_matter["image_alt"] = image_alt

    # Add optional SEO/AEO fields
    if post_data.get("tldr"):
        front_matter["tldr"] = post_data["tldr"]
    if post_data.get("faq"):
        front_matter["faq"] = post_data["faq"]

    content = f"---\n{yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)}---\n\n{post_data['content']}\n"

    with open(filename, "w") as f:
        f.write(content)

    print(f"Generated: {filename}")
    return filename

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Check for manual topic input from workflow_dispatch
    topic = os.environ.get("TOPIC_INPUT", "").strip() or None

    POSTS_DIR.mkdir(exist_ok=True)

    post_data = generate_post(client, topic=topic)
    image_path, image_alt = generate_hero_image(client, post_data, out_dir=Path("."))
    save_post(post_data, image_path=image_path, image_alt=image_alt)

if __name__ == "__main__":
    main()
