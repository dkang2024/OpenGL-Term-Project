from Settings import *

@ti.data_oriented
class Camera:
    '''
    Class for a moveable pinhole camera. I implemented all the key movement functions myself because it was pretty obvious how to do those things. However, I didn't know the exact math necessary for camera mouse movement so I used https://learnopengl.com/Getting-started/Camera for a reference on the math necessary for camera mouse movement. Any functions that I referenced the website on are explicitly marked.
    '''
    def __init__(self, app, cameraPosition, cameraSpeed, fov, mouseSensitivity, vectorUp = glm.vec3(0, 1, 0)):
        self.app, self.MAX_ANGLE = app, MAX_ANGLE
        self.cameraPosition, self.cameraSpeed, self.fov = cameraPosition, cameraSpeed, fov
        self.dirX, self.dirY, self.dirZ, self.movingDown = 0, 0, 0, 1
        self.mouseSensitivity, self.vectorUp, self.yaw, self.pitch = mouseSensitivity, vectorUp, -90, 0

        self.calculateUnitVectors()
        self.calculateLookAt()

    def calculateI(self):
        '''
        Calculate the camera's unit vector in the +x direction (derived myself [thanks 259])
        '''
        self.i = glm.normalize(glm.cross(self.vectorUp, self.k))

    def calculateJ(self):
        '''
        Calculate the camera's unit vector in the +y direction (dervied myself [thanks 259])
        '''
        self.j = glm.cross(self.k, self.i)

    def calculateK(self):
        '''
        Calculate the camera's k unit vector based on the yaw and pitch (based on website)
        '''
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
        x = glm.cos(yaw) * glm.cos(pitch)
        y = glm.sin(pitch)
        z = glm.sin(yaw) * glm.cos(pitch)
        self.k = -glm.normalize(glm.vec3(x, y, z))

    def calculateUnitVectors(self):
        '''
        Calculate all of the camera's unit vectors
        '''
        self.calculateK()
        self.calculateI()
        self.calculateJ()

    def moveCamera(self, frameTime):
        '''
        Move both the camera position and what it's looking at based on key movements (assuming no acceleration).
        '''
        deltaX, deltaY, deltaZ = self.dirX * self.i, self.dirY * self.j, self.dirZ * self.k
        deltaTotal = self.cameraSpeed * (deltaX + deltaY + deltaZ) * frameTime
        self.cameraPosition += deltaTotal 

        self.calculateLookAt()
    
    @staticmethod
    @ti.kernel
    def scaleWithSensitivity(dx: float, mouseSensitivity: float) -> float:
        '''
        Calculate scaled dx depending on mouse sensitivity (referenced website)
        '''
        return dx * mouseSensitivity
    
    @staticmethod
    @ti.kernel
    def constrainPitch(pitch: float, MAX_ANGLE: int) -> float:
        '''
        Constrain the pitch to be between 89 and -89 to avoid any shenanigans with the camera rotation inverting the view (referenced website) 
        '''
        newPitch = pitch
        if newPitch > MAX_ANGLE: 
            newPitch = MAX_ANGLE 
        elif newPitch < -MAX_ANGLE:
            newPitch = -MAX_ANGLE
        return newPitch
    
    def updateMouse(self, dx, dy):
        '''
        Update mouse dx depending on mouse changes in position on the screen (based on website)
        '''
        self.yaw += self.scaleWithSensitivity(dx, self.mouseSensitivity)
        self.pitch += self.scaleWithSensitivity(dy, self.mouseSensitivity)
        self.pitch = self.constrainPitch(self.pitch, self.MAX_ANGLE)

        self.calculateUnitVectors()
        self.calculateLookAt()
        
    def calculateLookAt(self):
        '''
        Calculate where the camera looks at 
        '''
        self.lookAt = self.cameraPosition - self.k

    @staticmethod
    @ti.kernel
    def taichiCalculateViewportWidth(viewportHeight: float, imageWidth: float, imageHeight: float) -> float:
        '''
        Calculate the viewport width by multiplying the viewport height by the same ratio of the imageWidth / imageHeight 
        '''
        return viewportHeight * (imageWidth / imageHeight)

    def calculateViewportWidth(self):
        '''
        Calculate the viewport width
        '''
        self.viewportWidth = self.taichiCalculateViewportWidth(self.viewportHeight, self.app.window_size[0], self.app.window_size[1])

    def calculateViewportHeight(self):
        '''
        Calculate the viewport height given the vertical FOV (angle between the camera and the camera's unit z direction) 
        '''
        tanTheta = glm.tan(glm.radians(self.fov) / 2)
        self.viewportHeight = glm.abs(2 * tanTheta)

    def calculateViewportVectors(self):
        '''
        Calculate the camera's viewport vectors (basically just the viewport distances but made vectors through the unit vectors)
        '''
        self.viewportWidthVector = self.viewportWidth * self.i
        self.viewportHeightVector = self.viewportHeight * self.j

    def calculatePixelDelta(self):
        '''
        Calculate the camera's pixel delta values (or the horizontal / vertical distance between screen pixels on the camera)
        '''
        self.pixelDX = self.viewportWidthVector / self.app.window_size[0]
        self.pixelDY = self.viewportHeightVector / self.app.window_size[1]

    def calculateFirstPixelPos(self):
        '''
        Calculates the position of the first pixel on the viewport in terms of the world's coordinate system
        '''
        viewportBottomLeft = self.cameraPosition - self.k - (self.viewportWidthVector + self.viewportHeightVector) / 2
        self.initPixelPos = viewportBottomLeft + (self.pixelDX + self.pixelDY) / 2

    def calculateRenderValues(self):
        '''
        Calculate the important camera render values
        '''
        self.calculateViewportHeight()
        self.calculateViewportWidth()
        self.calculateViewportVectors()
        self.calculatePixelDelta()
        self.calculateFirstPixelPos()

    def assignRenderValues(self):
        '''
        Assign each of the render values to the uniform input struct in the camera for the ray tracing compute shader
        '''
        self.app.rayTracer['camera.position'] = self.cameraPosition
        self.app.rayTracer['camera.pixelDX'] = self.pixelDX 
        self.app.rayTracer['camera.pixelDY'] = self.pixelDY 
        self.app.rayTracer['camera.initPixelPos'] = self.initPixelPos

    def render(self, frameTime):
        '''
        To be called during the render. Calculates and passes along to the uniform important render values (pixelDX, pixelDY, and initPixelPos)
        '''
        self.moveCamera(frameTime)
        self.calculateRenderValues()
        self.assignRenderValues()

    def calculateProjMat(self):
        '''
        Calculate the camera's projection matrix
        '''
        return glm.perspective(glm.radians(self.fov), self.app.window_size[0] / self.app.window_size[1], 0.1, 100)

    def calculateViewMat(self):
        '''
        Calculate the camera's view matrix
        '''
        return glm.lookAt(self.cameraPosition, self.lookAt, self.vectorUp)

    def assignPrevRenderValues(self):
        '''
        Assign each of the render values for the previous camera in the prevCamera struct for the ray tracing compute shader with TAA
        '''
        self.app.rayTracer['prevViewProj'].write(self.calculateProjMat() * self.calculateViewMat())