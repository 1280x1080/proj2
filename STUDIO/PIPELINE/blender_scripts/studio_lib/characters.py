"""Rigged character generator.

make_character(name, style) builds an armature + simple primitive body parts parented to bones,
plus face parts (eyes, pupils, lids, brows, mouth) that are animated directly:

    ch = make_character("Mia", dict(skin="#e9b896", shirt="#d4704f", ...), location=(0, 2, 0))
    ch.pose(frame, arm_r=(70, 40), head=(0, 0, 10))     # degrees
    ch.walk(f0, f1, start=(0, 1, 0), end=(0, 3, 0))
    ch.blink(frame);  ch.mouth(frame, 0.7);  ch.expression(frame, "surprised")
    extras = crowd(n, seed)                             # varied extras built from the same generator

Bone convention: arms hang down at rest; pose angles rotate around the bone's local X (forward
swing) / Z (outward raise).
"""
import math
import random

import bpy
from mathutils import Euler

from .scene import assign, mat, smooth

DEFAULT = dict(skin="#e9b896", hair="#2f2019", shirt="#3f6fb5", pants="#34495e", shoes="#2a2420",
               eyes="#3b2a1e", height=1.0, width=1.0, head=1.0, hair_style="short")

# bone: (head xyz, tail xyz, parent)
BONES = {
    "root": ((0, 0, 0), (0, 0, 0.2), None),
    "hips": ((0, 0, 0.92), (0, 0, 1.05), "root"),
    "spine": ((0, 0, 1.05), (0, 0, 1.38), "hips"),
    "neck": ((0, 0, 1.38), (0, 0, 1.48), "spine"),
    "head": ((0, 0, 1.48), (0, 0, 1.75), "neck"),
    "upper_arm.L": ((0.2, 0, 1.36), (0.24, 0, 1.08), "spine"),
    "forearm.L": ((0.24, 0, 1.08), (0.26, 0, 0.84), "upper_arm.L"),
    "upper_arm.R": ((-0.2, 0, 1.36), (-0.24, 0, 1.08), "spine"),
    "forearm.R": ((-0.24, 0, 1.08), (-0.26, 0, 0.84), "upper_arm.R"),
    "thigh.L": ((0.1, 0, 0.92), (0.1, 0, 0.5), "hips"),
    "shin.L": ((0.1, 0, 0.5), (0.1, 0, 0.07), "thigh.L"),
    "thigh.R": ((-0.1, 0, 0.92), (-0.1, 0, 0.5), "hips"),
    "shin.R": ((-0.1, 0, 0.5), (-0.1, 0, 0.07), "thigh.R"),
}


