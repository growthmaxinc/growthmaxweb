#!/usr/bin/env python3
"""
Generate a flat-vector hero image for a GrowthMax blog post.

Palette and style match the existing /blog-*.jpg hero images:
- Light sky background, thin horizontal guide lines
- Middle band of cards/blocks illustrating the post concept
- Dark teal footer strip with the title + subtitle

Usage:
    python generate-hero-image.py <out_path> <layout> [options...]

Layouts:
    timeline    — header_label, 4-5 steps (labels), footer_title, footer_subtitle
    split       — header_label, (left_label, left_sub, left_icon), center_label, center_sub,
                  (right_label, right_sub, right_icon), footer_title, footer_subtitle
    cards       — header_label, up to 5 card labels, footer_title, footer_subtitle (like the
                  5-signs-of-readiness illustration)

Icons supported: check, person, question, target, clock, book, rocket, gear, chart,
                 cycle, flag, scale, chat.
"""
import argparse
import json
import sys
from PIL import Image, ImageDraw, ImageFont

# Brand palette (mirrors the cyan/sky/blue Tailwind palette used across the site)
BG_TOP = (240, 249, 255)      # sky-50
BG_BOT = (236, 254, 255)      # cyan-50
GRID_LINE = (186, 230, 253, 70)  # sky-200 @ ~27%
CARD_BG = (255, 255, 255)
CARD_BORDER = (103, 232, 249)    # cyan-300
TEAL = (14, 116, 144)            # cyan-700
TEAL_DARK = (21, 94, 117)        # cyan-800
TEAL_VERY_DARK = (22, 78, 99)    # cyan-900
BLUE_DEEP = (30, 64, 175)        # blue-800
WHITE = (255, 255, 255)
SUBTEXT = (165, 243, 252)        # cyan-200 (for footer subtitle)
NUMBER_GRAY = (100, 116, 139)    # slate-500

FONT_DIR = "/usr/share/fonts/truetype/liberation"
# Liberation Sans is a metrically-compatible Helvetica/Arial substitute.
# Inter isn't on the image runner, and the hero panel text is stylised enough
# that the difference isn't visible at these sizes.
_FONT_MAP = {
    "Light":    "LiberationSans-Regular.ttf",
    "Regular":  "LiberationSans-Regular.ttf",
    "Medium":   "LiberationSans-Bold.ttf",
    "SemiBold": "LiberationSans-Bold.ttf",
    "Bold":     "LiberationSans-Bold.ttf",
}
def F(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{_FONT_MAP[name]}", size)

# -----------------------------------------------------------------------------
# shared helpers
# -----------------------------------------------------------------------------
W, H = 1200, 630

def make_canvas():
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img, "RGBA")
    # vertical gradient
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    # faint horizontal grid lines
    for y in (90, 180, 360, 450, 520):
        d.line([(0, y), (W, y)], fill=GRID_LINE, width=1)
    return img, d

def text_center(d, xy, text, font, fill):
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x, y = xy
    d.text((x - tw / 2, y - th / 2 - bbox[1]), text, font=font, fill=fill)

def draw_header(d, label):
    # wide-tracked uppercase label at top
    spaced = "   ".join(label.upper())
    text_center(d, (W / 2, 55), spaced, F("Medium", 20), TEAL_DARK)

def draw_footer(d, title, subtitle):
    # dark strip 535..630
    d.rectangle([(0, 535), (W, H)], fill=TEAL_VERY_DARK)
    text_center(d, (W / 2, 572), title, F("Light", 36), WHITE)
    text_center(d, (W / 2, 608), subtitle, F("Light", 18), SUBTEXT)

# -----------------------------------------------------------------------------
# icon set — drawn as simple flat shapes inside a circle
# -----------------------------------------------------------------------------
def _circle(d, cx, cy, r, fill):
    d.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=fill)

def icon_check(d, cx, cy, r, fg=WHITE):
    _circle(d, cx, cy, r, TEAL)
    # checkmark polyline
    pts = [(cx - r * 0.4, cy), (cx - r * 0.1, cy + r * 0.3), (cx + r * 0.45, cy - r * 0.3)]
    d.line(pts, fill=fg, width=max(4, int(r * 0.18)), joint="curve")

