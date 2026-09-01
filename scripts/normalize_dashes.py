#!/usr/bin/env python3
"""
Enforce the CLAUDE.md punctuation rule: no em dashes, no en dashes.

    "No em dashes and no en dashes. Use a comma in their place where
     appropriate, or restructure the sentence."

Why this exists
---------------
Every one of the 43 posts violated the rule (647 em dashes, 62 en dashes),
plus ~155 more across the static HTML pages. The cause was not model
misbehaviour: BRAND_VOICE in generate-post.py literally instructed the
model to "use em dashes sparingly for emphasis", directly contradicting
the house rule. The prompt is fixed; this script cleans the backlog and
runs as a post-generation net so nothing slips through again.

Replacement rules, applied in order:
  1. HTML entities (&mdash; &ndash;) are decoded so they get treated the same.
  2. Numeric and currency ranges  (60-80%, $40k-$250k)  ->  "60 to 80%".
  3. A dash directly after existing punctuation  (", -")  ->  drop the dash.
  4. A spaced dash before a clear sentence opener (This, It, They, ...)
     ->  a period, because a comma there would make a comma splice.
  5. Any remaining dash  ->  a comma.
  6. Tidy up doubled commas and stray whitespace.

Fenced code blocks, inline code, and URLs are left untouched.

Usage:
    python scripts/normalize_dashes.py                # rewrite files in place
    python scripts/normalize_dashes.py --check        # exit 1 if any remain
    python scripts/normalize_dashes.py --dry-run      # preview replacements
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DASH = "[—–]"

# Pages audited by seo_aeo_audit.py, plus the standalone brand page.
HTML_TARGETS = [
    "index.html", "ai-agents-for-business.html", "partnership.html", "404.html",
    "brand.html",
    "resources/ai-adoption-playbook.html", "resources/blog.html",
    "resources/faq.html",
    "solutions/index.html", "solutions/agent-development.html",
    "solutions/foundations.html", "solutions/bootcamp.html",
    "about/claude-partnership.html",
]

# Words that almost always begin a new independent clause. A comma before
# these produces a splice, so use a period and keep the capital.
SENTENCE_OPENERS = (
    "This", "That", "These", "Those", "It", "They", "You", "We", "He", "She",
    "There", "Here", "Your", "Our", "Their", "Its", "His", "Her", "I",
)

# Segments we must not rewrite: fenced blocks, inline code, URLs, HTML tags.
PROTECTED_RE = re.compile(
    r"```.*?```"                       # fenced code
    r"|`[^`\n]*`"                      # inline code
    r"|https?://[^\s)<>\]]+"            # bare URLs; must stop at the ")" that
                                       # closes a markdown link, or the dash
                                       # immediately after it gets swallowed
    r"|<(?!!--)[^>\n]+>",              # HTML tags, but NOT comments: a dash in
                                       # <!-- ... --> is still a dash we own
    re.DOTALL,
)


def _apply_rules(text):
    # 1. Decode entities so the rules below see real characters.
    text = text.replace("&mdash;", "—").replace("&ndash;", "–")
    text = text.replace("&#8212;", "—").replace("&#8211;", "–")

    # 2. Ranges: a number/unit on the left, a number or currency on the right.
    text = re.sub(
        r"(\d[\d,.]*\s*(?:%|k|K|m|M|bn|b|B)?)\s*" + DASH + r"\s*(\$?\d)",
        r"\1 to \2", text)

    # 3. Dash immediately following punctuation that already does the job.
    text = re.sub(r"([,;:])\s*" + DASH + r"\s*", r"\1 ", text)

    # 4. Spaced dash before a clear sentence opener -> full stop.
    openers = "|".join(SENTENCE_OPENERS)
    text = re.sub(r"\s*" + DASH + r"\s+(?=(?:" + openers + r")\b)", ". ", text)

    # 5. Everything else becomes a comma.
    text = re.sub(r"\s*" + DASH + r"\s*", ", ", text)

    # 6. Tidy: doubled commas, space before comma, comma before closing quote,
    #    and a comma left dangling at the end of a line.
    text = re.sub(r",\s*,+", ",", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",(\s*[.!?])", r"\1", text)
    text = re.sub(r",\s*\"$", '"', text, flags=re.MULTILINE)
    # Collapse runs of spaces left mid-line by a replacement, but NEVER touch
    # leading indentation: these files carry YAML front matter, where eating
    # two spaces turns a nested faq list into a parse error.
    text = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", text)
    return text


def normalize(text):
    """Apply the rules, skipping protected spans."""
    out, cursor = [], 0
    for m in PROTECTED_RE.finditer(text):
        out.append(_apply_rules(text[cursor:m.start()]))
        out.append(m.group(0))
        cursor = m.end()
    out.append(_apply_rules(text[cursor:]))
    return "".join(out)


def targets():
    yield from sorted((REPO_ROOT / "_posts").glob("*.md"))
    for rel in HTML_TARGETS:
        path = REPO_ROOT / rel
        if path.exists():
            yield path


def main():
    check = "--check" in sys.argv
    dry = "--dry-run" in sys.argv

    changed, remaining, total = [], 0, 0
    for path in targets():
        original = path.read_text(encoding="utf-8")
        count = len(re.findall(DASH, original)) + original.count("&mdash;") \
            + original.count("&ndash;")
        if not count:
            continue
        total += count
        updated = normalize(original)
        left = len(re.findall(DASH, updated))
        remaining += left
        rel = path.relative_to(REPO_ROOT)

        if check:
            print("  %s: %d dash(es)" % (rel, count))
            continue
        if dry:
            print("  %s: %d -> %d" % (rel, count, left))
            continue
        path.write_text(updated, encoding="utf-8")
        changed.append((rel, count, left))

    if check:
        if total:
            print("\nFAIL: %d dash(es) across the site violate the CLAUDE.md "
                  "punctuation rule.\nFix with: python scripts/normalize_dashes.py"
                  % total, file=sys.stderr)
            return 1
        print("No em dashes or en dashes found. Punctuation rule satisfied.")
        return 0

    if dry:
        print("\n[dry run] %d dash(es) would be replaced, %d would remain."
              % (total, remaining))
        return 0

    for rel, count, left in changed:
        print("  %-72s %3d replaced%s" % (rel, count - left,
              ("  (%d LEFT)" % left) if left else ""))
    print("\nNormalized %d file(s): %d dash(es) replaced, %d remaining."
          % (len(changed), total - remaining, remaining))
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
