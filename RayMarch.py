import glm 
import math 

class Ray:
    '''
    Ray used for raymarching
    '''
    def __init__(self, origin, direction):
        self.origin = origin 
        self.direction = direction 

    def pointOnRay(self, t):
        return self.origin + self.direction * t 
    
class Grid:
    def __init__(self, point1, point2):
        self.minX, self.maxX = glm.min(point1.x, point2.x), glm.max(point1.y, point2.y)
        self.minY, self.maxY = glm.min(point1.y, point2.y), glm.max(point1.y, point2.y)

    def getXGrid(self, ray):
        return ray.origin.x - self.minX 
    
    def getYGrid(self, ray):
        return ray.origin.y - self.minY

    def getXIndex(self, ray):
        return max(1, math.ceil(ray.origin.x - self.minX))
    
    def getYIndex(self, ray):
        return max(1, math.ceil(ray.origin.y - self.minY))

grid = Grid(glm.vec3(0), glm.vec3(10))
ray = Ray(glm.vec3(-2), glm.vec3(0.2, 0.5, 0.1))

rayDirSign = glm.sign(ray.direction)
mapPos = glm.ivec3(glm.floor(ray.origin))
deltaDist = glm.abs(glm.vec3(glm.length(ray.direction)) / ray.direction)
rayStep = glm.ivec3(rayDirSign)

sideDist = (rayDirSign * (glm.vec3(mapPos) - ray.origin) + (rayDirSign * 0.5) + 0.5) * deltaDist

for i in range(12):
    mask = glm.step(sideDist.xyz, glm.min(sideDist.yzx, sideDist.zxy))
    
    sideDist += mask * deltaDist 
    mapPos += glm.ivec3(mask) * rayStep 

    normal = -rayDirSign * mask
    t = glm.dot(normal, glm.vec3(mapPos) + max(glm.vec3(0), normal) - ray.origin) / glm.dot(normal, ray.direction)
    print(f'Map Position: {mapPos}, Mask: {mask}, Hit Location: {ray.pointOnRay(t)}, Normal: {normal}')
