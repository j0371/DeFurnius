"""Round 2 models: Dark One damage stages and portal, frost kit, poison idols, projectiles."""
import math

import numpy as np

from . import mesh as M
from .props import GLOW, STONE, TRIM, _mats, pillar, pedestal, prism, ring_segment, ice_spires


# ---- the Dark One: ego resistance as damage stages --------------------------------------------------
def _orb_mats():
    return _mats(glass={"kd": (40, 40, 60)}, mirror={"kd": (150, 160, 175)}, core={"kd": (6, 6, 10)},
                 trim={"kd": (18, 18, 24)}, glow={"kd": (230, 240, 255), "ke": (230, 240, 255)})


def _shell(radius, open_deg, mat_out, mat_in):
    """Sphere with a round opening facing +Z (open_deg = half-angle of the hole), double-walled."""
    th0 = math.radians(open_deg)
    outer = M.uv_sphere(radius, mat_out, seg=18, rings=8, theta0=th0, theta1=math.pi)
    inner = M.uv_sphere(radius - 0.08, mat_in, seg=18, rings=8, theta0=th0, theta1=math.pi).flip()
    m = M.Mesh().merge(outer).merge(inner)
    # rim between the walls so the opening isn't see-through
    rim_o = radius * math.sin(th0), radius * math.cos(th0)
    rim_i = (radius - 0.08) * math.sin(th0), (radius - 0.08) * math.cos(th0)
    m.merge(M.lathe([(rim_i[0], rim_i[1]), (rim_o[0], rim_o[1])], mat_out, sides=18).flip())
    return m.transform(M.rot_x(90))          # pole +Y -> +Z so the opening faces the player


def dark_one_stage(stage):
    """stage 0 = whole, 1 = cracked, 2 = open and bleeding light, 3 = nearly gone."""
    mats = _orb_mats()
    m = M.Mesh()
    r = (2.0, 2.0, 1.95, 1.8)[stage]
    if stage == 0:
        m.merge(M.uv_sphere(r, "mirror", seg=18, rings=5, theta1=math.pi / 2).transform(M.rot_z(-90)))
        m.merge(M.uv_sphere(r, "glass", seg=18, rings=5, theta0=math.pi / 2).transform(M.rot_z(-90)))
    else:
        open_deg = (0, 25, 48, 70)[stage]
        m.merge(_shell(r, open_deg, "glass", "mirror"))
        m.merge(M.uv_sphere(1.0, "core", seg=12, rings=6))
        cap = M.uv_sphere(1.15 if stage < 3 else 1.3, "glow", seg=10, rings=5, theta0=0.0, theta1=0.7) \
            .transform(M.rot_x(90)).moved(pos=(0, 0, 0.5))
        m.merge(cap).merge(cap.copy().flip())                          # light cap, visible from both sides
    n_shards = (3, 8, 14, 22)[stage]
    rng = np.random.default_rng(stage + 11)
    for _ in range(n_shards):
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        dist = rng.uniform(2.4, 3.0 + stage * 0.7)
        s = rng.uniform(0.12, 0.35)
        m.merge(M.cone(d * dist, d * dist + rng.normal(size=3) * 0.2 + d * s * 3, s, "mirror"
                       if stage > 1 else "trim", sides=3))
    return m, mats


def dark_one_dead():
    """Defeated: a darkened shell with a doorway-sized opening the player walks into."""
    mats = _mats(shell={"kd": (14, 14, 20)}, inside={"kd": (3, 3, 6)}, rim={"kd": (60, 60, 80), "ke": (60, 60, 80)})
    m = M.Mesh()
    th0 = math.radians(22)
    r = 3.0
    m.merge(M.uv_sphere(r, "shell", seg=20, rings=9, theta0=th0, theta1=math.pi).transform(M.rot_x(90)))
    m.merge(M.uv_sphere(r - 0.1, "inside", seg=20, rings=9, theta0=th0, theta1=math.pi).flip().transform(M.rot_x(90)))
    ring = M.lathe([((r - 0.1) * math.sin(th0), (r - 0.1) * math.cos(th0)),
                    (r * math.sin(th0), r * math.cos(th0))], "rim", sides=20).flip().transform(M.rot_x(90))
    m.merge(ring)
    m.merge(M.box((3.0, 0.2, 5.0), "inside", center=(0, -1.15, 0.2)))   # floor to walk on
    return m, mats


