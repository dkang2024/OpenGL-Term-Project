import moderngl_window as mglw
import moderngl as mgl 
import numpy as np

class Object: 
    def __init__(self, app):
        self.app = app 
        self.ctx = app.ctx 
    
    def getShaders(self, shaderName):
        with open(f'Shaders/{shaderName}.vert', 'r') as file:
            vertexShader = file.read()
        with open(f'Shaders/{shaderName}.frag', 'r') as file:
            fragmentShader = file.read()
        return vertexShader, fragmentShader 

class Triangle(Object):
    def __init__(self, app):
        super().__init__(app)

        #x, y, z, r, g, b
        self.vertices = ( 
            (-0.5, -0.5, -0.5, 1, 0, 0), 
            (0.0, 0.0, 0.0, 0, 1, 0), 
            (0.5, 0.5, 0.5, 0, 0, 1)
        )
        self.vertices = np.array(self.vertices, np.float32)

        self.vbo = self.ctx.buffer(self.vertices)
        self.numVertices = 3 