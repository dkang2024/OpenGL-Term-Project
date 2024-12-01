from Settings import *
from opensimplex.internals import _noise2, _noise3, _init 

perm, perm_grad_index3 = _init(SEED)

@njit(cache = True)
def noise2(x, y):
    '''
    Generate 2d simplex noise
    '''
    return _noise2(x, y, perm) 

@njit(cache = True)
def noise3(x, y, z):
    '''
    Generate 3d simplex noise
    '''
    return _noise3(x, y, z, perm, perm_grad_index3) 