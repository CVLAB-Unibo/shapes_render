import math
from pathlib import Path
from typing import Optional, Tuple

import bpy  # type: ignore

from utils.utils import (
    add_track_to_constraint,
    create_camera,
    create_sun_light,
    remove_objects,
    set_camera_params,
    set_engine_properties,
    set_render_properties,
)


def add_subdivision_surface_modifier(
    mesh_object: bpy.types.Object, level: int, is_simple: bool = False
) -> None:
    """
    https://docs.blender.org/api/current/bpy.types.SubsurfModifier.html
    """

    modifier: bpy.types.SubsurfModifier = mesh_object.modifiers.new(name="Subsurf", type="SUBSURF")

    modifier.levels = level
    modifier.render_levels = level
    modifier.subdivision_type = "SIMPLE" if is_simple else "CATMULL_CLARK"


def create_smooth_monkey(
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    subdivision_level: int = 2,
    name: Optional[str] = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_monkey_add(location=location, rotation=rotation, calc_uvs=True)

    current_object = bpy.context.object

    if name is not None:
        current_object.name = name

    # for polygon in current_object.data:
    #     polygon.use_smooth = True

    add_subdivision_surface_modifier(current_object, subdivision_level)

    return current_object


def set_scene_objects() -> bpy.types.Object:
    num_suzannes = 1
    for index in range(num_suzannes):
        create_smooth_monkey(
            location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 0.0), name="Suzanne" + str(index)
        )

    return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]


def main():

    # Read from hesiod
    path_render = Path("/home/rspezialetti/dev/shapes_render/render0.png")
    res_x = 1920
    res_y = 1080

    location_camera = (0.0, -7.0, 0.0)
    camera_rot_x = 30
    camera_rot_y = 120.0
    camera_rot_z = 0
    rotation_camera = (camera_rot_x, camera_rot_y, camera_rot_z)
    devices = [0, 1]

    ## Reset
    remove_objects()

    ## Suzannes
    center_suzanne = set_scene_objects()

    ## Camera
    camera = create_camera(location=location_camera, rotation=rotation_camera)

    add_track_to_constraint(camera, center_suzanne)
    set_camera_params(camera.data, center_suzanne, lens=50.0)

    # Lights
    create_sun_light(rotation=(0.0, math.pi * 0.5, -math.pi * 0.1))

    # Render Setting
    scene = bpy.data.scenes["Scene"]
    scene.camera = camera
    set_render_properties(scene, path_render, resolution_x=res_x, resolution_y=res_y)

    set_engine_properties(
        scene,
        ids_cuda_devices=devices,
        use_adaptive_sampling=False,
        num_samples=1,
    )

    # bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
