"""Writes simple Unity AnimationClip (.anim) files as YAML.

Position / scale / rotation tracks on the animated object itself (path ""), sampled
from Python functions. Unity stores LOCAL transform values per clip, so animate a
child (or a pivot) of the placed object, not the object whose scene position you
set. UNTESTED in the Unity editor; see scripts/VirgilMotion.cs for a code-driven
alternative that has no file-format risk.
"""
import math

HEADER = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {name}
  serializedVersion: 7
  m_Legacy: 0
  m_Compressed: 0
  m_UseHighQualityCurve: 1
"""


def euler_to_quat(x, y, z):
    """Degrees, Unity order (Z, X, Y applied intrinsically) -> (x, y, z, w)."""
    rx, ry, rz = (math.radians(a) / 2 for a in (x, y, z))
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return (sx * cy * cz + cx * sy * sz,
            cx * sy * cz - sx * cy * sz,
            cx * cy * sz - sx * sy * cz,
            cx * cy * cz + sx * sy * sz)


def _slopes(times, vals, loop):
    n = len(times)
    out = []
    for i in range(n):
        if loop:
            a, b = (i - 1) % n, (i + 1) % n
            ta = times[a] - (times[-1] if a > i else 0)
            tb = times[b] + (times[-1] if b < i else 0)
            dt = tb - ta
            out.append([(vb - va) / dt for va, vb in zip(vals[a], vals[b])])
        else:
            a, b = max(i - 1, 0), min(i + 1, n - 1)
            dt = (times[b] - times[a]) or 1.0
            out.append([(vb - va) / dt for va, vb in zip(vals[a], vals[b])])
    return out


def _f(v):
    return f"{v:.6g}"


def _vec(v, keys):
    return "{" + ", ".join(f"{k}: {_f(c)}" for k, c in zip(keys, v)) + "}"


def _vec_curve(times, vals, keys, loop, indent="    "):
    sl = _slopes(times, vals, loop)
    lines = []
    for t, v, s in zip(times, vals, sl):
        lines += [f"{indent}- serializedVersion: 3",
                  f"{indent}  time: {_f(t)}",
                  f"{indent}  value: {_vec(v, keys)}",
                  f"{indent}  inSlope: {_vec(s, keys)}",
                  f"{indent}  outSlope: {_vec(s, keys)}",
                  f"{indent}  tangentMode: 0",
                  f"{indent}  weightedMode: 0",
                  f"{indent}  inWeight: {_vec([1 / 3] * len(keys), keys)}",
                  f"{indent}  outWeight: {_vec([1 / 3] * len(keys), keys)}"]
    return lines


def _float_curve(times, vals, loop, indent):
    sl = _slopes(times, [[v] for v in vals], loop)
    lines = []
    for t, v, s in zip(times, vals, sl):
        lines += [f"{indent}- serializedVersion: 3", f"{indent}  time: {_f(t)}", f"{indent}  value: {_f(v)}",
                  f"{indent}  inSlope: {_f(s[0])}", f"{indent}  outSlope: {_f(s[0])}",
                  f"{indent}  tangentMode: 0", f"{indent}  weightedMode: 0",
                  f"{indent}  inWeight: 0.33333334", f"{indent}  outWeight: 0.33333334"]
    return lines


def clip(name, duration, pos=None, scale=None, euler=None, loop=True, samples=None):
    """pos/scale/euler are functions of time returning (x, y, z) tuples (or None to skip)."""
    n = samples or max(5, min(int(duration * 8) + 1, 25))
    times = [duration * i / (n - 1) for i in range(n)]
    out = [HEADER.format(name=name).rstrip("\n")]

    def section(title, fn, comp, keys, is_quat=False):
        if fn is None:
            out.append(f"  {title}: []")
            return
        vals = [fn(t) for t in times]
        if is_quat:
            vals = [euler_to_quat(*v) for v in vals]
        out.append(f"  {title}:")
        out.append("  - curve:")
        out.append("      serializedVersion: 2")
        out.append("      m_Curve:")
        out.extend(_vec_curve(times, vals, keys, loop, indent="      "))
        out.extend(["      m_PreInfinity: 2", "      m_PostInfinity: 2", "      m_RotationOrder: 4", "    path: "])

    section("m_RotationCurves", euler, 4, "xyzw", is_quat=True)
    out.append("  m_CompressedRotationCurves: []")
    out.append("  m_EulerCurves: []")
    section("m_PositionCurves", pos, 3, "xyz")
    section("m_ScaleCurves", scale, 3, "xyz")
    out.append("  m_FloatCurves: []")
    out.append("  m_PPtrCurves: []")
    out += ["  m_SampleRate: 60", "  m_WrapMode: 0", "  m_Bounds:", "    m_Center: {x: 0, y: 0, z: 0}",
            "    m_Extent: {x: 0, y: 0, z: 0}", "  m_ClipBindingConstant:", "    genericBindings: []",
            "    pptrCurveMapping: []", "  m_AnimationClipSettings:", "    serializedVersion: 2",
            "    m_AdditiveReferencePoseClip: {fileID: 0}", "    m_AdditiveReferencePoseTime: 0",
            "    m_StartTime: 0", f"    m_StopTime: {_f(duration)}", "    m_OrientationOffsetY: 0", "    m_Level: 0",
            "    m_CycleOffset: 0", "    m_HasAdditiveReferencePose: 0", f"    m_LoopTime: {1 if loop else 0}",
            "    m_LoopBlend: 0", "    m_LoopBlendOrientation: 0", "    m_LoopBlendPositionY: 0",
            "    m_LoopBlendPositionXZ: 0", "    m_KeepOriginalOrientation: 0", "    m_KeepOriginalPositionY: 1",
            "    m_KeepOriginalPositionXZ: 0", "    m_HeightFromFeet: 0", "    m_Mirror: 0"]
    # editor curves, so the clip shows its curves when opened in the Animation window
    ed = []
    for fn, prefix, comps in ((pos, "m_LocalPosition", "xyz"), (scale, "m_LocalScale", "xyz")):
        if fn is None:
            continue
        vals = [fn(t) for t in times]
        for ci, c in enumerate(comps):
            ed += ["  - serializedVersion: 2", "    curve:", "      serializedVersion: 2", "      m_Curve:"]
            ed += _float_curve(times, [v[ci] for v in vals], loop, "      ")
            ed += ["      m_PreInfinity: 2", "      m_PostInfinity: 2", "      m_RotationOrder: 4",
                   f"    attribute: {prefix}.{c}", "    path: ", "    classID: 4", "    script: {fileID: 0}",
                   "    flags: 0"]
    out.append("  m_EditorCurves:" if ed else "  m_EditorCurves: []")
    out += ed
    eed = []
    if euler is not None:
        vals = [euler(t) for t in times]
        for ci, c in enumerate("xyz"):
            eed += ["  - serializedVersion: 2", "    curve:", "      serializedVersion: 2", "      m_Curve:"]
            eed += _float_curve(times, [v[ci] for v in vals], loop, "      ")
            eed += ["      m_PreInfinity: 2", "      m_PostInfinity: 2", "      m_RotationOrder: 4",
                    f"    attribute: m_LocalEulerAnglesRaw.{c}", "    path: ", "    classID: 4",
                    "    script: {fileID: 0}", "    flags: 0"]
    out.append("  m_EulerEditorCurves:" if eed else "  m_EulerEditorCurves: []")
    out += eed
    out += ["  m_HasGenericRootTransform: 0", "  m_HasMotionFloatCurves: 0", "  m_Events: []"]
    return "\n".join(out) + "\n"


TAU = 2 * math.pi

CLIPS = {
    # name: (duration, loop, pos, scale, euler)
    "ring_bob": (4.0, True, lambda t: (0, 0.18 * math.sin(TAU * t / 4.0), 0), None, None),
    "pedestal_lower": (1.6, False,
                       lambda t: (0, -2.2 * (3 * (t / 1.6) ** 2 - 2 * (t / 1.6) ** 3), 0), None, None),
    "orb_pulse": (2.4, True, None, lambda t: (lambda s: (s, s, s))(1 + 0.05 * math.sin(TAU * t / 2.4)), None),
    "orb_spin": (12.0, True, None, None, lambda t: (0, 360 * t / 12.0, 0)),
    "launcher_pulse": (1.0, True, None,
                       lambda t: (lambda s: (s, 1, s))(1 + 0.08 * (0.5 - 0.5 * math.cos(TAU * t))), None),
    "pumpkin_idle": (2.0, True, lambda t: (0, 0.05 * math.sin(TAU * t / 2.0), 0), None,
                     lambda t: (0, 6 * math.sin(TAU * t / 2.0), 0)),
    "pumpkin_telegraph": (0.6, False, None,
                          lambda t: (lambda s: (s, s, s))(1 + 0.22 * math.sin(math.pi * min(t / 0.6, 1)) ** 2),
                          lambda t: (0, 0, 7 * math.sin(TAU * 8 * t) * (t / 0.6))),
    "hand_sway": (3.0, True, lambda t: (0.004 * math.sin(TAU * t / 3.0), 0.006 * math.sin(TAU * t / 1.5), 0), None,
                  lambda t: (1.5 * math.sin(TAU * t / 3.0), 0, 2.0 * math.sin(TAU * t / 3.0 + 1))),
}
