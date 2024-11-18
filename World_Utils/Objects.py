from Settings import *

class Sphere:
    '''
    Class for storing basic necessary attributes about a sphere to render and recording them to the SSBO
    '''
    def __init__(self, center, radius, material):
        self.center, self.radius, self.material = center, radius, material

    def record(self, renderArray, i):
        renderArray[i]['center'] = glm.vec4(self.center, 0)
        renderArray[i]['radius'] = self.radius 
        self.material.record(renderArray, i)

class Quad:
    '''
    Class for creating and recording a quad and then rendering it to the SSBO
    '''
    def __init__(self, point, side1, side2, material):
        self.point, self.side1, self.side2, self.material = point, side1, side2, material

        self.n = self.calculateN()
        self.normalVector = self.calculateNormalVector()
        self.D = self.calculateD()
        self.W = self.calculateW()
        self.area = self.calculateArea()
    
    def calculateN(self):
        '''
        Solve for the plane's normal vector (without normalizing it to a unit vector) (thanks 259)
        '''
        return glm.cross(self.side1, self.side2)

    def calculateNormalVector(self):
        '''
        Solve for the plane's normal vector (thanks 259)
        '''
        return glm.normalize(self.n)

    def calculateD(self):
        '''
        Calculate the plane's D value (or the value that's a constant in the equation of a plane [thanks 259])
        '''
        return glm.dot(self.normalVector, self.point)
    
    def calculateW(self):
        '''
        Calculate the mathematically useful w value for orienting points on a plane. https://raytracing.github.io/books/RayTracingTheNextWeek.html
        '''
        return self.n / glm.dot(self.n, self.n)
    
    def calculateArea(self):
        '''
        Calculate the area of the quad using the cross product (thanks 259)
        '''
        return glm.length(glm.cross(self.side1, self.side2))
    
    def record(self, renderArray, i):
        renderArray[i]['point'] = self.point
        renderArray[i]['side1'] = self.side1
        renderArray[i]['side2'] = self.side2
        renderArray[i]['normalVector'] = self.normalVector
        renderArray[i]['W'] = self.W
        renderArray[i]['D'] = self.D 
        renderArray[i]['area'] = self.area
        self.material.record(renderArray, i)

class Cube:
    '''
    Class for creating and recording a cube through a representation by 4 quads
    '''
    def __init__(self, point1, point2, material):
        self.point1, self.point2, self.material = point1, point2, material
        self.createQuads()
    
    def createQuads(self):
        '''
        Create all the quads that represent the cube. https://raytracing.github.io/books/RayTracingTheNextWeek.html gave this algorithm to create thix box representation for me. 
        '''
        self.quads = []
        boxMin, boxMax = glm.min(self.point1, self.point2), glm.max(self.point1, self.point2)

        sideX = glm.vec3(boxMax.x - boxMin.x, 0, 0)
        sideY = glm.vec3(0, boxMax.y - boxMin.y, 0)
        sideZ = glm.vec3(0, 0, boxMax.z - boxMin.z)

        self.quads.append(Quad(glm.vec3(boxMin.x, boxMin.y, boxMax.z), sideX, sideY, self.material)) # Front 
        self.quads.append(Quad(glm.vec3(boxMax.x, boxMin.y, boxMax.z), -sideZ, sideY, self.material)) # Right 
        self.quads.append(Quad(glm.vec3(boxMax.x, boxMin.y, boxMin.z), -sideX, sideY, self.material)) # Back
        self.quads.append(Quad(glm.vec3(boxMin.x, boxMin.y, boxMin.z), sideZ, sideY, self.material)) # Left 
        self.quads.append(Quad(glm.vec3(boxMin.x, boxMax.y, boxMax.z), sideX, -sideZ, self.material)) # Top 
        self.quads.append(Quad(glm.vec3(boxMin.x, boxMin.y, boxMin.z), sideX, sideY, self.material)) # Bottom