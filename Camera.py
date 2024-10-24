from numba import njit
import glm 

def nearZero(v):
    '''
    Checks whether all elements of the vector are near zero
    '''
    epsilon = 1e-5
    return v.x < epsilon and v.y < epsilon and v.z < epsilon

class Camera:
    def __init__(self, app, cameraPosition, cameraSpeed, fov, lookAt, vectorUp = glm.vec3(0, 1, 0)):
        self.app = app
        self.cameraPosition, self.cameraSpeed, self.fov, self.lookAt, self.vectorUp = cameraPosition, cameraSpeed, fov, lookAt, vectorUp 
        self.dirX, self.dirY, self.dirZ, self.movingDown = 0, 0, 0, 1

        self.calculateUnitVectors()

    def calculateI(self):
        '''
        Calculate the camera's unit vector in the +x direction
        '''
        crossProduct = glm.cross(self.vectorUp, self.k)
        if nearZero(crossProduct):
            crossProduct = glm.cross(glm.vec3(0, 0, 1), self.k)
        self.i = glm.normalize(glm.cross(self.vectorUp, self.k))
    
    def calculateJ(self):
        '''
        Calculate the camera's unit vector in the +y direction
        '''
        self.j = glm.cross(self.k, self.i)

    def calculateK(self):
        '''
        Calculate the camera's unit vector in the +z direction
        '''
        self.k = glm.normalize(self.cameraPosition - self.lookAt)

    def calculateUnitVectors(self):
        '''
        Calculate all of the camera's unit vectors
        '''
        self.calculateK()
        self.calculateI()
        self.calculateJ()

    def moveCamera(self, frameTime):
        '''
        Move both the camera position and what it's looking at based on key movements
        '''
        deltaX, deltaY, deltaZ = self.dirX * self.i, self.dirY * self.j, self.dirZ * self.k 
        deltaTotal = self.cameraSpeed * (deltaX + deltaY + deltaZ) * frameTime
        self.cameraPosition += deltaTotal 
        self.lookAt += deltaTotal
        self.calculateUnitVectors()

    @staticmethod 
    @njit(cache = True)
    def calculateMousePos(dx, dy, windowWidth, windowHeight):
        '''
        Calculate normalized dx, dy depending on mouse position on the screen
        '''
        return dx / windowWidth, dy / windowHeight
    
    def updateMouse(self, dx, dy):
        '''
        Update mouse dx dy depending on mouse changes in position on the screen
        '''
        dx, dy = self.calculateMousePos(dx, dy, self.app.window_size[0], self.app.window_size[1])
        self.calculateLookAt(dx, dy)

    @staticmethod 
    @njit(cache = True)
    def mouseToAngle(mouseDelta):
        '''
        Convert a normalized mouse delta on the screen into an angle for the camera unit vectors
        '''
        return 180 * mouseDelta
    
    @staticmethod 
    def calculateExtraDisplacement(distancePoint, angle, unitVector):
        '''
        Calculate the extra displacement based on how the camera is rotated
        '''
        return distancePoint * glm.tan(glm.radians(angle)) * unitVector
    
    def calculateLookAt(self, dx, dy):
        '''
        Calculate where a camera looks at with respect to mouse position
        '''
        alpha, beta = self.mouseToAngle(dx), self.mouseToAngle(dy)
        distancePoint = glm.distance(self.cameraPosition, self.lookAt)
        
        self.lookAt += self.calculateExtraDisplacement(distancePoint, alpha, self.i) + self.calculateExtraDisplacement(distancePoint, beta, self.j)
        self.calculateUnitVectors()

    def calculateFocalLength(self):
        '''
        Calculate the camera's focal length
        '''
        cameraPosVector = self.cameraPosition - self.lookAt 
        self.focalLength = glm.sqrt(glm.dot(cameraPosVector, cameraPosVector))

    @staticmethod
    @njit(cache = True)
    def numbaCalculateViewportWidth(viewportHeight, imageWidth, imageHeight):
        return viewportHeight * (imageWidth / imageHeight)

    def calculateViewportWidth(self):
        '''
        Calculate the viewport width
        '''
        self.viewportWidth = self.numbaCalculateViewportWidth(self.viewportHeight, self.app.window_size[0], self.app.window_size[1])

    def calculateViewportHeight(self):
        '''
        Calculate the viewport height
        '''
        tanTheta = glm.tan(glm.radians(self.fov) / 2)
        self.viewportHeight = glm.abs(2 * tanTheta * self.focalLength)

    def calculateViewportVectors(self):
        '''
        Calculate the camera's viewport vectors
        '''
        self.viewportWidthVector = self.viewportWidth * self.i 
        self.viewportHeightVector = self.viewportHeight * self.j 

    def calculatePixelDelta(self):
        '''
        Calculate the camera's pixel delta values
        '''
        self.pixelDX = self.viewportWidthVector / self.app.window_size[0]
        self.pixelDY = self.viewportHeightVector / self.app.window_size[1]

    def calculateFirstPixelPos(self):
        '''
        Calculates the position of the first pixel on the viewport in terms of the world's coordinate system
        '''
        viewportBottomLeft = self.cameraPosition - self.focalLength * self.k - (self.viewportWidthVector + self.viewportHeightVector) / 2
        self.initPixelPos = viewportBottomLeft + (self.pixelDX + self.pixelDY) / 2

    def calculateRenderValues(self):
        '''
        Calculate the important camera render values
        ''' 
        self.calculateFocalLength()
        self.calculateViewportHeight()
        self.calculateViewportWidth()
        self.calculateViewportVectors()
        self.calculatePixelDelta()
        self.calculateFirstPixelPos()

    def render(self, frameTime):
        '''
        To be called during the render. Calculates and passes along to the uniform important render values (pixelDX, pixelDY, and initPixelPos)
        '''
        self.moveCamera(frameTime)
        self.calculateRenderValues()
        self.app.rayTracer['cameraPosition'] = self.cameraPosition
        self.app.rayTracer['pixelDX'] = self.pixelDX
        self.app.rayTracer['pixelDY'] = self.pixelDY
        self.app.rayTracer['initPixelPos'] = self.initPixelPos