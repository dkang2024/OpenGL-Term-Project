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
    # amplitude
    a = 2
    
    height, aSum = 0, 0
    for _ in range(5):
        a /= 2
        aSum += a
        height += a * noise2(x / a, z / a)
    height /= aSum 

    return height ** 0.27

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
                elevation = getWorldHeight(worldX, worldZ)

                worldHeight = int(elevation * WORLD_SIZE_Y * CHUNK_SIZE)
                localHeight = min(worldHeight - initChunkPosition[Y_INDEX], CHUNK_SIZE)

                for y in range(localHeight):
                    worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])
                    worldArray[worldX, worldY, worldZ] = 1

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        self.generate(self.worldArray, self.initChunkPosition)