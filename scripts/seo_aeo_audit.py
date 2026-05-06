"""
SEO + AEO compliance audit for growthmaxinc.com.

This script is the machine-checked enforcement of `SEO-STANDARDS.md`.
Run it standalone (CLI) or import its functions from generate-post.py
for in-pipeline self-validation.

Usage:
    python scripts/seo_aeo_audit.py              # audit whole repo
    python scripts/seo_aeo_audit.py _posts/foo.md  # audit one post

Exit codes:
    0 — all errors clean (warnings allowed)
    1 — at least one error found

Categories:
    ERRORS (fail CI):    word counts, H2 hygiene, meta desc length,
                         required front matter, broken internal links,
                         invalid FAQ JSON-LD, H1 in post body
    WARNINGS (informational): TLDR length, < 3 question H2s, < 2 sibling links
"""

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

# Paths to Jekyll-rendered HTML pages we audit (everything else is excluded
# in _config.yml or rendered through layouts).
PAGES = [
    REPO_ROOT / "index.html",
    REPO_ROOT / "ai-agents-for-business.html",
    REPO_ROOT / "partnership.html",
    REPO_ROOT / "404.html",
    REPO_ROOT / "resources" / "ai-adoption-playbook.html",
    REPO_ROOT / "resources" / "blog.html",
    REPO_ROOT / "resources" / "faq.html",
    REPO_ROOT / "solutions" / "agent-development.html",
    REPO_ROOT / "solutions" / "foundations.html",
    REPO_ROOT / "solutions" / "bootcamp.html",
]

# Required post front-matter fields (per SEO-STANDARDS.md §5).
REQUIRED_POST_FIELDS = {
    "title", "subtitle", "description", "category", "read_time", "tags",
    "keywords", "slug", "image", "image_alt", "tldr", "faq",
    "pillar", "pillar_page", "primary_keyword",
}

# Pillar/page required fields (per §6).
REQUIRED_PAGE_FIELDS = {"title", "description", "permalink"}

# AEO answer length range (per §1).
AEO_MIN, AEO_MAX = 40, 60

# Meta description max (per §3).
META_DESC_MAX = 160

# TLDR max (per §4).
TLDR_MAX = 220

# H2s exempt from AEO check (CTA-style headings — they ask a question
# rhetorically before pushing the reader to a button or contact form).
CTA_H2_PATTERNS = [
    r"ready to",
    r"let'?s talk",
    r"get started",
    r"sign up",
    r"still have questions",
    r"have questions\??$",
    r"how ready is your",
    r"want to (learn|talk|explore)",
    r"need (help|support)",
]


# --- Utilities ---

class Findings:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append((str(where), msg))

    def warn(self, where, msg):
        self.warnings.append((str(where), msg))

    def report(self) -> int:
        """Print findings and return exit code (0=clean, 1=errors)."""
        if not self.errors and not self.warnings:
            print("\033[92m✓ SEO/AEO audit: all checks passed.\033[0m")
            return 0

        if self.warnings:
            print(f"\n\033[93mWARNINGS ({len(self.warnings)}):\033[0m")
            for where, msg in self.warnings:
                print(f"  {where}: {msg}")

        if self.errors:
            print(f"\n\033[91mERRORS ({len(self.errors)}):\033[0m")
            for where, msg in self.errors:
                print(f"  {where}: {msg}")
            print(f"\n\033[91mAudit FAILED — {len(self.errors)} error(s) must be fixed before merge.\033[0m")
            return 1

        print(f"\n\033[92m✓ SEO/AEO audit passed with {len(self.warnings)} warning(s).\033[0m")
        return 0


def _is_cta_h2(question_text: str) -> bool:
    q = question_text.lower()
    return any(re.search(p, q) for p in CTA_H2_PATTERNS)


