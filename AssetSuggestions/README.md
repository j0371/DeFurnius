# AssetSuggestions

First-pass, procedurally generated asset suggestions for DeFurnius, made by Virgil (the LampLighters).
Nothing here is wired into the Unity project. It sits outside `DeFurnius/Assets` on purpose, so it can't
conflict with mechanics work. Copy what you like into `Assets/` yourself.

**None of this has been opened in Unity.** It was built and checked in a container with no Unity, using a
small software renderer for the previews (back-facing triangles are painted magenta, and none remain).

Start with the images in `previews/`.

## What's here

| Folder | Contents |
| --- | --- |
| `previews/` | Contact sheets and mock scenes. `scene_start.png` is the view from the cellar through the gate. |
| `textures/<core>/` | 128x128 tileable PNGs: `floor_stone`, `wall_brick`, `platform_ring`, `abyss_fog`, `lintel_inscription`, three poison emblems. Hell cores also have emissive maps, `pumpkin_skin`, `pumpkin_face`. |
| `models/hands/` | Six hand variants (OBJ + MTL). |
| `models/props/` | Ring-segment platforms (3 styles), launcher pad, pedestal, full Limbo layout, gate, cellar, 3 pumpkin enemies, 3 Dark One orbs, pillars, obelisk, rubble, ice spires. |
| `animations/` | Unity `.anim` clips: ring bob, pedestal lower, orb pulse and spin, launcher pulse, pumpkin idle and telegraph, hand sway. |
| `scripts/VirgilMotion.cs` | Code-driven bob, spin, pulse, sway and "lower" with no file-format risk. |
| `ui/` | HUD arrow (idle and parry-window colour), parry ring, three ending cards. |
| `tools/` | The generators (Python, needs numpy and Pillow). |

### Aesthetic cores (textures)
Each core is a dark-to-light colour ramp plus accents, dithered with a 4x4 Bayer pattern for the retro look.

| Core | Kind | Idea |
| --- | --- | --- |
| `ash_dusk` | hell | Closest to the brief: ashy brown-grey stone, ember cracks. |
| `devil_black` | hell | Near-black with blood red. |
| `rotwood_autumn` | hell | Warm October browns, leans into the Halloween brief. |
| `woodcut` | hell | Four colours only. Wildly different. |
| `sulfur_ash` | hell | Sickly yellow-green. Wildly different. |
| `glacier` | frost | Cool blue-grey whites, safest Treachery. |
| `whiteout` | frost | Almost no colour, blinding. |
| `blue_ice` | frost | Saturated cyan ice. |

### Hands
All five non-thumb fingers plus a thumb; the three middle fingers point straight ahead for the precision shot,
the outer two splay. Roughly life size, fingers along +Z. Each has a small emissive "ember" where the bolt would form.

`hand_arachnid` (the brief, arching spider-leg outer fingers), `hand_boney`, `hand_black_metal`, `hand_knight`,
`hand_obsidian`, `hand_wraith`. All are placeholders: blocky, under 900 triangles, no rig.

## Using it in Unity (untested notes)
- **Textures:** set Filter Mode to Point (no filter) and Compression to None, or the dithering turns to mush.
- **Models:** the OBJs have flat-shaded normals and planar UVs (about 2 m per texture tile). The `.mtl` files point at
  `textures/ash_dusk/...` by relative path. Unity may not resolve those, so assign materials by hand.
- **Re-theming:** the same names exist in every core, so swapping the texture on a material re-themes the model.
  Use a frost core for Treachery.
- **`pumpkin_face.png`** is wrapped lat-long around the whole head, so the face repeats. It's fine for a first look; a
  proper head UV would put one face on the front.
- **Animation clips** store local values, so animate a child of the object you place. `VirgilMotion.cs` does the same
  from code and is the safer option if a clip won't load.
- The `.anim` files are hand-written YAML and are the least certain part of this drop.

## Regenerating
```
PYTHONPATH=<dir containing numpy and PIL> python3 AssetSuggestions/tools/gen_textures.py
PYTHONPATH=<dir containing numpy and PIL> python3 AssetSuggestions/tools/gen_models.py hands props scenes anims
```
Output is deterministic. Palettes live in `tools/assetlib/cores.py`, hands in `hands.py`, everything else in `props.py`.

## Known gaps
- Hands are rough. The arachnid reads as a spider more than as a hand.
- No audio, no real character art, nothing is rigged.
- Frost variants of the models are not separate meshes; only the textures change.
- Parry-window colour and the out-of-view arrow are provided as sprites only; the logic is yours.

---

# Round 2

Built on top of the first drop (same tools, same conventions). New output lives in `round2/` and
`previews/round2_*`, `previews/cores*`; the shared tools gained a few options.

| What | Where |
| --- | --- |
| **Textured scenes** of the arena kit in every core (hell: cellar through the gate, and a fight mock; frost: Treachery) | `previews/cores_overview.png`, `previews/cores/` |
| 3 new cores: `bone_rust`, `violet_dusk`, `sunlit_snow` (11 in total) | `textures/` |
| **Dark One damage stages** 0-3 (shell cracks open, shards fly off, light bleeds out) and a **defeated shell with a doorway** to walk into | `models/round2/dark_one_*` |
| Frost kit: crystal-rimmed ring segment, frosted pedestal, icicle row, snow drift | `models/round2/` |
| **Poison idols** (rooster, snake, pig) for per-level set dressing | `models/round2/idol_*` |
| **Projectiles**: ember, thorn and skull, each in a normal and a cyan "parry window" version; player bolt, muzzle flash, hit spark | `models/round2/proj_*`, `bolt_player`, ... |
| 3 more hands: `hand_arachnid_v2` (carapace, spined legs, eye cluster, much more spider), `hand_cage`, `hand_wire` | `models/hands_round2/` |
| **VFX sprites**: 16-frame flame loop, ember particles, smoke, spark burst, snowflakes, parry and hit flashes, damage and frost vignettes | `round2/vfx/`, `previews/round2_vfx.png` |
| **HUD**: 4 crosshairs, 3 rage meter styles (bar, vertical gauge, 24-segment dial), boss bar (dark and Treachery versions) | `round2/hud/`, `previews/round2_hud_mock.png` |
| Skies per core, and floor sigils (ring + poison animal) per hell core | `round2/sky/`, `round2/decals/` |
| 8 more `.anim` clips (tumbling projectiles, flash pops, Dark One drift) | `round2/animations/` |
| `VirgilFlipbook.cs` (plays a sprite sheet on a quad) and `VirgilBillboard.cs` | `scripts/` |

Regenerate with:
```
PYTHONPATH=<numpy+PIL dir> python3 AssetSuggestions/tools/gen_textures.py
PYTHONPATH=<numpy+PIL dir> python3 AssetSuggestions/tools/gen_scenes.py
PYTHONPATH=<numpy+PIL dir> python3 AssetSuggestions/tools/gen_round2.py models hands vfx hud sky decals anims
```

Notes
- The preview renderer now samples textures, so the scene mocks show real palettes. Its near plane was also fixed,
  which slightly changes some round 1 preview images.
- The cage hand uses thin two-sided hoops; a sliver at their rims shows as a back-face in the sheet. Harmless.
- `dark_one_stage1-3` use a double-walled shell (outer glass, inner mirror) plus a dark core and a light cap.
- Like round 1, nothing here has been opened in Unity.
