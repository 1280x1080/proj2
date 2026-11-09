"""Lights.  Only lights named Key* cast shadows (fast + clean)."""
import math

import bpy

from .scene import hex_rgb


def light(name, kind, loc, energy, color="#ffffff", rot=(0, 0, 0), size=0.5, spot_deg=60):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = hex_rgb(color)
    if hasattr(d, "shadow_soft_size"):
        d.shadow_soft_size = size
    if kind == "SPOT":
        d.spot_size = math.radians(spot_deg)
        d.spot_blend = 0.4
    d.use_shadow = name.startswith("Key")
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    return o


def three_point(target=(0, 2, 1.4), warm="#ffd9a8", cool="#a9c4ff", key_energy=600):
    """Key (shadows), fill (soft, no shadow), rim (back light, no shadow)."""
    tx, ty, tz = target
    k = light("Key", "AREA", (tx - 1.8, ty - 2.0, tz + 1.6), key_energy, warm, rot=(55, 0, -40), size=1.2)
    f = light("Fill", "AREA", (tx + 2.2, ty - 1.5, tz + 0.5), key_energy * 0.35, cool, rot=(75, 0, 50), size=2.0)
    r = light("Rim", "SPOT", (tx + 0.8, ty + 1.6, tz + 1.4), key_energy * 0.9, "#fff0d8", rot=(-50, 0, 160), size=0.3)
    return k, f, r


def practical(name, loc, energy=60, color="#ffc87a", radius=0.1):
    """Visible lamp / bulb (point, no shadow unless named Key*)."""
    return light(name, "POINT", loc, energy, color, size=radius)


def key_energy(obj, frame, value):
    obj.data.energy = value
    obj.data.keyframe_insert("energy", frame=frame)
