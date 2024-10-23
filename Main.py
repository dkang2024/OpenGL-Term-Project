from Camera import *

import moderngl_window as mglw
import math 
import moderngl as mgl 

class screenNames:
    POSITION = 'vertexPosition'
    TEXCOORD_0 = 'uv'

class Test(mglw.WindowConfig):
    resizable = True 
    aspect_ratio = None 
    gl_version = (4, 6)
    cursor = True  
    vsync = False 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.fullscreen_key = self.wnd.keys.F

        self.ctx.gc_mode = 'auto'
        self.camera = Camera(self, glm.vec3(0, 0, 0), 0.1, 60, glm.vec3(0, 0, -1))

        self.program = self.ctx.program(*self.loadWindow())
        self.initScreen()
        self.rayTracer = self.ctx.compute_shader(self.loadRayTracer())

        self.screenCoords = mglw.geometry.quad_fs(attr_names = screenNames, normals = False, name = 'Screen Coordinates')

    @staticmethod
    def loadWindow():
        '''
        Load the vertex and fragment shader
        '''
        with open('Shaders/Window.vert', 'r') as file:
            vertexShader = file.read()
        with open('Shaders/Window.frag', 'r') as file:
            fragmentShader = file.read()
        return vertexShader, fragmentShader

    @staticmethod 
    def removeComments(rayTracer):
        '''
        Remove the comments from the ray tracer to avoid any shenanigans with "import" statements in comments
        '''
        return [line for line in rayTracer if not line.startswith('//')]
    
    @staticmethod 
    def addImports(rayTracer):
        '''
        Add the imports from the 'import' statements in the rayTracer into the string
        '''
        for i, line in enumerate(rayTracer):
            if not line.startswith('import'):
                continue 
            
            importFileName = line[len('import') + 1:].strip()
            try: 
                with open(f'Shaders/{importFileName}.comp', 'r') as file:
                    rayTracer[i] = file.read().strip()
            except:
                raise RuntimeError('This file does not exist')

    def loadRayTracer(self):
        '''
        Load the ray tracing compute shader along with the other compute shaders beforehand to allow cleaner abstractions
        '''
        with open('Shaders/RayTracing.comp', 'r') as file:
            rayTracer = file.read().strip().split('\n')

        rayTracer = self.removeComments(rayTracer)
        self.addImports(rayTracer)
        return '\n'.join(rayTracer) 
        
    def initScreen(self):
        '''
        Initialize the screen texture to draw to so that the compute shader can "render" to the screen indirectly
        '''
        self.screen = self.ctx.texture(self.window_size, 2, dtype = 'f4')
        self.screen.repeat_x, self.screen.repeat_y = False, False 
        self.screen.bind_to_image(0)        
        self.screen.use(0)

    def cameraMovementKeys(self, key, modifiers, isPress: int):
        '''
        If statements to deal with setting camera movement directions. isPress is 1 or -1 (with 1 being it's a key press, and -1 being a key release in order to reverse direction)
        '''
        if key == self.wnd.keys.W:
            self.camera.dirZ = -1 * isPress  
        elif key == self.wnd.keys.S: 
            self.camera.dirZ = 1 * isPress
        
        if key == self.wnd.keys.A:
            self.camera.dirX = -1 * isPress
        elif key == self.wnd.keys.D: 
            self.camera.dirX = 1 * isPress
        
        if key == self.wnd.keys.SPACE and not modifiers.shift: 
            self.camera.dirZ = 1 * isPress
        elif key == self.wnd.keys.SPACE and modifiers.shift:
            self.camera.dirZ = -1 * isPress

    def key_event(self, key, action, modifiers):
        '''
        Move the camera based on the keys 
        '''
        if action == self.wnd.keys.ACTION_PRESS: 
            self.cameraMovementKeys(key, modifiers, 1)
        else: 
            self.cameraMovementKeys(key, modifiers, -1)
    
        self.camera.moveCamera()
        
    def mouse_position_event(self, mouseX, mouseY, dx, dy):

        self.camera.updateMouse(mouseX, mouseY)
        
    def resize(self, screenWidth, screenHeight):
        '''
        Resize the texture to fit the bigger screen and reset viewport. 
        '''
        self.window_size = (screenWidth, screenHeight)
        self.initScreen()
        self.ctx.viewport = (0, 0, screenWidth, screenHeight)

    def render(self, time, frameTime):
        '''
        Render the screen and display the fps
        '''
        self.ctx.clear()

        self.rayTracer.run(math.ceil(self.window_size[0] / 8), math.ceil(self.window_size[1] / 4))
        self.ctx.memory_barrier()
        self.screenCoords.render(self.program)
         
        if frameTime != 0:
            self.wnd.title = f'FPS: {1 / frameTime: .2f}'

if __name__ == '__main__':  
    Test.run()