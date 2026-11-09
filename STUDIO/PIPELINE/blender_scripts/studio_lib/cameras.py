"""Camera rigs with keyframed moves.  A rig = empty (target) + camera with a Track To constraint."""
import bpy


def camera(name, loc, target, lens=35.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cam = bpy.data.objects.new(name, cd)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    tgt = bpy.data.objects.new(f"{name}_target", None)
    bpy.context.collection.objects.link(tgt)
    tgt.location = target
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return cam, tgt


def move(cam, tgt, keys, ease="BEZIER"):
    """keys = [(frame, cam_loc, target_loc, lens), ...]"""
    for f, cl, tl, lens in keys:
        cam.location = cl
        cam.keyframe_insert("location", frame=f)
        tgt.location = tl
        tgt.keyframe_insert("location", frame=f)
        if lens:
            cam.data.lens = lens
            cam.data.keyframe_insert("lens", frame=f)
    for o in (cam, tgt, cam.data):
        if o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = ease
