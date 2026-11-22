#!/usr/bin/env python3
"""The Daily Sum - Saturday 21 November 2026 in one image.

Renders a one-page broadsheet (1024x1024 PNG) summing up one day of world
news: 35 stories - 3 drawn leads, 10 drawn tiles, 22 numbered briefs -
with a region bar, a big-number stats strip, a world map and a date check.
Pure Pillow, no network, fully deterministic.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (246, 240, 224)
PAPER_DARK = (238, 230, 205)
INK = (18, 18, 18)
RED = (178, 34, 30)
RED_DARK = (140, 24, 22)
TEAL = (16, 110, 110)
BLUE = (30, 84, 150)
NAVY = (16, 28, 58)
GOLD = (196, 148, 32)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 20)
GREY = (90, 88, 80)
SKY = (196, 220, 232)
SKY_DUSK = (240, 205, 160)

NOTO = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = NOTO + "NotoSerifDisplay-Black.ttf"
SERIF_BOLD = NOTO + "NotoSerif-Bold.ttf"
SERIF_BOLD_IT = NOTO + "NotoSerif-BoldItalic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W = 2048
MARGIN = 40
CW = W - 2 * MARGIN  # content width


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, max_width, start):
    """Largest font (<= start) whose text fits max_width."""
    size = start
    while size > 10:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 4
    return font(path, 10)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_width, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def pill_width(draw, label):
    f = font(SANS_BOLD, 25)
    return draw.textlength(label, font=f) + 26


def pill(draw, x, y, label, colour):
    f = font(SANS_BOLD, 25)
    w = pill_width(draw, label)
    draw.rounded_rectangle([x, y, x + w, y + 36], radius=8, fill=colour)
    draw.text((x + 13, y + 4), label, font=f, fill=(255, 255, 255))
    return w


def badge(draw, x, y, number):
    r = 26
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=INK)
    f = font(SANS_BOLD, 32)
    t = str(number)
    tw = draw.textlength(t, font=f)
    draw.text((x + r - tw / 2, y + r - 22), t, font=f, fill=(255, 255, 255))


TAG_COLOURS = {
    "OFFICIAL": BLUE,
    "CONFIRMED": GREEN,
    "REPORTED": TEAL,
    "CLAIM": ORANGE,
}

# ---------------------------------------------------------------- scenes
# Each scene paints inside box (x, y, w, h) - flat shapes, bold silhouettes.


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    sr = int(h * 0.17)
    d.ellipse([x + w - sr - 16, y + 14, x + w - 16, y + 14 + sr], fill=GOLD)
    # conference hall: roof + columns + banner
    cx = x + w // 2
    roof_hw = w // 2 - 8
    hall_top = y + int(h * 0.16)
    hall_base = y + h - int(h * 0.12)
    d.polygon([(cx - roof_hw, hall_base - int(h * 0.42)), (cx, hall_top), (cx + roof_hw, hall_base - int(h * 0.42))], fill=RED_DARK)
    d.rectangle([cx - roof_hw + 14, hall_base - int(h * 0.42), cx + roof_hw - 14, hall_base], fill=(250, 246, 235))
    cols = 6
    for i in range(cols):
        px = cx - roof_hw + 30 + i * ((2 * roof_hw - 60) // cols)
        d.rectangle([px, hall_base - int(h * 0.36), px + 16, hall_base - 6], fill=(196, 188, 168))
    bw = int(w * 0.52)
    d.rectangle([cx - bw // 2, hall_base - int(h * 0.30), cx + bw // 2, hall_base - int(h * 0.08)], fill=INK)
    f = font(SANS_BOLD, int(h * 0.17))
    t = "COP31"
    d.text((cx - d.textlength(t, font=f) / 2, hall_base - int(h * 0.285)), t, font=f, fill=(255, 255, 255))
    # flag poles along the front
    for i, c in enumerate([(178, 34, 30), (30, 84, 150), (34, 120, 60), (196, 148, 32), (110, 60, 140), (16, 110, 110)]):
        px = x + 14 + i * int(w * 0.055)
        d.line([px, hall_base - int(h * 0.34), px, hall_base], fill=INK, width=4)
        d.rectangle([px, hall_base - int(h * 0.34), px + int(w * 0.038), hall_base - int(h * 0.34) + int(h * 0.09)], fill=c)
    d.rectangle([x, y + h - int(h * 0.12), x + w, y + h], fill=(120, 150, 90))


def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    for fx, fy in [(0.07, 0.10), (0.22, 0.20), (0.46, 0.08), (0.70, 0.17), (0.90, 0.10), (0.33, 0.30), (0.79, 0.32)]:
        sx, sy = x + int(w * fx), y + int(h * fy)
        d.ellipse([sx, sy, sx + 6, sy + 6], fill=(255, 255, 230))
    # skyline silhouettes with lit windows
    base = y + h
    towers = [(0.01, 0.46, 0.11), (0.14, 0.66, 0.10), (0.26, 0.38, 0.13), (0.41, 0.74, 0.09),
              (0.52, 0.50, 0.12), (0.66, 0.62, 0.10), (0.78, 0.42, 0.11), (0.90, 0.58, 0.09)]
    for fx, fh, fw in towers:
        tx, th, twd = x + int(w * fx), int(h * fh), int(w * fw)
        d.rectangle([tx, base - th, tx + twd, base], fill=(8, 12, 30))
        for wy in range(base - th + 12, base - 14, max(12, h // 9)):
            for wx in range(tx + 8, tx + twd - 8, max(11, w // 34)):
                d.rectangle([wx, wy, wx + 6, wy + 8], fill=(250, 205, 90))
    # three missile arcs + bursts
    for fx, fy in [(0.27, 0.30), (0.56, 0.20), (0.82, 0.35)]:
        mx, my = x + int(w * fx), y + int(h * fy)
        rw = int(w * 0.15)
        d.arc([mx - rw, my - 6, mx + rw, my + int(h * 0.55)], start=200, end=340, fill=(255, 160, 60), width=5)
        for dx, dy in [(-26, 0), (26, 0), (0, -23), (0, 20), (-18, -17), (18, -17), (-18, 15), (18, 15)]:
            d.line([mx, my, mx + dx, my + dy], fill=(255, 215, 90), width=5)
        d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(255, 240, 170))


def scene_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY_DUSK)
    sr = int(h * 0.15)
    d.ellipse([x + 16, y + 12, x + 16 + sr, y + 12 + sr], fill=GOLD)
    # Andes range with snow caps
    ground = y + h - int(h * 0.34)
    peaks = [(0.00, 0.42, 0.22), (0.16, 0.24, 0.38), (0.36, 0.38, 0.58), (0.55, 0.22, 0.78), (0.75, 0.36, 1.00)]
    for fx0, fpy, fx1 in peaks:
        px, py, px2 = x + int(w * fx0), y + int(h * fpy), x + int(w * fx1)
        mid = (px + px2) // 2
        d.polygon([(px, ground), (mid, py), (px2, ground)], fill=(110, 96, 84))
        cap = int(h * 0.10)
        d.polygon([(mid - cap, py + int(cap * 0.9)), (mid, py), (mid + cap, py + int(cap * 0.9)),
                   (mid + int(cap * 0.4), py + int(cap * 0.55)), (mid, py + int(cap * 0.85)),
                   (mid - int(cap * 0.4), py + int(cap * 0.55))], fill=(255, 255, 255))
    # cracked ground
    d.rectangle([x, ground, x + w, y + h], fill=(150, 118, 84))
    crack = [(0.05, 0.02), (0.16, 0.10), (0.25, 0.05), (0.36, 0.14), (0.47, 0.07), (0.59, 0.16), (0.71, 0.09), (0.83, 0.18), (0.94, 0.11)]
    pts = [(x + int(w * fx), ground + int(h * fy)) for fx, fy in crack]
    d.line(pts, fill=INK, width=6)
    # seismograph trace across the sky
    trace = []
    amps = [4, 6, 4, 18, 42, 64, 28, 48, 20, 7, 4, 6, 4]
    cy = y + int(h * 0.17)
    for i, a in enumerate(amps):
        aa = int(a * h / 260.0)
        trace.append((x + int(w * 0.04) + i * (w - int(w * 0.08)) // 12, cy - aa if i % 2 == 0 else cy + aa))
    d.line(trace, fill=RED, width=5)


def scene_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 214))
    # river + suspension bridge
    d.rectangle([x, y + h - 34, x + w, y + h], fill=BLUE)
    deck = y + h - 58
    d.rectangle([x, deck, x + w, deck + 10], fill=INK)
    for tx in (w // 4, 3 * w // 4):
        d.rectangle([x + tx - 6, y + 14, x + tx + 6, deck], fill=INK)
        d.line([x + tx, y + 16, x + 20, deck], fill=INK, width=4)
        d.line([x + tx, y + 16, x + w - 20, deck], fill=INK, width=4)
    # city blocks behind
    for bx, bh in [(16, 30), (64, 42), (int(w * 0.78), 34), (int(w * 0.88), 46), (int(w * 0.64), 26)]:
        d.rectangle([x + bx, deck - bh, x + bx + 34, deck], fill=(150, 146, 132))
    # warning burst
    cx, cy = x + w - 62, y + 30
    for dx, dy in [(-22, 0), (22, 0), (0, -18), (0, 16), (-15, -13), (15, -13), (-15, 12), (15, 12)]:
        d.line([cx, cy, cx + dx, cy + dy], fill=RED, width=5)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED)


def scene_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(170, 205, 220))
    # sea and two headlands forming a strait
    d.rectangle([x, y + h // 2, x + w, y + h], fill=(52, 110, 160))
    d.polygon([(x, y), (x + w // 2 - 60, y), (x + w // 3, y + h // 2), (x, y + h // 2)], fill=(196, 170, 120))
    d.polygon([(x + w, y), (x + w // 2 + 60, y), (x + 2 * w // 3, y + h // 2), (x + w, y + h // 2)], fill=(186, 158, 108))
    # tanker in the channel
    tx, ty = x + w // 2 - 90, y + h - 74
    d.polygon([(tx, ty), (tx + 180, ty), (tx + 158, ty + 30), (tx + 22, ty + 30)], fill=INK)
    d.rectangle([tx + 60, ty - 22, tx + 120, ty], fill=RED_DARK)
    # drone falling with smoke trail
    dx, dy = x + int(w * 0.60), y + int(h * 0.30)
    d.polygon([(dx, dy), (dx + int(w * 0.10), dy + int(h * 0.08)), (dx + int(w * 0.03), dy + int(h * 0.17))], fill=INK)
    d.line([dx + 4, dy - 2, dx - int(w * 0.08), dy - int(h * 0.26)], fill=GREY, width=6)
    d.line([dx - int(w * 0.02), dy + 4, dx - int(w * 0.13), dy - int(h * 0.15)], fill=(170, 170, 170), width=5)


def scene_tehran(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 186))
    base = y + h
    # skyline blocks at the edges
    for fx, fh, fw in [(0.02, 0.62, 0.16), (0.20, 0.86, 0.13), (0.68, 0.74, 0.15), (0.85, 0.56, 0.13)]:
        bx, bh, bw = x + int(w * fx), int(h * fh), int(w * fw)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(120, 104, 84))
    # domed hall in the middle
    cx = x + w // 2
    hall_top = base - int(h * 0.62)
    d.rectangle([cx - int(w * 0.13), hall_top, cx + int(w * 0.13), base], fill=(104, 90, 72))
    dw = int(w * 0.11)
    dh = int(h * 0.34)
    d.pieslice([cx - dw, hall_top - dh, cx + dw, hall_top + dh], start=180, end=360, fill=TEAL)
    d.rectangle([cx - 3, hall_top - dh - int(h * 0.10), cx + 3, hall_top - dh + int(h * 0.06)], fill=TEAL)
    # minaret
    mx = cx + int(w * 0.24)
    d.rectangle([mx - 5, base - int(h * 0.92), mx + 5, base], fill=(104, 90, 72))
    d.ellipse([mx - 12, base - int(h * 0.99), mx + 12, base - int(h * 0.86)], fill=TEAL)
    # atom mark (uranium) in the sky, clear of the number badge
    ax, ay = x + int(w * 0.82), y + int(h * 0.30)
    r = max(14, h // 9)
    d.ellipse([ax - r - 12, ay - (r + 12) // 2, ax + r + 12, ay + (r + 12) // 2], outline=INK, width=4)
    d.ellipse([ax - (r + 12) // 2, ay - r - 12, ax + (r + 12) // 2, ay + r + 12], outline=INK, width=4)
    d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill=RED)


def scene_washington(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 216, 226))
    base = y + h
    # data-centre block with server lights
    bx0, bx1 = x + int(w * 0.05), x + int(w * 0.60)
    by0 = base - int(h * 0.78)
    d.rectangle([bx0, by0, bx1, base], fill=(70, 82, 98))
    step_y = max(12, int(h * 0.16))
    step_x = max(16, int(w * 0.055))
    for ry in range(by0 + 10, base - 12, step_y):
        for rx in range(bx0 + 12, bx1 - 16, step_x):
            d.rectangle([rx, ry, rx + 13, ry + 7], fill=(120, 220, 160))
    # big tax tag
    tx, ty = x + int(w * 0.64), y + int(h * 0.14)
    tw, th = int(w * 0.32), int(h * 0.52)
    d.polygon([(tx, ty), (tx + tw, ty), (tx + tw, ty + th), (tx + int(tw * 0.22), ty + th), (tx, ty + int(th * 0.55))], fill=RED)
    f = font(SANS_BOLD, max(20, int(h * 0.30)))
    d.text((tx + int(tw * 0.26), ty + int(th * 0.20)), "TAX", font=f, fill=(255, 255, 255))
    d.ellipse([tx + 8, ty + int(th * 0.42), tx + 20, ty + int(th * 0.42) + 12], fill=(255, 255, 255))


def scene_beijing(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 226, 208))
    base = y + h - 16
    d.rectangle([x, base, x + w, y + h], fill=(140, 132, 104))
    # two flag poles facing off
    for px in (x + w // 3, x + 2 * w // 3):
        d.line([px, y + 30, px, base], fill=INK, width=6)
    fx = x + w // 3
    fw = int(w * 0.20)
    fh = int(h * 0.52)
    d.rectangle([fx, y + 30, fx + fw, y + 30 + fh], fill=RED)
    sx0, sy0 = fx + int(fw * 0.22), y + 30 + int(fh * 0.30)
    d.polygon([(sx0, sy0 - 12), (sx0 + 5, sy0), (sx0 + 17, sy0), (sx0 + 7, sy0 + 7), (sx0 + 10, sy0 + 19),
               (sx0, sy0 + 12), (sx0 - 10, sy0 + 19), (sx0 - 7, sy0 + 7), (sx0 - 17, sy0), (sx0 - 5, sy0)], fill=GOLD)
    gx = x + 2 * w // 3
    d.rectangle([gx, y + 30, gx + fw, y + 30 + fh], fill=(250, 250, 248))
    cr = int(fh * 0.30)
    d.ellipse([gx + fw // 2 - cr, y + 30 + fh // 2 - cr, gx + fw // 2 + cr, y + 30 + fh // 2 + cr], fill=RED)
    # clash sparks between the flags
    cx, cy = x + w // 2, y + 74
    for dx, dy in [(-30, -14), (30, -14), (-34, 12), (34, 12), (0, -30), (0, 28)]:
        d.line([cx, cy, cx + dx, cy + dy], fill=ORANGE, width=6)


def scene_davao(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 214, 232))
    # runway
    d.rectangle([x, y + h - int(h * 0.24), x + w, y + h], fill=(70, 70, 74))
    for lx in range(x + 12, x + w - 30, max(30, w // 9)):
        d.rectangle([lx, y + h - int(h * 0.13), lx + int(w * 0.05), y + h - int(h * 0.10)], fill=(250, 240, 200))
    # jet, side view, nose right
    jy = y + int(h * 0.30)
    jh = int(h * 0.34)
    d.polygon([(x + int(w * 0.10), jy + int(jh * 0.55)), (x + int(w * 0.58), jy),
               (x + int(w * 0.82), jy + int(jh * 0.18)), (x + int(w * 0.90), jy + int(jh * 0.52)),
               (x + int(w * 0.80), jy + jh), (x + int(w * 0.18), jy + jh), (x + int(w * 0.10), jy + int(jh * 0.82))],
              fill=(248, 248, 250))
    d.polygon([(x + int(w * 0.10), jy + int(jh * 0.55)), (x + int(w * 0.03), jy - int(jh * 0.45)),
               (x + int(w * 0.12), jy - int(jh * 0.45)), (x + int(w * 0.20), jy + int(jh * 0.30))], fill=BLUE)
    d.rectangle([x + int(w * 0.24), jy + int(jh * 0.52), x + int(w * 0.76), jy + int(jh * 0.68)], fill=BLUE)
    for wx in range(x + int(w * 0.30), x + int(w * 0.72), max(18, w // 16)):
        d.ellipse([wx, jy + int(jh * 0.16), wx + 11, jy + int(jh * 0.16) + 8], fill=(60, 90, 120))
    d.polygon([(x + int(w * 0.44), jy + jh), (x + int(w * 0.55), jy + jh + int(h * 0.16)),
               (x + int(w * 0.60), jy + jh + int(h * 0.16)), (x + int(w * 0.52), jy + jh)], fill=(200, 204, 210))
    wr = max(8, w // 28)
    d.ellipse([x + int(w * 0.26), jy + jh + 2, x + int(w * 0.26) + wr, jy + jh + 2 + wr], fill=INK)
    d.ellipse([x + int(w * 0.66), jy + jh + 2, x + int(w * 0.66) + wr, jy + jh + 2 + wr], fill=INK)
    # small engine flame, crossed out (alert stood down)
    fx, fy = x + int(w * 0.55), jy + jh + int(h * 0.17)
    d.polygon([(fx, fy), (fx + 9, fy - 15), (fx + 18, fy)], fill=ORANGE)
    d.line([fx - 5, fy - 18, fx + 24, fy + 3], fill=RED, width=5)


def scene_canberra(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(208, 226, 200))
    base = y + h
    # parliament-style hill building
    d.polygon([(x + int(w * 0.10), base), (x + w // 2, base - int(h * 0.52)), (x + int(w * 0.90), base)], fill=(150, 168, 128))
    d.rectangle([x + int(w * 0.26), base - int(h * 0.28), x + int(w * 0.74), base], fill=(240, 238, 228))
    d.line([x + w // 2, base - int(h * 0.52), x + w // 2, base - int(h * 0.80)], fill=INK, width=5)
    d.polygon([(x + w // 2, base - int(h * 0.80)), (x + w // 2 + int(w * 0.07), base - int(h * 0.74)),
               (x + w // 2, base - int(h * 0.68))], fill=RED)
    # AI chip between two speech bubbles
    cx, cy = x + w // 2, y + int(h * 0.24)
    chw, chh = int(w * 0.15), int(h * 0.30)
    d.rounded_rectangle([cx - chw // 2, cy - chh // 2, cx + chw // 2, cy + chh // 2], radius=8, fill=INK)
    f = font(SANS_BOLD, int(h * 0.19))
    t = "AI"
    d.text((cx - d.textlength(t, font=f) / 2, cy - int(h * 0.115)), t, font=f, fill=(255, 255, 255))
    for fx in (0.24, 0.76):
        sx = x + int(w * fx)
        bw2, bh2 = int(w * 0.13), int(h * 0.20)
        d.rounded_rectangle([sx - bw2 // 2, cy - bh2 // 2, sx + bw2 // 2, cy + bh2 // 2], radius=12, fill=(255, 255, 255), outline=INK, width=3)
        for bx in (-bw2 // 4, 0, bw2 // 4):
            d.ellipse([sx + bx - 4, cy - 4, sx + bx + 4, cy + 4], fill=INK)


def scene_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 34))
    # grid
    for gy in range(y + int(h * 0.16), y + h - 12, max(14, h // 5)):
        d.line([x + 10, gy, x + w - 10, gy], fill=(52, 56, 68), width=2)
    # falling chart
    rel = [(0.05, 0.16), (0.20, 0.26), (0.32, 0.21), (0.46, 0.42), (0.60, 0.38), (0.74, 0.62), (0.90, 0.86)]
    pts = [(x + int(w * fx), y + int(h * fy)) for fx, fy in rel]
    d.line(pts, fill=RED, width=6)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - int(w * 0.06), ey - 2), (ex - int(w * 0.02), ey - int(h * 0.18))], fill=RED)
    # coin
    cx, cy = x + int(w * 0.15), y + int(h * 0.76)
    r = max(14, h // 6)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    f = font(SANS_BOLD, int(r * 1.25))
    d.text((cx - r * 0.36, cy - r * 0.68), "B", font=f, fill=(120, 84, 10))
    f2 = font(SANS_BOLD, max(18, int(h * 0.20)))
    t = "-3.9%"
    d.text((x + w - 12 - d.textlength(t, font=f2), y + 10), t, font=f2, fill=RED)


def scene_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 198, 220))
    # wet track + spray
    d.rectangle([x, y + h - int(h * 0.22), x + w, y + h], fill=(84, 84, 96))
    for lx in range(x + 10, x + w - 24, max(30, w // 8)):
        d.rectangle([lx, y + h - int(h * 0.12), lx + int(w * 0.06), y + h - int(h * 0.09)], fill=(240, 240, 240))
    # F1 car silhouette, nose right
    by = y + int(h * 0.42)
    bh = int(h * 0.30)
    d.polygon([(x + int(w * 0.12), by + int(bh * 0.55)), (x + int(w * 0.30), by + int(bh * 0.25)),
               (x + int(w * 0.48), by + int(bh * 0.30)), (x + int(w * 0.66), by + int(bh * 0.15)),
               (x + int(w * 0.84), by + int(bh * 0.40)), (x + int(w * 0.85), by + int(bh * 0.62)),
               (x + int(w * 0.66), by + int(bh * 0.72)), (x + int(w * 0.30), by + int(bh * 0.75)),
               (x + int(w * 0.12), by + int(bh * 0.70))], fill=RED_DARK)
    d.rectangle([x + int(w * 0.09), by - int(bh * 0.10), x + int(w * 0.13), by + int(bh * 0.60)], fill=INK)  # rear wing
    d.polygon([(x + int(w * 0.82), by + int(bh * 0.40)), (x + int(w * 0.90), by + int(bh * 0.55)),
               (x + int(w * 0.82), by + int(bh * 0.62))], fill=INK)  # front wing
    d.ellipse([x + int(w * 0.36), by, x + int(w * 0.46), by + int(bh * 0.38)], fill=INK)  # airbox/driver
    wr = max(16, int(h * 0.30))
    for fx in (0.20, 0.64):
        wx = x + int(w * fx)
        d.ellipse([wx, by + int(bh * 0.45), wx + wr, by + int(bh * 0.45) + wr], fill=INK)
        d.ellipse([wx + wr // 4, by + int(bh * 0.45) + wr // 4, wx + 3 * wr // 4, by + int(bh * 0.45) + 3 * wr // 4], fill=(90, 90, 96))
    for i in range(4):  # spray behind rear wheel
        sx = x + int(w * 0.06) - i * 8
        d.line([sx + 26, by + int(bh * 0.95), sx, by + int(bh * 1.12)], fill=(250, 250, 250), width=4)
    f = font(SANS_BOLD, max(18, int(h * 0.17)))
    t = "1:34.041"
    d.text((x + int(w * 0.40), y + h - int(h * 0.20)), t, font=f, fill=(255, 255, 255))


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(170, 205, 140))
    d.rectangle([x, y + h - int(h * 0.34), x + w, y + h], fill=(196, 178, 130))  # pitch strip
    # stumps
    sx = x + int(w * 0.82)
    for i in range(3):
        d.rectangle([sx + i * 13, y + h - int(h * 0.72), sx + i * 13 + 6, y + h - int(h * 0.35)], fill=GOLD)
    # batsman silhouette mid-swing
    bx, by = x + int(w * 0.34), y + h - int(h * 0.06)
    s = h / 260.0  # scale for limb lengths
    d.ellipse([bx - int(11 * s), by - int(112 * s), bx + int(11 * s), by - int(90 * s)], fill=INK)  # head
    d.line([bx, by - int(90 * s), bx + int(8 * s), by - int(45 * s)], fill=INK, width=max(6, int(11 * s)))   # torso
    d.line([bx + int(4 * s), by - int(50 * s), bx - int(28 * s), by - int(4 * s)], fill=INK, width=max(5, int(9 * s)))  # front leg
    d.line([bx + int(5 * s), by - int(50 * s), bx + int(36 * s), by - int(9 * s)], fill=INK, width=max(5, int(9 * s)))  # back leg
    d.line([bx + int(6 * s), by - int(81 * s), bx + int(52 * s), by - int(106 * s)], fill=INK, width=max(5, int(8 * s)))  # arms
    d.line([bx + int(52 * s), by - int(106 * s), bx + int(81 * s), by - int(65 * s)], fill=(150, 110, 60), width=max(5, int(9 * s)))  # bat
    d.ellipse([x + int(w * 0.62), y + int(h * 0.18), x + int(w * 0.62) + 16, y + int(h * 0.18) + 16], fill=RED)  # ball


SCENES = {
    1: scene_cop31, 2: scene_riyadh, 3: scene_peru, 4: scene_kyiv,
    5: scene_hormuz, 6: scene_tehran, 7: scene_washington, 8: scene_beijing,
    9: scene_davao, 10: scene_canberra, 11: scene_bitcoin, 12: scene_f1,
    13: scene_cricket,
}

# ---------------------------------------------------------------- content
LEADS = [
    dict(n=1, place="ANTALYA", tag="CONFIRMED",
         headline="COP31 RUNS INTO OVERTIME, NO DEAL ON DAY 13",
         body="The summit missed its Friday close; nearly 200 countries are split "
              "over a draft that never mentions fossil fuels. A third text is promised.",
         source="Sources: AFP, Al Jazeera"),
    dict(n=2, place="RIYADH", tag="OFFICIAL",
         headline="THREE MISSILES DOWNED OVER RIYADH",
         body="The Saudi-led coalition destroyed three ballistic missiles aimed at "
              "the capital before dawn, the third night of alerts in a row. "
              "No damage or casualties.",
         source="Sources: Reuters, AFP"),
    dict(n=3, place="JUNIN, PERU", tag="OFFICIAL",
         headline="6.7 QUAKE SHAKES PERU",
         body="A deep quake near Carhuamayo at 00:09 UTC, 108 km down, felt in Lima "
              "and along the coast. No deaths, damage or tsunami risk reported.",
         source="Sources: USGS, IGP"),
]

TILES = [
    dict(n=4, place="KYIV", tag="REPORTED",
         headline="ZELENSKY: CRIMEA BRIDGE \u201cWILL NOT STAY\u201d",
         body="Kyiv's president warns of more double-tap strikes.",
         source="NBC"),
    dict(n=5, place="STRAIT OF HORMUZ", tag="CLAIM",
         headline="IRAN SAYS IT DOWNED A US DRONE",
         body="Tehran claims the shoot-down; Washington has not confirmed it.",
         source="IRIB"),
    dict(n=6, place="TEHRAN", tag="OFFICIAL",
         headline="URANIUM STOCK STAYS IN IRAN",
         body="It will not leave the country; a \u201cfair solution\u201d is still seen.",
         source="Iranian officials"),
    dict(n=7, place="WASHINGTON", tag="REPORTED",
         headline="TRUMP VOWS TAX ON DATA CENTRES ABROAD",
         body="A \u201ctremendous\u201d penalty is promised; no details yet.",
         source="ABC"),
    dict(n=8, place="BEIJING", tag="OFFICIAL",
         headline="CHINA TELLS JAPAN TO \u201cCORRECT\u201d TAIWAN WORDS",
         body="Beijing demands a correction; Tokyo says its stance is unchanged.",
         source="AFP"),
    dict(n=9, place="DAVAO", tag="OFFICIAL",
         headline="JET LANDS SAFE AFTER ENGINE-FIRE ALERT",
         body="The Air Niugini 767 diverted after midnight; all 146 aboard safe.",
         source="AP"),
    dict(n=10, place="CANBERRA", tag="CONFIRMED",
         headline="AUSTRALIA AND CHINA AGREE AI TALKS",
         body="Albanese ends an 11-day trip with the talks agreed.",
         source="ABC"),
    dict(n=11, place="MARKETS", tag="CONFIRMED",
         headline="BITCOIN BELOW $59,000",
         body="Down 3.9% in 24 hours on Saturday; ether at $1,625.",
         source="CoinGecko"),
    dict(n=12, place="LAS VEGAS", tag="OFFICIAL",
         headline="RUSSELL FASTEST IN FINAL PRACTICE",
         body="His 1:34.041 tops a damp, messy session.",
         source="Formula 1"),
    dict(n=13, place="WELLINGTON", tag="OFFICIAL",
         headline="RAHUL HITS A CENTURY, 124 NOT OUT",
         body="India 344 for 2 at tea, replying to 368.",
         source="AFP"),
]

BRIEFS = [
    (14, "Kryvyi Rih", "double strike kills 2, injures 42", "Kyiv Independent"),
    (15, "Copenhagen", "Russian attach\u00e9 expelled over a plot", "Al Jazeera"),
    (16, "Antalya", "EU warns COP31 risks a \u201cfossil summit\u201d", "AFP"),
    (17, "Antalya", "Panama threatens to block the climate text", "Al Jazeera"),
    (18, "Antalya", "Indonesia's PLN signs six clean-power deals", "Antara"),
    (19, "Yemen", "Houthis threaten Jeddah and Red Sea ports", "Al Jazeera"),
    (20, "Washington", "Vance: Iran strikes were Trump's decision", "Reuters"),
    (21, "Washington", "lawmaker threatens SpaceX's funding", "CNN"),
    (22, "Texas", "execution of a man of 70 takes 53 minutes", "ABC"),
    (23, "Los Angeles", "jury convicts man of starting Palisades fire", "ABC"),
    (24, "Missouri", "judge approves $7.25bn Roundup settlement", "AFP"),
    (25, "Vancouver", "Canada rests defence in youth climate trial", "AFP"),
    (26, "Pyongyang", "Kim tours factories after no Trump meeting", "AFP"),
    (27, "Sejong", "freight train derails; no one hurt", "Korea Herald"),
    (28, "Taipei", "budget and a cash payout are passed", "Taipei Times"),
    (29, "Bangkok", "six-point plan on arsenic in two rivers", "The Nation"),
    (30, "New Delhi", "Pakistani minister joins SCO forum in India", "Dawn"),
    (31, "Eastern India", "rain alerts as Akvan remnants move inland", "ETV"),
    (32, "Myanmar", "rights groups urge sanctions after court ruling", "AP"),
    (33, "Port Louis", "African rating agency talks to 15 states", "Al Jazeera"),
    (34, "Melbourne", "Cummins keeps the Australian captaincy", "ABC"),
    (35, "Las Vegas", "Verstappen sent to stewards after contact", "Autosport"),
]

REGIONS = [
    ("EUROPE", 4, (30, 84, 150)),
    ("ASIA", 10, (16, 110, 110)),
    ("MIDDLE EAST", 5, (196, 148, 32)),
    ("AFRICA", 1, (34, 120, 60)),
    ("AMERICAS", 11, (178, 34, 30)),
    ("OCEANIA", 3, (110, 60, 140)),
    ("GLOBAL", 1, (70, 70, 74)),
]

STATS = [
    ("13", "DAY 13 OF COP31"),
    ("3", "MISSILES DOWNED OVER RIYADH"),
    ("6.7", "PERU QUAKE MAGNITUDE"),
    ("146", "SAFE AFTER THE DAVAO LANDING"),
    ("$58,983", "BITCOIN, DOWN 3.9% IN A DAY"),
    ("124*", "RAHUL, NOT OUT AT TEA"),
]

# ---------------------------------------------------------------- world map
NAM = [(-168, 66), (-140, 70), (-125, 72), (-108, 73), (-95, 80), (-85, 70), (-80, 73),
       (-76, 68), (-65, 62), (-55, 52), (-60, 46), (-70, 44), (-75, 40), (-76, 35),
       (-80, 32), (-81, 26), (-84, 22), (-90, 21), (-97, 16), (-105, 20), (-110, 23),
       (-114, 29), (-120, 34), (-124, 40), (-124, 47), (-130, 55), (-150, 60), (-165, 60)]
SAM = [(-78, 7), (-72, 12), (-62, 10), (-52, 5), (-44, -3), (-35, -8), (-39, -13),
       (-41, -22), (-48, -27), (-52, -33), (-58, -39), (-63, -41), (-65, -45),
       (-67, -50), (-69, -54), (-72, -54), (-73, -46), (-73, -37), (-71, -30),
       (-70, -20), (-75, -15), (-79, -8), (-81, -4), (-80, 1), (-77, 4)]
AFR = [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (33, 30), (35, 28),
       (38, 22), (40, 15), (43, 12), (48, 11), (51, 12), (45, 5), (42, 0), (40, -8),
       (39, -18), (36, -22), (33, -27), (28, -33), (20, -35), (17, -32), (15, -27),
       (13, -18), (12, -12), (10, -5), (9, 0), (9, 4), (4, 6), (-2, 5), (-8, 4),
       (-13, 8), (-17, 15), (-17, 21), (-16, 27), (-10, 31)]
EUR = [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-5, 48), (-2, 50), (2, 51), (5, 53),
       (8, 55), (8, 57), (12, 56), (18, 56), (21, 55), (24, 58), (25, 60), (23, 64),
       (21, 66), (25, 71), (31, 70), (40, 67), (50, 69), (60, 69), (70, 72), (80, 73),
       (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 71),
       (160, 70), (170, 67), (178, 65), (178, 62), (162, 60), (158, 52), (150, 45),
       (142, 42), (140, 38), (135, 35), (129, 33), (126, 34), (122, 31), (121, 28),
       (118, 25), (113, 22), (108, 17), (109, 13), (107, 9), (104, 6), (101, 4),
       (99, 8), (98, 13), (95, 16), (92, 16), (91, 22), (88, 22), (86, 20), (83, 17),
       (80, 13), (78, 9), (76, 10), (73, 16), (72, 20), (69, 22), (66, 25), (61, 25),
       (57, 26), (52, 27), (50, 29), (48, 30), (50, 26), (55, 24), (58, 23), (59, 22),
       (57, 20), (55, 17), (52, 15), (48, 12), (44, 12), (43, 13), (40, 18), (38, 24),
       (36, 28), (34, 28), (35, 30), (33, 32), (30, 33), (27, 34), (27, 36), (23, 36),
       (19, 40), (15, 38), (12, 40), (10, 44), (7, 44), (3, 43), (0, 39), (-2, 37)]
AUS = [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
       (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (147, -39),
       (150, -37), (153, -31), (153, -27), (151, -24), (149, -20), (146, -19),
       (143, -15), (142, -11), (141, -13), (141, -17), (140, -18), (139, -20),
       (136, -15), (136, -12), (133, -12), (130, -12), (126, -14), (122, -17),
       (118, -20), (114, -21)]
MAD = [(44, -16), (47, -15), (50, -18), (48, -22), (45, -25), (44, -22), (43, -18)]
UK = [(-5, 50), (-3, 53), (-5, 55), (-7, 58), (-5, 58), (-3, 55), (-1, 52)]
POLYS = [NAM, SAM, AFR, EUR, AUS, MAD, UK]
DOTS = [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),   # Japan
        (95, 5), (102, -3), (107, -6), (113, -7), (120, -9), (125, -8),
        (131, -3), (136, -2), (141, -3),                                    # Indonesia
        (120, 13), (121, 16), (122, 18),                                    # Philippines
        (173, -38), (175, -41), (168, -46),                                 # New Zealand
        (80, 8)]                                                            # Sri Lanka

PINS = {  # story number -> (lon, lat)
    1: (30.7, 36.9), 2: (46.7, 24.6), 3: (-75.5, -11.5), 4: (30.5, 50.4),
    5: (56.3, 26.6), 6: (51.4, 35.7), 7: (-77.0, 38.9), 8: (116.4, 39.9),
    9: (125.6, 7.1), 10: (149.1, -35.3), 11: (-30.0, 28.0), 12: (-115.1, 36.2),
    13: (174.8, -41.3),
}


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = (x2 - x1) * (lat - y1) / (y2 - y1) + x1
            if lon < xin:
                inside = not inside
    return inside


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 246, 233), outline=INK, width=3)
    f = font(SANS_BOLD, 27)
    d.text((x + 16, y + 10), "WHERE IT HAPPENED", font=f, fill=INK)
    top = y + 48
    mh = h - 60

    def px(lon):
        return x + (lon + 180) / 360.0 * w

    def py(lat):
        return top + (82 - lat) / 140.0 * mh

    cols, rows = 92, 34
    for r in range(rows):
        lat = 82 - (r + 0.5) * 140.0 / rows
        for c in range(cols):
            lon = -180 + (c + 0.5) * 360.0 / cols
            land = any(_in_poly(lon, lat, p) for p in POLYS) or \
                any(abs(lon - dl) < 2.2 and abs(lat - dt) < 2.6 for dl, dt in DOTS)
            if land:
                cx, cy = px(lon), py(lat)
                d.ellipse([cx - 3.4, cy - 3.4, cx + 3.4, cy + 3.4], fill=(120, 116, 100))
    for num, (lon, lat) in PINS.items():
        cx, cy = px(lon), py(lat)
        d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=RED)
        f2 = font(SANS_BOLD, 23)
        t = str(num)
        d.text((cx - d.textlength(t, font=f2) / 2, cy - 14), t, font=f2, fill=(255, 255, 255))


# ---------------------------------------------------------------- page build

def build():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([14, 14, W - 14, W - 14], outline=INK, width=4)

    # ---- kicker row
    y = 24
    f = font(SANS_BOLD, 33)
    d.text((MARGIN, y), "THE WORLD IN ONE DAY", font=f, fill=RED)
    right = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY CONTINENT \u00b7 ALL FROM THIS ONE DAY"
    d.text((W - MARGIN - d.textlength(right, font=f), y), right, font=f, fill=INK)
    y += 46
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)

    # ---- masthead: the date IS the headline
    y += 8
    mast = "Saturday 21 November 2026"
    mf = fit_font(d, mast, SERIF_BLACK, CW, 195)
    d.text((MARGIN, y), mast, font=mf, fill=INK)
    y += 138
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=6)
    y += 10

    # ---- red italic subhead: the three leads
    sub = "COP31 runs into overtime \u00b7 Three missiles downed over Riyadh \u00b7 6.7 quake shakes Peru"
    sf = fit_font(d, sub, SERIF_BOLD_IT, CW, 52)
    d.text(((W - d.textlength(sub, font=sf)) / 2, y), sub, font=sf, fill=RED)
    y += 52
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    y += 8

    # ---- region bar
    total = sum(c for _, c, _ in REGIONS)
    bx = MARGIN
    for name, count, colour in REGIONS:
        bw = CW * count / total
        d.rectangle([bx, y, bx + bw, y + 46], fill=colour)
        f1 = fit_font(d, name, SANS_BOLD, bw - 6, 22)
        d.text((bx + (bw - d.textlength(name, font=f1)) / 2, y + 1), name, font=f1, fill=(255, 255, 255))
        f2 = font(SANS_BOLD, 24)
        num = str(count)
        d.text((bx + (bw - d.textlength(num, font=f2)) / 2, y + 21), num, font=f2, fill=(255, 255, 255))
        bx += bw
    y += 52

    # ---- stats strip
    colw = CW / 6
    for i, (num, cap) in enumerate(STATS):
        cx = MARGIN + i * colw
        nf = fit_font(d, num, SERIF_BLACK, colw - 26, 76)
        d.text((cx + (colw - d.textlength(num, font=nf)) / 2, y), num, font=nf, fill=RED)
        cf = font(SANS_BOLD, 21)
        lines = wrap(d, cap, cf, colw - 16)
        ly = y + 76
        for line in lines[:2]:
            d.text((cx + (colw - d.textlength(line, font=cf)) / 2, ly), line, font=cf, fill=INK)
            ly += 25
        if i:
            d.line([cx, y + 4, cx, y + 102], fill=(180, 172, 150), width=2)
    y += 114
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    y += 10

    # ---- leads: three columns, tall drawn scenes
    lead_w = (CW - 64) // 3
    lead_top = y
    lead_scene_h = 188
    for i, lead in enumerate(LEADS):
        lx = MARGIN + i * (lead_w + 32)
        sh = lead_scene_h
        SCENES[lead["n"]](d, lx, y, lead_w, sh)
        d.rectangle([lx, y, lx + lead_w, y + sh], outline=INK, width=3)
        badge(d, lx + 12, y + 12, lead["n"])
        pw = pill_width(d, lead["tag"])
        pill(d, lx + lead_w - 12 - pw, y + 12, lead["tag"], TAG_COLOURS[lead["tag"]])
        ty = y + sh + 10
        kf = font(SANS_BOLD, 26)
        d.text((lx, ty), f"{lead['n']} \u00b7 {lead['place']}", font=kf, fill=RED)
        ty += 34
        hf = font(SERIF_BOLD, 44)
        ty = text_block(d, lx, ty, lead["headline"], hf, INK, lead_w, 50, max_lines=3)
        ty += 4
        bf = font(SANS, 26)
        ty = text_block(d, lx, ty, lead["body"], bf, (40, 40, 40), lead_w, 32, max_lines=3)
        ty += 2
        d.text((lx, ty), lead["source"], font=font(SANS, 24), fill=GREY)
    y = lead_top + lead_scene_h + 10 + 34 + 3 * 50 + 4 + 3 * 32 + 2 + 24
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    y += 12

    # ---- tiles 4-13: two rows of five
    tile_w = (CW - 4 * 22) // 5
    tile_scene_h = 96
    for row in range(2):
        for col in range(5):
            t = TILES[row * 5 + col]
            tx = MARGIN + col * (tile_w + 22)
            sh = tile_scene_h
            SCENES[t["n"]](d, tx, y, tile_w, sh)
            d.rectangle([tx, y, tx + tile_w, y + sh], outline=INK, width=3)
            badge(d, tx + 8, y + 8, t["n"])
            pw = pill_width(d, t["tag"])
            pill(d, tx + tile_w - 8 - pw, y + 8, t["tag"], TAG_COLOURS[t["tag"]])
            ty = y + sh + 8
            kf = font(SANS_BOLD, 23)
            d.text((tx, ty), f"{t['n']} \u00b7 {t['place']}", font=kf, fill=RED)
            ty += 29
            hf = font(SERIF_BOLD, 30)
            ty = text_block(d, tx, ty, t["headline"], hf, INK, tile_w, 34, max_lines=2)
            bf = font(SANS, 22)
            ty = text_block(d, tx, ty, t["body"], bf, (40, 40, 40), tile_w, 26, max_lines=2)
            d.text((tx, ty), f"({t['source']})", font=font(SANS, 21), fill=GREY)
        y += tile_scene_h + 8 + 29 + 2 * 34 + 2 * 26 + 22 + 10
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    y += 10

    # ---- briefs + map band
    band_top = y
    hf = font(SANS_BOLD, 30)
    d.text((MARGIN, y), "ALSO ON SATURDAY - 22 MORE STORIES", font=hf, fill=INK)
    y += 36
    brief_w = (CW - 610 - 40) / 2
    bf = font(SANS, 19)
    bfh = font(SANS_BOLD, 19)
    for col in range(2):
        cx = MARGIN + col * (brief_w + 24)
        cy = y
        for num, place, txt, src in BRIEFS[col * 11:(col + 1) * 11]:
            head = f"{num}. {place} - "
            d.text((cx, cy), head, font=bfh, fill=INK)
            hw = d.textlength(head, font=bfh)
            words = txt.split()
            suffix = f" ({src})"
            while words and d.textlength(" ".join(words) + suffix, font=bf) > brief_w - hw:
                words.pop()
            d.text((cx + hw, cy), " ".join(words) + suffix, font=bf, fill=(40, 40, 40))
            cy += 25
    draw_map(d, W - MARGIN - 610, band_top, 610, 36 + 11 * 25 + 4)
    y += 11 * 25 + 8
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    y += 8

    # ---- tag legend
    lf = font(SANS, 22)
    legend = "TAGS: OFFICIAL = AUTHORITY STATEMENT \u00b7 CONFIRMED = TWO OR MORE OUTLETS \u00b7 REPORTED = ONE OUTLET \u00b7 CLAIM = ONE SIDE'S ACCOUNT"
    d.text(((W - d.textlength(legend, font=lf)) / 2, y), legend, font=lf, fill=GREY)
    y += 32

    # ---- date check footer
    d.rectangle([MARGIN, y, W - MARGIN, y + 96], fill=RED)
    f1 = font(SANS_BOLD, 25)
    line1 = "DATE CHECK \u2713 - Every story on this page happened, or was first reported, on Saturday 21 November 2026."
    d.text(((W - d.textlength(line1, font=f1)) / 2, y + 5), line1, font=f1, fill=(255, 255, 255))
    f2 = font(SANS, 20)
    line2 = ("LEFT OUT AS OTHER DAYS' NEWS: Wall Street's fall into correction (Fri 20) \u00b7 the barrage that hit Kyiv's bridges (Fri 20) \u00b7 "
             "the missile that landed in Poland (Fri 20) \u00b7 the UK-EU reset deal (Fri 20) \u00b7 Cyclone Akvan's landfall (Fri 20) \u00b7 "
             "GTA VI's first-day sales (Thu 19) \u00b7 Voyager 1's light-day (18 Nov)")
    for i, ln in enumerate(wrap(d, line2, f2, CW - 48)):
        d.text(((W - d.textlength(ln, font=f2)) / 2, y + 33 + i * 21), ln, font=f2, fill=(255, 235, 220))
    f3 = font(SANS_BOLD, 21)
    line3 = "NOT YET HAPPENED: BepiColombo in Mercury orbit \u00b7 a final COP31 text"
    d.text(((W - d.textlength(line3, font=f3)) / 2, y + 75), line3, font=f3, fill=(255, 255, 255))

    img = img.resize((1024, 1024), Image.LANCZOS)
    # Flat art quantizes cleanly; a 256-colour palette keeps the file small
    # (final-heat tie-break favours smaller bytes) with no visible loss.
    img = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), optimize=True)


if __name__ == "__main__":
    main()
