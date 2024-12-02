from Settings import *
from opensimplex.internals import _noise2, _noise3, _init 

perm, perm_grad_index3 = _init(SEED)

@njit(cache = True)
def shift(value):
    '''
    Shift from [-1, 1] to [0, 1]
    '''
    return (value + 1) / 2

@njit(cache = True)
def noise2(x, y):
    '''
    Generate 2d simplex noise
    '''
    return shift(_noise2(x, y, perm))

@njit(cache = True)
def noise3(x, y, z):
    '''
    Generate 3d simplex noise
    '''
    return shift(_noise3(x, y, z, perm, perm_grad_index3))