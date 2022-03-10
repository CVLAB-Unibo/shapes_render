# Blender based Render for generating point cloud, mesh and voxel

## Setup Blender:
* Download Blender last [release](https://www.blender.org/download/)
* Unzip the archive
* Move the unzipped folder to `/usr/local`
* Create symbolic link to blender executable: `ln -s /usr/local/blender_xx_/blender /usr/bin/blender`

## Install Dependencies:
* `pip install numpy`
* `pip install hesiod` 

### Useful Resources:
* [ShapeNet Rendering](https://github.com/panmari/stanford-shapenet-renderer/blob/master/render_blender.py) with depth, albedo and RGB
* [Collection](https://github.com/yuki-koyama/blender-cli-rendering) of Blender Python scripts for generating scenes and rendering images directly from command-line interface
