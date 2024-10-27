from Settings import *

class crosshair:
    '''
    Class for drawing a crosshair on the screen 
    '''
    def __init__(self, app, width, length, color):
        self.ctx = app.ctx 

        self.vertical = mglw.geometry.quad_2d(size = (width, length), pos = (0.5, 0.5), normals = False, uvs = False)
        self.horizontal = mglw.geometry.quad_2d(size = (length, width), pos = (0.5, 0.5), normals = False, uvs = False)
        self.color = color 



    def render(self):
        '''
        Render the crosshair on the screen
        '''