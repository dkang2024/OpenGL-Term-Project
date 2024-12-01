from Settings import *
from Objects import *
from Materials import *
from World_Utils.Textures import Texture

class World:
    '''
    Create the scene with a list of hittables that are passed as a Shader Storage Buffer Object (SSBO) to the ray tracing compute shader
    '''
    def __init__(self, ctx, rayTracer):
        self.ctx, self.rayTracer = ctx, rayTracer

        self.worldSize = [256] * 3
        self.worldArray = np.zeros(self.worldSize, 'u1')

        defaultBlock = 1
        self.worldArray[0, 0, 0] = defaultBlock
        self.worldArray[1, 1, 1] = defaultBlock 
        self.worldArray[1, 0, 0] = defaultBlock 
        self.worldArray[0, 1, 0] = 2

        self.materialList = []
        self.materialList.append(LambertianMaterial(Texture('Grass')))
        self.materialList.append(DielectricMaterial(1 / 1.5))
        
        self.lights = []

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