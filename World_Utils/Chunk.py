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

@njit(cache = True)
def normalizeToElevation(elevation, rand):
    '''
    Normalize to elevation for smoother transitions between states
    '''
    return elevation * rand 

@njit(cache = True)
def decideVoxel(elevation, rand):
    '''
    Decide what the voxel should be depending on the elevation and a random number
    '''
    if elevation < 0.1:
        return STONE 
    elif elevation < 0.15:
        if normalizeToElevation(elevation, rand) > 0.05:
            return STONE
        return CLAY
    elif elevation < 0.25:
        if normalizeToElevation(elevation, rand) > 0.12:
            return CLAY
        return SAND
    elif elevation < 0.55:
        if normalizeToElevation(elevation, rand) > 0.35:
            return DIRT
        return GRASS
    elif elevation < 0.7:
        if normalizeToElevation(elevation, rand) > 0.45:
            return SNOW 
        return DIRT 
    return SNOW

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
                    elevation = convertToNormalized(worldY, CHUNK_SIZE * WORLD_SIZE_Y)

                    worldArray[worldX, worldY, worldZ] = decideVoxel(elevation, np.random.rand(1))

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        self.generate(self.worldArray, self.heightMap, self.initChunkPosition)
