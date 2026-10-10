"""Posable body matched to the T-pose front and side sheets.

One welded mesh, a humanoid armature, automatic weights, and a short
pose clip (arms up, one knee bent). Face is a simplified stand-in.
"""

import math
import os

import bpy
from mathutils import Vector

OUT_DIR = "/workspace/人物设定图/模型"
ART_DIR = "/opt/cursor/artifacts"

SKIN = (0.84, 0.55, 0.40, 1)
HAIR = (0.07, 0.07, 0.08, 1)
SHORTS = (0.08, 0.08, 0.09, 1)
EYE_W = (0.93, 0.91, 0.88, 1)
EYE_D = (0.07, 0.06, 0.05, 1)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def sphere(loc, radius, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, location=loc, segments=28, ring_count=16
    )
    obj = bpy.context.object
    obj.scale = scale
    activate(obj)
    bpy.ops.object.transform_apply(scale=True)
    return obj


def capsule(a, b, radius, vertices=24):
    a = Vector(a)
    b = Vector(b)
    mid = (a + b) / 2
    direction = b - a
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=direction.length, location=mid, vertices=vertices
    )
    obj = bpy.context.object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    activate(obj)
    bpy.ops.object.transform_apply(rotation=True)
    return obj


def build_body():
    parts = []
    # Head, narrow jaw, neck. Hair spikes sit on the skull and get painted black.
    parts.append(sphere((0, 0.0, 1.73), 0.108, (1.0, 0.95, 1.08)))
    parts.append(sphere((0, -0.02, 1.66), 0.078, (0.85, 0.8, 0.72)))
    parts.append(sphere((0, 0.0, 1.56), 0.07, (1.05, 0.9, 0.85)))

    # Torso. Width and depth follow the turnaround: wide delts, round mid chest.
    parts.append(sphere((0, -0.01, 1.36), 0.20, (1.15, 0.82, 0.95)))
    parts.append(sphere((0.09, -0.07, 1.33), 0.105))
    parts.append(sphere((-0.09, -0.07, 1.33), 0.105))
    parts.append(sphere((0, 0.08, 1.38), 0.16, (1.05, 0.7, 0.9)))
    parts.append(sphere((0.15, 0.03, 1.26), 0.09))
    parts.append(sphere((-0.15, 0.03, 1.26), 0.09))
    parts.append(sphere((0, 0.0, 1.16), 0.145, (1.05, 0.85, 0.7)))
    parts.append(sphere((0, 0.0, 1.00), 0.175, (1.15, 0.82, 0.62)))
    parts.append(sphere((0.08, 0.08, 0.96), 0.10))
    parts.append(sphere((-0.08, 0.08, 0.96), 0.10))

    # Shoulders and arms overlap the chest so the weld connects them.
    parts.append(sphere((0.26, 0.0, 1.46), 0.11))
    parts.append(sphere((-0.26, 0.0, 1.46), 0.11))
    parts.append(capsule((0.24, 0.0, 1.46), (0.50, 0.0, 1.45), 0.078))
    parts.append(capsule((-0.24, 0.0, 1.46), (-0.50, 0.0, 1.45), 0.078))
    parts.append(sphere((0.50, 0.0, 1.45), 0.062))
    parts.append(sphere((-0.50, 0.0, 1.45), 0.062))
    parts.append(capsule((0.48, 0.0, 1.45), (0.68, 0.0, 1.435), 0.052))
    parts.append(capsule((-0.48, 0.0, 1.45), (-0.68, 0.0, 1.435), 0.052))
    parts.append(sphere((0.70, -0.005, 1.43), 0.042, (0.85, 0.55, 1.15)))
    parts.append(sphere((-0.70, -0.005, 1.43), 0.042, (0.85, 0.55, 1.15)))

    # Legs overlap the pelvis.
    parts.append(capsule((0.11, 0.0, 0.92), (0.12, 0.01, 0.50), 0.095))
    parts.append(capsule((-0.11, 0.0, 0.92), (-0.12, 0.01, 0.50), 0.095))
    parts.append(sphere((0.12, 0.01, 0.50), 0.065))
    parts.append(sphere((-0.12, 0.01, 0.50), 0.065))
    parts.append(capsule((0.12, 0.01, 0.52), (0.12, 0.0, 0.04), 0.062))
    parts.append(capsule((-0.12, 0.01, 0.52), (-0.12, 0.0, 0.04), 0.062))
    parts.append(sphere((0.12, -0.04, 0.045), 0.055, (0.85, 1.8, 0.55)))
    parts.append(sphere((-0.12, -0.04, 0.045), 0.055, (0.85, 1.8, 0.55)))

    # Fix the spike loop: the first version stored r wrong if I passed a 4-tuple
    # into sphere(loc[:3]). Rebuild spikes here as real spheres.
    for loc, r in (
        ((0, 0.02, 1.84), 0.042),
        ((-0.06, 0.015, 1.82), 0.036),
        ((0.06, 0.015, 1.82), 0.036),
        ((-0.085, 0.0, 1.77), 0.028),
        ((0.085, 0.0, 1.77), 0.028),
    ):
        parts.append(sphere(loc, r))

    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = "Body"
    remesh = body.modifiers.new("Remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = 0.014
    smooth = body.modifiers.new("Smooth", "SMOOTH")
    smooth.factor = 0.4
    smooth.iterations = 5
    activate(body)
    bpy.ops.object.modifier_apply(modifier="Remesh")
    bpy.ops.object.modifier_apply(modifier="Smooth")
    for poly in body.data.polygons:
        poly.use_smooth = True
    return body


def build_armature():
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

    hips = bone("Hips", (0, 0, 0.96), (0, 0, 1.08))
    spine = bone("Spine", (0, 0, 1.08), (0, 0, 1.22), hips, True)
    spine1 = bone("Spine1", (0, 0, 1.22), (0, 0, 1.36), spine, True)
    chest = bone("Chest", (0, 0, 1.36), (0, 0, 1.50), spine1, True)
    neck = bone("Neck", (0, 0, 1.50), (0, 0, 1.62), chest, True)
    bone("Head", (0, 0, 1.62), (0, 0, 1.84), neck, True)

    l_clav = bone("LeftShoulder", (0.06, 0, 1.48), (0.24, 0, 1.47), chest)
    l_arm = bone("LeftUpperArm", (0.26, 0, 1.46), (0.48, 0, 1.45), l_clav)
    l_fore = bone("LeftLowerArm", (0.48, 0, 1.45), (0.64, 0, 1.44), l_arm, True)
    bone("LeftHand", (0.64, 0, 1.44), (0.74, 0, 1.43), l_fore, True)

    r_clav = bone("RightShoulder", (-0.06, 0, 1.48), (-0.24, 0, 1.47), chest)
    r_arm = bone("RightUpperArm", (-0.26, 0, 1.46), (-0.48, 0, 1.45), r_clav)
    r_fore = bone("RightLowerArm", (-0.48, 0, 1.45), (-0.64, 0, 1.44), r_arm, True)
    bone("RightHand", (-0.64, 0, 1.44), (-0.74, 0, 1.43), r_fore, True)

    l_up = bone("LeftUpLeg", (0.11, 0, 0.90), (0.12, 0.01, 0.50), hips)
    l_leg = bone("LeftLeg", (0.12, 0.01, 0.50), (0.12, 0, 0.10), l_up, True)
    l_foot = bone("LeftFoot", (0.12, 0, 0.08), (0.12, -0.16, 0.03), l_leg)
    bone("LeftToe", (0.12, -0.16, 0.03), (0.12, -0.22, 0.025), l_foot, True)

    r_up = bone("RightUpLeg", (-0.11, 0, 0.90), (-0.12, 0.01, 0.50), hips)
    r_leg = bone("RightLeg", (-0.12, 0.01, 0.50), (-0.12, 0, 0.10), r_up, True)
    r_foot = bone("RightFoot", (-0.12, 0, 0.08), (-0.12, -0.16, 0.03), r_leg)
    bone("RightToe", (-0.12, -0.16, 0.03), (-0.12, -0.22, 0.025), r_foot, True)

    bpy.ops.armature.select_all(action="SELECT")
    bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Z")
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def make_mat(name, color, rough=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    spec = bsdf.inputs.get("Specular IOR Level")
    if spec:
        spec.default_value = 0.2
    return mat


def assign_regions(obj):
    mesh = obj.data
    mesh.materials.append(make_mat("Skin", SKIN))
    mesh.materials.append(make_mat("Hair", HAIR, 0.75))
    mesh.materials.append(make_mat("Shorts", SHORTS, 0.72))
    for poly in mesh.polygons:
        c = Vector((0, 0, 0))
        for vi in poly.vertices:
            c += mesh.vertices[vi].co
        c /= len(poly.vertices)
        if 0.78 < c.z < 1.02 and abs(c.x) < 0.26:
            poly.material_index = 2
        elif c.z > 1.71 and c.y > -0.03:
            poly.material_index = 1
        elif abs(c.x) < 0.02 and c.y < -0.07 and 1.60 < c.z < 1.64:
            poly.material_index = 1
        else:
            poly.material_index = 0


def add_eyes(arm):
    parts = []
    for side, x in (("L", 0.04), ("R", -0.04)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, location=(x, -0.125, 1.705), segments=16, ring_count=8)
        eye = bpy.context.object
        eye.name = f"Eye{side}"
        eye.data.materials.append(make_mat(eye.name + "Mat", EYE_W, 0.3))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008, location=(x, -0.140, 1.705), segments=12, ring_count=8)
        pupil = bpy.context.object
        pupil.name = f"Pupil{side}"
        pupil.data.materials.append(make_mat(pupil.name + "Mat", EYE_D, 0.4))
        parts.extend((eye, pupil))
    for obj in parts:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        arm.data.bones.active = arm.data.bones["Head"]
        bpy.ops.object.parent_set(type="BONE", keep_transform=True)
        obj.parent_bone = "Head"
    return parts


def skin_mesh(body, arm):
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    try:
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        print("weights: automatic")
    except RuntimeError as exc:
        print("auto weights failed:", exc)
        bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE")


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(name, loc, scale):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = scale
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = loc
    bpy.context.collection.objects.link(cam)
    look_at(cam, (0, 0, 1.0))
    return cam


def setup_world():
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.50, 0.50, 0.50, 1)
    bg.inputs[1].default_value = 0.85
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.4
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(48), math.radians(8), math.radians(28))
    bpy.context.collection.objects.link(sun)
    fill_data = bpy.data.lights.new("Fill", "AREA")
    fill_data.energy = 280
    fill_data.size = 3
    fill = bpy.data.objects.new("Fill", fill_data)
    fill.location = (-2.0, -2.0, 1.8)
    look_at(fill, (0, 0, 1.1))
    bpy.context.collection.objects.link(fill)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
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


