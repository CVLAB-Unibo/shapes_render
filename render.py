import math
import os
import random
import sys
from typing import List, Tuple

import bpy
import hesiod
import open3d as o3d
import PIL

working_dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir_path)

from utils.utils import (
    add_material,
    add_track_to_constraint,
    create_camera,
    create_light,
    create_plane,
    remove_objects,
    set_camera_params,
    set_engine_params,
    set_render_params,
)


def get_random_numbers(length: int) -> List[float]:
    numbers = []
    for i in range(length):
        numbers.append(random.random())
    return numbers


def get_color(x: float) -> Tuple[float, float, float]:
    colors = [
        (0.776470, 0.894117, 0.545098),
        (0.482352, 0.788235, 0.435294),
        (0.137254, 0.603921, 0.231372),
    ]

    a = x * (len(colors) - 1)
    t = a - math.floor(a)
    c0 = colors[math.floor(a)]
    c1 = colors[math.ceil(a)]

    return (
        (1.0 - t) * c0[0] + t * c1[0],
        (1.0 - t) * c0[1] + t * c1[1],
        (1.0 - t) * c0[2] + t * c1[2],
    )


def set_scene_objects() -> bpy.types.Object:
    bpy.ops.import_mesh.ply(filepath="/home/rspezialetti/dev/shapes_render/shapes/model_mesh.ply")
    current_object = bpy.context.object
    current_object.name = "object"

    # Assign random colors for each triangle
    mesh = current_object.data
    mesh.vertex_colors.new(name="Col")
    random_numbers = get_random_numbers(len(mesh.vertex_colors["Col"].data))
    for index, vertex_color in enumerate(mesh.vertex_colors["Col"].data):
        vertex_color.color = get_color(random_numbers[index // 3]) + tuple([1.0])

    # Setup a material with wireframe visualization and per-face colors
    mat = add_material("Material_Visualization", use_nodes=True, make_node_tree_empty=True)
    current_object.data.materials.append(mat)

    output_node = mat.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    principled_node = mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    rgb_node = mat.node_tree.nodes.new(type="ShaderNodeRGB")
    mix_node = mat.node_tree.nodes.new(type="ShaderNodeMixShader")
    wire_node = mat.node_tree.nodes.new(type="ShaderNodeWireframe")
    wire_mat_node = mat.node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
    attrib_node = mat.node_tree.nodes.new(type="ShaderNodeAttribute")

    attrib_node.attribute_name = "Col"
    rgb_node.outputs["Color"].default_value = (0.1, 0.1, 0.1, 1.0)

    mat.node_tree.links.new(attrib_node.outputs["Color"], principled_node.inputs["Base Color"])
    mat.node_tree.links.new(principled_node.outputs["BSDF"], mix_node.inputs[1])
    mat.node_tree.links.new(rgb_node.outputs["Color"], wire_mat_node.inputs["Color"])
    mat.node_tree.links.new(wire_mat_node.outputs["BSDF"], mix_node.inputs[2])
    mat.node_tree.links.new(wire_node.outputs["Fac"], mix_node.inputs["Fac"])
    mat.node_tree.links.new(mix_node.outputs["Shader"], output_node.inputs["Surface"])

    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    focus_target = bpy.context.object

    return focus_target


from pathlib import Path


def main():

    path = "/home/rspezialetti/dev/shapes_render/shapes/model_mesh.ply"
    pcd = o3d.io.read_point_cloud(path)

    o3d.visualization.draw_geometries([pcd])

    # Read from hesiod
    num_samples = 20
    path_render = Path("/home/rspezialetti/dev/shapes_render/render0.png")
    res_x = int(1920 * 0.5)
    res_y = int(1080 * 0.5)

    # Location Camera
    location_camera = (0.0, -0.5, 5.76)

    # Location Light
    loc_light = (0, 0, 2)
    rot_light = (math.radians(0), math.radians(0), math.radians(0))
    energy = 3.0

    # Rotation Object
    rot_object = (math.radians(0), math.radians(0), math.radians(0))

    # Location Plane
    loc_plane = (0.0, 0.0, -1.76)

    devices = []

    # Reset
    remove_objects()

    # Instantiate a floor plane
    create_plane(size=200.0, location=loc_plane)

    # Object
    focus_target_object = set_scene_objects()

    # Camera
    camera_object = create_camera(location=location_camera)
    add_track_to_constraint(camera_object, focus_target_object)
    set_camera_params(camera_object.data, focus_target_object, lens=50, fstop=5)
    scene = bpy.data.scenes["Scene"]
    scene.camera = camera_object

    # Light
    light = create_light(location=loc_light, rotation=rot_light, name="sun", energy=energy)
    bpy.context.collection.objects.link(light)

    # Render Setting
    set_render_params(
        scene, path_render, resolution_x=res_x, resolution_y=res_y, use_transparent_bg=True
    )
    set_engine_params(scene, ids_cuda_devices=devices, num_samples=num_samples)

    obj = bpy.data.objects["object"]
    obj.rotation_euler = rot_object

    bpy.ops.render.render(write_still=True)
    # bpy.ops.wm.save_mainfile()


if __name__ == "__main__":
    main()
