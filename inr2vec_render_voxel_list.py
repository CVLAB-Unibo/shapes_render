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

import bmesh  # isort: skip

print(bpy.app.version_string)
working_dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir_path)

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
)


def load_voxel(path_file, radius, offset, scale, material):

    occupancies = np.load(path_file)["voxel"]
    points = np.where(occupancies)
    locations = np.zeros((points[0].shape[0], 3), dtype=float)
    locations[:, 0] = (points[0][:] + 0.5) / occupancies.shape[0]
    locations[:, 1] = (points[1][:] + 0.5) / occupancies.shape[1]
    locations[:, 2] = (points[2][:] + 0.5) / occupancies.shape[2]
    locations[:, 0] -= 0.5
    locations[:, 1] -= 0.5
    locations[:, 2] -= 0.5

    locations[:, 0] = locations[:, 0] * scale + offset[0]
    locations[:, 1] = locations[:, 1] * scale + offset[1]
    locations[:, 2] = locations[:, 2] * scale + offset[2]

    mesh = bmesh.new()

    bpy.ops.mesh.primitive_cube_add()
    cube_base_mesh = bpy.context.scene.objects["Cube"].data

    for i in range(locations.shape[0]):
        m = cube_base_mesh.copy()
        for vertex in m.vertices:
            vertex.co[0] = vertex.co[0] * radius + locations[i, 0]
            vertex.co[1] = vertex.co[1] * radius + locations[i, 1]
            vertex.co[2] = vertex.co[2] * radius + locations[i, 2]

        mesh.from_mesh(m)

    bpy.data.objects.remove(bpy.context.scene.objects["Cube"])

    mesh_cubes = bpy.data.meshes.new("Mesh")
    mesh.to_mesh(mesh_cubes)

    obj = bpy.data.objects.new("BRC_Occupancy", mesh_cubes)
    obj.name = "object"

    bpy.context.collection.objects.link(obj)
    focus_target = obj
    return focus_target


def main():

    path_input = Path(
        "/media/rspezialetti/Data/rspezialetti/projects/inr2vec/qualitatives/interp_vox_sh10/"
    )
    paths = list(path_input.rglob("*.npz"))
    paths.sort()

    # Save blender file
    save_blender = False
    num_samples = 500
    use_denoiser = True
    devices = [1]
    base_color = (0.0, 1.0, 0.0, 1.0)

    for path in paths[22:]:
        # Read from hesiod
        path_out = path_input / path.parts[-2] / "render"
        path_out.mkdir(exist_ok=True)
        path_render = path_out / f"{path.stem}.png"
        res_x = int(800)
        res_y = int(800)

        # Location Camera
        location_camera = (0, 3.0, 1.0)

        # Location Light
        loc_light = (0, 0, 1)
        rot_light = (math.radians(0), math.radians(0), math.radians(0))
        energy = 3.0

        # Rotation Object
        rot_object = (math.radians(0), math.radians(0), math.radians(54))

        # Reset
        remove_objects()

        # Object
        focus_target_object = load_voxel(
            path_file=path,
            radius=0.0125 / 2,
            offset=(0.0, 0.0, 0.0),
            scale=1.0,
            material=None,
        )
        dim_plane = focus_target_object.dimensions[-1] - 0.2

        # Instantiate a floor plane & Location Plane
        loc_plane = (0.0, 0.0, -dim_plane)
        # create_plane(size=1.0, location=loc_plane)
        # bpy.context.object.cycles.is_shadow_catcher = True

        # Material
        material = create_material("Material_Plane", use_nodes=True, make_node_tree_empty=True)
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
        set_principled_node(node_principled, base_color=base_color)

        node_diff = nodes.new("ShaderNodeBsdfDiffuse")

        node_output = nodes.new(type="ShaderNodeOutputMaterial")

        # create mix shader node
        node_mix = nodes.new(type="ShaderNodeMixShader")
        link_diff_mix = links.new(node_diff.outputs[0], node_mix.inputs[2])
        link_gloss_mix = links.new(node_principled.outputs[0], node_mix.inputs[1])
        link_mix_out = links.new(node_mix.outputs[0], node_output.inputs[0])

        focus_target_object.data.materials.append(material)

        # Camera
        camera_object = create_camera(location=location_camera)
        add_track_to_constraint(camera_object, focus_target_object)
        set_camera_params(camera_object.data, focus_target_object, lens=50)
        scene = bpy.data.scenes["Scene"]
        scene.camera = camera_object

        # Light
        # light = create_light(location=loc_light, rotation=rot_light, name="sun", energy=energy)
        light = create_light_area_vox(
            location=loc_light, rotation=rot_light, name="area", energy=25
        )
        bpy.context.collection.objects.link(light)

        # Render Setting
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

        bpy.ops.wm.read_factory_settings()


if __name__ == "__main__":
    main()
