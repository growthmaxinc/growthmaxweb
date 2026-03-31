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

Generate a complete blog post for the GrowthMax Inc website.
{topic_instruction}

EXISTING POSTS (do not duplicate these topics):
{existing_list}

REQUIREMENTS:
1. The post should be 800-1200 words
2. Use 4-6 H2 sections (## headers in markdown)
3. Open with a compelling hook paragraph (no heading)
4. End with a forward-looking conclusion
5. Pick a category from: {', '.join(CATEGORIES)}
6. Generate 3-5 relevant tags from these options: ai-strategy, implementation, organizational-change,
   people-culture, adoption, employee-experience, partnership, getting-started, leadership,
   training, agents, productivity, change-management
7. Write a meta description under 160 characters
8. Write a subtitle (one line)
9. Generate a URL slug (lowercase, hyphens, no special chars)

Respond in this exact JSON format:
{{
    "title": "The Post Title",
    "subtitle": "A compelling subtitle",
    "description": "Meta description under 160 chars",
    "category": "Category Name",
    "tags": ["tag1", "tag2", "tag3"],
    "keywords": "comma, separated, seo, keywords",
    "slug": "the-post-slug",
    "read_time": 7,
    "content": "The full markdown content of the post (H2 headers, paragraphs, bold text). Do NOT include the title as an H1 — the layout handles that."
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

def save_post(post_data):
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
        "image": "/growthMAX.PNG",
        "slug": slug,
    }

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
    save_post(post_data)

if __name__ == "__main__":
    main()
