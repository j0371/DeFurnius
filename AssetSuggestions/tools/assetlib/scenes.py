"""Textured mock scenes: the arena kit dressed in each aesthetic core."""
import math
import os

import numpy as np
from PIL import Image

from . import hands, mesh as M, props, render

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEXDIR = os.path.join(ROOT, "textures")


def load_tex(core_name, fname):
    p = os.path.join(TEXDIR, core_name, fname)
    return np.array(Image.open(p).convert("RGB"))


def themed(mats, core):
    """Copy materials, point maps at `core`, and recolour the untextured accents."""
    out = {}
    ramp = core["ramp"]
    for k, v in mats.items():
        v = dict(v)
        if "map" in v:
            base = os.path.basename(v["map"])
            if core["kind"] == "frost" and base.startswith("pumpkin"):
                base = "floor_stone.png"
            if core["kind"] == "frost" and base == "lintel_inscription.png":
                base = "wall_brick.png"
            v["map"] = base
            v["kd"] = ramp[3]
        elif k == "glow":
            v["kd"] = v["ke"] = core["glow"]
        elif k == "trim":
            v["kd"] = ramp[2]
        elif k in ("ice", "ice_dark"):
            v["kd"] = ramp[4] if k == "ice" else ramp[1]
        out[k] = v
    return out


def textures_for(mats, core_name):
    return {k: load_tex(core_name, v["map"]) for k, v in mats.items() if "map" in v}


def _merge(parts):
    m, mats = M.Mesh(), {}
    for prefix, (part, pm), kw in parts:
        part = part.copy()
        part.transform(kw.get("rot"), kw.get("pos", (0, 0, 0)), kw.get("scale", 1.0))
        if prefix:
            part.mats = [prefix + x for x in part.mats]
            pm = {prefix + k: v for k, v in pm.items()}
        m.merge(part)
        mats.update(pm)
    return m, mats


def start_view(core, size=360):
    m, mats = _merge([
        ("", props.cellar_room(), {}),
        ("", props.gate(), {}),
        ("", props.limbo_layout(), {"pos": (0, -0.8, 17)}),
        ("h_", hands.boney(), {"pos": (0, 0.95, 16.2), "scale": 6.0}),
    ])
    mats = themed(mats, core)
    tx = textures_for(mats, core["name"])
    return render.render(m, mats, np.array([0.0, 1.7, -4.8]), np.array([0, 1.3, 17]), size=size, fov=55,
                         ssaa=2, bg=tuple(core["ramp"][0]), textures=tx)[0]


def fight_view(core, size=360):
    parts = [("", props.limbo_layout(), {})]
    if core["kind"] == "hell":
        for k in range(6):
            a = math.radians(k * 60 + 36)
            parts.append(("", props.pumpkin_turret(),
                          {"rot": M.rot_y(math.degrees(a) + 180), "pos": (8.5 * math.sin(a), 0.6, 8.5 * math.cos(a))}))
        parts.append(("orb_", props.dark_one("split"), {"pos": (0, 7, 0)}))
    else:
        for k in range(6):
            a = math.radians(k * 60 + 36)
            parts.append(("", props.ice_spires(seed=k), {"pos": (8.5 * math.sin(a), 0.6, 8.5 * math.cos(a)),
                                                         "scale": 1.0}))
        orb = props.dark_one("split")
        orb[0].transform(pos=(0, 7, 0))
        parts.append(("orb_", orb, {}))
    m, mats = _merge(parts)
    mats = themed(mats, core)
    if core["kind"] == "frost":
        mats["orb_mirror"] = {"kd": (255, 255, 255), "ke": (255, 255, 255)}      # blinding half
        mats["orb_glass"] = {"kd": (120, 170, 215)}                               # translucent half, shaded
        mats["orb_trim"] = {"kd": core["ramp"][0]}
    tx = textures_for(mats, core["name"])
    bg = tuple(core["ramp"][2]) if core["kind"] == "frost" else tuple(core["ramp"][0])
    return render.render(m, mats, np.array([15.0, 12, -18]), np.array([0, 3, 0]), size=size, fov=45, ssaa=2,
                         bg=bg, textures=tx)[0]
