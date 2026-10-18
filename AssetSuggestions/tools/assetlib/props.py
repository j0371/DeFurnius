"""Arena kit, enemies, the Dark One and set dressing.

Unity conventions as in mesh.py. Materials reference the `ash_dusk` textures by
relative path; swap the texture folder to re-theme (see the README).
"""
import math

import numpy as np

from . import mesh as M

TEX = "../../textures/ash_dusk"


def _mats(**kw):
    return dict(kw)


STONE = {"kd": (110, 96, 84), "map": f"{TEX}/platform_ring.png"}
FLOOR = {"kd": (110, 96, 84), "map": f"{TEX}/floor_stone.png"}
WALL = {"kd": (110, 96, 84), "map": f"{TEX}/wall_brick.png"}
TRIM = {"kd": (70, 56, 48)}
GLOW = {"kd": (255, 138, 42), "ke": (255, 138, 42)}


def prism(poly, y0, y1, mat):
    """Extrude a convex polygon given as (x, z) points; any winding."""
    pts = [np.array([x, z]) for x, z in poly]
    a, b, c = pts[0], pts[1], pts[2]
    if (b[1] - a[1]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[1] - a[1]) < 0:
        pts = pts[::-1]
    top = [(p[0], y1, p[1]) for p in pts]
    bot = [(p[0], y0, p[1]) for p in pts]
    m = M.Mesh()
    for k in range(1, len(pts) - 1):
        m.add_tri(top[0], top[k], top[k + 1], mat)
        m.add_tri(bot[0], bot[k + 1], bot[k], mat)
    for k in range(len(pts)):
        k2 = (k + 1) % len(pts)
        m.add_quad(bot[k], bot[k2], top[k2], top[k], mat)
    return m


def arrow(length, width, y0, y1, mat):
    """Flat arrow pointing along +Z."""
    m = M.Mesh()
    m.merge(M.box((width * 0.35, y1 - y0, length * 0.55), mat, center=(0, (y0 + y1) / 2, -length * 0.22)))
    m.merge(prism([(-width / 2, length * 0.05), (width / 2, length * 0.05), (0, length * 0.5)], y0, y1, mat))
    return m


# ---- ring platforms ----------------------------------------------------------------------
def ring_segment(style="plain", r_in=6.0, r_out=9.0, span=50.0, thick=0.6):
    m = M.Mesh()
    mats = _mats(stone=STONE, trim=TRIM, glow=GLOW)
    steps = 6
    if style == "plain":
        m.merge(M.annular_sector(r_in, r_out, 0, span, thick, "stone", steps=steps, mat_side="trim"))
        m.merge(M.annular_sector(r_in + 0.15, r_in + 0.45, 1.5, span - 1.5, 0.12, "trim", steps=steps, y0=thick))
        m.merge(M.annular_sector(r_out - 0.45, r_out - 0.15, 1.5, span - 1.5, 0.12, "trim", steps=steps, y0=thick))
    elif style == "crenellated":
        m.merge(M.annular_sector(r_in, r_out, 0, span, thick, "stone", steps=steps, mat_side="trim"))
        for k in range(6):                                           # teeth on the outer lip
            a0 = 2 + k * (span - 4) / 6
            m.merge(M.annular_sector(r_out - 0.5, r_out, a0, a0 + (span - 4) / 12, 0.55, "trim",
                                     steps=1, y0=thick))
    elif style == "broken":
        m.merge(M.annular_sector(r_in, r_out, 0, span * 0.62, thick, "stone", steps=4, mat_side="trim"))
        m.merge(M.annular_sector(r_in + 0.5, r_out, span * 0.62, span * 0.8, thick * 0.7, "stone",
                                 steps=2, mat_side="trim"))
        m.merge(M.annular_sector(r_in + 1.2, r_out - 0.6, span * 0.8, span, thick * 0.45, "stone",
                                 steps=2, mat_side="trim"))
    # underside spikes (the abyss below)
    mid_r = (r_in + r_out) / 2
    for k in range(3):
        a = math.radians(span * (k + 0.5) / 3)
        base = np.array([mid_r * math.sin(a), 0.0, mid_r * math.cos(a)])
        m.merge(M.cone(base, base + np.array([0, -1.6 - 0.4 * (k % 2), 0]), 0.45, "trim", sides=5))
    # launcher pad near the clockwise end, arrow along the tangent (increasing angle)
    a = math.radians(span - 9)
    c = np.array([mid_r * math.sin(a), thick, mid_r * math.cos(a)])
    pad = M.limb(c, c + np.array([0, 0.1, 0]), 1.0, 1.0, "trim", sides=8)
    ar = arrow(1.4, 0.9, 0.1, 0.16, "glow")
    yaw = math.degrees(math.atan2(math.cos(a), -math.sin(a)))       # +Z -> tangent
    ar.transform(M.rot_y(yaw), pos=c)
    m.merge(pad).merge(ar)
    return m, mats


