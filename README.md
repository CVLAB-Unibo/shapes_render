# Blender based Render for generating rendering images directly of point cloud, mesh and voxel

Tested with Python 3.8.6 and Blender 3.0.1

## Setup Blender:
* Download Blender last [release](https://www.blender.org/download/)
* Unzip the archive `tar -xvf blender-3.1.0-linux-x64.tar.xz`
* Move the unzipped folder to `/usr/local/` `mv blender-3.1.0-linux-x64 /usr/local/`
* Create symbolic link to blender executable: `sudo ln -s /usr/local/blender-3.1.0-linux-x64/blender /usr/bin/blender`

## Install Dependencies:
* `pip install numpy`
* `pip install hesiod` 

## Add folder to PythonPath:
* `PYTHONPATH="${PYTHONPATH}:/path_to/shapes_render"`

### Useful Resources:
* [ShapeNet Rendering](https://github.com/panmari/stanford-shapenet-renderer/blob/master/render_blender.py) with depth, albedo and RGB
* [Collection](https://github.com/yuki-koyama/blender-cli-rendering) of Blender Python scripts for generating scenes and rendering images directly from command-line interface


