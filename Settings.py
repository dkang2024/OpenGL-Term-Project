import moderngl_window as mglw
import math 
import moderngl as mgl 
import numpy as np
import taichi as ti
import time 
import glm 
import os 
from PIL import Image
from numba import njit, prange

SEED = 16

X_INDEX = 0 
Y_INDEX = 1
Z_INDEX = 2

CHUNK_SIZE = 8
WORLD_SIZE = 2 #Number of chunks that the world contains

WORLD_CENTER_X = WORLD_SIZE * CHUNK_SIZE // 2
WORLD_CENTER_Y = WORLD_CENTER_X

GRASS = 1
DIRT = 2

ti.init(ti.cpu)
MAX_ANGLE = 89