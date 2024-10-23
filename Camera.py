from numba import njit
import glm 

class camera:
    def __init__(self, app, cameraPosition, cameraSpeed, fov, lookAt, vectorUp = glm.vec3(0, 1, 0), viewportWidth = 2):
        self.app, self.ctx = app, app.ctx 
        self.cameraPosition, self.cameraSpeed, self.fov, self.lookAt, self.vectorUp = cameraPosition, cameraSpeed, fov, lookAt, vectorUp 
        self.dirX, self.dirY, self.dirZ = 1, 1, -1
        self.mouseX, self.mouseY = 0.5, 0.5

        self.calculateUnitVectors()

    def calculateI(self):
        '''
        Calculate the camera's unit vector in the +x direction
        '''
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

    def moveCamera(self):
        '''
        Move both the camera position and what it's looking at based on key movements
        '''
        deltaX, deltaY, deltaZ = self.dirX * self.i, self.dirY * self.j, self.dirZ * self.k 
        deltaTotal = self.cameraSpeed * (deltaX + deltaY + deltaZ) 
        self.cameraPosition += deltaTotal 
        self.lookAt += deltaTotal

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
        self.dx, self.dy = self.calculateMousePos(dx, dy, self.app.window_size[0], self.app.window_size[1])

    @staticmethod 
    @njit(cache = True)
    def mouseToAngle(mouseDelta):
        '''
        Convert a normalized mouse delta on the screen into an angle for the camera unit vectors
        '''
        return 178 * (mouseDelta - 0.5)
    
    @staticmethod 
    def calculateExtraDisplacement(distancePoint, angle, unitVector):
        '''
        Calculate the extra displacement based on how the camera is rotated
        '''
        return distancePoint * glm.tan(glm.radians(angle)) * unitVector
    
    