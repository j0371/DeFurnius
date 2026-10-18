"""Sprites for effects, HUD pieces, skies and floor decals (numpy + Pillow)."""
import math

import numpy as np
from PIL import Image, ImageDraw

from . import emblems, tex

FIRE_RAMP = [(40, 6, 4), (150, 24, 8), (240, 90, 16), (255, 170, 40), (255, 230, 150), (255, 255, 235)]


def _rgba(rgb, alpha):
    out = np.zeros(alpha.shape + (4,), dtype=np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(alpha, 255, 0)
    return Image.fromarray(out, "RGBA")


def fire_sheet(frames=16, cell=64, seed=21):
    """4x4 sheet of looping flame frames (bottom-anchored teardrop)."""
    rng = np.random.default_rng(seed)
    n1 = tex.fbm(cell, 4, rng, 3)
    n2 = tex.fbm(cell, 8, rng, 2)
    cols = 4
    rows = frames // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:cell, 0:cell] / cell
    y = 1 - yy                                    # 0 at the bottom of the frame
    for f in range(frames):
        t = f / frames
        a = np.roll(n1, int(-t * cell), axis=0)    # noise scrolls upward, tiles seamlessly over the loop
        b = np.roll(n2, int(-2 * t * cell), axis=0)
        width = 0.34 * (1 - y) ** 0.7 + 0.04
        shape = np.exp(-((xx - 0.5 + 0.08 * (a - 0.5)) / width) ** 2)
        heat = shape * (0.95 - 0.85 * y ** 1.2) * (0.55 + 0.7 * a * 0.6 + 0.4 * b * 0.5)
        idx = np.clip(np.floor(heat * 7.0), 0, len(FIRE_RAMP) - 1).astype(int)
        rgb = np.array(FIRE_RAMP, dtype=np.uint8)[idx]
        alpha = heat > 0.16
        sheet.paste(_rgba(rgb, alpha), ((f % cols) * cell, (f // cols) * cell))
    return sheet


def ember_sprites(size=16):
    sheet = Image.new("RGBA", (size * 4, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    c = size // 2
    hot, mid = (255, 230, 150, 255), (255, 120, 30, 255)
    d.ellipse([c - 3, c - 3, c + 2, c + 2], fill=mid)
    d.ellipse([c - 1, c - 1, c + 1, c + 1], fill=hot)
    o = size
    d.polygon([(o + c, 2), (o + size - 3, c), (o + c, size - 3), (o + 3, c)], fill=mid)
    d.rectangle([o + c - 1, c - 1, o + c, c], fill=hot)
    o = size * 2
    d.rectangle([o + c - 1, 2, o + c, size - 3], fill=mid)
    d.rectangle([o + 2, c - 1, o + size - 3, c], fill=mid)
    d.rectangle([o + c - 1, c - 1, o + c, c], fill=hot)
    o = size * 3
    d.rectangle([o + c - 1, c - 1, o + c, c], fill=hot)
    for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0)):
        d.point((o + c + dx, c + dy), fill=mid)
    return sheet


def smoke_sheet(cell=64, frames=4, seed=5):
    rng = np.random.default_rng(seed)
    n = tex.fbm(cell, 4, rng, 3)
    sheet = Image.new("RGBA", (cell * frames, cell), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:cell, 0:cell] / cell
    d = np.hypot(xx - 0.5, yy - 0.5)
    for f in range(frames):
        r = 0.16 + 0.1 * f
        dens = np.clip((r - d) / r, 0, 1) * (0.6 + 0.6 * np.roll(n, f * 9, axis=1)) * (1 - f * 0.18)
        shade = np.clip(np.floor(dens * 4), 0, 3).astype(int)
        grey = np.array([(30, 28, 28), (58, 54, 52), (92, 86, 82), (130, 122, 118)], dtype=np.uint8)[shade]
        bayer = np.tile(tex.BAYER4, (cell // 4, cell // 4))
        sheet.paste(_rgba(grey, dens > 0.12 + 0.18 * bayer * (0.4 + 0.2 * f)), (f * cell, 0))
    return sheet


def spark_burst(size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    for k in range(8):
        a = math.radians(k * 45 + 22)
        r = c - 2 if k % 2 == 0 else c * 0.6
        d.line([(c, c), (c + math.cos(a) * r, c + math.sin(a) * r)], fill=(255, 220, 140, 255),
               width=3 if k % 2 == 0 else 2)
    d.ellipse([c - 6, c - 6, c + 6, c + 6], fill=(255, 250, 220, 255))
    return img


def snow_sprites(size=32):
    sheet = Image.new("RGBA", (size * 3, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    c = size // 2
    white = (245, 250, 255, 255)
    for i in range(3):
        o = i * size
        arms = (4, 6, 8)[i]
        for k in range(arms):
            a = math.pi * 2 * k / arms
            e = (o + c + math.cos(a) * (c - 3), c + math.sin(a) * (c - 3))
            d.line([(o + c, c), e], fill=white, width=1)
            if i > 0:
                mid = (o + c + math.cos(a) * (c / 2), c + math.sin(a) * (c / 2))
                for s in (-0.5, 0.5):
                    d.line([mid, (mid[0] + math.cos(a + s) * 4, mid[1] + math.sin(a + s) * 4)], fill=white, width=1)
        d.rectangle([o + c - 1, c - 1, o + c, c], fill=white)
    return sheet


def parry_flash(color, size=256):
    """Expanding ring plus soft flash for a successful parry. Hard-edged for the retro look."""
    yy, xx = np.mgrid[0:size, 0:size] / size
    d = np.hypot(xx - 0.5, yy - 0.5) * 2
    ring = (d > 0.78) & (d < 0.9)
    spokes = (np.abs(np.sin(np.arctan2(yy - 0.5, xx - 0.5) * 8)) < 0.12) & (d > 0.3) & (d < 0.78)
    core = d < 0.14
    bayer = np.tile(tex.BAYER4, (size // 4, size // 4))
    glow = (d < 0.6) & (bayer * 0.6 + 0.4 > d / 0.6)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    arr[glow] = (*color, 120)
    arr[ring | spokes] = (*color, 255)
    arr[core] = (255, 255, 255, 255)
    return Image.fromarray(arr, "RGBA")


def vignette(color, size=256):
    """Screen-edge overlay: clear in the middle, dithered toward opaque at the corners."""
    yy, xx = np.mgrid[0:size, 0:size] / size
    r = np.hypot(xx - 0.5, yy - 0.5) * 2 / math.sqrt(2)            # 0 centre, 1 corner
    p = np.clip((r - 0.5) / 0.5, 0, 1)
    bayer = np.tile(tex.BAYER4, (size // 4, size // 4))
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    arr[..., :3] = color
    arr[..., 3] = np.where(p > bayer, 210, 0)
    return Image.fromarray(arr, "RGBA")


# ---- HUD ------------------------------------------------------------------------------------------------------
def crosshairs(color=(255, 245, 220), size=64):
    """Four designs as one 4-wide sheet: dot-cross, claw ticks, ring and pips, chevrons."""
    sheet = Image.new("RGBA", (size * 4, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    c = size // 2
    col = tuple(color) + (255,)
    # 1: classic dot with gapped cross
    d.rectangle([c - 1, c - 1, c, c], fill=col)
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        for s in range(5, 12):
            d.point((c + dx * s, c + dy * s), fill=col)
            d.point((c + dx * s - (dy != 0) * 0, c + dy * s), fill=col)
    # 2: five claw ticks (the hand's five fingers) fanned above the centre
    o = size
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 22)
        d.line([(o + c + math.cos(a) * 8, c + math.sin(a) * 8), (o + c + math.cos(a) * 18, c + math.sin(a) * 18)],
               fill=col, width=2)
    d.rectangle([o + c - 1, c - 1, o + c, c], fill=col)
    # 3: ring with pips
    o = size * 2
    d.ellipse([o + c - 14, c - 14, o + c + 14, c + 14], outline=col, width=2)
    for k in range(4):
        a = math.radians(90 * k)
        d.rectangle([o + c + math.cos(a) * 18 - 1, c + math.sin(a) * 18 - 1,
                     o + c + math.cos(a) * 18 + 1, c + math.sin(a) * 18 + 1], fill=col)
    d.rectangle([o + c - 1, c - 1, o + c, c], fill=col)
    # 4: four chevrons pointing in
    o = size * 3
    for k in range(4):
        a = math.radians(90 * k)
        p = (o + c + math.cos(a) * 14, c + math.sin(a) * 14)
        l = (p[0] - math.cos(a) * 6 + math.sin(a) * 5, p[1] - math.sin(a) * 6 - math.cos(a) * 5)
        r = (p[0] - math.cos(a) * 6 - math.sin(a) * 5, p[1] - math.sin(a) * 6 + math.cos(a) * 5)
        d.line([l, p, r], fill=col, width=2)
    return sheet


def _segmented(w, h, segs, color_fn, gap=2):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sw = (w - gap * (segs - 1)) / segs
    for i in range(segs):
        x0 = i * (sw + gap)
        d.rectangle([x0, 0, x0 + sw - 1, h - 1], fill=color_fn(i / max(segs - 1, 1)) + (255,))
    return img


def rage_bar_horizontal(core, w=256, h=28):
    """Frame (with an empty well) and fill, as two images. Fill is segmented, ember to white-hot."""
    r = core["ramp"]
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rectangle([0, 0, w - 1, h - 1], fill=tuple(r[1]) + (255,), outline=tuple(r[4]) + (255,), width=2)
    d.rectangle([5, 5, w - 6, h - 6], fill=(6, 4, 4, 255), outline=tuple(r[0]) + (255,))
    for x in (0, w - 6):                                    # horn nubs
        d.polygon([(x, 0), (x + 6, 0), (x + 3, -0)], fill=tuple(r[4]) + (255,))
    fill = _segmented(w - 12, h - 12, 20, lambda t: tuple(int(a + (b - a) * t) for a, b in
                                                              zip(core["accent"], core["glow"])))
    return frame, fill


def rage_bar_vertical(core, w=40, h=200):
    r = core["ramp"]
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rectangle([8, 0, w - 9, h - 1], fill=tuple(r[1]) + (255,), outline=tuple(r[4]) + (255,), width=2)
    d.rectangle([13, 5, w - 14, h - 6], fill=(6, 4, 4, 255))
    for y in range(10, h - 8, 20):                          # tick marks
        d.line([(0, y), (7, y)], fill=tuple(r[4]) + (255,), width=2)
    fill = _segmented(h - 10, w - 26, 16, lambda t: tuple(int(a + (b - a) * t) for a, b in
                                                          zip(core["accent"], core["glow"]))).rotate(90, expand=True)
    return frame, fill


def rage_dial(core, size=128):
    """Circular 24-segment dial. Returns (frame, fill_segments list of 24 RGBA tiles)."""
    r = core["ramp"]
    frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.ellipse([2, 2, size - 3, size - 3], outline=tuple(r[4]) + (255,), width=3)
    d.ellipse([size // 2 - 22, size // 2 - 22, size // 2 + 22, size // 2 + 22], fill=tuple(r[1]) + (255,),
              outline=tuple(r[4]) + (255,), width=2)
    fills = []
    for i in range(24):
        t = i / 23
        col = tuple(int(a + (b - a) * t) for a, b in zip(core["accent"], core["glow"])) + (255,)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        di = ImageDraw.Draw(img)
        a0 = -90 + i * 15 + 1.5
        di.pieslice([8, 8, size - 9, size - 9], a0, a0 + 12, fill=col)
        di.ellipse([size // 2 - 30, size // 2 - 30, size // 2 + 30, size // 2 + 30], fill=(0, 0, 0, 0))
        fills.append(img)
    return frame, fills


def boss_bar(core, w=512, h=40, bright=False):
    """Boss health bar frame and fill. `bright` is the Treachery inversion."""
    r = core["ramp"]
    bg = (235, 240, 245) if bright else (8, 6, 8)
    edge = tuple(r[0] if bright else r[4])
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rectangle([14, 6, w - 15, h - 7], fill=bg + (255,), outline=edge + (255,), width=2)
    for side in (0, 1):                                     # orb-like end caps (the ego)
        cx = 14 if side == 0 else w - 15
        d.ellipse([cx - 13, h // 2 - 13, cx + 13, h // 2 + 13], fill=tuple(r[1]) + (255,), outline=edge + (255,),
                  width=2)
        d.ellipse([cx - 5, h // 2 - 5, cx + 5, h // 2 + 5], fill=(255, 255, 255, 255) if bright else
                  tuple(r[5]) + (255,))
    col = (r[0] if bright else core["accent"])
    fill = Image.new("RGBA", (w - 36, h - 18), tuple(col) + (255,))
    fd = ImageDraw.Draw(fill)
    for x in range(0, fill.width, 8):                       # scanline dither for texture
        fd.line([(x, 0), (x, fill.height)], fill=tuple(int(c * 0.82) for c in col) + (255,))
    return frame, fill


# ---- skies and decals -----------------------------------------------------------------------------------------------
def sky(core, w=512, h=256, seed=3):
    rng = np.random.default_rng(seed)
    r = core["ramp"]
    yy = np.linspace(0, 1, h)[:, None]                      # 0 = zenith
    n = tex.fbm(w, 3, rng, 4)[:h]
    if core["kind"] == "hell":
        v = 0.05 + 0.22 * yy ** 2 + 0.16 * (n - 0.5)
        horizon = np.exp(-((yy - 0.92) / 0.12) ** 2) * 0.7
        rgb = tex.shade(np.clip(v + horizon * 0.3, 0, 1), r, dither=1.0)
        bayer = np.tile(tex.BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
        hot = horizon * (0.45 + n) > 0.3 + bayer * 0.35                # dithered glow band, not a solid fill
        rgb[hot] = core["accent"]
        for _ in range(140):                                # drifting embers
            x, y = rng.integers(0, w), rng.integers(0, int(h * 0.9))
            rgb[y, x] = core["glow"]
    else:
        v = 0.9 - 0.3 * yy + 0.15 * (n - 0.5)
        rgb = tex.shade(np.clip(v, 0, 1), r, dither=1.0)
        for _ in range(220):
            x, y = rng.integers(0, w), rng.integers(0, h)
            rgb[y, x] = r[-1]
    return tex.to_image(rgb)


def floor_decal(core, which, size=256):
    """Big arena-centre sigil: ring, rune ticks and the poison animal, accent colour on transparent."""
    col = tuple(core["accent"]) + (255,)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size // 2
    d.ellipse([6, 6, size - 7, size - 7], outline=col, width=5)
    d.ellipse([22, 22, size - 23, size - 23], outline=col, width=2)
    for k in range(24):
        a = math.radians(15 * k)
        r0, r1 = (c - 28, c - 14) if k % 2 == 0 else (c - 22, c - 14)
        d.line([(c + math.cos(a) * r0, c + math.sin(a) * r0), (c + math.cos(a) * r1, c + math.sin(a) * r1)],
               fill=col, width=3)
    em = emblems.render(which, core["accent"]).resize((128, 128), Image.NEAREST)
    img.alpha_composite(em, (c - 64, c - 64))
    return img