def launcher_pad():
    m = M.Mesh()
    m.merge(M.limb((0, 0, 0), (0, 0.12, 0), 1.0, 1.0, "trim", sides=8))
    m.merge(M.limb((0, 0.12, 0), (0, 0.2, 0), 0.9, 0.7, "trim", sides=8))
    m.merge(arrow(1.4, 0.9, 0.2, 0.26, "glow"))
    return m, _mats(trim=TRIM, glow=GLOW)


def limbo_layout(n=6, r_in=7.0, r_out=10.0):
    """Full Limbo: central pedestal and n ring segments with gaps, launchers chained clockwise."""
    m = M.Mesh()
    mats = _mats(stone=STONE, trim=TRIM, glow=GLOW)
    span = 360.0 / n - 12.0
    for k in range(n):
        seg, _ = ring_segment("plain", r_in, r_out, span)
        seg.transform(M.rot_y(k * 360.0 / n + 6.0))
        m.merge(seg)
    ped, pm = pedestal()
    mats.update(pm)
    m.merge(ped.moved(pos=(0, 0, 0)))
    return m, mats


def pedestal():
    prof = [(0.0, 0.0), (2.2, 0.0), (2.2, 0.3), (1.7, 0.45), (1.7, 0.9), (1.1, 1.0), (1.1, 1.25),
            (1.45, 1.35), (1.45, 1.55), (0.0, 1.55)]
    m = M.lathe(prof, "stone", sides=10)
    m.merge(M.limb((0, 1.55, 0), (0, 1.62, 0), 0.9, 0.9, "glow", sides=10))   # glowing dish for the hand
    return m, _mats(stone=STONE, glow=GLOW)


# ---- doorway, cellar ------------------------------------------------------------------------
def gate():
    """The Gates of Hell doorway with a lintel for the inscription. Opening faces +Z."""
    mats = _mats(stone=WALL, lintel={"kd": (110, 96, 84), "map": f"{TEX}/lintel_inscription.png"},
                 glow=GLOW, trim=TRIM)
    m = M.Mesh()
    m.merge(M.box((0.7, 3.2, 0.8), "stone", center=(-1.35, 1.6, 0)))
    m.merge(M.box((0.7, 3.2, 0.8), "stone", center=(1.35, 1.6, 0)))
    m.merge(M.box((3.6, 0.7, 0.85), "lintel", center=(0, 3.4, 0)))
    m.merge(prism([(-1.9, -0.4), (1.9, -0.4), (1.9, 0.4), (-1.9, 0.4)], 3.75, 3.95, "trim"))
    for x in (-1.35, 1.35):                                                    # horned finials
        m.merge(M.cone((x, 3.2, 0), (x, 4.0, 0), 0.28, "trim", sides=5))
    m.merge(M.box((0.12, 0.12, 0.12), "glow", center=(-0.9, 3.0, 0.42)))
    m.merge(M.box((0.12, 0.12, 0.12), "glow", center=(0.9, 3.0, 0.42)))
    return m, mats


def cellar_room(w=5.0, h=3.4, d=6.0):
    """Cramped starting cellar. Origin at the doorway floor; room extends toward -Z."""
    mats = _mats(floor=FLOOR, wall=WALL, trim=TRIM, glow=GLOW)
    t = 0.3
    m = M.Mesh()
    m.merge(M.box((w + 2 * t, t, d), "floor", center=(0, -t / 2, -d / 2)))
    m.merge(M.box((w + 2 * t, t, d), "wall", center=(0, h + t / 2, -d / 2)))
    m.merge(M.box((t, h, d), "wall", center=(-w / 2 - t / 2, h / 2, -d / 2)))
    m.merge(M.box((t, h, d), "wall", center=(w / 2 + t / 2, h / 2, -d / 2)))
    m.merge(M.box((w + 2 * t, h, t), "wall", center=(0, h / 2, -d - t / 2)))
    side = w / 2 + t - 1.0                                                     # front wall around the 2 m gate opening
    m.merge(M.box((side, h, t), "wall", center=(-(1.0 + side / 2), h / 2, t / 2)))
    m.merge(M.box((side, h, t), "wall", center=((1.0 + side / 2), h / 2, t / 2)))
    m.merge(M.box((2.0, h - 3.05, t), "wall", center=(0, 3.05 + (h - 3.05) / 2, t / 2)))
    for x in (-w / 2 + 0.3, w / 2 - 0.3):                                      # wall torches (glow cubes)
        m.merge(M.box((0.14, 0.14, 0.14), "glow", center=(x, 1.9, -2.5)))
        m.merge(M.box((0.08, 0.5, 0.08), "trim", center=(x, 1.55, -2.5)))
    for k, (x, z) in enumerate(((-1.9, -4.8), (1.7, -5.2), (1.1, -1.4))):      # crates / barrels
        m.merge(M.box((0.7, 0.7, 0.7), "wall").transform(M.rot_y(20 * k + 10), pos=(x, 0.35, z)))
    return m, mats


