"""Generate OBJ models and turntable contact sheets.

Run from the repo root:
    PYTHONPATH=<dir with numpy and Pillow> python3 AssetSuggestions/tools/gen_models.py [group ...]
Groups: hands props scenes anims (default: hands).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from assetlib import anim, hands, mesh, props, render  # noqa: E402

M_ROT = mesh.rot_y(0)
ROOT = os.path.dirname(HERE)
MODELS = os.path.join(ROOT, "models")
PREV = os.path.join(ROOT, "previews")


SPHERE_UV = ("pumpkin",)


def build_group(name, variants, folder, chunk=6, uv_scale=0.5, fit=2.9):
    items = []
    for vname, fn in variants.items():
        m, mats = fn()
        mesh.write_obj(m, os.path.join(MODELS, folder, vname + ".obj"), mats, uv_scale=uv_scale,
                       sphere_uv=SPHERE_UV)
        items.append((vname, m, mats))
        print(f"{vname}: {m.tri_count()} tris")
    os.makedirs(PREV, exist_ok=True)
    pages = [items[i:i + chunk] for i in range(0, len(items), chunk)]
    for n, page in enumerate(pages, 1):
        suffix = "" if len(pages) == 1 else f"_{n}"
        render.sheet(page, size=220, title=name, fit=fit).save(os.path.join(PREV, f"models_{folder}{suffix}.png"))


def scene_start():
    """View from inside the cellar through the gate into the Limbo arena."""
    import numpy as np
    m, mats = mesh.Mesh(), {}
    parts = [("cellar_room", (0, 0, 0)), ("gate", (0, 0, 0))]
    for name, pos in parts:
        part, pm = props.VARIANTS[name]()
        m.merge(part.moved(pos=pos)); mats.update(pm)
    arena, am = props.limbo_layout()
    m.merge(arena.moved(pos=(0, -0.8, 17)))
    mats.update(am)
    hand, hm = hands.boney()
    for k, v in hm.items():
        mats["h_" + k] = v
    hand.mats = ["h_" + x for x in hand.mats]
    m.merge(hand.moved(M_ROT, pos=(0, -0.8 + 1.75, 17 - 0.8), scale=6.0))
    out = []
    eye = np.array([0.0, 1.7, -4.8])
    for tgt, fov in (((0, 1.4, 17), 60), ((0, 1.2, 17), 38)):
        im, back = render.render(m, mats, eye, np.array(tgt), size=480, fov=fov, ssaa=2,
                                 bg=(14, 12, 16))
        out.append(im)
    return out


def scene_overview():
    """High angle on the Limbo layout with the hand on the pedestal and a few enemies for scale."""
    import numpy as np
    m, mats = props.limbo_layout()
    hand, hm = hands.boney()
    for k, v in hm.items():
        mats["h_" + k] = v
    hand.mats = ["h_" + x for x in hand.mats]
    m.merge(hand.moved(M_ROT, pos=(0, 1.75, -0.8), scale=6.0))
    im, _ = render.render(m, mats, np.array([14, 15, -15]), np.array([0, 0, 0]), size=480, fov=45,
                          ssaa=2, bg=(14, 12, 16))
    return [im]


def scene_fight():
    """A fight-arena mock: ring floor, pumpkin turrets on platforms, the Dark One hanging above."""
    import numpy as np
    m, mats = mesh.Mesh(), {}
    arena, am = props.limbo_layout()
    m.merge(arena)
    mats.update(am)
    for k in range(6):
        a = np.radians(k * 60 + 36)
        for name, pos in (("pumpkin_turret", (8.5 * np.sin(a), 0.6, 8.5 * np.cos(a))),):
            part, pm = props.VARIANTS[name]()
            part.transform(mesh.rot_y(np.degrees(a) + 180), pos=pos)
            m.merge(part)
            mats.update(pm)
    orb, om = props.VARIANTS["dark_one_split"]()
    orb.mats = ["orb_" + x for x in orb.mats]                    # avoid clashing with the arena's "glow"
    mats.update({"orb_" + k: v for k, v in om.items()})
    m.merge(orb.moved(pos=(0, 7, 0)))
    im, _ = render.render(m, mats, np.array([15, 12, -18]), np.array([0, 3, 0]), size=480, fov=45,
                          ssaa=2, bg=(14, 12, 16))
    return [im]


def save_scenes():
    from PIL import Image
    for name, fn in (("scene_start", scene_start), ("scene_limbo_overview", scene_overview),
                     ("scene_fight_mock", scene_fight)):
        ims = fn()
        out = Image.new("RGB", (480 * len(ims), 480))
        for i, im in enumerate(ims):
            out.paste(im, (480 * i, 0))
        out.save(os.path.join(PREV, name + ".png"))
        print("scene", name)


def save_anims():
    d = os.path.join(ROOT, "animations")
    os.makedirs(d, exist_ok=True)
    for name, (dur, loop, pos, scale, euler) in anim.CLIPS.items():
        with open(os.path.join(d, name + ".anim"), "w", newline="\n") as f:
            f.write(anim.clip(name, dur, pos=pos, scale=scale, euler=euler, loop=loop))
        print("anim", name)


def main():
    groups = sys.argv[1:] or ["hands"]
    if "props" in groups:
        build_group("Arena kit, enemies, Dark One, dressing", props.VARIANTS, "props", chunk=5)
    if "anims" in groups:
        save_anims()
    if "scenes" in groups:
        save_scenes()
    if "hands" in groups:
        build_group("Hand variants (fingers toward +Z)", hands.VARIANTS, "hands", fit=2.3)


if __name__ == "__main__":
    main()
