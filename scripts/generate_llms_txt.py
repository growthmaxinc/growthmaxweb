#!/usr/bin/env python3
"""
Generate llms.txt from the live contents of _posts/.

Why this exists
---------------
llms.txt is the machine-readable map answer engines read first, so it is
core AEO surface area. It was hand-maintained, and by 2026-08-31 it had
drifted to listing 10 of 43 posts, with nothing published after
2026-06-01 represented. Every high-intent enterprise-buyer post was
invisible to LLM crawlers.

A manual step inside an automated pipeline will always drift. This makes
the file a build artifact instead: the static sections stay hand-written
here, and the post index is derived from front matter on every run.

Usage:
    python scripts/generate_llms_txt.py            # write llms.txt
    python scripts/generate_llms_txt.py --check    # exit 1 if stale
"""

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
OUT_PATH = REPO_ROOT / "llms.txt"
SITE_URL = "https://growthmaxinc.com"

# How many posts to list. llms.txt is a map, not an archive; the full set
# is always reachable via the blog index and sitemap linked at the bottom.
MAX_POSTS = 30

# Static sections. Edit these by hand; the post index below is generated.
HEADER = """# GrowthMax Inc

> AI consultancy that builds custom AI agents and runs AI-adoption training and bootcamps. Core thesis: **Partnership, Not Replacement**, meaning AI augments human expertise and judgment rather than replacing people. We help organizations adopt agentic AI in a way that is outcomes-focused, people-first, and honest about what AI can and can't do.

Contact: hi@growthmaxinc.com · https://www.linkedin.com/company/growthmaxinc/

## Core
- [Partnership, Not Replacement]({site}/partnership.html): Our central thesis, why AI should augment people rather than replace them.
- [AI Agents for Business]({site}/ai-agents-for-business.html): What custom AI agents are and how we build them.
- [FAQ]({site}/resources/faq.html): Common questions about AI adoption, agents, training, and working with GrowthMax.
- [AI Adoption Playbook]({site}/resources/ai-adoption-playbook.html): Practical, step-by-step guidance for adopting AI.

## Solutions
- [Agent Development]({site}/solutions/agent-development.html): Custom AI agents built around your workflows.
- [Bootcamp]({site}/solutions/bootcamp.html): Hands-on AI training to upskill your team.
- [Foundations]({site}/solutions/foundations.html): Getting started with AI on solid footing.
"""

FOOTER = """
## More
- [Blog (all posts)]({site}/resources/blog.html): Essays on AI adoption, change management, ROI, and people-first strategy.
- [Sitemap]({site}/sitemap.xml)
"""

# CLAUDE.md forbids em dashes and en dashes in site copy. Post front matter
# is LLM-generated and regularly contains them, so normalize on the way out
# rather than shipping a violation into llms.txt.
DASH_RE = re.compile(r"\s*[—–]\s*")


def clean(text):
    """Normalize dashes to commas and collapse whitespace."""
    if not text:
        return ""
    text = DASH_RE.sub(", ", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    # A trailing ", " artifact from a dash at the end of a clause.
    return text.rstrip(",").strip()


# Line-anchored, matching _parse_post() in seo_aeo_audit.py. A naive
# text.split("---") breaks on posts whose FAQ answers contain a literal
# "---", which silently truncates the front matter to its first few keys.
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def read_front_matter(path):
    """Parse the YAML front matter block from a Jekyll post."""
    m = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or None
    except yaml.YAMLError as e:
        print("  warning: could not parse front matter in %s: %s" % (path.name, e),
              file=sys.stderr)
        return None


def summarize(fm):
    """One-line summary for the index. Prefer subtitle, fall back to description."""
    for field in ("subtitle", "tldr", "description"):
        value = clean(fm.get(field))
        if value:
            # Keep entries scannable; one clause is enough for a map.
            if len(value) > 155:
                value = value[:152].rsplit(" ", 1)[0] + "..."
            return value
    return ""


def collect_posts():
    """All posts, newest first, as (title, url, summary)."""
    rows = []
    for path in POSTS_DIR.glob("*.md"):
        fm = read_front_matter(path)
        if not fm:
            continue
        slug = fm.get("slug") or path.stem[11:]
        title = clean(fm.get("title"))
        if not title or not slug:
            print("  warning: skipping %s (missing title or slug)" % path.name,
                  file=sys.stderr)
            continue
        # Filename date prefix is the sort key; it is the canonical publish date.
        rows.append((path.stem[:10], title, "%s/blog/%s/" % (SITE_URL, slug),
                     summarize(fm)))
    rows.sort(key=lambda r: r[0], reverse=True)
    return rows


def build():
    posts = collect_posts()
    lines = [HEADER.format(site=SITE_URL), "## Key Writing"]
    for _, title, url, summary in posts[:MAX_POSTS]:
        lines.append("- [%s](%s)%s" % (title, url, (": " + summary) if summary else ""))
    lines.append(FOOTER.format(site=SITE_URL).rstrip())
    return "\n".join(lines) + "\n", len(posts)


def main():
    content, total = build()

    if "--check" in sys.argv:
        current = OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else ""
        if current != content:
            print("llms.txt is stale. Run: python scripts/generate_llms_txt.py",
                  file=sys.stderr)
            return 1
        print("llms.txt is up to date (%d posts indexed)." % min(total, MAX_POSTS))
        return 0

    OUT_PATH.write_text(content, encoding="utf-8")
    print("Wrote llms.txt: %d of %d posts indexed (newest first)."
          % (min(total, MAX_POSTS), total))
    if "—" in content or "–" in content:
        print("  warning: output still contains a long dash", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
