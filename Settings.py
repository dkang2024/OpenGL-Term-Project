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

CHUNK_SIZE = 32
WORLD_SIZE = CHUNK_SIZE * 32

GRASS = 1
DIRT = 2

ti.init(ti.cpu)
MAX_ANGLE = 89