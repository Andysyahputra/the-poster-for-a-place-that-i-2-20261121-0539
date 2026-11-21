#!/usr/bin/env python3
"""SOLMARA — Where the Sun Sets Twice.

A travel poster for an invented place, drawn entirely in code with PIL.
Writes /output/entry.png (1024x1024, deterministic: no randomness, no
timestamps, fixed geometry and palette).

Place: SOLMARA, a cliffside town on a warm sea where two suns hang low
over the water at dusk, so every evening has two sunsets. Landmark: a
tall spiral lighthouse on the highest cliff.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
HORIZON = 640
OUT = "/output/entry.png"

# Palette: indigo, violet, amber, teal, cream.
INDIGO = (22, 24, 68)
VIOLET = (88, 58, 138)
AMBER = (246, 164, 82)
GOLD = (252, 196, 110)
PALE_GOLD = (250, 224, 160)
CREAM = (250, 236, 205)
TEAL = (16, 96, 104)
DEEP_TEAL = (10, 58, 66)
CLIFF = (24, 20, 46)
CLIFF_EDGE = (38, 32, 70)
SUN_CORE = (255, 190, 90)
LAMP = (255, 214, 120)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(width, height, stops):
    """Vertical gradient from a list of (position 0..1, color) stops."""
    col = Image.new("RGB", (1, height))
    px = []
    for y in range(height):
        t = y / max(height - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                px.append(lerp(c0, c1, f))
                break
        else:
            px.append(stops[-1][1])
    col.putdata(px)
    return col.resize((width, height))


def load_font(size, bold=True):
    """Best available elegant serif; fall back through known system paths."""
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def glow_disc(base, cx, cy, radius, color, peak_alpha=235):
    """Soft radial glow: concentric discs fading outward, then blurred."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 24
    for i in range(steps, 0, -1):
        r = radius * (1.0 + 0.9 * (steps - i) / steps)
        a = int(peak_alpha * (i / steps) ** 2 * 0.55)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=color + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    base.alpha_composite(layer)


def draw_bird(d, x, y, s, color):
    """One simple dark bird: two short strokes meeting at a point."""
    d.line([(x - s, y + s * 0.45), (x, y), (x + s, y + s * 0.45)],
           fill=color, width=3)
    d.line([(x - s * 0.55, y + s * 0.75), (x, y + s * 0.28),
            (x + s * 0.55, y + s * 0.75)], fill=color, width=2)


def draw_boat(d, x, y, scale, hull=(18, 16, 40)):
    """Small sailboat: dark hull, pale sail, thin mast."""
    w = 46 * scale
    h = 34 * scale
    # sail (pale, catching the sunset)
    d.polygon([(x, y - h), (x, y - 4 * scale),
               (x + w * 0.55, y - 4 * scale)], fill=(248, 226, 180))
    d.polygon([(x - 2 * scale, y - h * 0.72), (x - 2 * scale, y - 4 * scale),
               (x - w * 0.42, y - 4 * scale)], fill=(214, 176, 140))
    # mast
    d.line([(x, y - h), (x, y)], fill=hull, width=max(2, int(3 * scale)))
    # hull
    d.polygon([(x - w * 0.62, y), (x + w * 0.62, y),
               (x + w * 0.38, y + 12 * scale),
               (x - w * 0.38, y + 12 * scale)], fill=hull)


