from Loader import *

class cubeNames: 
    POSITION = 'vertexPosition'

class Cube:
    '''
    Class for drawing a cube on screen (that we're holding)
    '''
    def __init__(self, app, center, size):
        self.app, self.size, self.center, self.ctx, self.camera, self.world = app, size, center, app.ctx, app.camera, app.world

        self.createProgram()
        self.createVAO()
            
    def createProgram(self):
        '''
        Create the program from the cube's vertex and fragment shader and attach it to the window's context
        '''    
        self.program = self.ctx.program(*loadVertexAndFrag('Cube', 'Cube', 'Cube'))
        self.program['cubeCenter'] = self.center

    def createVAO(self):
        '''
        Create the VAO for the cube to render 
        '''
        self.vao = mglw.geometry.cube(center = self.center, size = glm.vec3(self.size), attr_names = cubeNames, normals = False, uvs = False, name = 'Cube Held')

    def assignCameraProj(self):
        '''
        Send in the camera's projection matrix to the renderer 
        '''
        self.program['proj'].write(self.camera.calculateProjMat())

    def render(self):
        '''
        Render the cube on the screen 
        '''
        self.assignCameraProj()
        self.program['voxelID'] = self.world.voxelPlaceID
        self.vao.render(self.program)