from Settings import * 
 
@njit(cache = True)
def getWorldIndex(initChunkPosition, x, y, z):
    return initChunkPosition[0] + x, initChunkPosition[1] + y, initChunkPosition[2] + z

class Chunk:
    '''
    Create and render a chunk of blocks
    '''
    def __init__(self, worldArray, initChunkPosition):
        self.worldArray = worldArray 
        self.initChunkPosition = list(initChunkPosition)

    @staticmethod 
    @njit(parallel = True, cache = True)
    def uploadHelper(worldArray, initChunkPosition):
        '''
        Upload the chunk to the world array
        '''
        for x in prange(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    worldArray[getWorldIndex(initChunkPosition, x, y, z)] = 1

    def upload(self):
        '''
        Upload the chunk to the world array
        '''
        return self.uploadHelper(self.worldArray, self.initChunkPosition)