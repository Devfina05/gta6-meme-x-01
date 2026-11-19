#!/usr/bin/env python3
"""GTA 6 loading-screen meme generator (original art, drawn in code).

Draws a 1080x1080 meme: a Vice City sunset where the make.fun ghost waits
on the beach for GTA 6 while the loading bar sits at 99% -- since 2013.
Everything is procedural Pillow drawing: no photos, no copied art, no
downloaded assets. The ghost is drawn from the make.fun mascot description
(white ghost, thick black outline, black four-pointed sparkle eyes, round
little hand holding a magenta coin with a white star).

Usage:  python3 meme/generate_meme.py [--out meme/meme.png]
"""
import argparse
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1080
SKY_TOP = (43, 16, 85)       # deep violet
SKY_MID = (146, 43, 120)     # magenta dusk
SKY_LOW = (255, 126, 95)     # orange sunset
SKY_HORIZON = (254, 180, 123)
SEA = (64, 32, 96)
SEA_LIGHT = (255, 150, 110)
SAND = (232, 190, 138)
SAND_DARK = (214, 164, 110)
SILHOUETTE = (26, 11, 46)
MAGENTA = (255, 46, 136)
WHITE = (255, 255, 255)
BLACK = (10, 10, 16)
SUN = (255, 236, 170)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, stops):
    """stops: list of (y_fraction, rgb). Pure-PIL fallback, no numpy needed."""
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    n = size[1]
    for y in range(n):
        f = y / max(n - 1, 1)
        for i in range(len(stops) - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                t = 0 if f1 == f0 else (f - f0) / (f1 - f0)
                d.line([(0, y), (size[0], y)], fill=lerp(c0, c1, t))
                break
        else:
            d.line([(0, y), (size[0], y)], fill=stops[-1][1])
    return img


def star4(cx, cy, r_long, r_short):
    """Four-pointed sparkle: 8 polygon points, long N/E/S/W, short diagonals."""
    pts = []
    for k in range(8):
        ang = math.pi / 2 + k * math.pi / 4
        r = r_long if k % 2 == 0 else r_short
        pts.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))
    return pts


