"""Small software rasteriser for previews (no GPU, no Unity).

Flat shading with one directional light. Faces seen from behind are painted
magenta, so a winding mistake in a generator shows up in the preview.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

LABEL = ImageFont.load_default(size=12)
LIGHT = np.array([-0.4, 0.8, -0.5])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _lookat(eye, target, up=(0, 1, 0)):
    f = np.asarray(target, float) - np.asarray(eye, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return r, u, f


NEAR = 0.05


def _clip_near(cam):
    """Clip a camera-space triangle against z=NEAR; returns 0-2 triangles."""
    inside = cam[:, 2] >= NEAR
    if inside.all():
        return [cam]
    if not inside.any():
        return []
    poly = []
    for i in range(3):
        a, b = cam[i], cam[(i + 1) % 3]
        ia, ib = inside[i], inside[(i + 1) % 3]
        if ia:
            poly.append(a)
        if ia != ib:
            t = (NEAR - a[2]) / (b[2] - a[2])
            poly.append(a + t * (b - a))
    return [np.array([poly[0], poly[k], poly[k + 1]]) for k in range(1, len(poly) - 1)]


def render(mesh, materials, eye, target, size=256, fov=38, bg=(44, 44, 54), ssaa=1):
    """Returns (PIL image, number of back-facing pixels drawn)."""
    W = size * ssaa
    r, u, f = _lookat(eye, target)
    eye = np.asarray(eye, float)
    focal = 0.5 * W / math.tan(math.radians(fov) / 2)
    img = np.zeros((W, W, 3), dtype=np.float32)
    img[:] = bg
    zbuf = np.zeros((W, W))  # stores 1/z (larger = nearer), interpolates linearly in screen space
    back_mask = np.zeros((W, W), dtype=bool)
    # painter-independent: z-buffer; loop triangles
    for tri, mat in zip(mesh.tris, mesh.mats):
        n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
        ln = np.linalg.norm(n)
        if ln < 1e-12:
            continue
        n /= ln
        rel = tri - eye
        cam_all = np.stack([rel @ r, rel @ u, rel @ f], axis=1)  # x right, y up, z forward
        facing = np.dot(n, eye - tri.mean(0))
        m = materials[mat]
        if facing >= 0:
            if "ke" in m:
                col = np.array(m["ke"], float)
            else:
                lam = max(0.0, float(np.dot(n, LIGHT)))
                col = np.array(m["kd"], float) * (0.52 + 0.62 * lam)
            is_back = False
        else:
            col = np.array([255, 0, 255], float)
            is_back = True
        for cam in _clip_near(cam_all):
            sx = W / 2 + focal * cam[:, 0] / cam[:, 2]
            sy = W / 2 - focal * cam[:, 1] / cam[:, 2]
            x0, x1 = int(max(0, math.floor(sx.min()))), int(min(W - 1, math.ceil(sx.max())))
            y0, y1 = int(max(0, math.floor(sy.min()))), int(min(W - 1, math.ceil(sy.max())))
            if x0 > x1 or y0 > y1:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2])
            if abs(d) < 1e-9:
                continue
            w0 = ((sy[1] - sy[2]) * (xs - sx[2]) + (sx[2] - sx[1]) * (ys - sy[2])) / d
            w1 = ((sy[2] - sy[0]) * (xs - sx[2]) + (sx[0] - sx[2]) * (ys - sy[2])) / d
            w2 = 1 - w0 - w1
            inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if not inside.any():
                continue
            z = w0 / cam[0, 2] + w1 / cam[1, 2] + w2 / cam[2, 2]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            win = inside & (z > sub)
            sub[win] = z[win]
            img[y0:y1 + 1, x0:x1 + 1][win] = np.clip(col, 0, 255)
            back_mask[y0:y1 + 1, x0:x1 + 1][win] = is_back
    out = Image.fromarray(img.astype(np.uint8), "RGB")
    if ssaa > 1:
        out = out.resize((size, size), Image.BOX)
    return out, int(back_mask.sum())


def views(mesh, materials, size=256, dist=None, cam_up=0.35, angles=(35, 125, 215, 305),
          target=None, ssaa=2, fit=2.9):
    lo, hi = mesh.bounds()
    centre = (lo + hi) / 2 if target is None else np.asarray(target, float)
    radius = float(np.linalg.norm(hi - lo)) / 2
    dist = dist or radius * fit
    imgs, back = [], 0
    for a in angles:
        t = math.radians(a)
        eye = centre + dist * np.array([math.sin(t), cam_up, math.cos(t)])
        im, b = render(mesh, materials, eye, centre, size=size, ssaa=ssaa)
        imgs.append(im)
        back += b
    return imgs, back


def sheet(items, size=200, cols=4, title="", fit=2.9):
    """items = [(label, mesh, materials)] -> contact sheet, 4 turntable views each."""
    rows = len(items)
    W, H = size * cols, rows * (size + 18) + (22 if title else 0)
    out = Image.new("RGB", (W, H), (14, 14, 18))
    d = ImageDraw.Draw(out)
    y = 0
    if title:
        d.text((6, 4), title, font=LABEL, fill=(235, 235, 235))
        y = 22
    for label, mesh, mats in items:
        imgs, back = views(mesh, mats, size=size, fit=fit)
        tag = f"{label}  ({mesh.tri_count()} tris)" + ("  BACKFACES!" if back else "")
        d.text((6, y + 2), tag, font=LABEL, fill=(235, 235, 235) if not back else (255, 90, 90))
        for i, im in enumerate(imgs):
            out.paste(im, (i * size, y + 18))
        y += size + 18
    return out
