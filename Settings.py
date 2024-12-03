import moderngl_window as mglw
import math 
import moderngl as mgl 
import numpy as np
import taichi as ti
import time 
import glm 
import os 
from PIL import Image
from opensimplex import OpenSimplex
from numba import njit, jit, prange
from random import randint

SEED = randint(0, 10000000)
generator = OpenSimplex(SEED)

X_INDEX = 0 
Y_INDEX = 1
Z_INDEX = 2

CHUNK_SIZE = 32

WORLD_SIZE_XZ = 32
WORLD_SIZE_Y = 5

WORLD_CENTER_Y = WORLD_SIZE_Y // 2 * CHUNK_SIZE

EMPTY_VOXEL = 0
GRASS = 1
DIRT = 2

ti.init(ti.cpu)
MAX_ANGLE = 89