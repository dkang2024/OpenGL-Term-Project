from Settings import *
from Window_Utils import *
from World_Utils import *
from World_Utils.Textures import Texture #Just because Pylance doesn't like working

class screenNames:
    POSITION = 'vertexPosition'
    TEXCOORD_0 = 'uv'

class Window(mglw.WindowConfig):
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
        self.initRenderer(10, 1, 0.01, 25, 10, VIEW_RANGE, 1)

        self.ctx.gc_mode = 'auto'
        self.ctx.enable(mgl.CULL_FACE)
        self.program = self.ctx.program(*loadVertexAndFrag('Window', 'Window', 'Window'))
        self.initScreen()
        self.initRand()

        worldSize = WORLD_SIZE_XZ * CHUNK_SIZE
        #self.camera = Camera(self, glm.vec3(0, 0, -1), 20, 60, 0.2)
        self.camera = Camera(self, glm.vec3(worldSize // 2, WORLD_CENTER_Y * 2, worldSize // 2), 20, 60, 0.2)
        self.screenCoords = mglw.geometry.quad_fs(attr_names = screenNames, normals = False, name = 'Screen Coordinates')
        self.world = World(self.ctx, self.rayTracer, self.camera)

        self.crosshair = Crosshair(self, 0.03, glm.vec3(1), self.window_size) #type: ignore
        self.cube = Cube(self, glm.vec3(1.2, -0.7, -1.5), 0.5) #type: ignore
        self.numberKeys = list(range(self.wnd.keys.NUMBER_1, self.wnd.keys.NUMBER_9 + 1))
        self.showUI = True 

        self.world.setTime(TIME_DAY)
        self.world.assignRender()

    def initRenderer(self, maxBounces, samplesPerPixel, temporalReuseFactor, temporalBlendReduction, badLightSamples, maxRaySteps, neighborhoodSize):
        '''
        Initialize the quantities necessary for the renderer and pass them in (including the temporal reuse mix factor)
        '''
        self.rayTracer['maxBounces'] = maxBounces
        rootSPP = int(np.sqrt(samplesPerPixel))
        self.rayTracer['rootSPP'] = rootSPP 
        self.rayTracer['invRootSPP'] = 1 / rootSPP
        self.rayTracer['temporalReuseFactor'] = temporalReuseFactor
        self.rayTracer['temporalBlendReduction'] = temporalBlendReduction
        self.rayTracer['badLightSamples'] = badLightSamples
        self.rayTracer['maxRaySteps'] = maxRaySteps
        self.rayTracer['neighborhoodSize'] = neighborhoodSize
    
    def loadTexture(self, name):
        '''
        Load a specific texture into the ray tracer
        '''
        faces = []
        for side in ('Side', 'Side', 'Top', 'Bot', 'Side', 'Side'):
            try: 
                image = Image.open(f'Textures/{name} {side}.jpg') 
            except:
                image = Image.open(f'Textures/{name} {side}.png') 
            
            image = image.convert('RGB')
            faces.append(image)

        imageSize = faces[0].size
        texture = self.ctx.texture_cube(imageSize, 3, dtype = 'f4')

        for i, img in enumerate(faces):
            data = np.array(img).astype('f4') / 255
            texture.write(i, data)
        
        texture.build_mipmaps()
        self.textureHandles = np.append(self.textureHandles, texture.get_handle())   
    
    def loadSameTexture(self, name):
        '''
        load a specific texture into the ray tracer that has the same elements on all sides
        '''
        try:
            image = Image.open(f'Textures/{name}.jpg')
        except:
            image = Image.open(f'Textures/{name}.png')
        image = image.convert('RGB')

        imageSize, faceData = image.size, np.array(image).astype('f4') / 255
        texture = self.ctx.texture_cube(imageSize, 3, dtype = 'f4')

        for i in range(6):
            texture.write(i, faceData)
        
        texture.build_mipmaps()
        self.textureHandles = np.append(self.textureHandles, texture.get_handle())

    def uploadTextureHandles(self):
        '''
        Upload the texture handles to the GPU 
        '''
        self.textureHandles = self.ctx.buffer(self.textureHandles)
        self.textureHandles.bind_to_storage_buffer(2)

    def loadTextures(self):
        '''
        Register the texture directory to moderngl window and load all the textures
        '''
        self.textureHandles = np.array([], dtype = 'u4')

        self.loadTexture('Grass')
        self.loadSameTexture('Dirt')
        self.loadSameTexture('Stone')
        self.loadSameTexture('Sand')
        self.loadSameTexture('Snow')
        self.loadSameTexture('Clay')
        self.loadSameTexture('Wood')
        self.uploadTextureHandles()
           
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
        self.seed.bind_to_image(3)

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

    def blockSelectionKeys(self, key):
        '''
        Select the block to be placed based on the key press
        '''
        if key not in self.numberKeys:
            return 
        
        keyIndex = self.numberKeys.index(key)
        self.world.setVoxel(keyIndex)

    def on_key_event(self, key, action, modifiers):
        '''
        Set the camera to be moving down if you're pressing / holding shift
        '''
        if modifiers.shift:
            self.camera.movingDown = -1
        else:
            self.camera.movingDown = 1

        if action != self.wnd.keys.ACTION_PRESS:
            return 
        
        self.blockSelectionKeys(key)
        
        if key == self.wnd.keys.F1:
            self.wnd.mouse_exclusivity = not self.wnd.mouse_exclusivity
            self.wnd.cursor = not self.wnd.cursor 
        elif key == self.wnd.keys.F2:
            self.showUI = not self.showUI
        
    def on_mouse_position_event(self, mouseX, mouseY, dx, dy):
        self.camera.updateMouse(dx, -dy) 

    def on_mouse_press_event(self, mouseX, mouseY, button):
        if button == LEFT_MOUSE_BUTTON:
            mapPos, _ = self.world.rayMarch(self.camera.getCameraCenterRay(), PLACE_MINE_DISTANCE)
            self.world.removeVoxel(mapPos)
        elif button == RIGHT_MOUSE_BUTTON:
            mapPos, normal = self.world.rayMarch(self.camera.getCameraCenterRay(), PLACE_MINE_DISTANCE)
            self.world.placeVoxel(mapPos, normal)

    def on_resize(self, screenWidth, screenHeight):
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

    def resetRayTracer(self):
        '''
        Reset the ray tracer's uniform values to defaults
        '''
        self.rayTracer['updatedVoxel'] = False 

    def on_close(self):
        '''
        On window close, save the world. DO NOT STOP RUNNING THE CODE BEFORE THIS FUNCTION ENDS OR THE WORLD SAVE WILL BE BAD
        '''
        print('Currently Saving World')
        self.world.saveWorld()
        print('Finished Saving')

    def on_render(self, t, frameTime):
        '''
        Render the screen and display the fps
        '''
        self.ctx.clear()
        self.cameraMovementKeys()
        self.camera.render(frameTime)

        workgroupX, workgroupY = math.ceil(self.window_size[X_INDEX] / 8), math.ceil(self.window_size[Y_INDEX] / 4)
        self.rayTracer.run(workgroupX, workgroupY)
        self.ctx.memory_barrier(mgl.SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.screenCoords.render(self.program)
        
        if self.showUI:
            self.crosshair.render()
            self.cube.render()
        
        self.updateFrameCount()
        self.camera.assignPrevRenderValues()
        self.resetRayTracer()
        
        self.wnd.title = f'FPS: {self.timer.fps: .2f}'

if __name__ == '__main__':  
    Window.run()