# ---- frost kit ---------------------------------------------------------------------------------------
ICE = {"kd": (200, 225, 240)}
ICE_DARK = {"kd": (120, 160, 190)}


def ring_segment_frost():
    seg, mats = ring_segment("plain")
    mats = dict(mats, ice=ICE, ice_dark=ICE_DARK)
    crystals, _ = ice_spires(seed=2)
    seg.merge(crystals.moved(M.rot_y(20), pos=(7.2, 0.6, 5.5), scale=0.45))
    seg.merge(crystals.moved(M.rot_y(70), pos=(3.8, 0.6, 7.4), scale=0.35))
    return seg, mats


def pedestal_frost():
    ped, mats = pedestal()
    mats = dict(mats, ice=ICE, ice_dark=ICE_DARK)
    crystals, _ = ice_spires(seed=9)
    for k in range(5):
        a = math.radians(72 * k + 15)
        ped.merge(crystals.moved(M.rot_y(30 * k), pos=(1.6 * math.sin(a), 0.4, 1.6 * math.cos(a)), scale=0.3))
    return ped, mats


def icicle_row(n=9, span=8.0):
    mats = _mats(ice=ICE, ice_dark=ICE_DARK)
    rng = np.random.default_rng(4)
    m = M.Mesh()
    for k in range(n):
        x = -span / 2 + span * k / (n - 1) + rng.uniform(-0.2, 0.2)
        h = rng.uniform(0.6, 2.2)
        m.merge(M.limb((x, 0, 0), (x, -h, 0), 0.22, 0.0, "ice" if k % 2 else "ice_dark", sides=4, cap1=False))
    m.merge(M.box((span + 0.6, 0.18, 0.5), "ice_dark", center=(0, 0.09, 0)))
    return m, mats


def snow_drift():
    mats = _mats(snow={"kd": (238, 244, 250)})
    m = M.Mesh()
    for (x, z, r) in ((0, 0, 1.4), (1.3, 0.4, 0.9), (-1.2, -0.3, 1.0), (0.3, -1.1, 0.7)):
        m.merge(M.uv_sphere(r, "snow", seg=8, rings=4, theta1=math.pi / 2, center=(x, 0, z), squash=(1.4, 0.55, 1.2)))
    return m, mats


# ---- poison idols (set dressing per level) -----------------------------------------------------------------
def idol_rooster():
    mats = _mats(stone=STONE, beak={"kd": (200, 150, 40)}, comb={"kd": (170, 40, 30)}, glow=GLOW)
    m = M.Mesh()
    m.merge(M.limb((0, 0, 0), (0, 0.4, 0), 0.7, 0.6, "stone", sides=6))
    m.merge(M.limb((0, 0.4, 0), (0, 2.6, 0), 0.45, 0.4, "stone", sides=6))
    m.merge(M.box((0.7, 0.6, 0.7), "stone", center=(0, 2.9, 0)))                       # head block
    m.merge(prism([(-0.14, 0.35), (0.14, 0.35), (0, 0.95)], 2.78, 2.9, "beak"))        # beak
    for k, h in enumerate((0.5, 0.75, 0.55)):
        m.merge(M.box((0.12, h, 0.2), "comb", center=(0, 3.2 + h / 2 - 0.05, -0.1 + 0.18 * k - 0.18)))
    m.merge(M.box((0.08, 0.08, 0.08), "glow", center=(0.3, 3.0, 0.36)))
    m.merge(M.box((0.08, 0.08, 0.08), "glow", center=(-0.3, 3.0, 0.36)))
    for a in (-30, 0, 30):                                                              # tail fan behind
        d = M.rot_z(a) @ np.array([0, 1.0, 0])
        m.merge(M.limb((0, 1.4, -0.4), (0, 1.4, -0.4) + d * 1.4 + np.array([0, 0, -0.5]), 0.12, 0.03, "comb", sides=3))
    return m, mats