def main():
    img = Image.new("RGBA", (W, H), INDIGO + (255,))

    # --- Sky: deep indigo -> violet -> warm amber at the horizon.
    sky = vgrad(W, HORIZON, [
        (0.00, INDIGO),
        (0.42, (58, 44, 112)),
        (0.68, VIOLET),
        (0.88, (196, 106, 96)),
        (1.00, AMBER),
    ])
    img.paste(sky, (0, 0))

    # --- Sea: amber at the horizon deepening to teal at the bottom.
    sea = vgrad(W, H - HORIZON, [
        (0.00, (238, 158, 88)),
        (0.18, (120, 130, 110)),
        (0.55, TEAL),
        (1.00, DEEP_TEAL),
    ])
    img.paste(sea, (0, HORIZON))

    # --- Faint early stars in the deep indigo top.
    d = ImageDraw.Draw(img, "RGBA")
    for (sx, sy, sr) in [(120, 60, 2), (300, 42, 2), (880, 70, 2),
                         (940, 150, 2), (60, 190, 2), (520, 36, 1),
                         (760, 110, 1), (180, 130, 1)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=CREAM + (150,))

    # --- The two suns, low over the sea.
    glow_disc(img, 610, 598, 76, (255, 170, 70), peak_alpha=200)
    glow_disc(img, 758, 552, 42, (250, 210, 120), peak_alpha=180)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([610 - 76, 598 - 76, 610 + 76, 598 + 76], fill=SUN_CORE)
    d.ellipse([758 - 42, 552 - 42, 758 + 42, 552 + 42], fill=PALE_GOLD)
    # thin bright rims where the suns meet the sea haze
    d.ellipse([610 - 76, 598 - 76, 610 + 76, 598 + 76],
              outline=(255, 226, 160), width=3)

    # --- Sunlight streaks on the water under each sun.
    streak = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(streak)
    for (cx, y0, wdt, a) in [(610, 660, 150, 130), (610, 700, 210, 100),
                             (610, 748, 260, 80), (610, 806, 300, 60),
                             (758, 660, 90, 110), (758, 700, 130, 80),
                             (758, 752, 170, 55)]:
        sd.rectangle([cx - wdt // 2, y0, cx + wdt // 2, y0 + 7],
                     fill=(252, 196, 110, a))
    streak = streak.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(streak)

    # --- Sailboats coming home.
    d = ImageDraw.Draw(img, "RGBA")
    draw_boat(d, 430, 742, 0.8)
    draw_boat(d, 700, 812, 1.15)
    draw_boat(d, 560, 905, 0.68)
    # their reflections
    for (cx, y0, wdt) in [(430, 762, 60), (700, 838, 90), (560, 923, 48)]:
        d.rectangle([cx - wdt // 2, y0, cx + wdt // 2, y0 + 4],
                    fill=(252, 196, 110, 90))

    # --- Cliffs: dark silhouetted headlands, left high, right low.
    d = ImageDraw.Draw(img, "RGBA")
    left_cliff = [(0, H), (0, 768), (58, 706), (148, 648), (205, 566),
                  (238, 512), (288, 520), (318, 612), (356, 700),
                  (382, 788), (396, H)]
    d.polygon(left_cliff, fill=CLIFF)
    d.line(left_cliff[:-1], fill=CLIFF_EDGE, width=3, joint="curve")
    right_cliff = [(W, H), (W, 792), (958, 726), (872, 692), (806, 736),
                   (782, 812), (776, H)]
    d.polygon(right_cliff, fill=CLIFF)
    d.line(right_cliff[:-1], fill=CLIFF_EDGE, width=3, joint="curve")

    # --- Town windows: a small village of tiny lit windows, two loose
    # rows tucked under the lighthouse on the cliff face.
    for (wx, wy) in [(140, 640), (178, 632), (216, 644), (252, 636),
                     (288, 648), (158, 668), (198, 676), (240, 668),
                     (282, 676), (120, 700), (330, 700)]:
        d.rectangle([wx - 2, wy - 3, wx + 2, wy + 3], fill=(255, 205, 110))
        d.ellipse([wx - 5, wy - 6, wx + 5, wy + 6],
                  fill=(255, 205, 110, 45))

    # --- The spiral lighthouse on the highest cliff.
    # Tower: tapered, base y=516, top y=330, centred on x=252.
    tower = [(228, 516), (276, 516), (264, 330), (240, 330)]
    # spiral band: diagonal stripes clipped to the tower shape.
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.polygon(tower, fill=255)
    stripes = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stripes)
    for k in range(-2, 6):
        y0 = 330 + k * 32
        sdraw.polygon([(222, y0), (282, y0 + 26), (282, y0 + 44),
                       (222, y0 + 18)], fill=(196, 84, 96, 255))
    stripes.putalpha(Image.composite(stripes.split()[3], Image.new("L", img.size, 0), mask))
    img.alpha_composite(stripes)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(tower, outline=(250, 236, 205), width=3)
    # lamp room + dome
    d.rectangle([236, 300, 268, 332], fill=(30, 24, 54))
    d.rectangle([232, 296, 272, 302], fill=(250, 236, 205))
    d.pieslice([238, 282, 266, 306], 180, 360, fill=(250, 236, 205))
    # lamp glow
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([222, 286, 282, 346], fill=(255, 214, 120, 200))
    gd.ellipse([236, 300, 268, 332], fill=(255, 236, 170, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(glow)
    # beam sweeping across the water to the right
    beam = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(268, 308), (268, 326), (1024, 452), (1024, 396)],
               fill=(255, 220, 130, 44))
    beam = beam.filter(ImageFilter.GaussianBlur(4))
    img.alpha_composite(beam)

    # --- Birds in the upper sky.
    d = ImageDraw.Draw(img, "RGBA")
    bird_color = (26, 22, 52, 235)
    for (bx, by, bs) in [(700, 170, 13), (748, 148, 11), (660, 196, 10),
                         (800, 190, 9), (620, 150, 8), (140, 352, 11),
                         (104, 316, 9)]:
        draw_bird(d, bx, by, bs, bird_color)

    # --- Type: SOLMARA, large serif capitals; tagline spaced beneath.
    title_font = load_font(118)
    tag_font = load_font(30)
    d = ImageDraw.Draw(img, "RGBA")
    title = "SOLMARA"
    bbox = d.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) // 2 - bbox[0]
    ty = 96
    # soft shadow to lift the name off the sky
    d.text((tx + 3, ty + 4), title, font=title_font, fill=(20, 16, 50, 220))
    d.text((tx, ty), title, font=title_font, fill=CREAM)

    tag = "WHERE THE SUN SETS TWICE"
    # letter-spaced small capitals, drawn one glyph at a time
    widths = [d.textlength(ch, font=tag_font) for ch in tag]
    gap = 7
    total = sum(widths) + gap * (len(tag) - 1)
    x = (W - total) // 2
    ty2 = 232
    for ch, wch in zip(tag, widths):
        d.text((x, ty2), ch, font=tag_font, fill=(250, 236, 205, 235))
        x += wch + gap
    # thin rule under the tagline
    d.line([(W // 2 - 150, 292), (W // 2 + 150, 292)],
           fill=CREAM + (170,), width=2)

    # --- Thin cream frame, inset from the edge: the classic travel
    # poster finish; it holds the whole composition together.
    d.rectangle([28, 28, W - 29, H - 29], outline=CREAM + (130,), width=3)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.convert("RGB").save(OUT, format="PNG", optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
