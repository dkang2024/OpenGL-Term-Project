
# Rea1is1ic Mine2raft 

## Description

This is a path traced Minecraft game with global illumination. Includes simplex noise world generation, lots of dynamic voxels using the DDA algorithm for ray marching, path tracing with a combination of temporal anti aliasing and resampled importance sampling, glass with dielectric ray scattering, mirrors with reflective ray scattering, placing / removing blocks with a block selection indicator, and world saving / loading.

## Run Instructions 

You will need to run the following command in a virtual environment / new python installation to be able to run the project: 
    
### pip install moderngl numpy taichi pyglm opensimplex pillow moderngl-window numba 