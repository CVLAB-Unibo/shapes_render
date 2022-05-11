import math
import os
import random
import sys
from json import load
from pathlib import Path
from typing import List, Tuple

import bpy
import numpy as np
import open3d as o3d

from utils.utils import (
    add_track_to_constraint,
    create_camera,
    create_light,
    create_light_area,
    create_light_area_vox,
    create_material,
    create_new_image_material,
    create_plane,
    remove_objects,
    set_camera_params,
    set_engine_params,
    set_principled_node,
    set_principled_node_as_glass,
    set_principled_node_as_gold,
    set_principled_node_as_rough_blue,
    set_render_params,
    voxels_to_cube,
)


def main():

    path_input = Path("shapes/chair_voxel.npz")
    path_out = Path("renders")
    path_out.mkdir(exist_ok=True, parents=True)
    voxels = np.load(path_input)["voxel"]

    # Save blender file
    save_blender = False
    num_samples = 500
    use_denoiser = True
    devices = [0]
    res_x = int(800)
    res_y = int(800)
    location_camera = (0, 3.0, 1.0)
    loc_light = (0, 0, 1)
    rot_light = (math.radians(0), math.radians(0), math.radians(0))
    energy = 25
    rot_object = (math.radians(0), math.radians(0), math.radians(54))
    add_plane = True
    save_blender = True
    use_denoiser = True
    base_color = (0.0, 1.0, 0.0, 1.0)
    lens = 85
    plane_only_shadow = True

    # Reset
    remove_objects()

    # Object
    focus_target_object = voxels_to_cube(
        voxels=voxels,
        radius=0.0125 / 2,
        offset=(0.0, 0.0, 0.0),
        scale=1.0,
    )

    # Location Plane
    if add_plane:
        z_plane = focus_target_object.dimensions[-1] * 0.5
        loc_plane = (0.0, 0.0, -z_plane)
        create_plane(size=100.0, location=loc_plane)
        bpy.context.object.cycles.is_shadow_catcher = plane_only_shadow

    # Material
    material = create_material("Material_Voxel", use_nodes=True, make_node_tree_empty=True)
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    set_principled_node(node_principled, base_color=base_color)

    node_diff = nodes.new("ShaderNodeBsdfDiffuse")
    node_output = nodes.new(type="ShaderNodeOutputMaterial")

    # Create mix shader node
    node_mix = nodes.new(type="ShaderNodeMixShader")
    links.new(node_diff.outputs[0], node_mix.inputs[2])
    links.new(node_principled.outputs[0], node_mix.inputs[1])
    links.new(node_mix.outputs[0], node_output.inputs[0])

    focus_target_object.data.materials.append(material)

    # Camera
    camera_object = create_camera(location=location_camera)
    add_track_to_constraint(camera_object, focus_target_object)
    set_camera_params(camera_object.data, focus_target_object, lens=lens)
    scene = bpy.data.scenes["Scene"]
    scene.camera = camera_object

    # Light
    light = create_light_area_vox(
        location=loc_light, rotation=rot_light, name="area", energy=energy
    )
    bpy.context.collection.objects.link(light)

    # Render Setting
    path_render = path_out / f"{path_input.stem}.png"
    set_render_params(
        scene, path_render, resolution_x=res_x, resolution_y=res_y, use_transparent_bg=True
    )
    set_engine_params(
        scene, ids_cuda_devices=devices, num_samples=num_samples, use_denoiser=use_denoiser
    )

    obj = bpy.data.objects["object"]
    obj.rotation_euler = rot_object

    bpy.ops.render.render(write_still=True)

    if save_blender:
        bpy.ops.wm.save_mainfile()


if __name__ == "__main__":
    main()
