from Settings import *
from Objects import *

class World:
    '''
    Create the scene with a list of hittables that are passed as a Shader Storage Buffer Object (SSBO) to the ray tracing compute shader
    '''
    def __init__(self, ctx, rayTracer):
        self.ctx, self.rayTracer = ctx, rayTracer
        self.sphereList, self.quadList = [], []

    def addHittable(self, hittable):
        '''
        Add a hittable object to the list of hittables
        '''
        if isinstance(hittable, Sphere):
            self.sphereList.append(hittable)
        else:
            self.quadList.append(hittable)

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
            ('center', 'f4', 4), # 16 bytes
            ('color', 'f4', 4), # 16 bytes
            ('radius', 'f4'), # 4 bytes
            ('materialID', 'i4'), # 4 bytes
            ('materialParameter', 'f4'), # 4 bytes
            ('textureID', 'i4') # 4 bytes
        ])
        self.sphereArray = self.recordToRender(self.sphereList, sphereDType)
        
        quadDType = np.dtype([
            ('point', 'f4', 4),
            ('side1', 'f4', 4),
            ('side2', 'f4', 4),
            ('color', 'f4', 4),
            ('normalVector', 'f4', 4),
            ('W', 'f4', 4),
            ('D', 'f4'), 
            ('materialID', 'i4'),
            ('materialParameter', 'f4'),
            ('textureID', 'i4')
        ])
        self.quadArray = self.recordToRender(self.quadList, quadDType)

    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.rayTracer['numSpheres'] = len(self.sphereList)
        self.spheres = self.ctx.buffer(self.sphereArray)
        self.spheres.bind_to_storage_buffer(0)

        self.rayTracer['numQuads'] = len(self.quadList)
        self.quads = self.ctx.buffer(self.quadArray)
        self.quads.bind_to_storage_buffer(1)
        self.rayTracer['numQuads'] = 0