def _strip_md(text: str) -> str:
    """Strip markdown formatting for accurate word counting."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def _first_para_after(body: str) -> str:
    """Return the first paragraph after the cursor (split on blank line or next heading)."""
    para = re.split(r"\n\s*\n|\n## |\n### ", body, maxsplit=1)[0].strip()
    return para


def _parse_post(path: Path):
    """Return (front_matter_dict, body_str) from a post markdown file."""
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"_yaml_error": str(e)}, m.group(2)
    return fm, m.group(2)


def _parse_page(path: Path):
    """Return (front_matter_dict, body_str) from a Jekyll HTML page."""
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        # Static HTML with no Jekyll front matter (e.g., 404.html may not have it).
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"_yaml_error": str(e)}, m.group(2)
    return fm, m.group(2)


# --- Per-post checks ---

def check_post(path: Path, findings: Findings):
    fm, body = _parse_post(path)
    name = path.relative_to(REPO_ROOT)

    if fm is None:
        findings.err(name, "no front matter found")
        return
    if "_yaml_error" in fm:
        findings.err(name, f"front matter YAML error: {fm['_yaml_error']}")
        return

    # 5. Required fields
    missing = REQUIRED_POST_FIELDS - set(fm.keys())
    for field in sorted(missing):
        findings.err(name, f"missing required front-matter field: {field}")

    # 3. Meta description length
    desc = fm.get("description", "")
    if isinstance(desc, str) and len(desc) > META_DESC_MAX:
        findings.err(name, f"description {len(desc)} chars (max {META_DESC_MAX})")

    # 4. TLDR length (warning, not error per §4 vs soft rules)
    tldr = fm.get("tldr", "")
    if isinstance(tldr, str) and len(tldr) > TLDR_MAX:
        findings.warn(name, f"tldr {len(tldr)} chars (recommended max {TLDR_MAX})")

    # 7. No H1 in body
    if re.search(r"^#\s+\S", body, re.MULTILINE):
        h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        findings.err(name, f"H1 found in body ('{h1_match.group(1)[:50]}'); layout already adds H1 from title")

    # 2. H2 hygiene — no trailing periods on H2s (questions end with ?)
    for m in re.finditer(r"^## ([^?\n]+\.)\s*$", body, re.MULTILINE):
        findings.err(name, f"H2 ends with period: '{m.group(1)}'")

    # 1. AEO word count on every question H2
    question_h2_count = 0
    for m in re.finditer(r"^## (.+\?)\s*$", body, re.MULTILINE):
        question = m.group(1)
        if _is_cta_h2(question):
            continue
        question_h2_count += 1
        para = _strip_md(_first_para_after(body[m.end():]))
        words = len(para.split())
        if not (AEO_MIN <= words <= AEO_MAX):
            findings.err(
                name,
                f"AEO answer to '{question[:55]}…' is {words} words (must be {AEO_MIN}-{AEO_MAX})",
            )

    # Soft rule: ≥ 3 question H2s per spoke post
    if question_h2_count < 3:
        findings.warn(name, f"only {question_h2_count} question-format H2s (recommend ≥3)")

    # 9. FAQ schema validity (faq is YAML, but it ends up serialized as JSON-LD via the layout)
    faq = fm.get("faq")
    if faq is not None:
        if not isinstance(faq, list):
            findings.err(name, "faq front-matter field must be a list of {q, a} dicts")
        else:
            for i, item in enumerate(faq):
                if not isinstance(item, dict) or "q" not in item or "a" not in item:
                    findings.err(name, f"faq item {i} missing 'q' or 'a' field")

    # 8. Internal link integrity (collected, checked across all posts at end)
    return _collect_internal_links(body, name)


def _collect_internal_links(body, name):
    """Return list of (source_name, target_url) for every internal link."""
    out = []
    for m in re.finditer(r"\[[^\]]+\]\((/[^\s)]*)\)", body):
        out.append((str(name), m.group(1)))
    return out


# --- Per-page (HTML) checks ---

def check_page(path: Path, findings: Findings):
    if not path.exists():
        findings.warn(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path,
                      "expected page file not found (skipped)")
        return []
    fm, body = _parse_page(path)
    name = path.relative_to(REPO_ROOT)

    if fm is None:
        # Static HTML without Jekyll front matter — only run a subset of checks.
        return _check_html_links(body, name)

    if "_yaml_error" in fm:
        findings.err(name, f"front matter YAML error: {fm['_yaml_error']}")
        return []

    # 6. Required fields
    missing = REQUIRED_PAGE_FIELDS - set(fm.keys())
    for field in sorted(missing):
        findings.err(name, f"missing required front-matter field: {field}")

    # 3. Meta description length
    desc = fm.get("description", "")
    if isinstance(desc, str) and len(desc) > META_DESC_MAX:
        findings.err(name, f"description {len(desc)} chars (max {META_DESC_MAX})")

    # 1. AEO word count for question H2s in HTML body
    # Strip JSON-LD blocks first so schema text doesn't get counted.
    body_clean = re.sub(
        r"<script[^>]*application/ld\+json[^>]*>.*?</script>",
        "",
        body,
        flags=re.DOTALL,
    )
    for m in re.finditer(r"<h2[^>]*>([^<]*\?)\s*</h2>", body_clean):
        question = m.group(1).strip()
        if _is_cta_h2(question):
            continue
        # First <p>...</p> after this h2
        pm = re.search(r"<p[^>]*>(.+?)</p>", body_clean[m.end():], re.DOTALL)
        if not pm:
            findings.err(name, f"question H2 '{question[:55]}…' has no <p> answer")
            continue
        inner = re.sub(r"<[^>]+>", "", pm.group(1)).strip()
        inner = re.sub(r"\s+", " ", inner)
        words = len(inner.split())
        if not (AEO_MIN <= words <= AEO_MAX):
            findings.err(
                name,
                f"AEO answer to '{question[:55]}…' is {words} words (must be {AEO_MIN}-{AEO_MAX})",
            )

    # 9. FAQ JSON-LD validity
    for m in re.finditer(
        r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',
        body,
        re.DOTALL,
    ):
        raw = m.group(1).strip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            findings.err(name, f"invalid JSON-LD: {e}")

    # 8. Collect internal links from HTML body
    return _check_html_links(body, name)


def _check_html_links(body, name):
    """Return list of (source_name, target_url) from HTML href attributes."""
    out = []
    for m in re.finditer(r'href="(/[^"]*)"', body):
        out.append((str(name), m.group(1)))
    return out


# --- Cross-file checks ---

def known_urls():
    """Build set of all URLs the site exposes."""
    urls = {"/", "/feed.xml", "/sitemap.xml", "/robots.txt"}

    # Posts → /blog/{slug}/ (per _config.yml permalink)
    for p in POSTS_DIR.glob("*.md"):
        # slug is in front matter OR derivable from filename
        text = p.read_text()
        m = re.search(r'^slug:\s*([^\s\n"]+)', text, re.MULTILINE)
        if m:
            urls.add(f"/blog/{m.group(1).strip()}/")
        # Also accept the date-prefixed filename's slug
        fm_match = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md", p.name)
        if fm_match:
            urls.add(f"/blog/{fm_match.group(1)}/")

    # Pages with explicit permalinks
    for page_path in PAGES:
        if not page_path.exists():
            continue
        text = page_path.read_text()
        m = re.search(r'^permalink:\s*([^\s\n"]+)', text, re.MULTILINE)
        if m:
            urls.add(m.group(1).strip())
        else:
            # Fallback: derive from path relative to repo root
            rel = "/" + str(page_path.relative_to(REPO_ROOT))
            urls.add(rel)

    return urls


def check_internal_links(all_links, findings: Findings):
    """Check every internal link resolves to a known URL."""
    valid = known_urls()
    for source, link in all_links:
        # Normalize: strip query strings and fragments
        target = link.split("#")[0].split("?")[0]
        if not target or target == "/":
            continue
        # Skip non-page assets (images, scripts, etc.)
        if re.search(r"\.(jpg|jpeg|png|svg|webp|gif|css|js|xml|pdf|ico|PNG)$", target):
            continue
        if target not in valid:
            findings.err(source, f"broken internal link: {target}")


# --- Public API for in-pipeline use ---

def validate_post_data(post_data: dict) -> tuple[bool, list[str]]:
    """Validate a generated post (dict from generate-post.py) against AEO rules.

    Returns (passed, error_messages). Used by generate-post.py to decide
    whether to retry generation.
    """
    errors = []
    content = post_data.get("content", "")

    # AEO word count on every question H2
    for m in re.finditer(r"^## (.+\?)\s*$", content, re.MULTILINE):
        question = m.group(1)
        if _is_cta_h2(question):
            continue
        para = _strip_md(_first_para_after(content[m.end():]))
        words = len(para.split())
        if not (AEO_MIN <= words <= AEO_MAX):
            errors.append(
                f"Question H2 '{question[:60]}' has {words}-word answer (must be {AEO_MIN}-{AEO_MAX})"
            )

    # Question H2 count
    qh2_count = sum(
        1 for m in re.finditer(r"^## (.+\?)\s*$", content, re.MULTILINE)
        if not _is_cta_h2(m.group(1))
    )
    if qh2_count < 3:
        errors.append(f"Only {qh2_count} question-format H2s (need ≥3)")

    # H2 hygiene
    for m in re.finditer(r"^## ([^?\n]+\.)\s*$", content, re.MULTILINE):
        errors.append(f"H2 ends with period: '{m.group(1)}'")

    # No H1 in body
    if re.search(r"^#\s+\S", content, re.MULTILINE):
        errors.append("H1 found in body — layout adds H1 from title; remove it")

    # Meta description length
    desc = post_data.get("description", "")
    if len(desc) > META_DESC_MAX:
        errors.append(f"Meta description {len(desc)} chars (max {META_DESC_MAX})")

    # TLDR length (warning, not error in pipeline either)
    # Skipped here — only enforced as a warning by the standalone audit.

    # Required generated fields
    for field in ("title", "subtitle", "description", "slug", "tldr", "faq",
                  "pillar", "pillar_page", "primary_keyword"):
        if field not in post_data:
            errors.append(f"missing required field: {field}")

    # FAQ schema
    faq = post_data.get("faq")
    if faq is not None:
        if not isinstance(faq, list):
            errors.append("faq must be a list of {q, a} dicts")
        else:
            for i, item in enumerate(faq):
                if not isinstance(item, dict) or "q" not in item or "a" not in item:
                    errors.append(f"faq item {i} missing 'q' or 'a' field")

    return (len(errors) == 0, errors)


# --- Main ---

def main():
    findings = Findings()
    all_links = []

    # Allow scoping to a single file: `python seo_aeo_audit.py _posts/foo.md`
    args = sys.argv[1:]
    if args:
        targets = [Path(a) if Path(a).is_absolute() else REPO_ROOT / a for a in args]
        for path in targets:
            if path.suffix == ".md" and path.parent.name == "_posts":
                links = check_post(path, findings) or []
                all_links.extend(links)
            elif path.suffix == ".html":
                links = check_page(path, findings) or []
                all_links.extend(links)
            else:
                findings.warn(path, "unsupported file type for audit")
    else:
        # Audit the whole site
        for post_path in sorted(POSTS_DIR.glob("*.md")):
            links = check_post(post_path, findings) or []
            all_links.extend(links)
        for page_path in PAGES:
            if page_path.exists():
                links = check_page(page_path, findings) or []
                all_links.extend(links)

    # Cross-file: internal link integrity
    check_internal_links(all_links, findings)

    # Summary
    print(f"\nAudit summary: {len(findings.errors)} errors, {len(findings.warnings)} warnings.")
    sys.exit(findings.report())


if __name__ == "__main__":
    main()
