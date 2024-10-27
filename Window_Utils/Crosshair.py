from Loader import *

class windowCrosshair:
    '''
    Class for drawing a crosshair on the screen 
    '''
    def __init__(self, app, size, color, windowSize):
        self.app, self.size, self.ctx = app, size, app.ctx

        self.createProgram(color)
        self.createVAO(windowSize)
            
    def createProgram(self, color):
        '''
        Create the program from the crosshair's vertex and fragment shader and attach it to the window's context
        '''    
        self.program = self.ctx.program(*loadVertexAndFrag('Crosshair', 'Crosshair', 'Crosshair'))
        self.program['color'] = color

    def resizeCrosshair(self, windowSize):
        '''
        Resize the crosshair according to the window size
        '''
        self.createVAO(windowSize)

    def createVAO(self, windowSize):
        '''
        Create the crosshair's VAO for rendering
        '''
        xSize = self.size / windowSize[0] * windowSize[1] #Calculate by dividing by the aspect ratio
        vertices = np.array([
            (-xSize, 0),
            (xSize, 0),
            (0, -self.size),
            (0, self.size)
        ], dtype = np.float32)
        vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(self.program, [(vbo, '2f', 'vertexPosition')])

    def render(self):
        '''
        Render the crosshair on the screen
        '''
        self.vao.render(mgl.LINES)