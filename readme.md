
# Rea1is1ic Mine2raft 

## Description

This is a path traced Minecraft game with global illumination. Includes simplex noise world generation, lots of dynamic voxels using the DDA algorithm for ray marching, path tracing with a combination of temporal anti aliasing and resampled importance sampling, glass with dielectric ray scattering, mirrors with reflective ray scattering, placing / removing blocks with a block selection indicator, and world saving / loading.

## Run Instructions 

You will need to run the following command in a virtual environment / new python installation to be able to run the project (DO NOT USE PYTHON 3.13 -> USE PYTHON 3.12): 
    
### pip install moderngl numpy taichi pyglm opensimplex pillow moderngl-window numba 

If you want to set the time of the day or the world name that's loaded / saved, you have to edit those global variables in the "Settings.py" file. Run the actual Minecraft by running "Main.py".

## WARNING (CAUTION WITH GPU)

You need a relatively modern GPU to run this program because it has to support OpenGL version 4.6 AND the OpenGL extensions of bindless textures and int64s. Otherwise, the program will crash. Furthermore, you should have a pretty powerful GPU to get a decent FPS because everything is ray traced. If you have a potato PC, lower the voxel view range global in "Settings.py".