def icon_person(d, cx, cy, r, fg=TEAL):
    # head
    _circle(d, cx, cy - r * 0.25, r * 0.35, fg)
    # body (rounded cap)
    d.rounded_rectangle(
        [(cx - r * 0.55, cy + r * 0.05), (cx + r * 0.55, cy + r * 0.75)],
        radius=int(r * 0.3),
        fill=fg,
    )
    # tiny star above head
    star_cx, star_cy = cx + r * 0.35, cy - r * 0.7
    s = r * 0.18
    d.polygon(
        [
            (star_cx, star_cy - s),
            (star_cx + s * 0.3, star_cy - s * 0.3),
            (star_cx + s, star_cy - s * 0.3),
            (star_cx + s * 0.45, star_cy + s * 0.15),
            (star_cx + s * 0.7, star_cy + s),
            (star_cx, star_cy + s * 0.5),
            (star_cx - s * 0.7, star_cy + s),
            (star_cx - s * 0.45, star_cy + s * 0.15),
            (star_cx - s, star_cy - s * 0.3),
            (star_cx - s * 0.3, star_cy - s * 0.3),
        ],
        fill=BLUE_DEEP,
    )

def icon_question(d, cx, cy, r, fg=WHITE):
    _circle(d, cx, cy, r, WHITE)
    d.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=TEAL, width=max(3, int(r * 0.08)))
    # question mark (rendered as text for clean letterform)
    text_center(d, (cx, cy), "?", F("SemiBold", int(r * 1.3)), TEAL)

def icon_target(d, cx, cy, r, fg=TEAL):
    d.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=fg, width=max(3, int(r * 0.12)))
    d.ellipse(
        [(cx - r * 0.55, cy - r * 0.55), (cx + r * 0.55, cy + r * 0.55)],
        outline=fg,
        width=max(3, int(r * 0.12)),
    )
    _circle(d, cx, cy, r * 0.18, fg)

def icon_clock(d, cx, cy, r, fg=TEAL):
    d.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=fg, width=max(3, int(r * 0.1)))
    # hands
    d.line([(cx, cy), (cx, cy - r * 0.6)], fill=fg, width=max(3, int(r * 0.1)))
    d.line([(cx, cy), (cx + r * 0.45, cy + r * 0.1)], fill=fg, width=max(3, int(r * 0.1)))
    _circle(d, cx, cy, r * 0.08, fg)

def icon_book(d, cx, cy, r, fg=WHITE):
    # open book on teal card: two pages
    w = r * 1.3
    h = r * 0.9
    d.rectangle([(cx - w, cy - h / 2), (cx, cy + h / 2)], fill=fg, outline=fg)
    d.rectangle([(cx, cy - h / 2), (cx + w, cy + h / 2)], fill=fg, outline=fg)
    # page lines (use background color)
    bg = TEAL
    for i in range(3):
        yy = cy - h / 3 + i * (h / 4)
        d.line([(cx - w * 0.85, yy), (cx - w * 0.15, yy)], fill=bg, width=2)
        d.line([(cx + w * 0.15, yy), (cx + w * 0.85, yy)], fill=bg, width=2)

def icon_rocket(d, cx, cy, r, fg=WHITE):
    # simple rocket: triangle body + fins + flame
    body_top = (cx, cy - r * 0.8)
    body_bl = (cx - r * 0.35, cy + r * 0.3)
    body_br = (cx + r * 0.35, cy + r * 0.3)
    d.polygon([body_top, body_bl, body_br], fill=fg)
    # fins
    d.polygon([(cx - r * 0.35, cy + r * 0.3), (cx - r * 0.7, cy + r * 0.5), (cx - r * 0.35, cy + r * 0.5)], fill=fg)
    d.polygon([(cx + r * 0.35, cy + r * 0.3), (cx + r * 0.7, cy + r * 0.5), (cx + r * 0.35, cy + r * 0.5)], fill=fg)
    # flame
    d.polygon(
        [(cx - r * 0.2, cy + r * 0.5), (cx, cy + r * 0.95), (cx + r * 0.2, cy + r * 0.5)],
        fill=BLUE_DEEP,
    )
    # porthole
    _circle(d, cx, cy - r * 0.15, r * 0.12, TEAL)

