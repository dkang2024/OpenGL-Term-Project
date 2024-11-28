from Settings import *
from Window_Utils import *
from World_Utils import *
from World_Utils.Textures import Texture #Just because Pylance doesn't like working
import time 

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

        self.loadTextures()
        self.rayTracer = self.ctx.compute_shader(loadComputeShader(self.ctx, 'RayTracer', 'RayTracing'))
        self.initRenderer(10, 1, 0.01)

        self.ctx.gc_mode = 'auto'
        self.program = self.ctx.program(*loadVertexAndFrag('Window', 'Window', 'Window'))
        self.initScreen()
        self.initRand()

        self.camera = Camera(self, glm.vec3(278, 278, -200), 100, 60, 0.2)
        self.screenCoords = mglw.geometry.quad_fs(attr_names = screenNames, normals = False, name = 'Screen Coordinates')
        self.crosshair = Crosshair(self, 0.03, glm.vec3(1.0, 1.0, 1.0), self.window_size) #type: ignore
        self.world = World(self.ctx, self.rayTracer)

        red = LambertianMaterial(Texture(glm.vec3(.65, .05, .05)))
        white = LambertianMaterial(Texture(glm.vec3(.73, .73, .73)))
        green = LambertianMaterial(Texture(glm.vec3(.12, .45, .15)))
        light = PointLight(glm.vec3(15))
        materialBack = ReflectiveMaterial(glm.vec3(0.8, 0.8, 0.8), 0)
        earth = LambertianMaterial(Texture('Earth'))
        materialGround = LambertianMaterial(Texture(glm.vec3(0.8, 0.8, 0.0)))
        materialCenter = LambertianMaterial(Texture(glm.vec3(0.1, 0.2, 0.5)))
        materialLeft = DielectricMaterial(1.0 / 1.3)
        
        self.world.addHittable(Quad(glm.vec3(555, 0, 0), glm.vec3(0, 555, 0), glm.vec3(0, 0, 555), green))
        self.world.addHittable(Quad(glm.vec3(0, 0, 0), glm.vec3(0, 555, 0), glm.vec3(0, 0, 555), red))
        self.world.addHittable(Quad(glm.vec3(343, 554, 332), glm.vec3(-130, 0, 0), glm.vec3(0, 0, -105), light))
        self.world.addHittable(Quad(glm.vec3(0, 0, 0), glm.vec3(555, 0, 0), glm.vec3(0, 0, 555), white))
        self.world.addHittable(Quad(glm.vec3(555, 555, 555), glm.vec3(-555, 0, 0), glm.vec3(0, 0, -555), white))
        self.world.addHittable(Quad(glm.vec3(0, 0, 555), glm.vec3(555, 0, 0), glm.vec3(0, 555, 0), white))
        #self.world.addHittable(Sphere(glm.vec3(190, 90, 190), 90, materialLeft))
        
        self.world.addHittable(Cube(glm.vec3(130, 0, 65), glm.vec3(295, 165, 230), white))
        self.world.addHittable(Cube(glm.vec3(265, 0, 295), glm.vec3(430, 330, 460), materialBack))

        self.world.addHittable(Sphere(glm.vec3(0, 0, -1), 0, materialCenter))
        
        self.world.createRenderArray()
        self.world.assignRender()

    def initRenderer(self, maxBounces, samplesPerPixel, temporalReuseFactor):
        '''
        Initialize the quantities necessary for the renderer and pass them in (including the temporal reuse mix factor)
        '''
        self.rayTracer['maxBounces'] = maxBounces
        rootSPP = int(np.sqrt(samplesPerPixel))
        self.rayTracer['rootSPP'] = rootSPP 
        self.rayTracer['invRootSPP'] = 1 / rootSPP
        self.rayTracer['temporalReuseFactor'] = temporalReuseFactor
    
    def loadTexture(self, name):
        '''
        Load a specific texture into the ray tracer
        '''
        texture = self.load_texture_2d(name)
        texture.use(self.textureBind)
        self.textureBind += 1

    def loadTextures(self):
        '''
        Register the texture directory to moderngl window and load all the textures
        '''
        self.textureBind = 2
        mglw.resources.register_texture_dir(os.path.abspath('Textures'))
        self.loadTexture('Brick Wall.jpg')
        self.loadTexture('Earth.jpg')
           
    def initScreen(self):
        '''
        Initialize two screen textures so that the renderer can draw to the screen indirectly using the texture. Initialize two textures and cycle between them to enable TAA. Note that I have to do this manually without using a helper function because of OPENGL shenanigans
        '''
        self.screen1 = self.ctx.texture(self.window_size, 4, dtype = 'f4')
        self.screen1.filter = (mgl.NEAREST, mgl.NEAREST)
        self.screen1.bind_to_image(0)        
        self.screen1.use(0)       

        self.screen2 = self.ctx.texture(self.window_size, 4, dtype = 'f4')
        self.screen2.filter = (mgl.NEAREST, mgl.NEAREST)
        self.screen2.bind_to_image(1)
        self.screen2.use(1)

        self.frameCount = 0
        self.rayTracer['frameCount'] = self.frameCount
        self.program['frameCount'] = self.frameCount
     
    def initRand(self):
        '''
        Initialize the random number image in order to sample from to generate a seed for the random number generator in GLSL. 
        '''
        RandGen = np.random.default_rng()
        self.seed = RandGen.integers(128, 100000, (*self.window_size, 4), dtype = 'u4')
        self.seed = self.ctx.texture(self.window_size, 4, data = self.seed, dtype = 'u4')
        self.seed.bind_to_image(2)

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
        self.initRand()
        self.ctx.viewport = (0, 0, screenWidth, screenHeight)

    def updateFrameCount(self):
        '''
        Update the framecount uniform in OpenGL for TAA
        '''
        self.frameCount += 1
        self.rayTracer['frameCount'] = self.frameCount
        self.program['frameCount'] = self.frameCount

    def render(self, t, frameTime):
        '''
        Render the screen and display the fps
        '''
        self.ctx.clear()
        self.cameraMovementKeys()
        self.camera.render(frameTime)

        workgroupX, workgroupY = math.ceil(self.window_size[0] / 8), math.ceil(self.window_size[1] / 4)
        self.rayTracer.run(workgroupX, workgroupY)
        self.ctx.memory_barrier(mgl.SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.screenCoords.render(self.program)
        self.crosshair.render()
        
        self.updateFrameCount()
        self.camera.assignPrevRenderValues()
        if frameTime != 0:
            self.wnd.title = f'FPS: {1 / frameTime: .2f}'

if __name__ == '__main__':  
    Test.run() 