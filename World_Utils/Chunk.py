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
    def __init__(self, worldArray, brickMap, heightMap, worldChunkIndex):
        self.worldArray, self.brickMap, self.heightMap = worldArray, brickMap, heightMap
        self.worldChunkIndex, self.initChunkPosition = worldChunkIndex, self.convertWorldIndexToPosition(worldChunkIndex)

    @staticmethod
    @njit(cache = True)
    def convertWorldIndexToPosition(worldIndex):
        return (worldIndex[X_INDEX] * CHUNK_SIZE, worldIndex[Y_INDEX] * CHUNK_SIZE, worldIndex[Z_INDEX] * CHUNK_SIZE)

    @staticmethod 
    @njit(parallel = True, nogil = True, cache = True)
    def generate(worldArray, heightMap, initChunkPosition):
        '''
        Upload and generate the chunk to the world array (also return if the chunk is filled at all for the brickmap)
        '''
        isChunkEmpty = EMPTY_CHUNK
        for x in prange(CHUNK_SIZE):
            worldX = getWorldIndex(x, initChunkPosition[X_INDEX])

            for z in range(CHUNK_SIZE):
                worldZ = getWorldIndex(z, initChunkPosition[Z_INDEX])
                elevation = heightMap[worldX, worldZ]

                worldHeight = getWorldHeight(elevation)
                localHeight = min(worldHeight - initChunkPosition[Y_INDEX], CHUNK_SIZE)

                if localHeight > 0:
                    isChunkEmpty = FILLED_CHUNK

                for y in range(localHeight):
                    worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])
                    
                    worldArray[worldX, worldY, worldZ] = 1

        return isChunkEmpty

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        isChunkEmpty = self.generate(self.worldArray, self.heightMap, self.initChunkPosition)
        self.brickMap[self.worldChunkIndex[X_INDEX], self.worldChunkIndex[Y_INDEX], self.worldChunkIndex[Z_INDEX]] = isChunkEmpty