def icon_gear(d, cx, cy, r, fg=WHITE):
    import math
    teeth = 8
    inner = r * 0.62
    outer = r * 0.95
    pts = []
    for i in range(teeth * 2):
        angle = math.pi / teeth * i
        rad = outer if i % 2 == 0 else inner
        pts.append((cx + rad * math.cos(angle), cy + rad * math.sin(angle)))
    d.polygon(pts, fill=fg)
    _circle(d, cx, cy, r * 0.3, TEAL)

def icon_chart(d, cx, cy, r, fg=WHITE):
    # bars of increasing height
    bar_w = r * 0.25
    gap = r * 0.1
    base_y = cy + r * 0.55
    heights = [0.4, 0.65, 0.85, 1.05]
    start = cx - (len(heights) * (bar_w + gap) - gap) / 2
    for i, h in enumerate(heights):
        x0 = start + i * (bar_w + gap)
        y0 = base_y - r * h
        d.rounded_rectangle([(x0, y0), (x0 + bar_w, base_y)], radius=3, fill=fg)
    # arrow up-right
    d.line([(cx - r * 0.55, cy + r * 0.15), (cx + r * 0.65, cy - r * 0.6)], fill=BLUE_DEEP, width=4)
    # arrowhead
    d.polygon(
        [(cx + r * 0.65, cy - r * 0.6), (cx + r * 0.35, cy - r * 0.6), (cx + r * 0.65, cy - r * 0.3)],
        fill=BLUE_DEEP,
    )

def icon_cycle(d, cx, cy, r, fg=WHITE):
    # two circular arrows
    d.arc([(cx - r * 0.85, cy - r * 0.85), (cx + r * 0.85, cy + r * 0.85)],
          start=220, end=80, fill=fg, width=max(4, int(r * 0.14)))
    d.arc([(cx - r * 0.85, cy - r * 0.85), (cx + r * 0.85, cy + r * 0.85)],
          start=40, end=260, fill=fg, width=max(4, int(r * 0.14)))
    # arrow heads
    d.polygon([(cx + r * 0.72, cy - r * 0.25), (cx + r * 0.45, cy - r * 0.55),
               (cx + r * 0.95, cy - r * 0.55)], fill=fg)
    d.polygon([(cx - r * 0.72, cy + r * 0.25), (cx - r * 0.45, cy + r * 0.55),
               (cx - r * 0.95, cy + r * 0.55)], fill=fg)

def icon_flag(d, cx, cy, r, fg=WHITE):
    # pole
    d.line([(cx - r * 0.5, cy - r * 0.75), (cx - r * 0.5, cy + r * 0.85)], fill=fg, width=max(3, int(r * 0.1)))
    # flag triangle
    d.polygon([
        (cx - r * 0.5, cy - r * 0.75),
        (cx + r * 0.7, cy - r * 0.35),
        (cx - r * 0.5, cy + r * 0.05),
    ], fill=fg)

def icon_scale(d, cx, cy, r, fg=WHITE):
    # central pillar
    d.line([(cx, cy - r * 0.8), (cx, cy + r * 0.6)], fill=fg, width=max(3, int(r * 0.1)))
    # top beam
    d.line([(cx - r * 0.75, cy - r * 0.75), (cx + r * 0.75, cy - r * 0.75)], fill=fg, width=max(3, int(r * 0.1)))
    # base
    d.line([(cx - r * 0.45, cy + r * 0.6), (cx + r * 0.45, cy + r * 0.6)], fill=fg, width=max(3, int(r * 0.1)))
    # pans
    d.polygon([(cx - r * 0.9, cy - r * 0.55), (cx - r * 0.2, cy - r * 0.55), (cx - r * 0.55, cy - r * 0.15)], fill=fg)
    d.polygon([(cx + r * 0.2, cy - r * 0.55), (cx + r * 0.9, cy - r * 0.55), (cx + r * 0.55, cy - r * 0.15)], fill=fg)
    # strings
    d.line([(cx - r * 0.55, cy - r * 0.75), (cx - r * 0.9, cy - r * 0.55)], fill=fg, width=2)
    d.line([(cx - r * 0.55, cy - r * 0.75), (cx - r * 0.2, cy - r * 0.55)], fill=fg, width=2)
    d.line([(cx + r * 0.55, cy - r * 0.75), (cx + r * 0.2, cy - r * 0.55)], fill=fg, width=2)
    d.line([(cx + r * 0.55, cy - r * 0.75), (cx + r * 0.9, cy - r * 0.55)], fill=fg, width=2)

