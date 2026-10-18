"""Hand / weapon variants for the first-person view.

Shared layout: wrist at z=0, fingers along +Z, back of hand up (+Y), thumb on -X.
Five non-thumb fingers; the three middle ones (index 1..3) aim straight ahead for
the precision shot, the outer two splay. Units are metres, roughly life size.
"""
import math

import numpy as np

from . import mesh as M

# per-finger layout: x offset, yaw (deg), length scale
FINGERS = [
    (-0.044, -24, 0.80),
    (-0.022, -3, 1.00),
    (0.000, 0, 1.12),
    (0.022, 3, 1.00),
    (0.044, 24, 0.80),
]
PALM_LEN = 0.085


def chain(start, yaw, lengths, radii, bends, mat, sides=6, joint=None, joint_mat=None,
          tip=None, tip_mat=None, box=False):
    """A jointed finger. bends are cumulative-per-joint pitches (+ve curls down)."""
    m = M.Mesh()
    p = np.asarray(start, float)
    pitch = 0.0
    for i, ln in enumerate(lengths):
        pitch += bends[i]
        d = M.rot_y(yaw) @ M.rot_x(pitch) @ np.array([0, 0, 1.0])
        q = p + d * ln
        if box:
            m.merge(M.limb(p, q, radii[i], radii[i + 1], mat, sides=4, twist=45))
        else:
            m.merge(M.limb(p, q, radii[i], radii[i + 1], mat, sides=sides))
        if joint and i < len(lengths) - 1:
            m.merge(joint(q, radii[i + 1], joint_mat or mat))
        p = q
    if tip:
        d = M.rot_y(yaw) @ M.rot_x(pitch + 15) @ np.array([0, 0, 1.0])
        m.merge(tip(p, d, radii[-1], tip_mat or mat))
    return m


def _knob(center, r, mat):
    return M.uv_sphere(r * 1.25, mat, seg=5, rings=3, center=center)


def _claw(p, d, r, mat):
    return M.cone(p, p + d * r * 4.5, r * 0.9, mat, sides=4)


def _spike(p, d, r, mat):
    return M.cone(p, p + d * r * 3.0, r * 0.9, mat, sides=4)


def _materials(**kw):
    return dict(kw)


def _thumb(mat, radii, bends, lengths, sides=6, box=False, joint=None, joint_mat=None,
           tip=None, tip_mat=None):
    return chain((-0.05, -0.004, 0.028), -52, lengths, radii, bends, mat, sides=sides,
                 box=box, joint=joint, joint_mat=joint_mat, tip=tip, tip_mat=tip_mat)


# ---- 1. arachnid ----------------------------------------------------------------
def arachnid():
    mats = _materials(chitin={"kd": (30, 23, 28)}, joint={"kd": (78, 46, 46)},
                      claw={"kd": (190, 176, 150)}, glow={"kd": (255, 140, 50), "ke": (255, 140, 50)})
    m = M.Mesh()
    m.merge(M.box((0.062, 0.022, PALM_LEN), "chitin", center=(0, 0, PALM_LEN / 2)))
    m.merge(M.box((0.05, 0.012, 0.05), "joint", center=(0, 0.015, 0.045)))               # carapace plate
    m.merge(M.uv_sphere(0.016, "glow", seg=6, rings=4, center=(0, -0.014, 0.05)))        # ember in palm
    for i, (x, yaw, k) in enumerate(FINGERS):
        aim = i in (1, 2, 3)
        bends = [-8, 6, 6] if aim else [-38, 62, 38]      # outer two arch like spider legs
        l = [0.060 * k, 0.062 * k, 0.050 * k]
        m.merge(chain((x, 0, PALM_LEN), yaw, l, [0.0075, 0.0058, 0.0045, 0.003], bends, "chitin",
                      sides=5, joint=_knob, joint_mat="joint", tip=_claw, tip_mat="claw"))
    m.merge(_thumb("chitin", [0.0075, 0.006, 0.0045], [30, 25], [0.04, 0.036], sides=5,
                   joint=_knob, joint_mat="joint", tip=_claw, tip_mat="claw"))
    m.merge(M.limb((0, 0, -0.04), (0, 0, 0.0), 0.034, 0.03, "joint", sides=6))           # wrist band
    return m, mats


