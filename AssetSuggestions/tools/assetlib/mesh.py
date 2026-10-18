"""Tiny low-poly mesh toolkit: primitives, transforms, flat-shaded OBJ/MTL export.

Conventions match Unity import: +Y up, +Z forward, +X right, metres.
Triangles are wound counter-clockwise when seen from outside.
"""
import math
import os

import numpy as np


# ---- transforms -------------------------------------------------------------
def rot_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


class Mesh:
    """Triangle soup with a material name per face."""

    def __init__(self):
        self.tris = []   # list of (3,3) float arrays
        self.mats = []   # material name per tri

    # -- building
    def add_tri(self, a, b, c, mat):
        self.tris.append(np.array([a, b, c], dtype=float))
        self.mats.append(mat)

    def add_quad(self, a, b, c, d, mat):
        """Quad given counter-clockwise from outside."""
        self.add_tri(a, b, c, mat)
        self.add_tri(a, c, d, mat)

    def merge(self, other):
        self.tris += other.tris
        self.mats += other.mats
        return self

    def copy(self):
        m = Mesh()
        m.tris = [t.copy() for t in self.tris]
        m.mats = list(self.mats)
        return m

    def transform(self, rot=None, pos=(0, 0, 0), scale=1.0):
        r = np.eye(3) if rot is None else rot
        s = np.asarray(scale, dtype=float)
        p = np.asarray(pos, dtype=float)
        self.tris = [((t * s) @ r.T) + p for t in self.tris]
        return self

    def moved(self, rot=None, pos=(0, 0, 0), scale=1.0):
        return self.copy().transform(rot, pos, scale)

    def flip(self):
        """Reverse winding (turn the mesh inside out)."""
        self.tris = [t[[0, 2, 1]] for t in self.tris]
        return self

    def recolor(self, mat):
        self.mats = [mat] * len(self.mats)
        return self

    # -- stats
    def tri_count(self):
        return len(self.tris)

    def bounds(self):
        v = np.concatenate(self.tris)
        return v.min(0), v.max(0)


# ---- primitives -------------------------------------------------------------
def box(size, mat, center=(0, 0, 0)):
    sx, sy, sz = (np.asarray(size, dtype=float) / 2)
    cx, cy, cz = center
    p = lambda x, y, z: (cx + x * sx, cy + y * sy, cz + z * sz)
    m = Mesh()
    m.add_quad(p(1, -1, -1), p(1, 1, -1), p(1, 1, 1), p(1, -1, 1), mat)      # +x
    m.add_quad(p(-1, -1, 1), p(-1, 1, 1), p(-1, 1, -1), p(-1, -1, -1), mat)  # -x
    m.add_quad(p(-1, 1, -1), p(-1, 1, 1), p(1, 1, 1), p(1, 1, -1), mat)      # +y
    m.add_quad(p(-1, -1, 1), p(-1, -1, -1), p(1, -1, -1), p(1, -1, 1), mat)  # -y
    m.add_quad(p(-1, -1, 1), p(1, -1, 1), p(1, 1, 1), p(-1, 1, 1), mat)      # +z
    m.add_quad(p(1, -1, -1), p(-1, -1, -1), p(-1, 1, -1), p(1, 1, -1), mat)  # -z
    return m


