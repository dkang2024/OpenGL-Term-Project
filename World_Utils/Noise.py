from Settings import *

@njit(cache = True)
def shift(value):
    '''
    Shift from [-1, 1] to [0, 1]
    '''
    return (value + 1) / 2

@njit(cache = True)
def convertToNormalized(position, worldSize):
    '''
    Convert the world position to [0, 1] for inputting into simplex noise 
    '''
    return position / (worldSize - 1)

@njit(cache = True)
def applyHeightRedistribution(elevation, fudgeFactor, redistribution):
    '''
    Apply height redistribution to make the valleys steeper or shallower
    '''
    return (elevation * fudgeFactor) ** redistribution

def generateHeightMap():
    '''
    Generate a height map given all the possible x coordinates and z coordinates
    '''
    worldSize = CHUNK_SIZE * WORLD_SIZE_XZ
    xCoords = zCoords = convertToNormalized(np.arange(worldSize), worldSize)

    NUM_OCTAVES, FUDGE_FACTOR, REDISTRIBUTION = 15, 1.2, 2.2

    elevation = np.zeros((worldSize, worldSize))
    amplitude, frequency, sumAmplitude = 1, 3, 0
    for _ in range(NUM_OCTAVES):
        elevation += amplitude * shift(generator.noise2array(xCoords * frequency, zCoords * frequency))
        sumAmplitude += amplitude 

        amplitude *= 0.5
        frequency *= 2
    
    elevation /= sumAmplitude
    elevation = applyHeightRedistribution(elevation, FUDGE_FACTOR, REDISTRIBUTION)

    return elevation