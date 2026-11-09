"""Optional toon-shader pass: converts every Principled material into flat 2-tone cel shading
(Shader to RGB -> constant colour ramp).  EEVEE only."""
import bpy


def apply_toon(threshold=0.35, shadow_mult=0.62, materials=None):
    for m in materials or bpy.data.materials:
        if not m.use_nodes:
            continue
        nt = m.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        out = nt.nodes.get("Material Output")
        if not bsdf or not out or nt.nodes.get("ToonRamp"):
            continue
        base = tuple(bsdf.inputs["Base Color"].default_value)
        diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
        diff.inputs["Color"].default_value = (1, 1, 1, 1)
        s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.name = "ToonRamp"
        ramp.color_ramp.interpolation = "CONSTANT"
        ramp.color_ramp.elements[0].color = (base[0] * shadow_mult, base[1] * shadow_mult, base[2] * shadow_mult * 1.08, 1)
        ramp.color_ramp.elements[1].position = threshold
        ramp.color_ramp.elements[1].color = base
        emit = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(diff.outputs[0], s2r.inputs[0])
        nt.links.new(s2r.outputs[0], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], emit.inputs[0])
        # keep real emission (lamps, screens) by adding it on top
        es = bsdf.inputs["Emission Strength"].default_value
        if es > 0:
            add = nt.nodes.new("ShaderNodeAddShader")
            e2 = nt.nodes.new("ShaderNodeEmission")
            e2.inputs[0].default_value = bsdf.inputs["Emission Color"].default_value
            e2.inputs[1].default_value = es
            nt.links.new(emit.outputs[0], add.inputs[0])
            nt.links.new(e2.outputs[0], add.inputs[1])
            nt.links.new(add.outputs[0], out.inputs["Surface"])
        else:
            nt.links.new(emit.outputs[0], out.inputs["Surface"])
