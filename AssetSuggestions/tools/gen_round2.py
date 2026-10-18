"""Round 2 generators: extra models, VFX sprites, HUD, skies, decals.

    PYTHONPATH=<dir with numpy and Pillow> python3 AssetSuggestions/tools/gen_round2.py [models hands vfx hud sky]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import gen_models  # noqa: E402
from assetlib import anim, emblems, hands2, props2, vfx  # noqa: E402
from assetlib.cores import CORES  # noqa: E402

ROOT = os.path.dirname(HERE)
R2 = os.path.join(ROOT, "round2")
PREV = os.path.join(ROOT, "previews")
LABEL = ImageFont.load_default(size=12)
CORE = {c["name"]: c for c in CORES}


def save(img, *parts):
    path = os.path.join(R2, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return img


def checker(w, h, a=(40, 40, 46), b=(52, 52, 60), s=8):
    img = Image.new("RGB", (w, h), a)
    d = ImageDraw.Draw(img)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=b)
    return img


def on_checker(sprite, scale=2):
    s = sprite.resize((sprite.width * scale, sprite.height * scale), Image.NEAREST)
    bg = checker(s.width, s.height).convert("RGBA")
    bg.alpha_composite(s)
    return bg


def vfx_group():
    fire = save(vfx.fire_sheet(), "vfx", "flame_sheet_4x4.png")
    embers = save(vfx.ember_sprites(), "vfx", "ember_particles_4x1.png")
    smoke = save(vfx.smoke_sheet(), "vfx", "smoke_sheet_4x1.png")
    spark = save(vfx.spark_burst(), "vfx", "spark_burst.png")
    snow = save(vfx.snow_sprites(), "vfx", "snowflakes_3x1.png")
    pf = save(vfx.parry_flash((60, 220, 255)), "vfx", "parry_flash.png")
    hit = save(vfx.parry_flash((255, 200, 80)), "vfx", "hit_flash.png")
    dv = save(vfx.vignette((150, 10, 10)), "vfx", "vignette_damage.png")
    fv = save(vfx.vignette((235, 245, 255)), "vfx", "vignette_frost.png")
    items = [("flame_sheet_4x4 (16 frames, loops)", fire, 2), ("ember_particles", embers, 4),
             ("smoke_sheet", smoke, 2), ("spark_burst", spark, 3), ("snowflakes", snow, 4),
             ("parry_flash (cyan = parry window)", pf, 1), ("hit_flash", hit, 1),
             ("vignette_damage", dv, 1), ("vignette_frost", fv, 1)]
    W = 1100
    sheet = Image.new("RGB", (W, 1500), (14, 14, 18))
    d = ImageDraw.Draw(sheet)
    x = y = 8
    row_h = 0
    for label, im, sc in items:
        t = on_checker(im, sc).convert("RGB")
        if x + t.width > W - 8:
            x, y, row_h = 8, y + row_h + 8, 0
        d.text((x, y), label, font=LABEL, fill=(235, 235, 235))
        sheet.paste(t, (x, y + 16))
        x += t.width + 12
        row_h = max(row_h, t.height + 16)
    sheet.crop((0, 0, W, y + row_h + 8)).save(os.path.join(PREV, "round2_vfx.png"))


def hud_group():
    ash, ice = CORE["ash_dusk"], CORE["glacier"]
    ch = save(vfx.crosshairs(), "hud", "crosshairs_4x1.png")
    ch_dark = save(vfx.crosshairs(color=(24, 34, 56)), "hud", "crosshairs_4x1_dark.png")
    fh, ff = vfx.rage_bar_horizontal(ash)
    save(fh, "hud", "rage_bar_h_frame.png")
    save(ff, "hud", "rage_bar_h_fill.png")
    fv, ffv = vfx.rage_bar_vertical(ash)
    save(fv, "hud", "rage_bar_v_frame.png")
    save(ffv, "hud", "rage_bar_v_fill.png")
    fd, segs = vfx.rage_dial(ash)
    save(fd, "hud", "rage_dial_frame.png")
    for i, s in enumerate(segs):
        save(s, "hud", "rage_dial_segments", f"seg_{i:02d}.png")
    bf, bfill = vfx.boss_bar(ash)
    save(bf, "hud", "boss_bar_frame.png")
    save(bfill, "hud", "boss_bar_fill.png")
    bf2, bfill2 = vfx.boss_bar(ice, bright=True)
    save(bf2, "hud", "boss_bar_frame_frost.png")
    save(bfill2, "hud", "boss_bar_fill_frost.png")

    def mock(style, core, bright):
        W, H = 480, 270
        bg = vfx.sky(core, W, H).convert("RGBA")
        if not bright:
            bg.alpha_composite(vfx.vignette((0, 0, 0), 256).resize((W, H), Image.NEAREST))
        frame, fill = vfx.boss_bar(core, bright=bright)
        bar_f, bar_fill = (bf2, bfill2) if bright else (bf, bfill)
        bg.alpha_composite(bar_f.resize((360, 30), Image.NEAREST), (60, 14))
        pct = 0.62
        bg.alpha_composite(bar_fill.crop((0, 0, int(bar_fill.width * pct), bar_fill.height)).resize(
            (int(270 * pct), 15), Image.NEAREST), (80, 22))
        cx = {0: 0, 1: 64, 2: 128}[style]
        bg.alpha_composite((ch_dark if bright else ch).crop((cx, 0, cx + 64, 64)), (W // 2 - 32, H // 2 - 32))
        if bright:
            return bg.convert("RGB")                             # Treachery has no rage meter
        if style == 0:
            bg.alpha_composite(fh, (20, H - 44))
            bg.alpha_composite(ff.crop((0, 0, int(ff.width * 0.7), ff.height)), (26, H - 38))
        elif style == 1:
            bg.alpha_composite(fv, (20, H - 214))
            bg.alpha_composite(ffv.crop((0, int(ffv.height * 0.35), ffv.width, ffv.height)), (27, H - 214 + 5 + int(ffv.height * 0.35)))
        else:
            bg.alpha_composite(fd.resize((96, 96), Image.NEAREST), (16, H - 112))
            for s in segs[:17]:
                bg.alpha_composite(s.resize((96, 96), Image.NEAREST), (16, H - 112))
        return bg.convert("RGB")

    sheet = Image.new("RGB", (480 * 3, 270 * 2 + 40), (14, 14, 18))
    d = ImageDraw.Draw(sheet)
    names = ("A: segmented bar + dot cross", "B: vertical gauge + claw ticks", "C: dial + ring")
    for i in range(3):
        sheet.paste(mock(i, ash, False), (480 * i, 20))
        d.text((480 * i + 6, 4), names[i], font=LABEL, fill=(235, 235, 235))
        sheet.paste(mock(i, ice, True), (480 * i, 270 + 40))
    d.text((6, 270 + 22), "Treachery (frost) version of the boss bar", font=LABEL, fill=(235, 235, 235))
    sheet.save(os.path.join(PREV, "round2_hud_mock.png"))


def sky_group():
    tiles = []
    for c in CORES:
        im = save(vfx.sky(c), "sky", f"sky_{c['name']}.png")
        tiles.append((c["name"], im))
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 340, rows * 190), (14, 14, 18))
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(tiles):
        x, y = (i % cols) * 340, (i // cols) * 190
        d.text((x + 6, y + 2), n, font=LABEL, fill=(235, 235, 235))
        sheet.paste(im.resize((330, 165), Image.NEAREST), (x + 5, y + 18))
    sheet.save(os.path.join(PREV, "round2_skies.png"))


def decal_group():
    hell = [c for c in CORES if c["kind"] == "hell"]
    sheet = Image.new("RGB", (3 * 260, len(hell) * 260), (30, 28, 30))
    for r, c in enumerate(hell):
        for k, name in enumerate(emblems.EMBLEMS):
            im = save(vfx.floor_decal(c, name), "decals", c["name"], f"decal_{name}.png")
            bg = Image.new("RGBA", im.size, tuple(c["ramp"][1]) + (255,))
            bg.alpha_composite(im)
            sheet.paste(bg.convert("RGB"), (k * 260 + 2, r * 260 + 2))
    sheet.save(os.path.join(PREV, "round2_decals.png"))


def hands_group():
    gen_models.build_group("Round 2 hands", hands2.VARIANTS, "hands_round2", chunk=3, fit=2.3)


def anims_group():
    d = os.path.join(R2, "animations")
    os.makedirs(d, exist_ok=True)
    for name, (dur, loop, pos, scale, euler) in anim.CLIPS2.items():
        with open(os.path.join(d, name + ".anim"), "w", newline="\n") as f:
            f.write(anim.clip(name, dur, pos=pos, scale=scale, euler=euler, loop=loop))
        print("anim", name)


def models():
    gen_models.build_group("Round 2 models", props2.VARIANTS, "round2", chunk=5, fit=2.9)


def main():
    groups = sys.argv[1:] or ["models"]
    if "models" in groups:
        models()
    if "hands" in groups:
        hands_group()
    if "anims" in groups:
        anims_group()
    for name, fn in (("vfx", vfx_group), ("hud", hud_group), ("sky", sky_group), ("decals", decal_group)):
        if name in groups:
            fn()


if __name__ == "__main__":
    main()
