"""Generate textures, emblems, UI cards and contact sheets.

Run from the repo root:
    PYTHONPATH=<dir with numpy and Pillow> python3 AssetSuggestions/tools/gen_textures.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from assetlib import emblems, textures, ui  # noqa: E402
from assetlib.cores import CORES  # noqa: E402

ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, "textures")
PREV = os.path.join(ROOT, "previews")
LABEL = ImageFont.load_default(size=12)


def save(img, *parts):
    path = os.path.join(*parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def tiled(img, n=2):
    out = Image.new("RGB", (img.width * n, img.height * n))
    for y in range(n):
        for x in range(n):
            out.paste(img, (x * img.width, y * img.height))
    return out


def sheet(core, imgs, emblem_imgs):
    """Contact sheet: 2x2 tiled textures with labels, then emblems."""
    cell = 256
    cols = 4
    names = [n for n in imgs if not n.endswith("_emissive")] + \
            [n for n in imgs if n.endswith("_emissive")]
    rows = (len(names) + cols - 1) // cols
    h = rows * (cell + 18) + 110
    out = Image.new("RGB", (cols * cell, h), (20, 20, 20))
    d = ImageDraw.Draw(out)
    for i, n in enumerate(names):
        t = tiled(imgs[n], 2 if imgs[n].width == 128 else 4).resize((cell, cell), Image.NEAREST)
        x, y = (i % cols) * cell, (i // cols) * (cell + 18)
        out.paste(t, (x, y + 18))
        d.text((x + 4, y + 2), n, font=LABEL, fill=(230, 230, 230))
    y0 = rows * (cell + 18) + 4
    d.text((4, y0), f"{core['name']}: {core['note']}", font=LABEL, fill=(230, 230, 230))
    for i, e in enumerate(emblem_imgs):
        bg = Image.new("RGB", e.size, core["ramp"][1])
        bg.paste(e, (0, 0), e)
        out.paste(bg, (4 + i * 70, y0 + 24))
    return out


def main():
    all_sheets = []
    for idx, core in enumerate(CORES):
        built = textures.build(core, idx)
        imgs = {n: textures.tex.to_image(a) for n, a in built.items()}
        for n, im in imgs.items():
            save(im, TEX, core["name"], n + ".png")
        eimgs = []
        for en in emblems.EMBLEMS:
            e = emblems.render(en, core["accent"])
            save(e, TEX, core["name"], "emblems", en + ".png")
            eimgs.append(e)
        save(ui.lintel(core), TEX, core["name"], "lintel_inscription.png")
        sh = sheet(core, imgs, eimgs)
        save(sh, PREV, f"textures_{core['name']}.png")
        all_sheets.append(sh)
        print("built", core["name"], len(imgs), "textures")

    # one overview: floor + wall + platform for every core, side by side
    cell = 192
    out = Image.new("RGB", (3 * cell, len(CORES) * (cell + 16)), (20, 20, 20))
    d = ImageDraw.Draw(out)
    for r, core in enumerate(CORES):
        for c, n in enumerate(("floor_stone", "wall_brick", "platform_ring")):
            t = Image.open(os.path.join(TEX, core["name"], n + ".png")).convert("RGB")
            t = tiled(t, 2).resize((cell, cell), Image.NEAREST)
            out.paste(t, (c * cell, r * (cell + 16) + 16))
        d.text((4, r * (cell + 16) + 1), f"{core['name']} ({core['kind']})",
               font=LABEL, fill=(230, 230, 230))
    save(out, PREV, "textures_overview.png")

    # shared UI assets (same for every core)
    white, cyan, amber = (255, 255, 255), (60, 220, 255), (255, 200, 40)
    save(ui.hud_arrow(white), ROOT, "ui", "hud_arrow_idle.png")
    save(ui.hud_arrow(cyan), ROOT, "ui", "hud_arrow_parry_window.png")
    save(ui.hud_parry_ring(amber), ROOT, "ui", "hud_parry_ring.png")
    for k in ("known", "liberated", "true"):
        save(ui.ending_card(k), ROOT, "ui", f"ending_{k}.png")
    print("done")


if __name__ == "__main__":
    main()
