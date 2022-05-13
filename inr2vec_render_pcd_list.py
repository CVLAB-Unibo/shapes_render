import copy
import math
import time
from pathlib import Path
from typing import List

import bpy
import numpy as np
import open3d as o3d

from utils.utils import (
    add_track_to_constraint,
    create_camera,
    create_light,
    create_material,
    create_plane,
    pcd_to_sphere,
    remove_objects,
    set_camera_params,
    set_engine_params,
    set_principled_node,
    set_principled_node_as_rough_blue,
    set_render_params,
)


def main():

    path_base = Path("../datasets/inr2vec/qualitatives/")
    path_input = path_base / "rec_pcd_modelnet40/gt"
    path_out = path_base / "rec_pcd_modelnet40/renders_gt"
    path_out.mkdir(exist_ok=True, parents=True)

    paths = list(path_input.rglob("*.ply"))
    paths.sort()

    # Read from hesiod
    num_samples = 100
    res_x = int(800)
    res_y = int(800)
    devices = [0]
    location_camera = (0, 4.0, 1.0)
    loc_light = (0, 0, 2)
    rot_light = (math.radians(0), math.radians(0), math.radians(0))
    energy = 3.0
    rot_object = (math.radians(0), math.radians(0), math.radians(30))
    add_plane = False
    devices = [0]
    save_blender = False
    use_denoiser = True
    base_color = (0.6, 0.79, 1.0, 1.0)
    lens = 50
    plane_only_shadow = False
    radius_sphere = 0.017
    use_color = False
    subdivision = 1

    for path in paths:
        time_start = time.time()
        # Reset
        remove_objects()

        # Object
        pcd = o3d.io.read_point_cloud(str(path))

        pts = np.asarray(pcd.points)
        pts_temp = copy.deepcopy(pts)
        x, y, z = pts_temp[:, 0], pts_temp[:, 1], pts_temp[:, 2]
        pts[:, 0] = -1 * x
        pts[:, 1] = -1 * z
        pts[:, 2] = y

        colors = np.asarray(pcd.colors)
        if len(colors):
            pts = np.concatenate((pts, colors), axis=1)

        print(f"here {len(bpy.data.objects.items())}")
        focus_target_object = pcd_to_sphere(pts, radius=radius_sphere, scale=1, subdivision=subdivision)  # type: ignore

        if pts.shape[1] > 3 and use_color:
            mat = create_material(
                "Material_Visualization", use_nodes=True, make_node_tree_empty=True
            )

            output_node = mat.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
            principled_node = mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
            rgb_node = mat.node_tree.nodes.new(type="ShaderNodeRGB")
            mix_node = mat.node_tree.nodes.new(type="ShaderNodeMixShader")
            attrib_node = mat.node_tree.nodes.new(type="ShaderNodeAttribute")
            attrib_node.attribute_name = "Col"
            rgb_node.outputs["Color"].default_value = (0.1, 0.1, 0.1, 1.0)

            mat.node_tree.links.new(
                attrib_node.outputs["Color"], principled_node.inputs["Base Color"]
            )
            mat.node_tree.links.new(principled_node.outputs["BSDF"], mix_node.inputs[1])
            mat.node_tree.links.new(mix_node.outputs["Shader"], output_node.inputs["Surface"])
        else:
            # Material
            mat = create_material("Material_Right", use_nodes=True, make_node_tree_empty=True)
            output_node = mat.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
            principled_node = mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
            set_principled_node(principled_node, base_color=base_color)
            mat.node_tree.links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])

        focus_target_object.data.materials.append(mat)
        # Location Plane
        if add_plane:
            z_plane = (focus_target_object.dimensions[-1] * 0.5) + 0.1
            loc_plane = (0.0, 0.0, -z_plane)
            create_plane(size=100.0, location=loc_plane)
            bpy.context.object.cycles.is_shadow_catcher = plane_only_shadow

        # Camera
        camera_object = create_camera(location=location_camera)
        add_track_to_constraint(camera_object, focus_target_object)
        set_camera_params(camera_object.data, focus_target_object, lens=lens)
        scene = bpy.data.scenes["Scene"]
        scene.camera = camera_object

        # Light
        light = create_light(location=loc_light, rotation=rot_light, name="sun", energy=energy)
        bpy.context.collection.objects.link(light)

        # Render Setting
        path_render = path_out / f"{path.stem}.png"
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
            bpy.ops.wm.save_mainfile(filepath="debug")
        time_end = time.time() - time_start
        print(f"Time one shape: {time_end}")
        bpy.ops.wm.read_factory_settings()


if __name__ == "__main__":
    main()
