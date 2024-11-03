from Settings import *

class sceneWorld:
    '''
    Create the scene with a list of hittables that are passed as a Shader Storage Buffer Object (SSBO) to the ray tracing compute shader
    '''
    def __init__(self, ctx, rayTracer):
        self.ctx, self.rayTracer = ctx, rayTracer
        self.hittableList = []

    def addHittable(self, hittable):
        '''
        Add a hittable object to the list of hittables
        '''
        self.hittableList.append(hittable)

    def recordSphere(self, i, sphere):
        '''
        Record a sphere to the render array
        '''
        # (c_x, c_y, c_z, R, r, g, b)
        self.renderArray[i]['center'] = glm.vec4(sphere.center, 0)
        self.renderArray[i]['color'] = glm.vec4(sphere.color, 0)
        self.renderArray[i]['radius'] = sphere.radius 
        self.renderArray[i]['materialID'] = sphere.materialID
        self.renderArray[i]['materialParameter'] = sphere.materialParameter

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
            ('padding', 'f4') # 8 bytes
        ])

        self.renderArray = np.empty(len(self.hittableList), sphereDType)

        for i, hittable in enumerate(self.hittableList):
            self.recordSphere(i, hittable)
        
    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.rayTracer['numHittables'] = len(self.hittableList)
        
        self.ssbo = self.ctx.buffer(self.renderArray, dynamic = True)
        self.ssbo.bind_to_storage_buffer(0)