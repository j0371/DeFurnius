"""Tileable procedural texture helpers (numpy + Pillow).

Everything returns float arrays in [0, 1] until `shade()` maps them through a
palette ramp with ordered dithering, which is what gives the retro look.
"""
import numpy as np
from PIL import Image

BAYER4 = (np.array([[0, 8, 2, 10],
                    [12, 4, 14, 6],
                    [3, 11, 1, 9],
                    [15, 7, 13, 5]]) + 0.5) / 16.0


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _smooth(f):
    return f * f * (3 - 2 * f)


def value_noise(size, cells, rng):
    """Tileable value noise, `cells` lattice points per side."""
    g = rng.random((cells, cells))
    x = np.arange(size) / size * cells
    i0 = np.floor(x).astype(int)
    f = _smooth(x - i0)
    i0 %= cells
    i1 = (i0 + 1) % cells
    gx0 = g[:, i0] * (1 - f) + g[:, i1] * f  # interpolate along x
    out = gx0[i0, :] * (1 - f)[:, None] + gx0[i1, :] * f[:, None]
    return out


def fbm(size, cells, rng, octaves=4, gain=0.5):
    total = np.zeros((size, size))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        total += amp * value_noise(size, cells * 2 ** o, rng)
        norm += amp
        amp *= gain
    return total / norm


def voronoi(size, cells, rng):
    """Tileable worley noise. Returns (F1, F2) distances in cell units."""
    jit = rng.random((cells, cells, 2))
    u = (np.arange(size) + 0.5) / size * cells
    ux, uy = np.meshgrid(u, u)
    bx, by = np.floor(ux).astype(int), np.floor(uy).astype(int)
    f1 = np.full((size, size), 9.0)
    f2 = np.full((size, size), 9.0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = bx + dx, by + dy
            p = jit[cy % cells, cx % cells]
            d = np.hypot(ux - (cx + p[..., 0]), uy - (cy + p[..., 1]))
            f2 = np.minimum(f2, np.maximum(f1, d))
            f1 = np.minimum(f1, d)
    return f1, f2


def cracks(size, cells, rng, width=0.07):
    """1.0 on crack lines, 0.0 elsewhere (soft edge)."""
    f1, f2 = voronoi(size, cells, rng)
    edge = f2 - f1
    return np.clip(1.0 - edge / width, 0.0, 1.0)


def bricks(size, rows, rng, mortar=2):
    """Offset brick pattern. Returns (brick_shade 0..1, mortar_mask 0/1)."""
    h = size // rows
    cols = max(2, rows // 2)
    w = size // cols
    shade_ = np.zeros((size, size))
    mask = np.zeros((size, size))
    for r in range(rows):
        off = (w // 2) if r % 2 else 0
        ys = np.arange(r * h, (r + 1) * h)
        for c in range(cols):
            xs = (c * w + off + np.arange(w)) % size
            shade_[np.ix_(ys, xs)] = 0.35 + 0.65 * rng.random()
            mask[np.ix_(ys, xs[:mortar])] = 1
        mask[r * h:r * h + mortar, :] = 1
    return shade_, mask


def shade(v, ramp, dither=0.9):
    """Map a [0,1] field through a dark->light colour ramp with Bayer dither."""
    n = len(ramp)
    size_y, size_x = v.shape
    b = np.tile(BAYER4, (size_y // 4 + 1, size_x // 4 + 1))[:size_y, :size_x]
    idx = np.clip(np.floor(v * (n - 1) + (b - 0.5) * dither + 0.5), 0, n - 1).astype(int)
    pal = np.array(ramp, dtype=np.uint8)
    return pal[idx]


def to_image(arr):
    return Image.fromarray(np.asarray(arr, dtype=np.uint8), "RGB")


def tint_mask(rgb, mask, color):
    """Paint `color` where mask > 0.5 (hard, retro)."""
    out = rgb.copy()
    out[mask > 0.5] = color
    return out
