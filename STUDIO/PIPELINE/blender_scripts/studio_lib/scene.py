"""Scene reset, materials and fast CPU render settings."""
import bpy

FPS = 30


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start = 1
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.resolution_percentage = 50  # 540x960 half-res renders, upscaled by the compositor
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.05, 0.055, 0.07, 1)
    bg.inputs[1].default_value = 0.6
    sc.view_settings.view_transform = "Standard"  # natural colour, no filmic wash / punchy grade
    sc.view_settings.look = "None"
    return sc


def fast_eevee(sc=None, samples=1, denoise=True):
    """CPU EEVEE: 1 sample + OpenImageDenoise in the compositor, ray tracing off."""
    sc = sc or bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    ee = sc.eevee
    ee.taa_render_samples = samples
    for attr, val in (("use_raytracing", False), ("use_gtao", True), ("use_shadows", True),
                      ("shadow_ray_count", 1), ("shadow_step_count", 2), ("use_bloom", False)):
        if hasattr(ee, attr):
            setattr(ee, attr, val)
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    if denoise:
        sc.use_nodes = True
        nt = sc.node_tree
        nt.nodes.clear()
        rl = nt.nodes.new("CompositorNodeRLayers")
        dn = nt.nodes.new("CompositorNodeDenoise")
        out = nt.nodes.new("CompositorNodeComposite")
        nt.links.new(rl.outputs["Image"], dn.inputs["Image"])
        nt.links.new(dn.outputs["Image"], out.inputs["Image"])
    return sc


def mat(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*hex_rgb(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*hex_rgb(emit), 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def hex_rgb(h):
    """sRGB hex -> linear RGB tuple (Blender colour sockets are linear)."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def assign(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


def key(obj, path, frame, value=None, index=-1):
    if value is not None:
        if index >= 0:
            getattr(obj, path)[index] = value
        else:
            setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame, index=index)


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj
