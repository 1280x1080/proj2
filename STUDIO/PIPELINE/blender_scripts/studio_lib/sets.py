"""Reusable sets.  Units: metres, Z up, camera usually looks along +Y."""
import bpy

from .scene import assign, mat, smooth


def box(name, size, loc, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 3
    return assign(o, material)


def cyl(name, r, depth, loc, material, verts=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return smooth(assign(o, material))


def sphere(name, r, loc, material, scale=(1, 1, 1), segs=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs // 2, radius=r, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    return smooth(assign(o, material))


def living_room(w=5.0, d=5.0, h=2.7, wall="#cdb89a", floor="#8d6a4b"):
    """Open-front box room (back wall at +Y), with a window, door, sofa, rug and a floor lamp."""
    M = dict(wall=mat("wall", wall, 0.9), floor=mat("floor", floor, 0.55), trim=mat("trim", "#e9dfcf", 0.5),
             sofa=mat("sofa", "#5a6f7d", 0.8), wood=mat("wood", "#6b4a32", 0.5), rug=mat("rug", "#8e3f3a", 0.95),
             glass=mat("night", "#1d3263", 0.2, emit="#2c4677", emit_strength=0.6),
             shade=mat("lampshade", "#ffe2a6", 0.7, emit="#ffc87a", emit_strength=2.0))
    objs = {}
    objs["floor"] = box("Floor", (w, d, 0.1), (0, d / 2, -0.05), M["floor"])
    objs["back"] = box("WallBack", (w, 0.1, h), (0, d, h / 2), M["wall"])
    objs["left"] = box("WallLeft", (0.1, d, h), (-w / 2, d / 2, h / 2), M["wall"])
    objs["right"] = box("WallRight", (0.1, d, h), (w / 2, d / 2, h / 2), M["wall"])
    objs["window"] = box("Window", (1.2, 0.04, 1.0), (-1.2, d - 0.06, 1.55), M["glass"])
    objs["door"] = box("Door", (0.9, 0.06, 2.05), (1.5, d - 0.06, 1.025), M["wood"], bevel=0.01)
    objs["sofa_base"] = box("SofaBase", (2.0, 0.85, 0.45), (0, d - 0.6, 0.225), M["sofa"], bevel=0.06)
    objs["sofa_back"] = box("SofaBack", (2.0, 0.25, 0.5), (0, d - 0.15, 0.7), M["sofa"], bevel=0.06)
    objs["rug"] = cyl("Rug", 1.3, 0.01, (0, d / 2, 0.005), M["rug"], 48)
    objs["rug"].scale = (1.4, 1.0, 1.0)
    objs["lamp_pole"] = cyl("LampPole", 0.02, 1.5, (-1.8, d - 0.7, 0.75), M["wood"], 12)
    objs["lamp_shade"] = cyl("LampShade", 0.22, 0.32, (-1.8, d - 0.7, 1.6), M["shade"], 24)
    return objs