# ---- enemies ----------------------------------------------------------------------------------
PUMPKIN = {"kd": (184, 80, 30), "map": f"{TEX}/pumpkin_skin.png"}
PUMPKIN_FACE = {"kd": (184, 80, 30), "map": f"{TEX}/pumpkin_face.png"}
STEM = {"kd": (70, 82, 40)}


def pumpkin_turret():
    """Stationary shooter: carved head on a stone post. Face looks along +Z."""
    mats = _mats(pumpkin=PUMPKIN_FACE, stem=STEM, stone=STONE, trim=TRIM, glow=GLOW)
    m = M.Mesh()
    m.merge(M.lathe([(0.0, 0.0), (0.7, 0.0), (0.7, 0.25), (0.45, 0.4), (0.45, 1.2), (0.6, 1.3),
                     (0.6, 1.45), (0.0, 1.45)], "stone", sides=8))
    m.merge(M.uv_sphere(0.8, "pumpkin", seg=12, rings=7, center=(0, 2.15, 0), squash=(1.12, 0.9, 1.0)))
    m.merge(M.limb((0, 2.85, 0), (0.12, 3.1, 0), 0.12, 0.09, "stem", sides=5))
    m.merge(M.cone((0.12, 3.1, 0), (0.28, 3.25, 0.05), 0.09, "stem", sides=5))
    return m, mats


def pumpkin_floater():
    """Hovering variant with a halo of thorns instead of a post."""
    mats = _mats(pumpkin=PUMPKIN_FACE, stem=STEM, trim=TRIM, glow=GLOW)
    m = M.Mesh()
    m.merge(M.uv_sphere(0.75, "pumpkin", seg=12, rings=7, squash=(1.15, 0.88, 1.0)))
    m.merge(M.limb((0, 0.62, 0), (0.1, 0.9, 0), 0.11, 0.08, "stem", sides=5))
    for k in range(8):
        a = math.radians(45 * k)
        base = np.array([math.sin(a) * 1.15, -0.1, math.cos(a) * 1.15])
        m.merge(M.cone(base, base + np.array([math.sin(a) * 0.5, -0.25, math.cos(a) * 0.5]), 0.13, "trim", sides=4))
    return m, mats


def pumpkin_totem():
    """Three stacked heads on a stake: tall silhouette, reads from across the arena."""
    mats = _mats(pumpkin=PUMPKIN_FACE, stem=STEM, trim=TRIM)
    m = M.Mesh()
    m.merge(M.limb((0, 0, 0), (0, 3.6, 0), 0.12, 0.05, "trim", sides=5))
    for k, (y, r) in enumerate(((0.9, 0.72), (1.95, 0.6), (2.8, 0.48))):
        s = M.uv_sphere(r, "pumpkin", seg=10, rings=6, center=(0, y, 0), squash=(1.1, 0.9, 1.0))
        m.merge(s)
    m.merge(M.cone((0, 3.55, 0), (0, 4.1, 0), 0.07, "trim", sides=4))
    return m, mats


# ---- the Dark One ---------------------------------------------------------------------------
GLASS = {"kd": (40, 40, 60)}
MIRROR = {"kd": (150, 160, 175)}


