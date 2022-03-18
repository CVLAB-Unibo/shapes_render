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

# venv installation
OPT="-fPIC" pyenv install 3.9.0
pyenv local 3.9.0
python -m venv .venv

#
apt-get install subversion

# Follow https://wiki.blender.org/wiki/Building_Blender/Linux/Ubuntu
mkdir blender-git
cd blender-git
cd blender
git checkout blender-v2.93-release
cd ..
mkdir lib
cd lib
svn checkout https://svn.blender.org/svnroot/bf-blender/trunk/lib/linux_centos7_x86_64
cd ../blender
make update
cd ..
mkdir build
cd build
cmake -C ../blender/build_files/cmake/config/bpy_module.cmake  
ccmake .

PYTHON_EXECUTABLE=/home/rspezialetti/.pyenv/versions/3.9.0/bin/python3.9 
PYTHON_INCLUDE_CONFIG_DIR=/home/rspezialetti/.pyenv/versions/3.9.0/include/python3.9
PYTHON_INCLUDE_DIR=/home/rspezialetti/.pyenv/versions/3.9.0/include/python3.9
PYTHON_LIBPATH=/home/rspezialetti/.pyenv/versions/3.9.0/include/python3.9/lib
PYTHON_LIBRARY=/home/rspezialetti/.pyenv/versions/3.9.0/lib/libpython3.9.a
PYTHON_SITE_PACKAGES=/home/rspezialetti/dev/shapes_render/.venv/lib/python3.9/site-packages

Save and Generate
make -j 8
make install
python -c "import bpy ; bpy.ops.render.render(write_still=True)"
