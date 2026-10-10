"""Rig the sheet-lofted body and bake the design drawings onto it."""

import json
import math
import os

import bpy
from mathutils import Vector

ROOT = "/workspace/人物设定图"
OUT = os.path.join(ROOT, "模型")
ART = "/opt/cursor/artifacts"
FRONT = os.path.join(ROOT, "T字正面.jpg")
BACK = os.path.join(ROOT, "T字背面.jpg")
SIDE = os.path.join(ROOT, "侧面.jpg")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def import_body():
    bpy.ops.wm.obj_import(
        filepath=os.path.join(OUT, "body.obj"),
        forward_axis="NEGATIVE_Y",
        up_axis="Z",
    )
    body = bpy.context.selected_objects[0]
    body.name = "Body"
    print("imported dim", tuple(round(v, 3) for v in body.dimensions))
    print("imported loc", tuple(body.location))
    return body


def weld(body):
    activate(body)
    remesh = body.modifiers.new("Remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = 0.01
    smooth = body.modifiers.new("Smooth", "SMOOTH")
    smooth.factor = 0.25
    smooth.iterations = 3
    bpy.ops.object.modifier_apply(modifier="Remesh")
    bpy.ops.object.modifier_apply(modifier="Smooth")
    for poly in body.data.polygons:
        poly.use_smooth = True
    print("welded", len(body.data.vertices), len(body.data.polygons))
    return body


def bake_sheets(body, marks):
    activate(body)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")

    mat = bpy.data.materials.new("Sheet")
    mat.use_nodes = True
    body.data.materials.clear()
    body.data.materials.append(mat)
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    geom = nodes.new("ShaderNodeNewGeometry")
    sep_pos = nodes.new("ShaderNodeSeparateXYZ")
    sep_n = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geom.outputs["Position"], sep_pos.inputs["Vector"])
    links.new(geom.outputs["Normal"], sep_n.inputs["Vector"])

    scale = marks["scale"]
    cx = marks["center_x_px"]
    bot = marks["bot"]
    fw = marks["fw"]
    fh = marks["fh"]

    def image_tex(path, name, x):
        img = bpy.data.images.load(path)
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.name = name
        tex.location = (x, 0)
        tex.interpolation = "Linear"
        tex.extension = "EXTEND"
        return tex

    front_tex = image_tex(FRONT, "Front", -200)
    back_tex = image_tex(BACK, "Back", -200)
    side_tex = image_tex(SIDE, "Side", -200)

    def map_front(tex):
        # u = (x / scale + cx) / fw
        # image y = bot - z / scale ; blender v is from the bottom
        # v = 1 - y / fh
        comb = nodes.new("ShaderNodeCombineXYZ")
        math_x = nodes.new("ShaderNodeMath")
        math_x.operation = "ADD"
        div_x = nodes.new("ShaderNodeMath")
        div_x.operation = "DIVIDE"
        div_x.inputs[1].default_value = scale
        links.new(sep_pos.outputs["X"], div_x.inputs[0])
        links.new(div_x.outputs["Value"], math_x.inputs[0])
        math_x.inputs[1].default_value = cx
        div_u = nodes.new("ShaderNodeMath")
        div_u.operation = "DIVIDE"
        div_u.inputs[1].default_value = fw
        links.new(math_x.outputs["Value"], div_u.inputs[0])

        div_z = nodes.new("ShaderNodeMath")
        div_z.operation = "DIVIDE"
        div_z.inputs[1].default_value = scale
        links.new(sep_pos.outputs["Z"], div_z.inputs[0])
        y_img = nodes.new("ShaderNodeMath")
        y_img.operation = "SUBTRACT"
        y_img.inputs[0].default_value = bot
        links.new(div_z.outputs["Value"], y_img.inputs[1])
        y_div = nodes.new("ShaderNodeMath")
        y_div.operation = "DIVIDE"
        y_div.inputs[1].default_value = fh
        links.new(y_img.outputs["Value"], y_div.inputs[0])
        v = nodes.new("ShaderNodeMath")
        v.operation = "SUBTRACT"
        v.inputs[0].default_value = 1.0
        links.new(y_div.outputs["Value"], v.inputs[1])
        links.new(div_u.outputs["Value"], comb.inputs["X"])
        links.new(v.outputs["Value"], comb.inputs["Y"])
        links.new(comb.outputs["Vector"], tex.inputs["Vector"])

    map_front(front_tex)
    map_front(back_tex)

    # Side image. Larger image X is the front, mesh front is -Y.
    # pixel_x = anchor - mesh_y / side_scale
    s_anchor = marks["side_anchor"]
    s_scale = marks["side_scale"]
    s_top = marks["side_top"]
    s_span = marks["side_span"]
    s_w = marks["side_w"]
    s_h = marks["side_h"]
    comb_s = nodes.new("ShaderNodeCombineXYZ")
    y_div = nodes.new("ShaderNodeMath")
    y_div.operation = "DIVIDE"
    y_div.inputs[1].default_value = s_scale
    links.new(sep_pos.outputs["Y"], y_div.inputs[0])
    px = nodes.new("ShaderNodeMath")
    px.operation = "SUBTRACT"
    px.inputs[0].default_value = s_anchor
    links.new(y_div.outputs["Value"], px.inputs[1])
    pu = nodes.new("ShaderNodeMath")
    pu.operation = "DIVIDE"
    pu.inputs[1].default_value = s_w
    links.new(px.outputs["Value"], pu.inputs[0])
    # z to side image y
    zn = nodes.new("ShaderNodeMath")
    zn.operation = "DIVIDE"
    zn.inputs[1].default_value = marks["height"]
    links.new(sep_pos.outputs["Z"], zn.inputs[0])
    inv = nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    links.new(zn.outputs["Value"], inv.inputs[1])
    sy = nodes.new("ShaderNodeMath")
    sy.operation = "MULTIPLY_ADD" if False else "MULTIPLY"
    # side y = top + (1 - z/H) * span
    mul = nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = s_span
    links.new(inv.outputs["Value"], mul.inputs[0])
    add = nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.inputs[1].default_value = s_top
    links.new(mul.outputs["Value"], add.inputs[0])
    pv = nodes.new("ShaderNodeMath")
    pv.operation = "DIVIDE"
    pv.inputs[1].default_value = s_h
    links.new(add.outputs["Value"], pv.inputs[0])
    vside = nodes.new("ShaderNodeMath")
    vside.operation = "SUBTRACT"
    vside.inputs[0].default_value = 1.0
    links.new(pv.outputs["Value"], vside.inputs[1])
    links.new(pu.outputs["Value"], comb_s.inputs["X"])
    links.new(vside.outputs["Value"], comb_s.inputs["Y"])
    links.new(comb_s.outputs["Vector"], side_tex.inputs["Vector"])

    # Arms keep the front drawing. Torso front/back/side follow the normal.
    abs_x = nodes.new("ShaderNodeMath")
    abs_x.operation = "ABSOLUTE"
    links.new(sep_pos.outputs["X"], abs_x.inputs[0])
    is_arm = nodes.new("ShaderNodeMath")
    is_arm.operation = "GREATER_THAN"
    is_arm.inputs[1].default_value = 0.30
    links.new(abs_x.outputs["Value"], is_arm.inputs[0])

    frontish = nodes.new("ShaderNodeMath")
    frontish.operation = "LESS_THAN"
    frontish.inputs[1].default_value = -0.2
    links.new(sep_n.outputs["Y"], frontish.inputs[0])
    backish = nodes.new("ShaderNodeMath")
    backish.operation = "GREATER_THAN"
    backish.inputs[1].default_value = 0.2
    links.new(sep_n.outputs["Y"], backish.inputs[0])

    mix_fb = nodes.new("ShaderNodeMix")
    mix_fb.data_type = "RGBA"
    links.new(backish.outputs["Value"], mix_fb.inputs["Factor"])
    links.new(front_tex.outputs["Color"], mix_fb.inputs[6])
    links.new(back_tex.outputs["Color"], mix_fb.inputs[7])

    mix_side = nodes.new("ShaderNodeMix")
    mix_side.data_type = "RGBA"
    # Use side only when neither front nor back.
    side_fac = nodes.new("ShaderNodeMath")
    side_fac.operation = "ADD"
    links.new(frontish.outputs["Value"], side_fac.inputs[0])
    links.new(backish.outputs["Value"], side_fac.inputs[1])
    one_minus = nodes.new("ShaderNodeMath")
    one_minus.operation = "SUBTRACT"
    one_minus.inputs[0].default_value = 1.0
    links.new(side_fac.outputs["Value"], one_minus.inputs[1])
    links.new(one_minus.outputs["Value"], mix_side.inputs["Factor"])
    links.new(mix_fb.outputs["Result"], mix_side.inputs[6])
    links.new(side_tex.outputs["Color"], mix_side.inputs[7])

    mix_arm = nodes.new("ShaderNodeMix")
    mix_arm.data_type = "RGBA"
    links.new(is_arm.outputs["Value"], mix_arm.inputs["Factor"])
    links.new(mix_side.outputs["Result"], mix_arm.inputs[6])
    links.new(front_tex.outputs["Color"], mix_arm.inputs[7])
    links.new(mix_arm.outputs["Result"], emit.inputs["Color"])
    links.new(emit.outputs["Emission"], out.inputs["Surface"])

    bake_img = bpy.data.images.new("Bake", 2048, 2048, alpha=False)
    bake_node = nodes.new("ShaderNodeTexImage")
    bake_node.image = bake_img
    nodes.active = bake_node

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.render.bake.margin = 16
    try:
        scene.render.bake.margin_type = "EXTEND"
    except TypeError:
        pass
    bpy.ops.object.bake(type="EMIT")
    fill_image_holes(bake_img)
    bake_path = os.path.join(OUT, "body_bake.png")
    bake_img.filepath_raw = bake_path
    bake_img.file_format = "PNG"
    bake_img.save()
    print("baked", bake_path)

    # Replace the shader with the baked texture so the glb is self-contained.
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bake_img
    uv = nodes.new("ShaderNodeUVMap")
    links.new(uv.outputs["UV"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.62
    spec = bsdf.inputs.get("Specular IOR Level")
    if spec:
        spec.default_value = 0.18
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return body


def build_armature(body, marks):
    vs = [v.co.copy() for v in body.data.vertices]

    def picked(fn):
        sel = [v for v in vs if fn(v)]
        if not sel:
            return Vector((0, 0, 0))
        c = Vector((0, 0, 0))
        for v in sel:
            c += v
        return c / len(sel)

    arm_data = bpy.data.armatures.new("Skeleton")
    arm = bpy.data.objects.new("Skeleton", arm_data)
    bpy.context.collection.objects.link(arm)
    activate(arm)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(name, head, tail, parent=None, connect=False):
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent:
            b.parent = parent
            b.use_connect = connect
        return b

    split_z = marks["split_z"]
    chest_z = marks["chest_z"]
    shoulder_z = marks["shoulder_z"]
    hips = bone("Hips", (0, 0, split_z + 0.02), (0, 0, split_z + 0.16))
    spine = bone("Spine", hips.tail, (0, 0, (chest_z + split_z) * 0.5), hips, True)
    chest = bone("Chest", spine.tail, (0, -0.01, shoulder_z + 0.02), spine, True)
    neck = bone("Neck", chest.tail, (0, 0, shoulder_z + 0.12), chest, True)
    head_top = max(v.z for v in vs)
    bone("Head", neck.tail, (0, -0.01, head_top - 0.01), neck, True)

    def limb_x(sign):
        arm_vs = [v for v in vs if sign * v.x > 0.22 and v.z > shoulder_z - 0.18]
        if not arm_vs:
            return
        xs = [v.x for v in arm_vs]
        inner = min(xs) if sign > 0 else max(xs)
        outer = max(xs) if sign > 0 else min(xs)
        mid = 0.5 * (inner + outer)
        z = shoulder_z
        prefix = "Left" if sign > 0 else "Right"
        clav = bone(prefix + "Shoulder", (sign * 0.06, 0, shoulder_z), (inner, 0, z), chest)
        up = bone(prefix + "UpperArm", (inner, -0.01, z), (mid, -0.01, z - 0.01), clav)
        fore = bone(prefix + "LowerArm", up.tail, (outer * 0.92, -0.01, z - 0.02), up, True)
        bone(prefix + "Hand", fore.tail, (outer, -0.01, z - 0.025), fore, True)

    limb_x(1)
    limb_x(-1)

    def leg(sign, name):
        leg_vs = [v for v in vs if sign * v.x > 0.04 and v.z < split_z + 0.05]
        if not leg_vs:
            return
        zs = [v.z for v in leg_vs]
        top = max(zs)
        bot = min(zs)
        knee = bot + 0.48 * (top - bot)
        x = sign * 0.11
        up = bone(name + "UpLeg", (x, 0, top), (x, 0.01, knee), hips)
        low = bone(name + "Leg", up.tail, (x, 0, bot + 0.04), up, True)
        foot = bone(name + "Foot", low.tail, (x, -0.12, 0.03), low)
        bone(name + "Toe", foot.tail, (x, -0.18, 0.02), foot, True)

    leg(1, "Left")
    leg(-1, "Right")
    bpy.ops.armature.select_all(action="SELECT")
    bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Z")
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def skin(body, arm):
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    try:
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        print("weights automatic")
    except RuntimeError as exc:
        print("auto weights failed", exc)
        bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE")


def best_rotation(arm, bone_name, child_name, score):
    winner = None
    best = None
    bone = arm.pose.bones[bone_name]
    for axis in range(3):
        for sign in (1, -1):
            for pb in arm.pose.bones:
                pb.rotation_euler = (0, 0, 0)
            angles = [0.0, 0.0, 0.0]
            angles[axis] = math.radians(70) * sign
            bone.rotation_euler = angles
            bpy.context.view_layer.update()
            value = score(arm.pose.bones[child_name].head)
            if best is None or value > best:
                best = value
                winner = (axis, sign)
    for pb in arm.pose.bones:
        pb.rotation_euler = (0, 0, 0)
    return winner


def apply_rot(bone, axis, sign, degrees):
    angles = [0.0, 0.0, 0.0]
    angles[axis] = math.radians(degrees) * sign
    bone.rotation_euler = angles


def key_pose(arm):
    activate(arm)
    bpy.ops.object.mode_set(mode="POSE")
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    arm_axis = best_rotation(arm, "LeftUpperArm", "LeftHand", lambda h: h.z)
    knee_axis = best_rotation(arm, "LeftLeg", "LeftToe", lambda h: h.y)
    print("axes", arm_axis, knee_axis)
    action = bpy.data.actions.new("ArmAndKnee")
    arm.animation_data_create()
    arm.animation_data.action = action
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 24
    scene.frame_set(1)
    for pb in arm.pose.bones:
        pb.rotation_euler = (0, 0, 0)
        pb.keyframe_insert("rotation_euler", frame=1)
    scene.frame_set(24)
    if "LeftUpperArm" in arm.pose.bones:
        apply_rot(arm.pose.bones["LeftUpperArm"], *arm_axis, 70)
        apply_rot(arm.pose.bones["RightUpperArm"], *arm_axis, 70)
    if "LeftLeg" in arm.pose.bones:
        apply_rot(arm.pose.bones["LeftLeg"], *knee_axis, 65)
    bpy.context.view_layer.update()
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_euler", frame=24)
    print("hand", tuple(round(v, 3) for v in arm.pose.bones["LeftHand"].head))


def add_camera(name, loc, scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = scale
    cam = bpy.data.objects.new(name, data)
    cam.location = loc
    bpy.context.collection.objects.link(cam)
    look_at(cam, (0, 0, 0.95))
    return cam


def setup_render():
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.49, 0.49, 0.49, 1)
    bg.inputs[1].default_value = 0.9
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 2.4
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(42), 0, math.radians(24))
    bpy.context.collection.objects.link(sun)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 720
    scene.render.resolution_y = 960
    try:
        scene.view_settings.view_transform = "Standard"
    except TypeError:
        pass


def render_to(path, cam):
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.filepath = path
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("rendered", path)


def fill_image_holes(image):
    import numpy as np

    w, h = image.size
    px = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)
    rgb = px[:, :, :3]
    holes = rgb.sum(axis=2) < 0.08
    print("bake holes", int(holes.sum()))
    for _ in range(10):
        if not holes.any():
            break
        acc = np.zeros_like(rgb)
        count = np.zeros((h, w), dtype=np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                shifted = np.roll(np.roll(rgb, dy, 0), dx, 1)
                src = np.roll(np.roll(~holes, dy, 0), dx, 1)
                use = holes & src
                acc[use] += shifted[use]
                count[use] += 1
        good = count > 0
        rgb[good] = acc[good] / count[good, None]
        holes[good] = False
    px[:, :, :3] = rgb
    image.pixels = px.ravel()
    image.update()


def main():
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(OUT, "landmarks.json")) as f:
        marks = json.load(f)
    clear_scene()
    body = import_body()
    activate(body)
    solid = body.modifiers.new("Solid", "SOLIDIFY")
    solid.thickness = 0.024
    solid.offset = 0.0
    remesh = body.modifiers.new("Remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = 0.01
    smooth = body.modifiers.new("Smooth", "SMOOTH")
    smooth.factor = 0.15
    smooth.iterations = 2
    bpy.ops.object.modifier_apply(modifier="Solid")
    before = len(body.data.vertices)
    bpy.ops.object.modifier_apply(modifier="Remesh")
    after = len(body.data.vertices)
    print("solidify", before, "remesh", after)
    if after < before * 0.25:
        raise RuntimeError("remesh collapsed the body")
    bpy.ops.object.modifier_apply(modifier="Smooth")
    activate(body)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for poly in body.data.polygons:
        poly.use_smooth = True
    bake_sheets(body, marks)
    arm = build_armature(body, marks)
    skin(body, arm)
    setup_render()
    cams = {
        "front": add_camera("CamFront", (0, -4.6, 0.95), 2.15),
        "side": add_camera("CamSide", (4.6, 0, 0.95), 2.15),
        "back": add_camera("CamBack", (0, 4.6, 0.95), 2.15),
    }
    render_to(os.path.join(ART, "sheet-rig-front.png"), cams["front"])
    render_to(os.path.join(ART, "sheet-rig-side.png"), cams["side"])
    render_to(os.path.join(ART, "sheet-rig-back.png"), cams["back"])
    key_pose(arm)
    bpy.context.scene.frame_set(24)
    render_to(os.path.join(ART, "sheet-rig-pose.png"), cams["front"])
    bpy.context.scene.frame_set(1)
    glb = os.path.join(OUT, "人物骨骼.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb,
        export_format="GLB",
        export_animations=True,
        export_skins=True,
        export_image_format="AUTO",
    )
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(ART, "character-rig.glb"),
        export_format="GLB",
        export_animations=True,
        export_skins=True,
        export_image_format="AUTO",
    )
    print("exported", glb, os.path.getsize(glb))


if __name__ == "__main__":
    main()
