"""64x64 pixel-art emblems for the three poisons (Wheel of Life animals).

Drawn as an alpha mask, then coloured per core. Rough silhouettes on purpose.
"""
import math

from PIL import Image, ImageDraw

S = 64


def _new():
    m = Image.new("L", (S, S), 0)
    return m, ImageDraw.Draw(m)


def rooster():
    m, d = _new()
    d.polygon([(18, 40), (3, 14), (10, 10), (15, 22), (12, 5), (20, 6), (25, 28)], fill=255)  # tail
    d.ellipse([16, 28, 46, 54], fill=255)                                   # body
    d.polygon([(32, 34), (40, 20), (49, 20), (45, 38)], fill=255)            # neck
    d.ellipse([39, 12, 53, 27], fill=255)                                   # head
    for cx, cy in ((42, 12), (46, 9), (50, 11)):
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=255)                # comb
    d.polygon([(52, 17), (61, 21), (52, 24)], fill=255)                      # beak
    d.line([(28, 52), (27, 61)], fill=255, width=3)                          # legs
    d.line([(37, 52), (38, 61)], fill=255, width=3)
    d.ellipse([46, 16, 49, 19], fill=0)                                     # eye
    d.line([(24, 36), (36, 44)], fill=0, width=1)                            # wing line
    return m


def snake():
    m, d = _new()
    pts = []
    for i in range(41):
        t = i / 40
        x = 6 + t * 44
        y = 36 + 14 * math.sin(t * 2 * math.pi * 1.25)
        pts.append((x, y))
    for i in range(len(pts) - 1):
        w = int(round(8 - 4 * i / 40))
        d.line([pts[i], pts[i + 1]], fill=255, width=max(w, 3))
        r = max(w, 3) / 2
        d.ellipse([pts[i][0] - r, pts[i][1] - r, pts[i][0] + r, pts[i][1] + r], fill=255)
    hx, hy = pts[0]
    d.polygon([(hx - 7, hy - 6), (hx + 3, hy - 9), (hx + 6, hy + 5), (hx - 6, hy + 6)], fill=255)
    d.ellipse([hx - 4, hy - 5, hx - 1, hy - 2], fill=0)
    d.line([(hx - 7, hy), (hx - 13, hy - 3)], fill=255, width=1)             # tongue
    d.line([(hx - 7, hy), (hx - 13, hy + 3)], fill=255, width=1)
    return m


def pig():
    m, d = _new()
    d.polygon([(10, 24), (8, 6), (24, 14)], fill=255)                        # ears
    d.polygon([(54, 24), (56, 6), (40, 14)], fill=255)
    d.ellipse([10, 12, 54, 56], fill=255)                                   # head
    d.ellipse([22, 34, 42, 50], fill=0)                                     # snout ring (cut)
    d.ellipse([24, 36, 40, 48], fill=255)                                   # snout
    d.ellipse([27, 40, 30, 45], fill=0)                                     # nostrils
    d.ellipse([34, 40, 37, 45], fill=0)
    d.ellipse([19, 26, 24, 31], fill=0)                                     # eyes
    d.ellipse([40, 26, 45, 31], fill=0)
    return m


EMBLEMS = {"greed_rooster": rooster, "hatred_snake": snake, "delusion_pig": pig}


def render(name, color):
    mask = EMBLEMS[name]()
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    solid = Image.new("RGBA", (S, S), tuple(color) + (255,))
    img.paste(solid, (0, 0), mask.point(lambda v: 255 if v > 127 else 0))
    return img
