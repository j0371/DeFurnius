"""Round 2 hand variants: a better arachnid, a reliquary cage and a wire minimalist.

Same layout rules as hands.py: wrist at z=0, fingers along +Z, back of hand +Y, thumb on -X,
five non-thumb fingers with the middle three pointing straight ahead.
"""
import math

import numpy as np

from . import hands as H
from . import mesh as M


def arachnid_v2():
    """Carapace palm, 3-segment spined legs for fingers, pedipalp thumb, eye cluster on the back."""
    mats = dict(chitin={"kd": (30, 23, 28)}, plate={"kd": (52, 34, 40)}, joint={"kd": (92, 52, 48)},
                spine={"kd": (190, 176, 150)}, glow={"kd": (255, 140, 50), "ke": (255, 140, 50)},
                eye={"kd": (255, 60, 40), "ke": (255, 60, 40)})
    m = M.Mesh()
    for z, w, d in ((0.02, 0.07, 0.04), (0.055, 0.075, 0.05), (0.085, 0.07, 0.04)):      # overlapping carapace plates
        m.merge(M.box((w, 0.018, d), "plate", center=(0, 0.012, z)))
    m.merge(M.box((0.06, 0.02, PALM := 0.085), "chitin", center=(0, -0.003, 0.0425)))
    m.merge(M.uv_sphere(0.017, "glow", seg=6, rings=4, center=(0, -0.016, 0.05)))
    for x, z in ((-0.012, 0.075), (0.012, 0.075), (-0.022, 0.06), (0.022, 0.06)):         # spider eyes
        m.merge(M.box((0.008, 0.006, 0.008), "eye", center=(x, 0.024, z)))
    for i, (x, yaw, k) in enumerate(H.FINGERS):
        aim = i in (1, 2, 3)
        bends = [-6, 8, 8] if aim else [-42, 70, 46]
        l = [0.062 * k, 0.066 * k, 0.054 * k]
        rad = [0.0075, 0.0058, 0.0046, 0.003]
        m.merge(H.chain((x, 0, PALM), yaw, l, rad, bends, "chitin", sides=5,
                        joint=H._knob, joint_mat="joint", tip=H._claw, tip_mat="spine"))
        # a pair of spines on each finger's first segment
        d0 = M.rot_y(yaw) @ M.rot_x(bends[0]) @ np.array([0, 0, 1.0])
        p0 = np.array([x, 0, PALM]) + d0 * l[0] * 0.55
        for s in (-1, 1):
            m.merge(M.cone(p0, p0 + np.array([s * 0.012, 0.012, -0.004]), 0.0035, "spine", sides=3))
    m.merge(H._thumb("chitin", [0.0085, 0.0065, 0.004], [24, 22], [0.032, 0.026], sides=5,
                     joint=H._knob, joint_mat="joint", tip=H._claw, tip_mat="spine"))
    for s in (-1, 1):                                                                   # two vestigial side legs at the wrist
        m.merge(H.chain((s * 0.03, 0, 0.0), s * 70, [0.04, 0.04], [0.005, 0.004, 0.003], [-40, 70], "chitin",
                        sides=4, tip=H._claw, tip_mat="spine"))
    m.merge(M.limb((0, 0, -0.045), (0, 0, 0.0), 0.034, 0.03, "joint", sides=6))
    return m, mats


def _band(p0, p1, r, mat, sides=8):
    """Open two-sided hoop: an outer wall plus a slightly smaller inside-out wall, so it reads
    from both sides and you can still see the ember through it. (Slivers at the rims show as
    back-faces in the previews; they are 0.8 mm wide.)"""
    outer = M.limb(p0, p1, r, r, mat, sides=sides, cap0=False, cap1=False)
    inner = M.limb(p0, p1, r - 0.0008, r - 0.0008, mat, sides=sides, cap0=False, cap1=False).flip()
    return M.Mesh().merge(outer).merge(inner)


