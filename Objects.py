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
            (-0.6, -0.8, 0.0, 1.0, 0.0, 0.0), 
            (0.6, -0.8, 0.0, 0.0, 1.0, 0.0),
            (0.0, 0.8, 0.0, 0.0, 0.0, 1.0)
        )
        self.numVertices = 3 
        self.vertices = np.array(self.vertices, np.float32)

        self.program = self.ctx.program(*self.getShaders('Default'))

        self.vbo = self.ctx.buffer(self.vertices)
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f 3f', 'vertexPosition', 'vertexColor')])

    def render(self):
        self.vao.render()