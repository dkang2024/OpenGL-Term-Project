from Settings import *
from Window_Utils import *
from World_Utils import *

class screenNames:
    POSITION = 'vertexPosition'
    TEXCOORD_0 = 'uv'

class Test(mglw.WindowConfig):
    resizable = True 
    aspect_ratio = None 
    gl_version = (4, 6)
    cursor = False 
    vsync = False 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.fullscreen_key = self.wnd.keys.F12
        self.wnd.mouse_exclusivity = True 

        self.ctx.gc_mode = 'auto'
        self.program = self.ctx.program(*loadVertexAndFrag('Window', 'Window', 'Window'))
        self.initScreen()
        self.rayTracer = self.ctx.compute_shader(loadComputeShader(self.ctx, 'RayTracer', 'RayTracing'))

        self.camera = viewerCamera(self, glm.vec3(0, 0, 0), 1, 60, 0.2)
        self.screenCoords = mglw.geometry.quad_fs(attr_names = screenNames, normals = False, name = 'Screen Coordinates')
        self.crosshair = windowCrosshair(self, 0.03, glm.vec3(1.0, 1.0, 1.0), self.window_size) #type: ignore

        self.world = sceneWorld(self.ctx, self.rayTracer)
        self.world.addHittable(sphere3(glm.vec3(0, 0, -1), 0.5, glm.vec4(1, 0, 0, 1)))
        self.world.addHittable(sphere3(glm.vec3(0, -100.5, -1), 100, glm.vec4(0, 1, 0, 1)))
        self.world.assignRender()
     
    def initScreen(self):
        '''
        Initialize the screen texture to draw to so that the compute shader can "render" to the screen indirectly
        '''
        self.screen = self.ctx.texture(self.window_size, 4, dtype = 'f4')
        self.screen.filter = (mgl.NEAREST, mgl.NEAREST)
        self.screen.bind_to_image(0)        
        self.screen.use(0)

    def cameraMovementKeys(self):
        '''
        If statements to deal with setting camera movement directions. Utilizing the built in key_event function resulted in jank movement (it's much better suited to key presses rather than holds). It also made the camera pretty unresponsive. 
        '''
        if self.wnd.is_key_pressed(self.wnd.keys.W):
            self.camera.dirZ = -1 
        elif self.wnd.is_key_pressed(self.wnd.keys.S): 
            self.camera.dirZ = 1
        else:
            self.camera.dirZ = 0
        
        if self.wnd.is_key_pressed(self.wnd.keys.A):
            self.camera.dirX = -1 
        elif self.wnd.is_key_pressed(self.wnd.keys.D): 
            self.camera.dirX = 1 
        else:
            self.camera.dirX = 0
        
        if self.wnd.is_key_pressed(self.wnd.keys.SPACE): 
            self.camera.dirY = self.camera.movingDown
        else:
            self.camera.dirY = 0

    def key_event(self, key, action, modifiers):
        '''
        Set the camera to be moving down if you're pressing / holding shift
        '''
        if modifiers.shift:
            self.camera.movingDown = -1
        else:
            self.camera.movingDown = 1

        if self.wnd.is_key_pressed(self.wnd.keys.F1):
            self.wnd.mouse_exclusivity = not self.wnd.mouse_exclusivity
            self.wnd.cursor = not self.wnd.cursor
        
    def mouse_position_event(self, mouseX, mouseY, dx, dy):
        self.camera.updateMouse(dx, -dy) 

    def resize(self, screenWidth, screenHeight):
        '''
        Resize the texture to fit the bigger screen and reset viewport dimensions (prevents weird screen shenanigans)
        '''
        self.window_size = (screenWidth, screenHeight)
        self.crosshair.resizeCrosshair(self.window_size)
        self.initScreen()
        self.ctx.viewport = (0, 0, screenWidth, screenHeight)

    def render(self, time, frameTime):
        '''
        Render the screen and display the fps
        '''
        self.ctx.clear()
        self.cameraMovementKeys()
        self.camera.render(frameTime)
       
        self.rayTracer.run(math.ceil(self.window_size[0] / 8), math.ceil(self.window_size[1] / 4))
        self.ctx.memory_barrier(mgl.SHADER_IMAGE_ACCESS_BARRIER_BIT)
        self.screenCoords.render(self.program)

        self.crosshair.render()
        
        if frameTime != 0:
            self.wnd.title = f'FPS: {1 / frameTime: .2f}'

if __name__ == '__main__':  
    Test.run() 