def best_rotation(arm, bone_name, child_name, score):
    """Pick the local euler axis that moves a child bone the way score() wants."""
    winner = None
    best = None
    bone = arm.pose.bones[bone_name]
    for axis in range(3):
        for sign in (1, -1):
            for pb in arm.pose.bones:
                pb.rotation_euler = (0, 0, 0)
            angles = [0.0, 0.0, 0.0]
            angles[axis] = math.radians(80) * sign
            bone.rotation_euler = angles
            bpy.context.view_layer.update()
            value = score(arm.pose.bones[child_name].head)
            print("try", bone_name, axis, sign, round(value, 3),
                  tuple(round(v, 3) for v in arm.pose.bones[child_name].head))
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
    # Arm lift: hand should rise. Knee bend: toe should swing backward (+Y).
    arm_axis = best_rotation(arm, "LeftUpperArm", "LeftHand", lambda h: h.z)
    knee_axis = best_rotation(arm, "LeftLeg", "LeftToe", lambda h: h.y)
    print("arm axis", arm_axis, "knee axis", knee_axis)

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
    apply_rot(arm.pose.bones["LeftUpperArm"], *arm_axis, 75)
    apply_rot(arm.pose.bones["RightUpperArm"], *arm_axis, 75)
    apply_rot(arm.pose.bones["LeftLeg"], *knee_axis, 75)
    bpy.context.view_layer.update()
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_euler", frame=24)
    print("posed hand", tuple(round(v, 3) for v in arm.pose.bones["LeftHand"].head))
    print("posed toe", tuple(round(v, 3) for v in arm.pose.bones["LeftToe"].head))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ART_DIR, exist_ok=True)
    clear_scene()
    body = build_body()
    assign_regions(body)
    print("verts", len(body.data.vertices), "faces", len(body.data.polygons))
    arm = build_armature()
    skin_mesh(body, arm)
    groups = [g.name for g in body.vertex_groups]
    print("vertex groups", len(groups))
    add_eyes(arm)
    setup_world()
    cams = {
        "front": add_camera("CamFront", (0, -4.4, 1.0), 2.3),
        "side": add_camera("CamSide", (4.4, 0.0, 1.0), 2.3),
        "back": add_camera("CamBack", (0, 4.4, 1.0), 2.3),
        "threeq": add_camera("CamThreeQ", (2.8, -3.4, 1.15), 2.35),
    }
    render_to(os.path.join(ART_DIR, "rig-rest-front.png"), cams["front"])
    render_to(os.path.join(ART_DIR, "rig-rest-side.png"), cams["side"])
    render_to(os.path.join(ART_DIR, "rig-rest-back.png"), cams["back"])

    key_pose(arm)
    bpy.context.scene.frame_set(24)
    render_to(os.path.join(ART_DIR, "rig-pose.png"), cams["front"])
    bpy.context.scene.frame_set(1)

    glb = os.path.join(OUT_DIR, "人物骨骼.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb,
        export_format="GLB",
        export_animations=True,
        export_skins=True,
    )
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(ART_DIR, "character-rig.glb"),
        export_format="GLB",
        export_animations=True,
        export_skins=True,
    )
    print("exported", glb, os.path.getsize(glb))


if __name__ == "__main__":
    main()