def icon_chat(d, cx, cy, r, fg=WHITE):
    d.rounded_rectangle(
        [(cx - r * 0.85, cy - r * 0.7), (cx + r * 0.85, cy + r * 0.3)],
        radius=int(r * 0.2),
        fill=fg,
    )
    # tail
    d.polygon([(cx - r * 0.3, cy + r * 0.3), (cx - r * 0.55, cy + r * 0.75),
               (cx - r * 0.05, cy + r * 0.3)], fill=fg)
    # dots
    for dx in (-0.4, 0, 0.4):
        _circle(d, cx + r * dx, cy - r * 0.2, r * 0.07, TEAL)

ICONS = {
    "check": icon_check,
    "person": icon_person,
    "question": icon_question,
    "target": icon_target,
    "clock": icon_clock,
    "book": icon_book,
    "rocket": icon_rocket,
    "gear": icon_gear,
    "chart": icon_chart,
    "cycle": icon_cycle,
    "flag": icon_flag,
    "scale": icon_scale,
    "chat": icon_chat,
}

# -----------------------------------------------------------------------------
# layouts
# -----------------------------------------------------------------------------
def layout_cards(d, header, cards, footer_title, footer_subtitle):
    """5 or fewer cards across a row. Each card: {label, icon, highlight?}"""
    n = len(cards)
    top, bot = 175, 460
    pad = 60
    gap = 20
    card_w = (W - pad * 2 - gap * (n - 1)) / n
    for i, c in enumerate(cards):
        x0 = pad + i * (card_w + gap)
        x1 = x0 + card_w
        highlighted = c.get("highlight", False)
        fill = TEAL_DARK if highlighted else CARD_BG
        outline = TEAL if highlighted else CARD_BORDER
        d.rounded_rectangle([(x0, top), (x1, bot)], radius=18, fill=fill, outline=outline, width=3)
        # icon circle
        icon_cx = (x0 + x1) / 2
        icon_cy = top + 68
        if highlighted:
            # on highlighted card use white-filled circle bg
            _circle(d, icon_cx, icon_cy, 42, WHITE)
            ICONS[c["icon"]](d, icon_cx, icon_cy, 32, fg=TEAL_DARK)
        else:
            ICONS[c["icon"]](d, icon_cx, icon_cy, 36)
        # number
        num_color = SUBTEXT if highlighted else NUMBER_GRAY
        text_center(d, (icon_cx, icon_cy + 82), f"{i+1:02d}", F("Medium", 14), num_color)
        # label (wrap up to 2 lines)
        label = c["label"]
        lines = _wrap(label, 14)
        ly = icon_cy + 122
        label_color = WHITE if highlighted else TEAL_VERY_DARK
        for ln in lines[:2]:
            text_center(d, (icon_cx, ly), ln, F("SemiBold", 18), label_color)
            ly += 26
    draw_header(d, header)
    draw_footer(d, footer_title, footer_subtitle)

def _wrap(text, max_chars):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def layout_timeline(d, header, steps, footer_title, footer_subtitle):
    """Horizontal flow: circles connected by lines, with step labels underneath."""
    n = len(steps)
    top = 220
    pad = 110
    span = W - pad * 2
    step_x = [pad + i * span / (n - 1) for i in range(n)]
    # connecting line
    d.line([(step_x[0], top), (step_x[-1], top)], fill=TEAL, width=4)
    for i, s in enumerate(steps):
        cx = step_x[i]
        cy = top
        # outer ring + inner fill
        _circle(d, cx, cy, 48, WHITE)
        d.ellipse([(cx - 48, cy - 48), (cx + 48, cy + 48)], outline=TEAL, width=4)
        ICONS[s["icon"]](d, cx, cy, 28, fg=TEAL)
        # step number label
        text_center(d, (cx, cy + 76), f"STEP {i+1:02d}", F("Medium", 13), BLUE_DEEP)
        # step label (wrap)
        lines = _wrap(s["label"], 14)
        ly = cy + 108
        for ln in lines[:2]:
            text_center(d, (cx, ly), ln, F("SemiBold", 19), TEAL_VERY_DARK)
            ly += 26
    draw_header(d, header)
    draw_footer(d, footer_title, footer_subtitle)

