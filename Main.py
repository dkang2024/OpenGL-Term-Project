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
    def loadRayTracer():
        '''
        Load the ray tracing compute shader
        '''
        with open('Shaders/RayTracing.comp', 'r') as file:
            return file.read()
        
    def initScreen(self):
        '''
        Initialize the screen texture to draw to so that the compute shader can "render" to the screen indirectly
        '''
        self.screen = self.ctx.texture(self.window_size, 2, dtype = 'f4')
        self.screen.repeat_x, self.screen.repeat_y = False, False 
        self.screen.bind_to_image(0)        
        self.screen.use(0)
        
    def resize(self, screenWidth, screenHeight):
        '''
        Resize the texture to fit the bigger screen and reset viewport. 
        '''
        self.window_size = (screenWidth, screenHeight)
        self.initScreen()
        self.ctx.viewport = (0, 0, screenWidth, screenHeight)

    def render(self, time, frameTime):
        self.ctx.clear()

        self.rayTracer.run(math.ceil(self.window_size[0] / 8), math.ceil(self.window_size[1] / 4))
        self.ctx.memory_barrier()
        self.screenCoords.render(self.program)
         
        if frameTime != 0:
            self.wnd.title = f'FPS: {1 / frameTime: .2f}'
            
Test.run()