from numba import njit
import time 
import glm 

def nearZero(v):
    '''
    Checks whether all elements of the vector are near zero to deal with floating point inaccuracies
    '''
    epsilon = 1e-7
    return v.x < epsilon and v.y < epsilon and v.z < epsilon

class Camera:
    '''
    Class for a moveable camera. I created all the code here without the help of any tutorials (I had to think up and create the functions / math myself). 
    '''
    def __init__(self, app, cameraPosition, cameraSpeed, fov, lookAt, vectorUp = glm.vec3(0, 1, 0)):
        self.app = app
        self.cameraPosition, self.cameraSpeed, self.fov, self.lookAt, self.vectorUp = cameraPosition, cameraSpeed, fov, lookAt, vectorUp 
        self.dirX, self.dirY, self.dirZ, self.movingDown = 0, 0, 0, 1

        self.calculateUnitVectors()

    def calculateI(self):
        '''
        Calculate the camera's unit vector in the +x direction by taking the cross product of the "up" direction with the k unit vector (random direction that is NOT in the direction of +z so that the cross product doesn't result in 0)
        '''
        crossProduct = glm.cross(self.vectorUp, self.k)
        if nearZero(crossProduct): #If vectorUp and k are almost parallel, take the cross with another vector that isn't parallel. 
            crossProduct = glm.cross(glm.vec3(0, 0, 1), self.k)
        self.i = glm.normalize(crossProduct)
    
    def calculateJ(self):
        '''
        Calculate the camera's unit vector in the +y direction by taking the cross product of the k hat direction with the i hat direction (note the right handed coordinate system)
        '''
        self.j = glm.cross(self.k, self.i)

    def calculateK(self):
        '''
        Calculate the camera's unit vector in the +z direction by taking the vector from the lookAt to the camera position (keep in mind the camera looks in the -z direction because we need to adopt a right handed coordinate system)
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
        Move both the camera position and what it's looking at based on key movements (assuming no acceleration).
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
        '''
        Calculate the viewport width by multiplying the viewport height by the same ratio of the imageWidth / imageHeight 
        '''
        return viewportHeight * (imageWidth / imageHeight)

    def calculateViewportWidth(self):
        '''
        Calculate the viewport width
        '''
        self.viewportWidth = self.numbaCalculateViewportWidth(self.viewportHeight, self.app.window_size[0], self.app.window_size[1])

    def calculateViewportHeight(self):
        '''
        Calculate the viewport height given the vertical FOV (angle between the camera and the camera's unit z direction) 
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