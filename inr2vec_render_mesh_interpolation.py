import math
import os
import random
import sys
from json import load
from pathlib import Path
from typing import List, Tuple

import bpy

print(bpy.app.version_string)
working_dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir_path)

from utils.utils import (
    add_track_to_constraint,
    create_camera,
    create_light,
    create_plane,
    load_mesh,
    remove_objects,
    set_camera_params,
    set_engine_params,
    set_render_params,
)


def main():

    path_base = Path("/media/rspezialetti/Data/rspezialetti/projects/inr2vec/qualitatives/")
    path_input = path_base / "interp_mesh_manifold40/"
    paths = list(path_input.rglob("*.ply"))
    paths.sort()

    # Read from hesiod
    num_samples = 100
    res_x = int(800)
    res_y = int(800)
    devices = [0]
    lens = 70

    # Location Camera
    location_camera = (0, 4.0, 1.0)

    # Location Light
    loc_light = (0, 0, 2)
    rot_light = (math.radians(0), math.radians(0), math.radians(0))
    energy = 3.0
    save_blender = False
    add_plane = False
    use_denoiser = True

    for path in paths:
        path_out = path_input / path.parts[-2] / "render"
        path_out.mkdir(exist_ok=True)
        path_render = path_out / f"{path.stem}.png"
        # Reset
        remove_objects()

        # Rotation Object
        rot_object = (math.radians(0), math.radians(0), math.radians(210))

        # Object
        focus_target_object = load_mesh(path)

        # Location Plane
        if add_plane:
            z_plane = focus_target_object.dimensions[-1] - 0.2
            loc_plane = (0.0, 0.0, z_plane)
            create_plane(size=1.0, location=loc_plane)

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
            bpy.ops.wm.save_mainfile()


if __name__ == "__main__":
    main()
