from Settings import *
from Objects import *
from Materials import *

class World:
    '''
    Create the scene with a list of hittables that are passed as a Shader Storage Buffer Object (SSBO) to the ray tracing compute shader
    '''
    def __init__(self, ctx, rayTracer):
        self.ctx, self.rayTracer = ctx, rayTracer

        self.worldArray = np.zeros((256, 256, 256, 4), 'f4')
        self.worldArray[0, 0, 0] = (1, 1, 1, 1)
        self.worldArray[1, 1, 1] = (1, 1, 1, 1)

        materialDType = np.dtype([
            ('color', 'f4', 3),
            ('materialID', 'i4'),
            ('materialParameter', 'f4'),
            ('textureID', 'i4'),
            ('padding', 'f4', 2)
        ])
        self.materialArray = np.empty(1, materialDType)
        self.materialArray[0]['color'] = glm.vec3(1, 0, 0)
        self.materialArray[0]['materialID'] = 0
        self.materialArray[0]['textureID'] = 0

        self.lights = []

    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.materials = self.ctx.buffer(self.materialArray)
        self.materials.bind_to_storage_buffer(0)

        self.world = self.ctx.texture3d((256, 256, 256), 4, self.worldArray, dtype = 'f4')
        self.world.bind_to_image(2)

        self.rayTracer['numLights'] = -10