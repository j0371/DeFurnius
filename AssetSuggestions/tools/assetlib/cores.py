"""Aesthetic cores: each is a dark->light colour ramp plus accent colours.

`kind` is "hell" (levels 1-4) or "frost" (Treachery / The Dark One).
"""
from .tex import hex_rgb


def _core(name, kind, ramp, accent, glow, pumpkin=None, note="", gain=1.0):
    return {
        "gain": gain,
        "name": name,
        "kind": kind,
        "ramp": [hex_rgb(c) for c in ramp],
        "accent": hex_rgb(accent),
        "glow": hex_rgb(glow),
        "pumpkin": hex_rgb(pumpkin) if pumpkin else None,
        "note": note,
    }


CORES = [
    # ---- hell cores -------------------------------------------------------
    _core("ash_dusk", "hell",
          ["#0a0807", "#171210", "#251d19", "#372b24", "#4d3d33", "#6b5748"],
          "#c2541c", "#ff8a2a", "#b8501e",
          "Closest to the brief: ashy brown-grey stone, ember cracks, DUSK-ish."),
    _core("devil_black", "hell",
          ["#030203", "#0c0507", "#1b0a0f", "#33121a", "#521a24", "#7a2630"],
          "#d1202a", "#ff5a3c", "#8a1a12",
          "Near-black with blood red, closer to Devil Daggers."),
    _core("rotwood_autumn", "hell",
          ["#0f0a06", "#1e130a", "#33200f", "#4e3216", "#6f4a1e", "#97682a"],
          "#d9791c", "#ffb040", "#d9791c",
          "Warm October browns and ochre, leans into the Halloween brief."),
    _core("woodcut", "hell",
          ["#000000", "#14110f", "#2c2723", "#cfc7b4"],
          "#b3261e", "#e14a3a", "#b3261e",
          "Four colours only: ink, soot, bone paper and one red. Wildly different.",
          gain=0.7),
    _core("sulfur_ash", "hell",
          ["#0a0b06", "#16180c", "#262a14", "#3b4120", "#575f2e", "#7d8640"],
          "#c8c020", "#f0ea50", "#b0a418",
          "Sickly sulfur green-yellow. Wildly different, more toxic than fiery."),
    # ---- frost cores (Treachery) -----------------------------------------
    _core("glacier", "frost",
          ["#5b758c", "#7f97aa", "#a4b8c6", "#c9d6de", "#e3ecf1", "#f8fbff"],
          "#7fd3ff", "#ffffff", None,
          "Cool blue-grey whites. Safest reading of the inversion brief."),
    _core("whiteout", "frost",
          ["#9a9fa6", "#b8bcc2", "#d2d5d9", "#e6e8ea", "#f4f5f6", "#ffffff"],
          "#a8d8ff", "#ffffff", None,
          "Almost no colour: neutral greys to pure white, blinding."),
    _core("blue_ice", "frost",
          ["#3d6a8c", "#5d8fb2", "#85b5d1", "#add2e6", "#d4eaf5", "#f2fbff"],
          "#00cfff", "#e8fbff", None,
          "Saturated cyan ice. Most colourful, least 'inverted ash'."),
    # ---- round 2 additions (appended so earlier cores keep their seeds) ------
    _core("bone_rust", "hell",
          ["#0b0907", "#1c1713", "#33291f", "#554533", "#85704f", "#b7a073"],
          "#b5441b", "#ff7a2e", "#c8671f",
          "Catacomb bone and rusted iron. Lighter and chalkier than the others."),
    _core("violet_dusk", "hell",
          ["#07050b", "#120c1c", "#201631", "#33224c", "#4d3472", "#75529e"],
          "#d03fb0", "#ff6adf", "#c0562a",
          "Occult violet with magenta cracks. Pumpkins stay orange so they still pop."),
    _core("sunlit_snow", "frost",
          ["#a69a92", "#bfb4ac", "#d6ccc4", "#e8dfd8", "#f6f0eb", "#fffaf5"],
          "#ffd9a0", "#fffaf0", None,
          "Warm-tinted snow, the one frost core with a hint of the autumn palette."),
]