def layout_split(d, header, left, center, right, footer_title, footer_subtitle):
    """Two contrasting columns joined by a center circle."""
    band_top, band_bot = 150, 445
    # left block (teal)
    lx0, lx1 = 140, 420
    d.polygon([(lx0, band_top), (lx1, band_top + 10),
               (lx1, band_bot), (lx0 + 10, band_bot)], fill=TEAL)
    # right block (deep blue)
    rx0, rx1 = 780, 1060
    d.polygon([(rx0, band_top + 10), (rx1, band_top),
               (rx1 - 10, band_bot), (rx0, band_bot)], fill=BLUE_DEEP)
    # floor line
    d.line([(70, band_bot + 20), (W - 70, band_bot + 20)], fill=TEAL_DARK, width=3)

    # icons
    ICONS[left["icon"]](d, (lx0 + lx1) / 2, band_top + 90, 50, fg=WHITE)
    ICONS[right["icon"]](d, (rx0 + rx1) / 2, band_top + 90, 50, fg=WHITE)
    # big labels
    text_center(d, ((lx0 + lx1) / 2, band_top + 195), left["label"].upper(),
                F("SemiBold", 32), WHITE)
    text_center(d, ((rx0 + rx1) / 2, band_top + 195), right["label"].upper(),
                F("SemiBold", 32), WHITE)
    # sub lines under labels
    for i, ln in enumerate(_wrap(left["sub"], 22)[:3]):
        text_center(d, ((lx0 + lx1) / 2, band_top + 240 + i * 22), ln,
                    F("Light", 16), (224, 242, 254))
    for i, ln in enumerate(_wrap(right["sub"], 22)[:3]):
        text_center(d, ((rx0 + rx1) / 2, band_top + 240 + i * 22), ln,
                    F("Light", 16), (224, 242, 254))

    # + signs
    text_center(d, (520, band_top + 115), "+", F("Light", 52), TEAL_DARK)
    text_center(d, (680, band_top + 115), "+", F("Light", 52), TEAL_DARK)

    # center circle with the "decision" word
    cx, cy = 600, band_top + 115
    _circle(d, cx, cy, 62, WHITE)
    d.ellipse([(cx - 62, cy - 62), (cx + 62, cy + 62)], outline=TEAL_DARK, width=3)
    text_center(d, (cx, cy - 10), center["label"].upper(), F("SemiBold", 18), TEAL_VERY_DARK)
    text_center(d, (cx, cy + 16), center["sub"], F("Light", 14), TEAL_DARK)
    # dotted arc between boxes over the circle
    # (approximate dashed arc)
    import math
    for deg in range(210, 330, 6):
        rad = math.radians(deg)
        px = cx + 180 * math.cos(rad)
        py = cy + 80 * math.sin(rad)
        d.ellipse([(px - 2, py - 2), (px + 2, py + 2)], fill=TEAL)

    draw_header(d, header)
    draw_footer(d, footer_title, footer_subtitle)

# -----------------------------------------------------------------------------
# entry point — driven by JSON config on stdin for flexibility
# -----------------------------------------------------------------------------
def render(cfg, out_path):
    """Render a hero image from a config dict to out_path (JPG).

    cfg must include: layout, header, footer_title, footer_subtitle, and the
    layout-specific fields (cards/steps/left+center+right). See module docstring.
    """
    img, d = make_canvas()
    layout = cfg["layout"]
    if layout == "cards":
        layout_cards(d, cfg["header"], cfg["cards"], cfg["footer_title"], cfg["footer_subtitle"])
    elif layout == "timeline":
        layout_timeline(d, cfg["header"], cfg["steps"], cfg["footer_title"], cfg["footer_subtitle"])
    elif layout == "split":
        layout_split(d, cfg["header"], cfg["left"], cfg["center"], cfg["right"],
                     cfg["footer_title"], cfg["footer_subtitle"])
    else:
        raise ValueError(f"unknown layout: {layout}")
    img.save(out_path, "JPEG", quality=88, optimize=True)
    return out_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--config", required=True, help="path to JSON config")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    render(cfg, args.out)
    print(f"wrote {args.out}")

if __name__ == "__main__":
    main()
