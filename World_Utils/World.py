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

        self.sphereList, self.quadList, self.lightList = [], [], []

    def addHittable(self, hittable):
        '''
        Add a hittable object to the list of hittables
        '''
        if isinstance(hittable, Sphere):
            self.sphereList.append(hittable)
        elif isinstance(hittable, Quad) and not isinstance(hittable.material, PointLight):
            self.quadList.append(hittable)
        elif isinstance(hittable, Quad):
            self.lightList.append(hittable)
        else:
            self.quadList = self.quadList + hittable.quads

    @staticmethod
    def recordToRender(objectList, dType):
        '''
        Record the object list in an array with a dtype specified
        '''
        objectArray = np.empty(len(objectList), dType)
        for i, hittable in enumerate(objectList):
            hittable.record(objectArray, i)
        return objectArray
        
    def createRenderArray(self):
        '''
        Create the render array from the current hittable list by passing in the specific values for the SSBO 
        '''
        sphereDType = np.dtype([ #Multiple of 16 bytes
            ('center', 'f4', 3), # 16 bytes
            ('radius', 'f4'), # 4 bytes
            ('color', 'f4', 3), # 16 bytes   
            ('materialID', 'i4'), # 4 bytes
            ('materialParameter', 'f4'), # 4 bytes
            ('textureID', 'i4'), # 4 bytes
            ('padding', 'f4', 2)
        ])
        self.sphereArray = self.recordToRender(self.sphereList, sphereDType)
        
        quadDType = np.dtype([
            ('point', 'f4', 3),
            ('area', 'f4'),
            ('side1', 'f4', 3),
            ('D', 'f4'), 
            ('side2', 'f4', 3),
            ('materialID', 'i4'),
            ('color', 'f4', 3),
            ('materialParameter', 'f4'),
            ('normalVector', 'f4', 3),
            ('textureID', 'i4'),
            ('W', 'f4', 3),
            ('padding', 'f4')    
        ])
        self.quadArray = self.recordToRender(self.quadList, quadDType)
        self.lightArray = self.recordToRender(self.lightList, quadDType)

    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.materials = self.ctx.buffer(self.materialArray)
        self.materials.bind_to_storage_buffer(0)

        self.world = self.ctx.texture3d((256, 256, 256), 4, self.worldArray, dtype = 'f4')
        self.world.bind_to_image(2)

        self.rayTracer['numSpheres'] = 0
        self.spheres = self.ctx.buffer(self.sphereArray)
        self.spheres.bind_to_storage_buffer(1)

        self.rayTracer['numQuads'] = 0
        self.quads = self.ctx.buffer(self.quadArray)
        self.quads.bind_to_storage_buffer(2)

        self.rayTracer['numLights'] = 0
        self.lights = self.ctx.buffer(self.lightArray)
        self.lights.bind_to_storage_buffer(3)