def cage():
    """Reliquary: each finger is a three-rod cage, the palm holds a caged ember."""
    mats = dict(rod={"kd": (86, 80, 92)}, ring={"kd": (150, 130, 70)}, glow={"kd": (255, 150, 60), "ke": (255, 150, 60)},
                chain={"kd": (50, 48, 56)})
    m = M.Mesh()
    palm = 0.085
    for k in range(6):                                                                  # palm cage ribs
        a = math.radians(60 * k)
        top = (0.045 * math.cos(a), 0.045 * math.sin(a), palm * 0.5)
        m.merge(M.limb((0.0, 0.0, 0.0), top, 0.003, 0.003, "rod", sides=3).moved(pos=(0, 0, 0)))
        m.merge(M.limb(top, (0, 0, palm), 0.003, 0.003, "rod", sides=3))
    m.merge(M.uv_sphere(0.02, "glow", seg=6, rings=4, center=(0, 0, palm * 0.5)))
    for z in (0.0, palm * 0.5, palm):
        m.merge(_band((0, 0, z - 0.003), (0, 0, z + 0.003), 0.046, "ring"))
    for i, (x, yaw, k) in enumerate(H.FINGERS):
        aim = i in (1, 2, 3)
        bends = [2, 3, 3] if aim else [6, 12, 10]
        l = [0.04 * k, 0.034 * k, 0.03 * k]
        base = np.array([x, 0, palm])
        pitch = 0
        p = base
        for j, ln in enumerate(l):
            pitch += bends[j]
            d = M.rot_y(yaw) @ M.rot_x(pitch) @ np.array([0, 0, 1.0])
            q = p + d * ln
            side = np.cross(d, [0, 1, 0])
            side = side / np.linalg.norm(side)
            up = np.cross(side, d)
            for t in range(3):                                                          # three rods around the axis
                a = math.radians(120 * t)
                off = (math.cos(a) * side + math.sin(a) * up) * 0.007
                m.merge(M.limb(p + off, q + off, 0.0017, 0.0017, "rod", sides=3))
            m.merge(_band(q - d * 0.002, q + d * 0.002, 0.0095, "ring", sides=6))
            p = q
        m.merge(M.cone(p, p + M.rot_y(yaw) @ M.rot_x(pitch + 10) @ np.array([0, 0, 0.018]), 0.006, "ring", sides=4))
    m.merge(H._thumb("rod", [0.004, 0.0035, 0.003], [26, 22], [0.032, 0.026], sides=4))
    for k in range(3):                                                                  # hanging chain at the wrist
        m.merge(M.box((0.008, 0.008, 0.008), "chain", center=(0.02 * (k - 1), -0.03 - 0.012 * k, -0.02 - 0.01 * k)))
    m.merge(_band((0, 0, -0.04), (0, 0, 0.0), 0.034, "ring"))
    return m, mats


def wire():
    """Minimal: hair-thin one-triangle-thick strokes with cube joints. Reads as a schematic hand."""
    mats = dict(wire={"kd": (225, 225, 235), "ke": (225, 225, 235)}, node={"kd": (255, 140, 50), "ke": (255, 140, 50)})
    m = M.Mesh()
    palm = 0.085
    pts = [(-0.05, 0, 0.0), (0.05, 0, 0.0), (0.045, 0, palm), (-0.045, 0, palm)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        m.merge(M.limb(a, b, 0.0016, 0.0016, "wire", sides=3))
    m.merge(M.limb((-0.05, 0, 0), (0.045, 0, palm), 0.0012, 0.0012, "wire", sides=3))
    for i, (x, yaw, k) in enumerate(H.FINGERS):
        aim = i in (1, 2, 3)
        bends = [0, 2, 2] if aim else [6, 10, 8]
        l = [0.05 * k, 0.045 * k, 0.04 * k]
        p = np.array([x, 0, palm])
        pitch = 0
        for j, ln in enumerate(l):
            pitch += bends[j]
            q = p + M.rot_y(yaw) @ M.rot_x(pitch) @ np.array([0, 0, 1.0]) * ln
            m.merge(M.limb(p, q, 0.0016, 0.0016, "wire", sides=3))
            m.merge(M.box((0.006, 0.006, 0.006), "node", center=q))
            p = q
    m.merge(H._thumb("wire", [0.0016, 0.0016, 0.0016], [26, 22], [0.034, 0.028], sides=3))
    return m, mats


VARIANTS = {"hand_arachnid_v2": arachnid_v2, "hand_cage": cage, "hand_wire": wire}
