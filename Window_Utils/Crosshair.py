from Settings import *
from Loader import *

class crosshair:
    '''
    Class for drawing a crosshair on the screen 
    '''
    def __init__(self, app, width, length, color):
        self.vertical = mglw.geometry.quad_2d(size = (width, length), pos = (0, 0), normals = False, uvs = False)
        self.horizontal = mglw.geometry.quad_2d(size = (length, width), pos = (0, 0), normals = False, uvs = False)

        self.program = app.ctx.program(*loadVertexAndFrag('Crosshair', 'Crosshair', 'Crosshair'))
        self.program['color'] = color

    def render(self):
        '''
        Render the crosshair on the screen
        '''
        self.horizontal.render(self.program)
        self.vertical.render(self.program)