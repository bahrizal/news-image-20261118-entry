#!/usr/bin/env python3
"""Render the 18 November 2026 world-news front page as a 1024x1024 PNG.

Pure PIL drawing: flat colours, simple geometric illustrations, wrapped
headlines. Fully deterministic -- no randomness, no timestamps, no network.
Run: python3 gen.py  ->  writes entry.png next to this file.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 236)      # warm newsprint
INK = (17, 17, 17)
RED = (178, 34, 34)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LIGHT = (238, 232, 220)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


F_TITLE = font("DejaVuSans-Bold.ttf", 46)
F_DATE = font("DejaVuSans-Bold.ttf", 40)
F_HERO_HEAD = font("DejaVuSans-Bold.ttf", 42)
F_HERO_SUB = font("DejaVuSans.ttf", 21)
F_CAT = font("DejaVuSans-Bold.ttf", 17)
F_HEAD = font("DejaVuSans-Bold.ttf", 24)
F_SUB = font("DejaVuSans.ttf", 16)
F_FOOT = font("DejaVuSans.ttf", 18)
F_FOOT_B = font("DejaVuSans-Bold.ttf", 18)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap, returns list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def starburst(draw, cx, cy, r, fill):
    """Simple 12-point explosion star."""
    import math
    pts = []
    for i in range(24):
        ang = math.pi * i / 12
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


# ---------------------------------------------------------------- icons

def icon_bridge(draw, x, y, w, h):
    """Crimean Bridge over water, explosion above the deck."""
    sky = (214, 228, 240)
    draw.rectangle([x, y, x + w, y + h], fill=sky)
    water_y = y + int(h * 0.62)
    draw.rectangle([x, water_y, x + w, y + h], fill=(58, 110, 160))
    for i in range(4):  # wave lines
        wy = water_y + 10 + i * 12
        draw.line([x + 8, wy, x + w - 8, wy], fill=(140, 185, 220), width=3)
    # bridge deck + arch + pylons
    deck_y = water_y - 14
    draw.line([x + 6, deck_y, x + w - 6, deck_y], fill=INK, width=7)
    draw.arc([x + w * 0.28, deck_y - 52, x + w * 0.72, deck_y + 20],
             start=180, end=360, fill=INK, width=6)
    for px in (0.32, 0.5, 0.68):
        draw.line([x + w * px, deck_y - 46, x + w * px, deck_y], fill=INK, width=4)
    # broken gap + explosion at centre
    draw.rectangle([x + w * 0.47, deck_y - 4, x + w * 0.53, deck_y + 4], fill=sky)
    starburst(draw, x + w * 0.5, deck_y - 34, 26, (255, 140, 0))
    starburst(draw, x + w * 0.5, deck_y - 34, 14, (255, 210, 0))


def icon_radar(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 238, 226))
    cx, cy, r = x + w / 2, y + h / 2 + 4, min(w, h) / 2 - 8
    for rr in (r, r * 0.66, r * 0.33):
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                     outline=(46, 110, 74), width=3)
    draw.line([cx - r, cy, cx + r, cy], fill=(46, 110, 74), width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=(46, 110, 74), width=2)
    # sweep + blips
    draw.line([cx, cy, cx + r * 0.8, cy - r * 0.55], fill=(178, 34, 34), width=4)
    draw.ellipse([cx + r * 0.45 - 5, cy - r * 0.35 - 5,
                  cx + r * 0.45 + 5, cy - r * 0.35 + 5], fill=(178, 34, 34))
    draw.ellipse([cx - r * 0.5 - 4, cy + r * 0.45 - 4,
                  cx - r * 0.5 + 4, cy + r * 0.45 + 4], fill=(46, 110, 74))
    # drone above the radar
    dx, dy = cx, y + 16
    draw.rectangle([dx - 16, dy - 5, dx + 16, dy + 5], fill=INK)
    draw.line([dx - 24, dy - 8, dx - 10, dy - 8], fill=INK, width=3)
    draw.line([dx + 10, dy - 8, dx + 24, dy - 8], fill=INK, width=3)
    draw.ellipse([dx - 30, dy - 12, dx - 18, dy - 4], outline=INK, width=2)
    draw.ellipse([dx + 18, dy - 12, dx + 30, dy - 4], outline=INK, width=2)


def icon_plane(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(220, 232, 244))
    cx, cy = x + w / 2, y + h / 2
    # contrails
    for k in range(3):
        draw.line([x + 6, cy + 26 + k * 10, cx - 30, cy + 18 + k * 10],
                  fill=(255, 255, 255), width=4)
    # simple jet silhouette (side view, nose right)
    body = [(cx - 62, cy + 4), (cx + 52, cy - 8), (cx + 74, cy + 2),
            (cx + 52, cy + 12), (cx - 62, cy + 14)]
    draw.polygon(body, fill=(31, 78, 121))
    draw.polygon([(cx - 18, cy + 2), (cx + 6, cy - 26), (cx + 16, cy - 26),
                  (cx + 2, cy + 2)], fill=(31, 78, 121))  # tail fin
    draw.polygon([(cx - 8, cy + 4), (cx + 14, cy + 30), (cx + 26, cy + 30),
                  (cx + 8, cy + 4)], fill=(31, 78, 121))  # wing
    draw.ellipse([cx + 56, cy - 4, cx + 66, cy + 4], fill=WHITE)


def icon_trade(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 238, 226))
    # Canada flag (left, tilted) and China flag (right, tilted)
    draw.rectangle([x + 18, y + 22, x + 88, y + 78], fill=WHITE, outline=INK, width=2)
    draw.rectangle([x + 18, y + 22, x + 38, y + 78], fill=(200, 30, 30))
    draw.rectangle([x + 68, y + 22, x + 88, y + 78], fill=(200, 30, 30))
    draw.ellipse([x + 46, y + 38, x + 60, y + 58], fill=(200, 30, 30))
    draw.rectangle([x + w - 88, y + 22, x + w - 18, y + 78], fill=(222, 41, 16),
                   outline=INK, width=2)
    for sx, sy in ((x + w - 78, y + 30), (x + w - 62, y + 30),
                   (x + w - 78, y + 46), (x + w - 62, y + 46)):
        starburst(draw, sx, sy, 5, (255, 222, 0))
    # rising arrow between them
    draw.line([x + w / 2 - 34, y + h - 26, x + w / 2 + 34, y + 26],
              fill=(30, 107, 74), width=6)
    draw.polygon([(x + w / 2 + 34, y + 26), (x + w / 2 + 14, y + 26),
                  (x + w / 2 + 34, y + 46)], fill=(30, 107, 74))


def icon_chip(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 235, 228))
    cx, cy = x + w / 2, y + h / 2
    # pins + body (headline already carries the $115.8BN figure)
    for i in range(4):
        py = cy - 24 + i * 16
        draw.line([cx - 58, py, cx - 40, py], fill=(180, 150, 40), width=5)
        draw.line([cx + 40, py, cx + 58, py], fill=(180, 150, 40), width=5)
    draw.rectangle([cx - 40, cy - 32, cx + 40, cy + 32], fill=(30, 30, 34))
    draw.rectangle([cx - 22, cy - 18, cx + 22, cy + 18], fill=(118, 185, 0))
    draw.text((cx - 11, cy - 10), "AI", font=font("DejaVuSans-Bold.ttf", 20),
              fill=WHITE)


def icon_gavel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 240))
    cx, cy = x + w / 2, y + h / 2 + 6
    # gavel head (rotated bar) + handle
    draw.polygon([(cx - 46, cy - 26), (cx + 10, cy - 52), (cx + 22, cy - 34),
                  (cx - 34, cy - 8)], fill=(90, 50, 20))
    draw.line([cx - 8, cy - 18, cx + 34, cy + 30], fill=(120, 70, 30), width=9)
    draw.ellipse([cx - 52, cy + 30, cx + 52, cy + 44], outline=(90, 50, 20), width=4)
    # red prohibition ring
    draw.ellipse([x + w - 58, y + 6, x + w - 14, y + 50], outline=RED, width=6)
    draw.line([x + w - 52, y + 44, x + w - 20, y + 12], fill=RED, width=6)


# ---------------------------------------------------------------- page

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # frame
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=4)
    d.rectangle([16, 16, W - 17, H - 17], outline=INK, width=1)

    # ---- masthead
    draw_centered(d, W / 2, 30, "THE WORLD IN ONE DAY", F_TITLE, INK)
    d.line([60, 92, W - 60, 92], fill=INK, width=2)
    draw_centered(d, W / 2, 102, "WEDNESDAY  ·  18 NOVEMBER 2026", F_DATE, RED)
    d.line([60, 152, W - 60, 152], fill=INK, width=3)

    # ---- hero: Crimean Bridge
    hx, hy, hw, hh = 24, 164, W - 48, 296
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=WHITE, outline=INK, width=2)
    d.rectangle([hx, hy, hx + hw, hy + 30], fill=(27, 42, 74))
    draw_centered(d, hx + hw / 2, hy + 4, "UKRAINE  —  WAR IN EUROPE", F_CAT, WHITE)
    head = wrap(d, "UKRAINE HITS CRIMEAN BRIDGE AGAIN", F_HERO_HEAD, hw - 40)
    y = hy + 42
    for line in head:
        d.text((hx + 20, y), line, font=F_HERO_HEAD, fill=INK)
        y += 48
    d.text((hx + 20, y + 2),
           "Kyiv strikes the strategic crossing as Russia pounds Kyiv's bridges",
           font=F_HERO_SUB, fill=GREY)
    icon_bridge(d, hx + 20, hy + 172, hw - 40, 108)

    # ---- grid of five stories
    stories = [
        ("MIDDLE EAST", (122, 31, 31), icon_radar,
         "IRAN DRONES HIT US RADAR IN BAHRAIN",
         "Bahrain sounds the all-clear"),
        ("ASIA-PACIFIC", (20, 69, 107), icon_plane,
         "TRUMP LANDS IN MANILA FOR QUAD TALKS",
         "Ahead of a China visit"),
        ("TRADE  ·  APEC", (30, 107, 74), icon_trade,
         "CANADA–CHINA EXTEND TRADE DEALS",
         "Xi meets Carney at APEC"),
        ("BUSINESS", (90, 125, 0), icon_chip,
         "NVIDIA POSTS $115.8BN QUARTER",
         "Record quarterly revenue"),
        ("BRITAIN", (91, 44, 111), icon_gavel,
         "UK SANCTIONS 8 SETTLEMENT FIRMS",
         "Over settlements and Gaza aid"),
    ]
    gx, gy = 24, 476
    pw, ph = 314, 236
    gap = 12
    for i, (cat, accent, icon, headline, sub) in enumerate(stories):
        col, row = i % 3, i // 3
        px = gx + col * (pw + gap)
        py = gy + row * (ph + gap)
        d.rectangle([px, py, px + pw, py + ph], fill=WHITE, outline=INK, width=2)
        d.rectangle([px, py, px + pw, py + 30], fill=accent)
        draw_centered(d, px + pw / 2, py + 4, cat, F_CAT, WHITE)
        icon(d, px + 14, py + 38, pw - 28, 76)
        lines = wrap(d, headline, F_HEAD, pw - 28)
        y = py + 120
        for line in lines[:3]:
            d.text((px + 14, y), line, font=F_HEAD, fill=INK)
            y += 28
        d.text((px + 14, py + 208), sub, font=F_SUB, fill=GREY)

    # sixth cell: ALSO TODAY
    px = gx + 2 * (pw + gap)
    py = gy + 1 * (ph + gap)
    d.rectangle([px, py, px + pw, py + ph], fill=(27, 42, 74), outline=INK, width=2)
    draw_centered(d, px + pw / 2, py + 10, "ALSO TODAY", F_CAT, (255, 210, 0))
    d.line([px + 16, py + 40, px + pw - 16, py + 40], fill=(255, 210, 0), width=2)
    also = [
        "Dhoni retires from the IPL",
        "Cyclone Akvan builds over the Bay of Bengal",
        "Gaza: WFP serves one hot meal every two days",
    ]
    y = py + 54
    for item in also:
        d.text((px + 18, y), "•", font=F_SUB, fill=(255, 210, 0))
        for line in wrap(d, item, F_SUB, pw - 48):
            d.text((px + 36, y), line, font=F_SUB, fill=WHITE)
            y += 22
        y += 12

    # ---- footer
    d.line([60, 962, W - 60, 962], fill=INK, width=2)
    draw_centered(d, W / 2, 972, "Six stories, one day — Wednesday 18 November 2026",
                  F_FOOT, INK)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
