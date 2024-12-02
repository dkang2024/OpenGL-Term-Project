from Settings import *
from Noise import *
 
@njit(cache = True)
def getWorldIndex(position, initChunkPosition):
    '''
    Get the world position from the current position and the smallest init chunk position
    '''
    return position + initChunkPosition

@njit(cache = True)
def convertToNormalized(position):
    '''
    Convert the world position to [-1, 1] for inputting into simplex noise 
    '''
    return position / WORLD_SIZE_XZ - 0.5

@njit(cache = True)
def getWorldElevation(x, z):
    '''
    Simplex noise world generation with help from https://www.redblobgames.com/maps/terrain-from-noise/
    '''
    x, z = convertToNormalized(x), convertToNormalized(z)

    NUM_OCTAVES, FUDGE_FACTOR, REDISTRIBUTION = 15, 1.2, 0.6

    elevation, amplitude, frequency, sumAmplitude = 0, 1, 0.1, 0
    for _ in range(NUM_OCTAVES):
        elevation += amplitude * noise2(x * frequency, z * frequency)
        sumAmplitude += amplitude 

        amplitude *= 0.5
        frequency *= 2
    
    elevation /= sumAmplitude 
    elevation = (elevation * FUDGE_FACTOR) ** REDISTRIBUTION

    return elevation

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
                elevation = getWorldElevation(worldX, worldZ)

                worldHeight = getWorldHeight(elevation)
                localHeight = min(worldHeight - initChunkPosition[Y_INDEX], CHUNK_SIZE)

                for y in range(localHeight):
                    worldY = getWorldIndex(y, initChunkPosition[Y_INDEX])
                    worldArray[worldX, worldY, worldZ] = 1

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        self.generate(self.worldArray, self.initChunkPosition)