def dark_one(style="split"):
    mats = _mats(glass=GLASS, mirror=MIRROR, trim={"kd": (18, 18, 24)}, glow={"kd": (230, 240, 255),
                                                                              "ke": (230, 240, 255)})
    m = M.Mesh()
    if style == "split":
        half = lambda t0, t1, mat: M.uv_sphere(2.0, mat, seg=18, rings=5, theta0=t0, theta1=t1) \
            .transform(M.rot_z(-90))                                          # pole +Y -> +X
        m.merge(half(0.0, math.pi / 2, "mirror"))                              # +X half reflective
        m.merge(half(math.pi / 2, math.pi, "glass"))                           # -X half translucent glass
        for k in range(3):                                                    # shard halo
            ring = M.uv_sphere(0.2, "trim", seg=4, rings=2)
            a = math.radians(120 * k)
            m.merge(ring.moved(pos=(2.7 * math.sin(a), 0.4 * k - 0.4, 2.7 * math.cos(a))))
    elif style == "faceted":
        m.merge(M.uv_sphere(2.0, "glass", seg=7, rings=4))
        for k in range(10):
            a = math.radians(36 * k)
            d = np.array([math.sin(a), 0.35 * math.sin(k * 1.7), math.cos(a)])
            d /= np.linalg.norm(d)
            m.merge(M.cone(d * 1.9, d * 3.0, 0.3, "mirror", sides=4))
    elif style == "eye":
        m.merge(M.uv_sphere(2.0, "glass", seg=16, rings=9))
        m.merge(M.box((0.14, 2.4, 0.08), "glow", center=(0, 0, 1.98)))
        for k in range(12):                                                   # lashes around the slit
            a_ = math.radians(30 * k)
            base = np.array([0.8 * math.sin(a_), 1.1 * math.cos(a_), 1.85])
            m.merge(M.cone(base, base + np.array([0.5 * math.sin(a_), 0.6 * math.cos(a_), 0.5]),
                           0.1, "mirror", sides=3))
    return m, mats


# ---- set dressing ---------------------------------------------------------------------------------
def pillar(style="fluted"):
    mats = _mats(stone=STONE, trim=TRIM)
    m = M.Mesh()
    if style == "fluted":
        m.merge(M.limb((0, 0, 0), (0, 0.3, 0), 0.8, 0.8, "trim", sides=8))
        m.merge(M.limb((0, 0.3, 0), (0, 4.3, 0), 0.55, 0.5, "stone", sides=8))
        m.merge(M.limb((0, 4.3, 0), (0, 4.6, 0), 0.8, 0.8, "trim", sides=8))
    elif style == "broken":
        m.merge(M.limb((0, 0, 0), (0, 0.3, 0), 0.8, 0.8, "trim", sides=8))
        m.merge(M.limb((0, 0.3, 0), (0.15, 2.4, 0.1), 0.55, 0.5, "stone", sides=8))
        m.merge(M.cone((0.15, 2.4, 0.1), (0.35, 2.9, 0.1), 0.5, "stone", sides=3))
    elif style == "obelisk":
        m.merge(M.limb((0, 0, 0), (0, 5.0, 0), 0.7, 0.3, "stone", sides=4, twist=45))
        m.merge(M.cone((0, 5.0, 0), (0, 5.7, 0), 0.3, "trim", sides=4))
    return m, mats


def rubble(seed=3, n=7):
    rng = np.random.default_rng(seed)
    mats = _mats(stone=STONE)
    m = M.Mesh()
    for _ in range(n):
        s = rng.uniform(0.25, 0.9, 3)
        c = M.box(s, "stone")
        c.transform(M.rot_y(rng.uniform(0, 90)) @ M.rot_x(rng.uniform(-20, 20)),
                    pos=(rng.uniform(-1.4, 1.4), s[1] / 2, rng.uniform(-1.4, 1.4)))
        m.merge(c)
    return m, mats


def ice_spires(seed=5):
    """Treachery dressing: a cluster of frost crystals."""
    rng = np.random.default_rng(seed)
    mats = _mats(ice={"kd": (200, 225, 240)}, ice_dark={"kd": (120, 160, 190)})
    m = M.Mesh()
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, 1.3)
        base = np.array([r * math.cos(a), 0, r * math.sin(a)])
        h = rng.uniform(1.0, 3.8)
        tilt = np.array([rng.uniform(-0.25, 0.25), 0, rng.uniform(-0.25, 0.25)])
        m.merge(M.limb(base, base + np.array([0, h, 0]) + tilt * h, 0.3, 0.0,
                       "ice" if k % 3 else "ice_dark", sides=5, cap1=False))
    return m, mats


VARIANTS = {
    "ring_segment_plain": lambda: ring_segment("plain"),
    "ring_segment_crenellated": lambda: ring_segment("crenellated"),
    "ring_segment_broken": lambda: ring_segment("broken"),
    "launcher_pad": launcher_pad,
    "pedestal": pedestal,
    "limbo_layout": limbo_layout,
    "gate": gate,
    "cellar_room": cellar_room,
    "pumpkin_turret": pumpkin_turret,
    "pumpkin_floater": pumpkin_floater,
    "pumpkin_totem": pumpkin_totem,
    "dark_one_split": lambda: dark_one("split"),
    "dark_one_faceted": lambda: dark_one("faceted"),
    "dark_one_eye": lambda: dark_one("eye"),
    "pillar_fluted": lambda: pillar("fluted"),
    "pillar_broken": lambda: pillar("broken"),
    "obelisk": lambda: pillar("obelisk"),
    "rubble": rubble,
    "ice_spires": ice_spires,
}