def idol_snake():
    mats = _mats(stone=STONE, scale={"kd": (56, 90, 56)}, glow=GLOW)
    m = M.Mesh()
    m.merge(M.limb((0, 0, 0), (0, 0.4, 0), 0.7, 0.6, "stone", sides=6))
    pts = []
    for i in range(33):
        t = i / 32
        a = t * 3 * 2 * math.pi
        pts.append(np.array([0.7 * math.cos(a), 0.4 + t * 2.4, 0.7 * math.sin(a)]))
    for i in range(32):
        r = 0.2 - 0.07 * i / 32
        m.merge(M.limb(pts[i], pts[i + 1], r, r * 0.95, "scale", sides=5))
    m.merge(M.limb((0, 0.4, 0), (0, 2.5, 0), 0.32, 0.3, "stone", sides=6))
    hd = pts[-1]
    m.merge(M.box((0.34, 0.2, 0.46), "scale", center=hd + np.array([0, 0.1, 0.1])))
    m.merge(M.box((0.06, 0.06, 0.06), "glow", center=hd + np.array([0.12, 0.2, 0.28])))
    m.merge(M.box((0.06, 0.06, 0.06), "glow", center=hd + np.array([-0.12, 0.2, 0.28])))
    return m, mats


def idol_pig():
    mats = _mats(stone=STONE, snout={"kd": (196, 120, 120)}, glow=GLOW)
    m = M.Mesh()
    m.merge(M.limb((0, 0, 0), (0, 0.4, 0), 0.7, 0.6, "stone", sides=6))
    m.merge(M.limb((0, 0.4, 0), (0, 2.2, 0), 0.5, 0.45, "stone", sides=6))
    m.merge(M.box((1.1, 0.95, 0.9), "stone", center=(0, 2.75, 0)))                      # broad head
    m.merge(M.box((0.5, 0.36, 0.3), "snout", center=(0, 2.6, 0.55)))                    # snout
    for x in (-0.12, 0.12):
        m.merge(M.box((0.07, 0.1, 0.05), "stone", center=(x, 2.6, 0.72)))
    for x in (-0.5, 0.5):
        m.merge(prism([(x - 0.18, 0.0), (x + 0.18, 0.0), (x + (0.28 if x > 0 else -0.28), -0.35)], 3.15, 3.22, "stone"))
    for x in (-0.3, 0.3):
        m.merge(M.box((0.12, 0.12, 0.08), "glow", center=(x, 2.9, 0.46)))
    return m, mats


# ---- projectiles ---------------------------------------------------------------------------------------------
def _proj_mats(parry):
    if parry:   # the parry window recolours the projectile
        return _mats(body={"kd": (60, 220, 255), "ke": (60, 220, 255)}, hot={"kd": (230, 250, 255),
                                                                           "ke": (230, 250, 255)},
                     dark={"kd": (10, 60, 80)})
    return _mats(body={"kd": (255, 120, 30), "ke": (255, 120, 30)}, hot={"kd": (255, 235, 170), "ke": (255, 235, 170)},
                 dark={"kd": (70, 24, 10)})


def proj_ember(parry=False):
    """Fast round ember with a short tail. Flies along +Z."""
    m = M.Mesh()
    m.merge(M.uv_sphere(0.16, "body", seg=6, rings=4))
    m.merge(M.uv_sphere(0.08, "hot", seg=5, rings=3))
    m.merge(M.cone((0, 0, -0.1), (0, 0, -0.9), 0.14, "body", sides=5))
    m.merge(M.cone((0, 0, -0.1), (0, 0, -0.55), 0.07, "hot", sides=4))
    return m, _proj_mats(parry)


