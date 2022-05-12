# Blender based Render for generating rendering images directly for point cloud, mesh and voxel

Tested with Python 3.9.0 Blender 2.93.10, Optix 7.2.0 and GCC 9.4.0

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

# Creat a virutalenv
```
OPT="-fPIC" pyenv install 3.9.0
pyenv local 3.9.0
python -m venv .venv
```

# Install Blender bpy from sources
```
# This guide is a custom version of https://wiki.blender.org/wiki/Building_Blender/Linux/Ubuntu
# Create a folder and pull blender from github
mkdir blender-git
cd blender-git
# Clone from git
git clone https://git.blender.org/blender.git
cd blender
# Checkout that specific version
git checkout blender-v2.93-release
cd ..
# Download the libraries
mkdir lib
cd lib
svn checkout https://svn.blender.org/svnroot/bf-blender/trunk/lib/linux_centos7_x86_64
cd ../blender
make update
cd ..
# Create folder for build files
mkdir build
cd build
# Configure cmake to build bpy
cmake -C ../blender/build_files/cmake/config/bpy_module.cmake  ../blender
# Change some variable in cmake configuration you can use cmake-gui or ccmake.
ccmake .
# Use the python interpreter installed with pyenv
PYTHON_EXECUTABLE=/home/marcello/.pyenv/versions/3.9.0/bin/python3.9 
PYTHON_INCLUDE_CONFIG_DIR=/home/marcello/.pyenv/versions/3.9.0/include/python3.9
PYTHON_INCLUDE_DIR=/home/marcello/.pyenv/versions/3.9.0/include/python3.9
PYTHON_LIBPATH=/home/marcello/.pyenv/versions/3.9.0/include/python3.9/lib
PYTHON_LIBRARY=/home/marcello/.pyenv/versions/3.9.0/lib/libpython3.9.a
# This is the folder containing the create virtual env, bpy module will be installed here
PYTHON_SITE_PACKAGES=/home/marcello/dev/shapes_render/.venv/lib/python3.9/site-packages
# Setup the optix denoiser (optional)
WITH_CYCLES_DEVICE_OPTIX = TRUE
WITH_CYCLES_CUDA_BINARIES = TRUE
# Download optix from NVIDIA
OPTIX_INCLUDE_DIR=/home/marcello/dev/blender-git/NVIDIA-OptiX-SDK-7.2.0-linux64-x86_64/include

# Save and Generate
make -j 8
make install
# Test the installed version
python -c "import bpy ; bpy.ops.render.render(write_still=True)"
```