# ---- 2. boney exoskeleton -----------------------------------------------------------
def boney():
    mats = _materials(bone={"kd": (212, 202, 172)}, bone_dark={"kd": (150, 136, 108)},
                      glow={"kd": (255, 150, 60), "ke": (255, 150, 60)})
    m = M.Mesh()
    for x in (-0.04, -0.02, 0.0, 0.02, 0.04):                                         # metacarpals
        m.merge(M.limb((x * 0.8, 0, 0.0), (x, 0, PALM_LEN), 0.0058, 0.0066, "bone", sides=5))
    for z in (0.02, 0.045, 0.07):                                                     # rib-like straps
        m.merge(M.box((0.108, 0.006, 0.008), "bone_dark", center=(0, 0.007, z)))
    m.merge(M.uv_sphere(0.012, "glow", seg=5, rings=3, center=(0, -0.004, 0.05)))
    for i, (x, yaw, k) in enumerate(FINGERS):
        aim = i in (1, 2, 3)
        bends = [4, 4, 4] if aim else [6, 12, 10]
        l = [0.040 * k, 0.030 * k, 0.026 * k]
        m.merge(chain((x, 0, PALM_LEN), yaw, l, [0.0066, 0.0056, 0.0046, 0.003], bends, "bone",
                      sides=5, joint=_knob, joint_mat="bone_dark", tip=_claw, tip_mat="bone_dark"))
    m.merge(_thumb("bone", [0.007, 0.0058, 0.0042], [28, 22], [0.032, 0.028], sides=5,
                   joint=_knob, joint_mat="bone_dark", tip=_claw, tip_mat="bone_dark"))
    for dz, r in ((-0.03, 0.03), (-0.012, 0.032)):                                    # wrist vertebrae
        m.merge(M.limb((0, 0, dz - 0.007), (0, 0, dz + 0.007), r, r, "bone_dark", sides=6))
    return m, mats


# ---- 3. black metal ---------------------------------------------------------------------
def black_metal():
    mats = _materials(metal={"kd": (24, 24, 29)}, trim={"kd": (110, 24, 24)},
                      spike={"kd": (74, 74, 82)}, glow={"kd": (255, 70, 40), "ke": (255, 70, 40)})
    m = M.Mesh()
    m.merge(M.box((0.098, 0.024, PALM_LEN), "metal", center=(0, 0, PALM_LEN / 2)))
    m.merge(M.box((0.09, 0.008, 0.03), "trim", center=(0, 0.016, 0.07)))
    m.merge(M.box((0.03, 0.004, 0.03), "glow", center=(0, -0.013, 0.05)))
    for i, (x, yaw, k) in enumerate(FINGERS):
        aim = i in (1, 2, 3)
        bends = [0, 0, 0] if aim else [10, 16, 12]
        l = [0.036 * k, 0.030 * k, 0.026 * k]
        f = chain((x, 0, PALM_LEN), yaw, l, [0.0105, 0.0095, 0.0085, 0.0065], bends, "metal", box=True,
                  tip=_claw, tip_mat="spike")
        m.merge(f)
        m.merge(_spike((x, 0.014, PALM_LEN - 0.004), np.array([0, 0.7, 0.7]), 0.005, "spike"))
    m.merge(_thumb("metal", [0.011, 0.009, 0.007], [20, 18], [0.03, 0.026], box=True,
                   tip=_claw, tip_mat="spike"))
    m.merge(M.limb((0, 0, -0.05), (0, 0, 0.0), 0.046, 0.04, "metal", sides=6))      # cuff
    for k in range(5):                                                                 # cuff spikes
        a = math.radians(-60 + 30 * k)
        base = np.array([math.sin(a) * 0.046, math.cos(a) * 0.046, -0.04])
        m.merge(_spike(base, np.array([math.sin(a), math.cos(a), -0.3]), 0.007, "spike"))
    return m, mats


