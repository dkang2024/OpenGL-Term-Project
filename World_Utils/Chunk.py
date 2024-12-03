from Settings import *
from Noise import *
 
@njit(cache = True)
def getWorldIndex(position, initChunkPosition):
    '''
    Get the world position from the current position and the smallest init chunk position
    '''
    return position + initChunkPosition

@njit(cache = True)
def getWorldHeight(elevation):
    '''
    Convert elevation to world height
    '''
    return int(elevation * CHUNK_SIZE * WORLD_SIZE_Y)

class Chunk:
    '''
    Create and render a chunk of blocks
    '''
    def __init__(self, worldArray, heightMap, brickmapPosition, initChunkPosition):
        self.worldArray, self.heightMap = worldArray, heightMap
        self.brickmapPosition, self.initChunkPosition = brickmapPosition, initChunkPosition

    @staticmethod 
    @njit(parallel = True, nogil = True, cache = True)
    def generate(worldArray, heightMap, initChunkPosition):
        '''
        Upload and generate the chunk to the world array
        '''
        for x in prange(CHUNK_SIZE):
            worldX = getWorldIndex(x, initChunkPosition[X_INDEX])

            for z in range(CHUNK_SIZE):
                worldZ = getWorldIndex(z, initChunkPosition[Z_INDEX])
                elevation = heightMap[worldX, worldZ]

                worldHeight = getWorldHeight(elevation)
                localHeight = min(worldHeight - initChunkPosition[Y_INDEX], CHUNK_SIZE)

                for y in range(localHeight):
                    worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])
                    worldArray[worldX, worldY, worldZ] = 1

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        self.generate(self.worldArray, self.heightMap, self.initChunkPosition)