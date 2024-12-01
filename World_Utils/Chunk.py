from Settings import *
from Noise import *
 
@njit(cache = True)
def getWorldIndex(position, initChunkPosition):
    '''
    Get the world position from the current position and the smallest init chunk position
    '''
    return position + initChunkPosition

@njit(cache = True)
def getWorldHeight(x, z):
    a1 = WORLD_CENTER_Y 
    a2, a4, a8 = a1 * 0.5, a1 * 0.25, a1 * 0.125

    # frequency
    f1 = 0.005
    f2, f4, f8 = f1 * 2, f1 * 4, f1 * 8

    if noise2(0.1 * x, 0.1 * z) < 0:
        a1 /= 1.07

    height = 0
    height += noise2(x * f1, z * f1) * a1 + a1
    height += noise2(x * f2, z * f2) * a2 - a2
    height += noise2(x * f4, z * f4) * a4 + a4
    height += noise2(x * f8, z * f8) * a8 - a8

    height = max(height,  noise2(x * f8, z * f8) + 2)

    return int(height)

class Chunk:
    '''
    Create and render a chunk of blocks
    '''
    def __init__(self, worldArray, brickmapPosition, initChunkPosition):
        self.worldArray, self.brickmapPosition, self.initChunkPosition = worldArray, brickmapPosition, initChunkPosition

    @staticmethod 
    @njit(parallel = True, cache = True)
    def generate(worldArray, initChunkPosition):
        '''
        Upload and generate the chunk to the world array
        '''
        for x in prange(CHUNK_SIZE):
            worldX = getWorldIndex(x, initChunkPosition[X_INDEX])

            for z in range(CHUNK_SIZE):
                worldZ = getWorldIndex(z, initChunkPosition[Z_INDEX])
                worldHeight = getWorldHeight(worldX, worldZ)
                localHeight = min(worldHeight - initChunkPosition[Y_INDEX], CHUNK_SIZE)

                for y in range(localHeight):
                    worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])
                    worldArray[worldX, worldY, worldZ] = 1

    @staticmethod 
    @njit(cache = True)
    def checkFilled(worldArray, initChunkPosition):
        '''
        Check whether the chunk is filled for the brickmap
        '''
        for x in range(CHUNK_SIZE):
            worldX = getWorldIndex(x, initChunkPosition[X_INDEX])

            for y in range(CHUNK_SIZE):
                worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])

                for z in range(CHUNK_SIZE):
                    worldZ = getWorldIndex(z, initChunkPosition[Z_INDEX])

                    if worldArray[worldX, worldY, worldZ] != EMPTY_VOXEL:
                        return False 

        return True

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        self.generate(self.worldArray, self.initChunkPosition)