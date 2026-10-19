"""UI and text assets: lintel inscription, HUD projectile indicator, ending cards."""
import math

from PIL import Image, ImageDraw, ImageFont


def _font(px):
    return ImageFont.load_default(size=px)


def pixel_text(text, px, fg, bg, pad=6, scale=3):
    """Render text with no antialiasing at `px`, then upscale with nearest."""
    probe = Image.new("L", (1, 1))
    f = _font(px)
    box = ImageDraw.Draw(probe).textbbox((0, 0), text, font=f)
    w, h = box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2
    img = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.text((pad - box[0], pad - box[1]), text, font=f, fill=1)
    mask = img.resize((w * scale, h * scale), Image.NEAREST).convert("L")
    out = Image.new("RGB", mask.size, bg)
    out.paste(Image.new("RGB", mask.size, fg), (0, 0), mask)
    return out


def lintel(core):
    """Carved stone lintel with the Dante line, for the cellar doorway."""
    r = core["ramp"]
    text = pixel_text("ABANDON ALL HOPE, YE WHO ENTER HERE", 11,
                      r[-1] if core["kind"] == "hell" else r[0], r[1], pad=5, scale=2)
    w, h = 512, 64
    img = Image.new("RGB", (w, h), r[1])
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=r[3], width=3)
    d.rectangle([5, 5, w - 6, h - 6], outline=r[0], width=1)
    t = text.copy()
    t.thumbnail((w - 20, h - 16), Image.NEAREST)
    img.paste(t, ((w - t.width) // 2, (h - t.height) // 2))
    return img


def hud_arrow(color, size=48):
    """Chevron that sits on the screen edge and points toward a threat."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size // 2
    d.polygon([(c, 6), (size - 8, size - 10), (c, size - 18), (8, size - 10)],
              fill=tuple(color) + (255,))
    return img


def hud_parry_ring(color, size=96):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, size - 5, size - 5], outline=tuple(color) + (255,), width=4)
    for a in range(0, 360, 45):
        x = size / 2 + math.cos(math.radians(a)) * (size / 2 - 4)
        y = size / 2 + math.sin(math.radians(a)) * (size / 2 - 4)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=tuple(color) + (255,))
    return img


def ending_card(kind, size=(640, 360)):
    """The three ending screens as concept cards (Unity text goes in a Canvas)."""
    w, h = size
    if kind == "known":
        bg, fg, lines = (0, 0, 0), (235, 235, 235), ["It is known."]
    elif kind == "liberated":
        bg, fg, lines = (255, 255, 255), (20, 20, 20), ["You Have Been Liberated"]
    else:
        bg, fg = (0, 0, 0), (225, 225, 225)
        lines = ["You embarked on your fight, and fought well.",
                 "The darkness You fight is within You;",
                 "do You now see that the light that You seek",
                 "is too, within You."]
    img = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(img)
    f = _font(20 if len(lines) == 1 else 15)
    total = len(lines) * 26
    y = (h - total) // 2
    for ln in lines:
        w_ = d.textlength(ln, font=f)
        d.text(((w - w_) / 2, y), ln, font=f, fill=fg)
        y += 26
    return img