def proj_thorn(parry=False):
    """Needle-like shot: reads as 'fast' and has a clear silhouette to parry."""
    m = M.Mesh()
    m.merge(M.limb((0, 0, -0.5), (0, 0, 0.5), 0.1, 0.0, "body", sides=4, cap1=False, twist=45))
    m.merge(M.limb((0, 0, -0.5), (0, 0, -0.9), 0.0, 0.1, "hot", sides=4, cap0=False))
    for a in (0, 90, 180, 270):
        d = M.rot_z(a) @ np.array([1.0, 0, 0])
        m.merge(M.cone(d * 0.1 + np.array([0, 0, -0.35]), d * 0.28 + np.array([0, 0, -0.7]), 0.05, "dark", sides=3))
    return m, _proj_mats(parry)


def proj_skull(parry=False):
    """Chunky tumbling skull-ish cube. Slower-looking but still fast, big hit target."""
    m = M.Mesh()
    m.merge(M.box((0.32, 0.3, 0.34), "body"))
    m.merge(M.box((0.22, 0.12, 0.2), "dark", center=(0, -0.2, 0.0)))
    for x in (-0.08, 0.08):
        m.merge(M.box((0.07, 0.07, 0.04), "dark", center=(x, 0.03, 0.175)))
    m.merge(M.cone((0, 0, -0.17), (0, 0, -1.0), 0.15, "hot", sides=4))
    return m, _proj_mats(parry)


def bolt_player():
    """The hand's bolt: white-hot core and orange streak. Length 2 m along +Z."""
    mats = _mats(core={"kd": (255, 250, 220), "ke": (255, 250, 220)},
                 flame={"kd": (255, 130, 40), "ke": (255, 130, 40)})
    m = M.Mesh()
    m.merge(M.cone((0, 0, 1.0), (0, 0, 1.45), 0.05, "core", sides=4))
    m.merge(M.limb((0, 0, 1.0), (0, 0, -0.2), 0.05, 0.03, "core", sides=4))
    m.merge(M.limb((0, 0, 1.0), (0, 0, -1.0), 0.11, 0.0, "flame", sides=5, cap1=False))
    for a in (45, 135):                                                     # cross-fins for readability
        r = M.rot_z(a)
        m.merge(M.box((0.34, 0.01, 1.1), "flame", center=(0, 0, 0.1)).transform(r))
    return m, mats


def muzzle_flash():
    mats = _mats(flame={"kd": (255, 150, 50), "ke": (255, 150, 50)}, core={"kd": (255, 245, 200), "ke": (255, 245, 200)})
    m = M.Mesh()
    for k in range(7):
        a = math.radians(360 * k / 7)
        d = np.array([math.cos(a), math.sin(a), 0.6])
        m.merge(M.cone(np.zeros(3), d / np.linalg.norm(d) * (0.45 if k % 2 else 0.3), 0.07, "flame", sides=4))
    m.merge(M.cone(np.zeros(3), np.array([0, 0, 0.7]), 0.12, "core", sides=5))
    return m, mats


def hit_spark():
    mats = _mats(spark={"kd": (255, 220, 140), "ke": (255, 220, 140)})
    rng = np.random.default_rng(8)
    m = M.Mesh()
    for _ in range(12):
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        m.merge(M.cone(d * 0.1, d * rng.uniform(0.35, 0.8), 0.03, "spark", sides=3))
    return m, mats


VARIANTS = {
    "dark_one_stage0": lambda: dark_one_stage(0),
    "dark_one_stage1": lambda: dark_one_stage(1),
    "dark_one_stage2": lambda: dark_one_stage(2),
    "dark_one_stage3": lambda: dark_one_stage(3),
    "dark_one_dead": dark_one_dead,
    "ring_segment_frost": ring_segment_frost,
    "pedestal_frost": pedestal_frost,
    "icicle_row": icicle_row,
    "snow_drift": snow_drift,
    "idol_rooster": idol_rooster,
    "idol_snake": idol_snake,
    "idol_pig": idol_pig,
    "proj_ember": proj_ember,
    "proj_ember_parry": lambda: proj_ember(True),
    "proj_thorn": proj_thorn,
    "proj_thorn_parry": lambda: proj_thorn(True),
    "proj_skull": proj_skull,
    "proj_skull_parry": lambda: proj_skull(True),
    "bolt_player": bolt_player,
    "muzzle_flash": muzzle_flash,
    "hit_spark": hit_spark,
}
