import moderngl_window as mglw
import math 
import moderngl as mgl 
from numba import njit
import pyglet
from pyglet import shapes 
import time 
import glm 

EPSILON = 1e-7
MAX_ANGLE = 89