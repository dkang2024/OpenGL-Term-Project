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
        self.renderArray[i]['center'] = sphere.center
        self.renderArray[i]['radius'] = sphere.radius 
        self.renderArray[i]['color'] = sphere.color

    def createRenderArray(self):
        '''
        Create the render array from the current hittable list by passing in the specific values for the SSBO 
        '''
        # (c_x, c_y, c_z, R, r, g, b, a). Use the alpha in order to prevent the necessity of padding
        sphereDType = np.dtype([
            ('center', 'f4', 3),
            ('radius', 'f4'),
            ('color', 'f4', 4)
        ])

        self.renderArray = np.empty(len(self.hittableList), sphereDType)

        for i, hittable in enumerate(self.hittableList):
            self.recordSphere(i, hittable)
        
    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.createRenderArray()
        self.rayTracer['numHittables'] = len(self.hittableList)
        
        self.ssbo = self.ctx.buffer(self.renderArray)
        self.ssbo.bind_to_storage_buffer()