# ---- 4. knight gauntlet ---------------------------------------------------------------------
def knight():
    mats = _materials(steel={"kd": (150, 156, 168)}, gold={"kd": (186, 146, 52)},
                      leather={"kd": (52, 36, 30)}, glow={"kd": (255, 210, 120), "ke": (255, 210, 120)})
    m = M.Mesh()
    m.merge(M.box((0.1, 0.022, PALM_LEN), "steel", center=(0, 0, PALM_LEN / 2)))
    m.merge(M.box((0.102, 0.004, 0.012), "gold", center=(0, 0.012, 0.0)))
    m.merge(M.box((0.026, 0.004, 0.026), "glow", center=(0, -0.012, 0.05)))
    for i, (x, yaw, k) in enumerate(FINGERS):
        aim = i in (1, 2, 3)
        bends = [0, 4, 4] if aim else [8, 14, 10]
        l = [0.036 * k, 0.030 * k, 0.026 * k]
        m.merge(chain((x, 0, PALM_LEN), yaw, l, [0.0105, 0.0098, 0.009, 0.0072], bends, "steel", box=True,
                      joint=lambda c, r, mat: M.box((r * 2.4, r * 2.2, 0.006), mat, center=c),
                      joint_mat="gold", tip=lambda p, d, r, mt: M.box((r * 2, r * 1.6, 0.012), mt,
                                                                       center=p + d * 0.004),
                      tip_mat="gold"))
    m.merge(_thumb("steel", [0.011, 0.0095, 0.008], [22, 18], [0.03, 0.026], box=True,
                   joint=lambda c, r, mat: M.box((r * 2.4, r * 2.2, 0.006), mat, center=c),
                   joint_mat="gold"))
    prof = [(0.04, -0.09), (0.047, -0.06), (0.054, -0.02), (0.05, 0.0)]
    m.merge(M.lathe(prof, "steel", sides=8).transform(M.rot_x(90)))                    # outer shell, axis -> +Z
    m.merge(M.lathe([(r - 0.006, y) for r, y in prof], "leather", sides=8).flip()      # inner liner so the
            .transform(M.rot_x(90)))                                                   # open cuff isn't see-through
    for rim in (M.lathe([(0.05, 0.0), (0.044, 0.0)], "steel", sides=8),                  # close the rims between
                M.lathe([(0.034, -0.09), (0.04, -0.09)], "steel", sides=8)):             # shell and liner
        m.merge(rim.transform(M.rot_x(90)))
    return m, mats


# ---- 5. obsidian shard (wild) ------------------------------------------------------------------
def obsidian():
    mats = _materials(glass={"kd": (38, 20, 66)}, edge={"kd": (96, 60, 160)},
                      glow={"kd": (190, 90, 255), "ke": (190, 90, 255)})
    m = M.Mesh()
    m.merge(M.limb((0, 0, -0.01), (0, 0, PALM_LEN), 0.05, 0.036, "glass", sides=5, twist=18))
    m.merge(M.uv_sphere(0.014, "glow", seg=5, rings=3, center=(0, -0.012, 0.045)))
    for i, (x, yaw, k) in enumerate(FINGERS):
        aim = i in (1, 2, 3)
        bends = [-4, 4, 3] if aim else [-14, 24, 16]
        l = [0.046 * k, 0.046 * k, 0.04 * k]
        m.merge(chain((x, 0, PALM_LEN), yaw, l, [0.0075, 0.006, 0.0045, 0.0], bends, "glass", sides=3,
                      joint=lambda c, r, mat: M.cone(c - np.array([0, 0, 0.004]),
                                                     c + np.array([0, 0.014, -0.004]), r, mat, sides=3),
                      joint_mat="edge"))
    m.merge(_thumb("glass", [0.0075, 0.006, 0.0], [24, 20], [0.034, 0.03], sides=3))
    for a in (-50, -20, 20, 50):                                                       # wrist shards
        d = M.rot_z(a) @ np.array([0, 1.0, -0.4])
        m.merge(M.cone(np.array([0, 0, -0.01]), np.array([0, 0, -0.01]) + d * 0.07, 0.012, "edge", sides=3))
    return m, mats


# ---- 6. ash wraith (wild) -------------------------------------------------------------------------
def wraith():
    mats = _materials(ash={"kd": (120, 116, 112)}, cinder={"kd": (58, 52, 50)},
                      glow={"kd": (255, 120, 50), "ke": (255, 120, 50)})
    m = M.Mesh()
    m.merge(M.box((0.058, 0.014, PALM_LEN), "ash", center=(0, 0, PALM_LEN / 2)))
    m.merge(M.uv_sphere(0.009, "glow", seg=5, rings=3, center=(0, -0.009, 0.05)))
    for i, (x, yaw, k) in enumerate(FINGERS):
        aim = i in (1, 2, 3)
        bends = [3, 6, 5] if aim else [8, 18, 20]
        l = [0.07 * k, 0.07 * k, 0.06 * k]
        m.merge(chain((x * 0.7, 0, PALM_LEN), yaw, l, [0.006, 0.0042, 0.0028, 0.0], bends, "ash", sides=4))
    m.merge(_thumb("ash", [0.0062, 0.0042, 0.0], [26, 20], [0.05, 0.04], sides=4))
    for k, x in enumerate((-0.02, 0.0, 0.02)):                                         # trailing rags
        m.merge(M.box((0.012, 0.002, 0.11 - 0.02 * abs(k - 1)), "cinder", center=(x, -0.004, -0.055)))
    return m, mats


VARIANTS = {
    "hand_arachnid": arachnid,
    "hand_boney": boney,
    "hand_black_metal": black_metal,
    "hand_knight": knight,
    "hand_obsidian": obsidian,
    "hand_wraith": wraith,
}
