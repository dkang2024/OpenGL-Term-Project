from Settings import *
from Chunk import *
from Materials import *
from World_Utils.Textures import Texture

class World:
    '''
    Create the scene with a list of hittables that are passed as a Shader Storage Buffer Object (SSBO) to the ray tracing compute shader
    '''
    def __init__(self, ctx, rayTracer):
        self.ctx, self.rayTracer = ctx, rayTracer

        self.worldSize = [WORLD_SIZE_XZ * CHUNK_SIZE, WORLD_SIZE_Y * CHUNK_SIZE, WORLD_SIZE_XZ * CHUNK_SIZE]
        self.worldArray = np.zeros(self.worldSize, 'u1')

        self.chunkList = []
        self.generateChunks()

        self.materialList = []
        self.materialList.append(LambertianMaterial(Texture('Grass')))
        self.materialList.append(LambertianMaterial(Texture('Dirt')))
        self.materialList.append(DielectricMaterial(Texture(glm.vec3(0.3, 0.8, 0.3)), 1 / 1.5))
        self.materialList.append(ReflectiveMaterial(Texture(glm.vec3(0.5, 0.7, 0.5)), 0.1))
        
        self.lights = []

    @staticmethod
    @njit(cache = True)
    def convertWorldIndexToPosition(worldIndex):
        return (worldIndex[X_INDEX] * CHUNK_SIZE, worldIndex[Y_INDEX] * CHUNK_SIZE, worldIndex[Z_INDEX] * CHUNK_SIZE)

    def generateChunks(self):
        for worldXIndex in range(WORLD_SIZE_XZ):
            for worldYIndex in range(WORLD_SIZE_Y):
                for worldZIndex in range(WORLD_SIZE_XZ):
                    chunkIndex = (worldXIndex, worldYIndex, worldZIndex)
                    chunkPosition = self.convertWorldIndexToPosition(chunkIndex)
                    
                    chunk = Chunk(self.worldArray, chunkIndex, chunkPosition)
                    self.chunkList.append(chunk)
                    chunk.upload()
                
    def assignMaterials(self):
        materialDType = np.dtype([
            ('color', 'f4', 3),
            ('materialID', 'i4'),
            ('materialParameter', 'f4'),
            ('textureID', 'i4'),
            ('padding', 'f4', 2)
        ])

        self.materialArray = np.empty(len(self.materialList), materialDType)

        for i, material in enumerate(self.materialList):
            material.record(self.materialArray, i)

        self.materials = self.ctx.buffer(self.materialArray)
        self.materials.bind_to_storage_buffer(0)

    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.assignMaterials()

        self.world = self.ctx.texture3d(self.worldSize, 1, self.worldArray, dtype = 'u1')
        self.world.bind_to_image(2)

        self.rayTracer['numLights'] = len(self.lights)