def star5(cx, cy, r_outer, r_inner):
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        r = r_outer if k % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def text_centered(draw, cx, y, text, font, fill, outline=None, outline_w=6):
    """Draw text centred on cx, top at y, with an optional thick outline."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = cx - w // 2 - bbox[0]
    if outline is not None:
        for dx in range(-outline_w, outline_w + 1, 2):
            for dy in range(-outline_w, outline_w + 1, 2):
                if dx * dx + dy * dy <= outline_w * outline_w:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


def draw_palm(draw, base_x, base_y, height, lean, flip=False):
    """A dark palm silhouette: curved trunk + drooping fronds."""
    top_x = base_x + lean
    top_y = base_y - height
    # Trunk as a chain of thick segments along a gentle curve.
    steps = 12
    prev = (base_x, base_y)
    for i in range(1, steps + 1):
        t = i / steps
        x = base_x + lean * t * t + (6 if flip else -6) * math.sin(t * math.pi)
        y = base_y - height * t
        draw.line([prev, (x, y)], fill=SILHOUETTE, width=max(10, int(16 * (1 - t * 0.6))))
        prev = (x, y)
    # Fronds: drooping quadratic curves from the crown, one per direction.
    for spread in [-110, -70, -30, 10, 55, 95]:
        direction = -1 if flip else 1
        reach = 95 - abs(spread) // 3
        end_x = top_x + direction * reach * math.cos(math.radians(spread * 0.55))
        end_y = top_y + 34 + abs(spread) // 2
        ctrl_x = top_x + direction * reach * 0.55
        ctrl_y = top_y - 52
        pts = []
        for i in range(11):
            t = i / 10
            x = (1 - t) ** 2 * top_x + 2 * (1 - t) * t * ctrl_x + t * t * end_x
            y = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * ctrl_y + t * t * end_y
            pts.append((x, y))
        draw.line(pts, fill=SILHOUETTE, width=9, joint="curve")
    # Coconuts.
    draw.ellipse([top_x - 12, top_y + 2, top_x + 2, top_y + 16], fill=SILHOUETTE)
    draw.ellipse([top_x + 2, top_y + 4, top_x + 16, top_y + 18], fill=SILHOUETTE)


def draw_ghost(draw, cx, top, width, height):
    """The make.fun ghost: white body, thick black outline, sparkle eyes,
    one round hand raised holding a magenta coin with a white star."""
    x0, x1 = cx - width // 2, cx + width // 2
    dome_r = width // 2
    hem_y = top + height - 46  # where the scalloped hem starts
    # Black outline: same shapes, expanded outward.
    pad = 10
    draw.pieslice([x0 - pad, top - pad, x1 + pad, top + 2 * dome_r + pad],
                  180, 360, fill=BLACK)
    draw.rectangle([x0 - pad, top + dome_r, x1 + pad, hem_y + pad], fill=BLACK)
    for i in range(3):
        bx = x0 + i * width // 3
        draw.ellipse([bx - pad, hem_y - 6, bx + width // 3 + pad, hem_y + 46 + pad],
                     fill=BLACK)
    # White body.
    draw.pieslice([x0, top, x1, top + 2 * dome_r], 180, 360, fill=WHITE)
    draw.rectangle([x0, top + dome_r, x1, hem_y], fill=WHITE)
    for i in range(3):
        bx = x0 + i * width // 3
        draw.ellipse([bx, hem_y - 6, bx + width // 3, hem_y + 46], fill=WHITE)
    # Sparkle eyes.
    eye_y = top + int(height * 0.34)
    eye_dx = int(width * 0.20)
    for ex in (cx - eye_dx, cx + eye_dx):
        draw.polygon(star4(ex, eye_y, 26, 8), fill=BLACK)
    # Tiny smile.
    draw.arc([cx - 26, eye_y + 42, cx + 26, eye_y + 82], 20, 160,
             fill=BLACK, width=5)
    # Raised round hand on the right, holding the magenta star coin.
    hx, hy = x1 - 6, top + int(height * 0.52)
    draw.ellipse([hx - 26, hy - 26, hx + 26, hy + 26], fill=WHITE,
                 outline=BLACK, width=6)
    coin_cx, coin_cy, coin_r = hx + 34, hy - 44, 40
    draw.ellipse([coin_cx - coin_r - 5, coin_cy - coin_r - 5,
                  coin_cx + coin_r + 5, coin_cy + coin_r + 5], fill=BLACK)
    draw.ellipse([coin_cx - coin_r, coin_cy - coin_r,
                  coin_cx + coin_r, coin_cy + coin_r], fill=MAGENTA)
    draw.polygon(star5(coin_cx, coin_cy, 26, 11), fill=WHITE)


def build():
    rng = random.Random(6)
    img = vertical_gradient((W, H), [
        (0.00, SKY_TOP), (0.35, SKY_MID), (0.52, SKY_LOW), (0.60, SKY_HORIZON),
    ])
    d = ImageDraw.Draw(img, "RGBA")

    # Sun with a soft glow, low on the horizon.
    sun_cx, sun_cy, sun_r = 540, 560, 108
    for r, alpha in ((260, 28), (200, 40), (150, 60)):
        d.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r],
                  fill=SUN + (alpha,))
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=SUN)

    # Ocean band with light streaks reflecting the sunset.
    d.rectangle([0, 600, W, 760], fill=SEA)
    for _ in range(26):
        y = rng.randint(612, 748)
        x = rng.randint(40, W - 320)
        length = rng.randint(60, 300)
        d.line([(x, y), (x + length, y)], fill=SEA_LIGHT + (rng.randint(60, 150),),
               width=rng.choice([2, 3, 4]))

    # Skyline silhouette on the horizon, a few windows lit.
    x = -20
    while x < W + 20:
        bw = rng.randint(46, 110)
        bh = rng.randint(40, 130)
        d.rectangle([x, 600 - bh, x + bw, 600], fill=SILHOUETTE)
        for _ in range(rng.randint(1, 5)):
            wx = rng.randint(x + 6, x + bw - 10)
            wy = rng.randint(600 - bh + 8, 592)
            d.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 209, 102))
        x += bw + rng.randint(4, 26)

    # Sand.
    d.rectangle([0, 760, W, H], fill=SAND)
    d.rectangle([0, 760, W, 772], fill=SAND_DARK)
    for _ in range(40):
        sx = rng.randint(0, W)
        sy = rng.randint(780, H - 8)
        d.ellipse([sx, sy, sx + 5, sy + 3], fill=SAND_DARK)

    # Palm silhouettes framing the scene, crowns above the skyline.
    draw_palm(d, 96, 800, 360, 46)
    draw_palm(d, 1000, 812, 360, -40, flip=True)

    # Beach towel under the ghost, carrying the make.fun name.
    towel = [330, 968, 750, 1052]
    d.rounded_rectangle(towel, radius=18, fill=(255, 255, 255))
    d.rounded_rectangle(towel, radius=18, outline=MAGENTA, width=6)
    # Stripe along the towel's bottom edge, clear of the name above it.
    d.line([(336, 1038), (744, 1038)], fill=MAGENTA, width=6)
    font_towel = load_font(58)
    text_centered(d, 540, 974, "make.fun", font_towel, MAGENTA)

    # The ghost waits on the towel, coin in hand.
    draw_ghost(d, 540, 620, 300, 360)

    # Captions: big, outlined, readable even at 480 px.
    font_title = load_font(168)
    text_centered(d, 540, 58, "GTA 6", font_title, WHITE, outline=BLACK,
                  outline_w=10)
    font_load = load_font(92)
    text_centered(d, 540, 252, "LOADING…", font_load, WHITE, outline=BLACK,
                  outline_w=8)
    # Progress bar, stuck at 99%.
    bar = [160, 372, 920, 418]
    d.rounded_rectangle(bar, radius=23, outline=WHITE, width=5)
    d.rounded_rectangle([166, 378, 166 + int(748 * 0.99), 412], radius=17,
                        fill=MAGENTA)
    font_sub = load_font(56)
    text_centered(d, 540, 440, "99% — SINCE 2013", font_sub, WHITE,
                  outline=BLACK, outline_w=7)
    return img


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="meme/meme.png")
    args = ap.parse_args(argv)
    img = build()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    print(f"wrote {out} {img.size} {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
