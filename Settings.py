import moderngl_window as mglw
import math 
import moderngl as mgl 
import numpy as np
import taichi as ti
import pyglet
from pyglet import shapes 
import time 
import glm 
import os 

ti.init(ti.cpu)
MAX_ANGLE = 89