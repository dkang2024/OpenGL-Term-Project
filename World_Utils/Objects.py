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

        self.normalVector = self.calculateNormalVector()
        self.D = self.calculateD()
        self.W = self.calculateW()
    
    def calculateNormalVector(self):
        '''
        Solve for the plane's normal vector (thanks 259)
        '''
        return glm.normalize(glm.cross(self.side1, self.side2))

    def calculateD(self):
        '''
        Calculate the plane's D value (or the value that's a constant in the equation of a plane [thanks 259])
        '''
        return glm.dot(self.normalVector, self.point)
    
    def calculateW(self):
        '''
        Calculate the mathematically useful w value for orienting points on a plane. https://raytracing.github.io/books/RayTracingTheNextWeek.html
        '''
        return self.normalVector / glm.dot(self.normalVector, self.normalVector)
    
    def record(self, renderArray, i):
        renderArray[i]['point'] = glm.vec4(self.point, 0)
        renderArray[i]['side1'] = glm.vec4(self.side1, 0) 
        renderArray[i]['side2'] = glm.vec4(self.side2, 0)
        renderArray[i]['normalVector'] = glm.vec4(self.normalVector, 0)
        renderArray[i]['W'] = glm.vec4(self.W, 0)
        renderArray[i]['D'] = self.D 
        self.material.record(renderArray, i)
