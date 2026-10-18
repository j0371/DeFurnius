"""Render every aesthetic core's arena mock scenes and an overview sheet.

    PYTHONPATH=<dir with numpy and Pillow> python3 AssetSuggestions/tools/gen_scenes.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from assetlib import scenes  # noqa: E402
from assetlib.cores import CORES  # noqa: E402

PREV = os.path.join(os.path.dirname(HERE), "previews", "cores")
LABEL = ImageFont.load_default(size=13)
SIZE = 360


def main():
    os.makedirs(PREV, exist_ok=True)
    rows = []
    for core in CORES:
        fight = scenes.fight_view(core, SIZE)
        if core["kind"] == "hell":
            ims = [scenes.start_view(core, SIZE), fight]
        else:
            ims = [fight]
        sheet = Image.new("RGB", (SIZE * len(ims), SIZE))
        for i, im in enumerate(ims):
            sheet.paste(im, (i * SIZE, 0))
        sheet.save(os.path.join(PREV, f"scene_{core['name']}.png"))
        rows.append((core, sheet))
        print("scene", core["name"])
    # overview: two columns per row
    out = Image.new("RGB", (SIZE * 2, len(rows) * (SIZE + 20)), (14, 14, 18))
    d = ImageDraw.Draw(out)
    for r, (core, sheet) in enumerate(rows):
        y = r * (SIZE + 20)
        d.text((6, y + 2), f"{core['name']} ({core['kind']}): {core['note']}", font=LABEL, fill=(235, 235, 235))
        out.paste(sheet, (0, y + 20))
    out.save(os.path.join(os.path.dirname(PREV), "cores_overview.png"))


if __name__ == "__main__":
    main()
