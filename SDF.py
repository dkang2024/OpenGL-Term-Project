import glm 
import numpy as np

class Ray:
    def __init__(self, origin, direction):
        self.origin = glm.floor(origin)
        self.direction = glm.normalize(direction)

    def pointOnRay(self, t):
        return self.origin + self.direction * t 

WORLD_SIZE = 10

class Brickmap: 
    def __init__(self):
        self.chunks = []

        self.worldSize = [WORLD_SIZE] * 3
        self.worldArray = np.ones(self.worldSize, 'u1')

    def checkWorld(self, mapPosition):
        if not (glm.all(glm.greaterThanEqual(mapPosition, glm.vec3(0))) and glm.all(glm.lessThan(mapPosition, glm.vec3(self.worldSize)))):
            return False
        mapPosition = glm.ivec3(glm.floor(mapPosition))
        return self.worldArray[mapPosition.x, mapPosition.y, mapPosition.z] == 1
    
    def minDist(self, ray):
        minDist = 1000000000000000000000000000000000000000000000000000
        for worldX in range(WORLD_SIZE):
            for worldY in range(WORLD_SIZE):
                for worldZ in range(WORLD_SIZE):
                    if self.worldArray[worldX, worldY, worldZ] != 1:
                        continue 
                    distance = sdfVoxel(ray.origin, (worldX, worldY, worldZ))
                    if distance < minDist:
                        minDist = distance 
        
        return minDist
        
    def rayMarch(self, ray):
        for i in range(50):
            if self.checkWorld(ray.origin):
                return ray.origin
            minDist = self.minDist(ray)
            print(ray.origin, minDist)
            ray.origin += ray.direction * minDist
            print(ray.origin)

def sdfVoxel(mapPos, voxelPosition): 
    d = glm.abs(mapPos - (voxelPosition + glm.vec3(0.5))) - glm.vec3(0.5)
    return glm.length(glm.max(d, 0.0)) + glm.min(glm.max(d.x, glm.max(d.y, d.z)), 0.0)

ray = Ray(glm.vec3(-1.5), glm.vec3(0.4, 0.2, 0.3))
brickmap = Brickmap()
print(brickmap.rayMarch(ray))