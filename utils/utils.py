"""
Module containing generic utils.

Author: Riccardo Spezialetti
Mail: riccardo.spezialetti@unibo.it
"""
from pathlib import Path
from typing import List, Optional, Tuple

import bpy  # type: ignore


def remove_objects() -> None:
    """
    Remove all the objects in the scene.
    """
    for item in bpy.data.objects:
        bpy.data.objects.remove(item)


def set_render_properties(
    scene: bpy.types.Scene,
    path_render: Path,
    use_transparent_bg: bool = False,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    percentage_resolution: int = 100,
) -> None:
    """Set Renderer Properties.

    Args:
        scene: the scene to render.
        path_render: the to the rendered image.
        use_transparent_bg: If True render with trasparent background. Defaults to False.
        resolution_x: the width for the image. Defaults to 1920.
        resolution_y: the height for the image. Defaults to 1080.
        percentage_resolution: the scale percentage for the resolutio of the image. Defaults to 100.
    """
    scene.render.resolution_percentage = percentage_resolution
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.filepath = str(path_render)
    scene.render.image_settings.file_format = path_render.suffix[1:].upper()
    scene.render.engine = "CYCLES"
    scene.render.use_motion_blur = False
    scene.render.film_transparent = use_transparent_bg


def set_engine_properties(
    scene: bpy.types.Scene,
    num_samples: int = 4096,
    ids_cuda_devices: List[int] = [],
    use_adaptive_sampling: bool = False,
) -> None:
    """Set Engine properties.

    Args:
        scene: the scene to render.
        num_samples: The number of samples to render for cycles. Defaults to 4096.
        ids_cuda_devices: Ids to use for rendering, if empty use all the availabe devices. Defaults to [].
        use_adaptive_sampling: If True use adaptive sampling. Defaults to False.

    Raises:
        ValueError: if adaptive sampling is False and the number of samples is zero.
    """

    if not use_adaptive_sampling:
        if num_samples == 0:
            raise ValueError("Use adaptive sampling is false but num samples is zero.")

    scene.view_layers[0].cycles.use_denoising = True

    scene.cycles.use_adaptive_sampling = use_adaptive_sampling
    if not use_adaptive_sampling:
        scene.cycles.samples = num_samples

    cuda_devices = []
    bpy.context.preferences.addons["cycles"].preferences.get_devices()
    for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
        name = dev["name"]
        dev["use"] = 0
        if "NVIDIA" in name:
            if name not in cuda_devices:
                cuda_devices.append(name)

    if len(ids_cuda_devices):
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"

        for id_dev in ids_cuda_devices:
            for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
                if cuda_devices[id_dev] == dev["name"]:
                    dev["use"] = 1
    else:
        for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
            dev["use"] = 1

    devices_enable = []
    for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
        if dev["use"]:
            devices_enable.append(dev["name"])

    print(f"Devices for rendering: {devices_enable}")


def add_track_to_constraint(
    camera_object: bpy.types.Object, track_to_target_object: bpy.types.Object
) -> None:
    constraint = camera_object.constraints.new(type="TRACK_TO")
    constraint.target = track_to_target_object
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"


def create_camera(
    location: Tuple[float, float, float], rotation: Tuple[float, float, float]
) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=location, rotation=rotation, scale=(0.4, 0, 0))

    bpy.ops.object.camera_add()
    cam = bpy.data.objects["Camera"]
    cam.rotation_mode = "XYZ"

    # cam.location.x = location[0]
    # cam.location.y = location[1]
    # cam.location.z = location[2]

    # cam.rotation_euler[0] = rotation[0]
    # cam.rotation_euler[1] = rotation[1]
    # cam.rotation_euler[2] = rotation[2]
    print(cam.location)
    print(cam.rotation_euler)
    return cam


def set_camera_params(
    camera: bpy.types.Camera,
    focus_target_object: bpy.types.Object,
    lens: float = 85.0,
    fstop: float = 1.4,
) -> None:
    # Simulate Sony's FE 85mm F1.4 GM
    camera.sensor_fit = "HORIZONTAL"
    camera.sensor_width = 36.0
    camera.sensor_height = 24.0
    camera.lens = lens
    camera.dof.use_dof = True
    camera.dof.focus_object = focus_target_object
    camera.dof.aperture_fstop = fstop
    camera.dof.aperture_blades = 11


def create_sun_light(
    location: Tuple[float, float, float] = (0.0, 0.0, 5.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    name: Optional[str] = None,
) -> bpy.types.Object:
    bpy.ops.object.light_add(type="SUN", location=location, rotation=rotation)

    if name is not None:
        bpy.context.object.name = name

    return bpy.context.object
