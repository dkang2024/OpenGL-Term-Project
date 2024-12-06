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
from numba import njit, prange
from random import randint

SEED = randint(0, 10000000)
generator = OpenSimplex(SEED)

X_INDEX = 0 
Y_INDEX = 1
Z_INDEX = 2

CHUNK_SIZE = 32

WORLD_SIZE_XZ = 50
WORLD_SIZE_Y = 5

WORLD_CENTER_Y = WORLD_SIZE_Y // 2 * CHUNK_SIZE

EMPTY_VOXEL = 0
GRASS = 1
DIRT = 2
STONE = 3
SAND = 4
SNOW = 5
CLAY = 6

RED_LIGHT = 7

RED_GLASS = 8
GREEN_GLASS = 9
BLUE_GLASS = 10
REGULAR_GLASS = 11

EMPTY_CHUNK = 0 
FILLED_CHUNK = 1

PLACE_MINE_DISTANCE = 5

LEFT_MOUSE_BUTTON = 1 
RIGHT_MOUSE_BUTTON = 2

ti.init(ti.cpu)
MAX_ANGLE = 89