class Character:
    def __init__(self, name, arm, parts, face, style):
        self.name, self.arm, self.parts, self.face, self.style = name, arm, parts, face, style

    # ------------------------------------------------------------------ posing
    def pb(self, bone):
        return self.arm.pose.bones[bone]

    def rot(self, frame, bone, xyz_deg):
        b = self.pb(bone)
        b.rotation_mode = "XYZ"
        b.rotation_euler = Euler([math.radians(v) for v in xyz_deg], "XYZ")
        b.keyframe_insert("rotation_euler", frame=frame)

    def pose(self, frame, arm_l=(0, 0), arm_r=(0, 0), elbow_l=0, elbow_r=0, head=(0, 0, 0), spine=(0, 0, 0),
             legs=None):
        """arm = (forward swing, outward raise) in degrees."""
        self.rot(frame, "upper_arm.L", (arm_l[0], 0, -arm_l[1]))
        self.rot(frame, "upper_arm.R", (arm_r[0], 0, arm_r[1]))
        self.rot(frame, "forearm.L", (elbow_l, 0, 0))
        self.rot(frame, "forearm.R", (elbow_r, 0, 0))
        self.rot(frame, "head", head)
        self.rot(frame, "spine", spine)
        if legs:
            for b, v in legs.items():
                self.rot(frame, b, v)

    def place(self, frame, loc, yaw_deg=0.0):
        self.arm.location = loc
        self.arm.rotation_euler = (0, 0, math.radians(yaw_deg))
        self.arm.keyframe_insert("location", frame=frame)
        self.arm.keyframe_insert("rotation_euler", frame=frame)

    def walk(self, f0, f1, start, end, stride_frames=16, amp=28):
        """Simple walk cycle between two floor points (keys legs, arms, bob, root)."""
        dx, dy = end[0] - start[0], end[1] - start[1]
        yaw = math.degrees(math.atan2(-dx, dy))
        for f in range(f0, f1 + 1, 2):
            u = (f - f0) / max(1, f1 - f0)
            ph = (f - f0) / stride_frames * 2 * math.pi
            s = math.sin(ph)
            loc = (start[0] + dx * u, start[1] + dy * u, abs(math.cos(ph)) * 0.025)
            self.place(f, loc, yaw)
            self.rot(f, "thigh.L", (-amp * s, 0, 0))
            self.rot(f, "thigh.R", (amp * s, 0, 0))
            self.rot(f, "shin.L", (max(0, amp * 1.3 * math.sin(ph + 1.4)), 0, 0))
            self.rot(f, "shin.R", (max(0, amp * 1.3 * math.sin(ph + 1.4 + math.pi)), 0, 0))
            self.rot(f, "upper_arm.L", (amp * 0.7 * s, 0, -4))
            self.rot(f, "upper_arm.R", (-amp * 0.7 * s, 0, 4))

    # ------------------------------------------------------------------ face
    def blink(self, frame, dur=4):
        for lid in self.face["lids"]:
            for f, sz in ((frame - 1, 0.001), (frame + dur // 2, 1.0), (frame + dur, 0.001)):
                lid.scale = (1, 1, sz)
                lid.keyframe_insert("scale", frame=f)

    def mouth(self, frame, amount):
        m = self.face["mouth"]
        m.scale = (1.0 - 0.2 * amount, 1, 0.25 + 1.6 * amount)
        m.keyframe_insert("scale", frame=frame)

    def lipsync(self, words, offset_frames=0, fps=30):
        """words = [{'start','end',...}] (seconds) from timing.json."""
        from .lipsync import mouth_curve
        for f, a in mouth_curve(words, fps):
            self.mouth(f + offset_frames, a)

    def expression(self, frame, kind="neutral"):
        brow = {"neutral": (0.0, 0), "surprised": (0.014, 0), "angry": (-0.012, 18), "worried": (0.015, -15),
                "happy": (0.01, 0)}[kind]
        for side, b in zip((1, -1), self.face["brows"]):
            b.location.z = self.face["brow_z"] + brow[0]
            b.rotation_euler = (0, math.radians(brow[1] * side), 0)
            b.keyframe_insert("location", frame=frame)
            b.keyframe_insert("rotation_euler", frame=frame)
        pup = 1.25 if kind == "surprised" else 1.0
        for p in self.face["pupils"]:
            p.scale = (pup, pup, pup)
            p.keyframe_insert("scale", frame=frame)

    def look(self, frame, x=0.0, z=0.0):
        for p, base in zip(self.face["pupils"], self.face["pupil_base"]):
            p.location = (base[0] + x * 0.012, base[1], base[2] + z * 0.01)
            p.keyframe_insert("location", frame=frame)


def _part(name, prim, arm, bone, loc, scale, material, rot=(0, 0, 0)):
    if prim == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=loc, rotation=rot)
    elif prim == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1, depth=1, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    smooth(assign(o, material))
    if bone:
        o.parent = arm
        o.parent_type = "BONE"
        o.parent_bone = bone
        # keep world transform: compensate for bone tail offset
        bm = arm.matrix_world @ arm.data.bones[bone].matrix_local
        from mathutils import Matrix
        o.matrix_parent_inverse = (bm @ Matrix.Translation((0, arm.data.bones[bone].length, 0))).inverted()
    return o


def make_character(name, style=None, location=(0, 0, 0)):
    st = dict(DEFAULT)
    st.update(style or {})
    hgt, wid, hs = st["height"], st["width"], st["head"]
    M = {k: mat(f"{name}_{k}", st[k], 0.55 if k != "skin" else 0.45) for k in ("skin", "hair", "shirt", "pants", "shoes")}
    M["white"] = mat("eye_white", "#fbfaf7", 0.3)
    M["pupil"] = mat("pupil", "#120c0a", 0.2)
    M["mouth"] = mat("mouth", "#5a2320", 0.6)

    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm = bpy.context.active_object
    arm.name = f"{name}_rig"
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    eb.remove(eb[0])
    for bn, (h, t, par) in BONES.items():
        b = eb.new(bn)
        b.head = (h[0] * wid, h[1], h[2] * hgt)
        b.tail = (t[0] * wid, t[1], t[2] * hgt)
        if par:
            b.parent = eb[par]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")

    P = {}
    z = lambda v: v * hgt  # noqa: E731
    P["torso"] = _part(f"{name}_torso", "sphere", arm, "spine", (0, 0, z(1.2)), (0.2 * wid, 0.13, 0.26 * hgt), M["shirt"])
    P["pelvis"] = _part(f"{name}_pelvis", "sphere", arm, "hips", (0, 0, z(0.95)), (0.19 * wid, 0.12, 0.12), M["pants"])
    for s, side in (("L", 1), ("R", -1)):
        x = side * 0.1 * wid
        P[f"thigh{s}"] = _part(f"{name}_thigh.{s}", "cyl", arm, f"thigh.{s}", (x, 0, z(0.71)), (0.075, 0.075, 0.44 * hgt), M["pants"])
        P[f"shin{s}"] = _part(f"{name}_shin.{s}", "cyl", arm, f"shin.{s}", (x, 0, z(0.29)), (0.062, 0.062, 0.44 * hgt), M["pants"])
        P[f"shoe{s}"] = _part(f"{name}_shoe.{s}", "sphere", arm, f"shin.{s}", (x, -0.04, 0.05), (0.07, 0.13, 0.05), M["shoes"])
        ax = side * 0.22 * wid
        P[f"uarm{s}"] = _part(f"{name}_uarm.{s}", "cyl", arm, f"upper_arm.{s}", (ax, 0, z(1.22)), (0.05, 0.05, 0.3 * hgt), M["shirt"])
        P[f"farm{s}"] = _part(f"{name}_farm.{s}", "cyl", arm, f"forearm.{s}", (ax * 1.08, 0, z(0.96)), (0.042, 0.042, 0.26 * hgt), M["skin"])
        P[f"hand{s}"] = _part(f"{name}_hand.{s}", "sphere", arm, f"forearm.{s}", (ax * 1.12, 0, z(0.81)), (0.05, 0.04, 0.06), M["skin"])
    P["neck"] = _part(f"{name}_neck", "cyl", arm, "neck", (0, 0, z(1.44)), (0.05, 0.05, 0.12), M["skin"])
    hz = z(1.6) + 0.02 * hs
    P["head"] = _part(f"{name}_head", "sphere", arm, "head", (0, 0, hz), (0.15 * hs, 0.14 * hs, 0.17 * hs), M["skin"])
    hair_scale = (0.158 * hs, 0.15 * hs, 0.14 * hs)
    P["hair"] = _part(f"{name}_hair", "sphere", arm, "head", (0, 0.025, hz + 0.08 * hs), hair_scale, M["hair"])
    if st["hair_style"] == "bob":
        P["hair_back"] = _part(f"{name}_hairback", "sphere", arm, "head", (0, 0.04, hz - 0.02), (0.165 * hs, 0.14 * hs, 0.15 * hs), M["hair"])

    face = dict(lids=[], pupils=[], pupil_base=[], brows=[])
    fy = -0.135 * hs  # face plane (camera looks along +Y, so the face points to -Y)
    for side in (1, -1):
        ex = side * 0.055 * hs
        ez = hz + 0.01 * hs
        _part(f"{name}_eye{side}", "sphere", arm, "head", (ex, fy + 0.012, ez), (0.03 * hs, 0.012, 0.036 * hs), M["white"])
        p = _part(f"{name}_pupil{side}", "sphere", arm, "head", (ex, fy - 0.0, ez), (0.014 * hs, 0.006, 0.016 * hs), M["pupil"])
        face["pupils"].append(p)
        face["pupil_base"].append(tuple(p.location))
        lid = _part(f"{name}_lid{side}", "sphere", arm, "head", (ex, fy - 0.004, ez + 0.012), (0.034 * hs, 0.014, 0.04 * hs), M["skin"])
        lid.scale = (1, 1, 0.001)
        face["lids"].append(lid)
        br = _part(f"{name}_brow{side}", "cube", arm, "head", (ex, fy - 0.03, ez + 0.036 * hs), (0.045 * hs, 0.01, 0.011), M["hair"])
        face["brows"].append(br)
        face["brow_z"] = br.location.z
    m = _part(f"{name}_mouth", "sphere", arm, "head", (0, fy + 0.004, hz - 0.075 * hs), (0.035 * hs, 0.01, 0.012 * hs), M["mouth"])
    face["mouth"] = m

    arm.location = location
    ch = Character(name, arm, P, face, st)
    return ch


def crowd(n, seed=0, area=((-2, 2), (3, 5))):
    """Extras built from the same generator with random colours / proportions."""
    r = random.Random(seed)
    skins = ["#f1c7a4", "#e9b896", "#c68a62", "#9a6440", "#6e4630"]
    shirts = ["#d4704f", "#4f7a5a", "#7b5ea7", "#3f6fb5", "#e3b23c", "#8e3f3a", "#5a6f7d"]
    out = []
    for i in range(n):
        st = dict(skin=r.choice(skins), shirt=r.choice(shirts), hair=r.choice(["#1d1612", "#5a3a22", "#c9c4bd", "#8a5a2b"]),
                  pants=r.choice(["#2e3440", "#34495e", "#5a4a3b"]), height=r.uniform(0.9, 1.1), width=r.uniform(0.9, 1.15),
                  hair_style=r.choice(["short", "bob"]))
        loc = (r.uniform(*area[0]), r.uniform(*area[1]), 0)
        out.append(make_character(f"Extra{i}", st, loc))
    return out