def limb(p0, p1, r0, r1, mat, sides=6, cap0=True, cap1=True, twist=0.0):
    """Tapered prism from p0 (radius r0) to p1 (radius r1)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    a = _unit(p1 - p0)
    helper = np.array([0, 1, 0]) if abs(a[1]) < 0.9 else np.array([1, 0, 0])
    u = _unit(np.cross(helper, a))
    v = np.cross(a, u)  # u x v = a
    ang = [2 * math.pi * k / sides + math.radians(twist) for k in range(sides)]
    ring = lambda c, r: [c + r * (math.cos(t) * u + math.sin(t) * v) for t in ang]
    b, t = ring(p0, r0), ring(p1, r1)
    m = Mesh()
    for k in range(sides):
        k2 = (k + 1) % sides
        m.add_quad(b[k], b[k2], t[k2], t[k], mat)
        if cap1 and r1 > 0:
            m.add_tri(p1, t[k], t[k2], mat)
        if cap0 and r0 > 0:
            m.add_tri(p0, b[k2], b[k], mat)
    return m


def cone(base, tip, r, mat, sides=6):
    return limb(base, tip, r, 0.0, mat, sides=sides, cap1=False)


def uv_sphere(radius, mat, seg=10, rings=6, center=(0, 0, 0),
              theta0=0.0, theta1=math.pi, squash=(1, 1, 1)):
    """Sphere (or band of it). theta measured from +Y pole, 0..pi."""
    cx, cy, cz = center
    sq = np.asarray(squash, float)

    def pt(i, j):
        th = theta0 + (theta1 - theta0) * j / rings
        ph = 2 * math.pi * i / seg
        d = np.array([math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)])
        return np.array([cx, cy, cz]) + radius * d * sq

    m = Mesh()
    for j in range(rings):
        for i in range(seg):
            a, b = pt(i, j), pt(i + 1, j)
            c, d = pt(i + 1, j + 1), pt(i, j + 1)
            # looking from outside, increasing phi runs clockwise (x->z), so flip
            if j == 0 and theta0 == 0:
                m.add_tri(a, d, c, mat)
            elif j == rings - 1 and theta1 == math.pi:
                m.add_tri(a, d, b, mat)
            else:
                m.add_quad(a, d, c, b, mat)
    return m.flip()


def annular_sector(r_in, r_out, a0, a1, thick, mat, steps=8, y0=0.0, mat_side=None):
    """Ring segment: angles in degrees around +Y (0 deg = +Z), y0 = bottom."""
    ms = mat_side or mat
    y1 = y0 + thick
    ang = [math.radians(a0 + (a1 - a0) * k / steps) for k in range(steps + 1)]
    P = lambda r, a, y: (r * math.sin(a), y, r * math.cos(a))
    m = Mesh()
    for k in range(steps):
        a, b = ang[k], ang[k + 1]
        m.add_quad(P(r_in, a, y1), P(r_in, b, y1), P(r_out, b, y1), P(r_out, a, y1), mat)     # top
        m.add_quad(P(r_in, a, y0), P(r_out, a, y0), P(r_out, b, y0), P(r_in, b, y0), ms)      # bottom
        m.add_quad(P(r_out, a, y0), P(r_out, a, y1), P(r_out, b, y1), P(r_out, b, y0), ms)    # outer
        m.add_quad(P(r_in, b, y0), P(r_in, b, y1), P(r_in, a, y1), P(r_in, a, y0), ms)        # inner
    a, b = ang[0], ang[-1]
    m.add_quad(P(r_in, a, y0), P(r_in, a, y1), P(r_out, a, y1), P(r_out, a, y0), ms)          # end A
    m.add_quad(P(r_out, b, y0), P(r_out, b, y1), P(r_in, b, y1), P(r_in, b, y0), ms)          # end B
    return m.flip()


def lathe(profile, mat, sides=8):
    """Revolve (radius, y) profile points (bottom->top) around Y."""
    m = Mesh()
    for k in range(len(profile) - 1):
        (r0, y0), (r1, y1) = profile[k], profile[k + 1]
        for i in range(sides):
            a, b = 2 * math.pi * i / sides, 2 * math.pi * (i + 1) / sides
            q = lambda r, y, t: (r * math.cos(t), y, r * math.sin(t))
            if r0 == 0 and r1 == 0:
                continue
            m.add_quad(q(r0, y0, b), q(r0, y0, a), q(r1, y1, a), q(r1, y1, b), mat)
    return m


# ---- export -----------------------------------------------------------------
def _face_normal(t):
    n = np.cross(t[1] - t[0], t[2] - t[0])
    ln = np.linalg.norm(n)
    return n / ln if ln > 1e-12 else np.array([0, 1, 0.0])


def _uv(t, n, mode, scale, rect=None):
    """Planar projection along the face's dominant axis (retro, texel-density based).

    rect = (x0, x1, y0, y1): on faces pointing along Z, map that XY rectangle onto 0..1.
    """
    ax = np.argmax(np.abs(n))
    if rect is not None and ax == 2:
        x0, x1, y0, y1 = rect
        return [((float(v[0]) - x0) / (x1 - x0), (float(v[1]) - y0) / (y1 - y0)) for v in t]
    cols = {0: (2, 1), 1: (0, 2), 2: (0, 1)}[ax]
    return [(float(v[cols[0]]) * scale, float(v[cols[1]]) * scale) for v in t]


def write_obj(mesh, path, materials, name=None, uv_scale=1.0, sphere_uv=()):
    """Flat-shaded OBJ + MTL. `materials` = {name: {"kd": (r,g,b 0-255), "ke": optional}}.

    Materials listed in `sphere_uv` get lat/long UVs around the mesh centre instead
    of planar ones (for a face texture wrapped on a head).
    """
    name = name or os.path.splitext(os.path.basename(path))[0]
    base = os.path.splitext(path)[0]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    centre = np.concatenate(mesh.tris).mean(0)
    lines = [f"# generated by Virgil/AssetSuggestions, {mesh.tri_count()} tris",
             f"mtllib {os.path.basename(base)}.mtl", f"o {name}"]
    vs, vts, vns, faces = [], [], [], []
    for t, mat in zip(mesh.tris, mesh.mats):
        n = _face_normal(t)
        if mat in sphere_uv:
            uvs = []
            for v in t:
                d = _unit(v - centre)
                uvs.append((0.5 + math.atan2(d[2], d[0]) / (2 * math.pi),
                            0.5 + math.asin(max(-1, min(1, d[1]))) / math.pi))
            us = [u for u, _ in uvs]
            if max(us) - min(us) > 0.5:
                uvs = [(u + 1 if u < 0.5 else u, v) for u, v in uvs]
        else:
            uvs = _uv(t, n, "planar", uv_scale, materials[mat].get("uvrect"))
        i0 = len(vs)
        vs += [tuple(v) for v in t]
        vts += uvs
        vns.append(tuple(n))
        faces.append((mat, i0, len(vns) - 1))
    lines += [f"v {x:.5f} {y:.5f} {z:.5f}" for x, y, z in vs]
    lines += [f"vt {u:.5f} {v:.5f}" for u, v in vts]
    lines += [f"vn {x:.5f} {y:.5f} {z:.5f}" for x, y, z in vns]
    cur = None
    for mat, i0, ni in faces:
        if mat != cur:
            lines.append(f"usemtl {mat}")
            cur = mat
        a, b, c = i0 + 1, i0 + 2, i0 + 3
        lines.append(f"f {a}/{a}/{ni + 1} {b}/{b}/{ni + 1} {c}/{c}/{ni + 1}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    used = sorted(set(mesh.mats))
    mtl = []
    for m in used:
        kd = materials[m]["kd"]
        mtl += [f"newmtl {m}", "Ka 0 0 0",
                f"Kd {kd[0] / 255:.4f} {kd[1] / 255:.4f} {kd[2] / 255:.4f}", "Ks 0 0 0"]
        if "ke" in materials[m]:
            ke = materials[m]["ke"]
            mtl.append(f"Ke {ke[0] / 255:.4f} {ke[1] / 255:.4f} {ke[2] / 255:.4f}")
        if "map" in materials[m]:
            mtl.append(f"map_Kd {materials[m]['map']}")
        mtl.append("")
    with open(base + ".mtl", "w") as f:
        f.write("\n".join(mtl))
