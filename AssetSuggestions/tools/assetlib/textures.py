"""Builds the tileable texture set for one aesthetic core."""
import numpy as np
from PIL import Image, ImageDraw

from . import tex

SIZE = 128


def _rng(core_idx, salt):
    return np.random.default_rng(1000 * core_idx + salt)


def _shade(core, v, **kw):
    """Palette-map a field, scaled by the core's `gain` (keeps tiny ramps from blowing out)."""
    return tex.shade(v * core.get("gain", 1.0), core["ramp"], **kw)


def floor_stone(core, idx):
    """Returns (albedo RGB array, emissive RGB array)."""
    rng = _rng(idx, 1)
    base = tex.fbm(SIZE, 4, rng, 4)
    crack = tex.cracks(SIZE, 5, rng, 0.10)
    v = np.clip(base * 0.9 + 0.05 - crack * 0.35, 0, 1)
    rgb = _shade(core, v)
    emissive = np.zeros_like(rgb)
    if core["kind"] == "hell":
        hot = crack > 0.55
        rgb = tex.tint_mask(rgb, hot, core["accent"])
        emissive[hot] = core["glow"]
    else:
        frost = crack > 0.6
        rgb = tex.tint_mask(rgb, frost, core["accent"])
        sp = tex.value_noise(SIZE, 64, rng) > 0.93
        rgb[sp] = core["ramp"][-1]
    return rgb, emissive


def wall_brick(core, idx):
    rng = _rng(idx, 2)
    shade, mortar = tex.bricks(SIZE, 8, rng)
    grain = tex.fbm(SIZE, 8, rng, 3)
    v = np.clip(0.25 + 0.45 * shade + 0.35 * grain, 0, 1)
    v[mortar > 0.5] *= 0.25
    rgb = _shade(core, v)
    if core["kind"] == "frost":
        drift = tex.fbm(SIZE, 4, rng, 3) > 0.62
        rgb[drift] = core["ramp"][-1]
    return rgb


def platform_ring(core, idx):
    """Slab with bevelled frame, a glowing groove and corner rivets."""
    rng = _rng(idx, 3)
    v = 0.30 + 0.30 * tex.fbm(SIZE, 4, rng, 3)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    edge = np.minimum(np.minimum(xx, SIZE - 1 - xx), np.minimum(yy, SIZE - 1 - yy))
    v[edge < 6] += 0.28
    v[(edge >= 6) & (edge < 8)] -= 0.20
    groove = (np.abs(edge - 20) < 2)
    v[groove] -= 0.25
    rgb = _shade(core, np.clip(v, 0, 1))
    emissive = np.zeros_like(rgb)
    rgb[groove] = core["accent"]
    emissive[groove] = core["glow"] if core["kind"] == "hell" else 0
    for cx in (10, SIZE - 11):
        for cy in (10, SIZE - 11):
            rgb[cy - 2:cy + 2, cx - 2:cx + 2] = core["ramp"][-1]
    return rgb, emissive


def abyss_fog(core, idx):
    """Murky fog panel for the pit below the arena / sky fill."""
    rng = _rng(idx, 4)
    n = tex.fbm(SIZE, 3, rng, 5)
    yy = np.linspace(0, 1, SIZE)[:, None]
    if core["kind"] == "hell":
        v = np.clip(0.05 + 0.25 * n + 0.15 * (1 - yy), 0, 1)
    else:
        v = np.clip(0.55 + 0.35 * n + 0.1 * yy, 0, 1)
    return _shade(core, v, dither=1.1)


def pumpkin_skin(core, idx):
    rng = _rng(idx, 5)
    xx = np.arange(SIZE)[None, :] / SIZE
    ribs = 0.5 + 0.5 * np.cos(2 * np.pi * xx * 8)
    n = tex.fbm(SIZE, 6, rng, 3)
    v = np.clip(0.25 + 0.5 * ribs.repeat(SIZE, 0) + 0.25 * n, 0, 1)
    ramp = _pumpkin_ramp(core)
    return tex.shade(v, ramp)


def _pumpkin_ramp(core):
    p = np.array(core["pumpkin"], dtype=float)
    return [tuple(int(x) for x in p * k) for k in (0.18, 0.38, 0.62, 0.85, 1.0)]


def pumpkin_face(core, idx):
    """64x64 face texture: carved glowing eyes and jagged mouth."""
    s = 64
    img = Image.new("RGB", (s, s), core["ramp"][0])
    ramp = _pumpkin_ramp(core)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, s, s], fill=ramp[2])
    for x in range(0, s, 8):
        d.line([(x, 0), (x, s)], fill=ramp[1], width=2)
    glow = core["glow"]
    d.polygon([(10, 18), (26, 18), (18, 32)], fill=glow)       # left eye
    d.polygon([(38, 18), (54, 18), (46, 32)], fill=glow)       # right eye
    d.polygon([(30, 30), (34, 30), (32, 38)], fill=ramp[0])     # nose
    mouth = [(8, 40), (16, 46), (22, 40), (28, 48), (32, 40),
             (36, 48), (42, 40), (48, 46), (56, 40), (50, 56), (14, 56)]
    d.polygon(mouth, fill=glow)
    return np.array(img)


def build(core, idx):
    """Returns {filename: RGB array} for one core."""
    out = {}
    floor, floor_em = floor_stone(core, idx)
    out["floor_stone"] = floor
    out["wall_brick"] = wall_brick(core, idx)
    plat, plat_em = platform_ring(core, idx)
    out["platform_ring"] = plat
    out["abyss_fog"] = abyss_fog(core, idx)
    if core["kind"] == "hell":
        out["floor_stone_emissive"] = floor_em
        out["platform_ring_emissive"] = plat_em
        out["pumpkin_skin"] = pumpkin_skin(core, idx)
        out["pumpkin_face"] = pumpkin_face(core, idx)
    return out
