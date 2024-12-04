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
<<<<<<< HEAD
        isChunkEmpty = EMPTY_CHUNK
=======
>>>>>>> parent of 9557f96 (Changes)
        for x in prange(CHUNK_SIZE):
            worldX = getWorldIndex(x, initChunkPosition[X_INDEX])

            for z in range(CHUNK_SIZE):
                worldZ = getWorldIndex(z, initChunkPosition[Z_INDEX])
                elevation = heightMap[worldX, worldZ]

                worldHeight = getWorldHeight(elevation)
                localHeight = min(worldHeight - initChunkPosition[Y_INDEX], CHUNK_SIZE)

<<<<<<< HEAD
                if localHeight > 0:
                    isChunkEmpty = FILLED_CHUNK

=======
>>>>>>> parent of 9557f96 (Changes)
                for y in range(localHeight):
                    worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])
                    worldArray[worldX, worldY, worldZ] = 1

<<<<<<< HEAD
        return isChunkEmpty

=======
>>>>>>> parent of 9557f96 (Changes)
    def upload(self):
        '''
        Upload the chunk to the world array
        '''
<<<<<<< HEAD
        isChunkEmpty = self.generate(self.worldArray, self.heightMap, self.initChunkPosition)
        self.brickMap[self.worldChunkIndex[X_INDEX], self.worldChunkIndex[Y_INDEX], self.worldChunkIndex[Z_INDEX]] = isChunkEmpty
=======
        self.generate(self.worldArray, self.heightMap, self.initChunkPosition)
>>>>>>> parent of 9557f96 (Changes)
