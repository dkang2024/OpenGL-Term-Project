import glm 
import numpy as np 
import copy 

X_INDEX = 0
Y_INDEX = 1
Z_INDEX = 2

CHUNK_SIZE = 10
WORLD_SIZE = 12

EPSILON = 1e-20

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin 
        self.direction = self.clampRay(direction)

    @staticmethod 
    def clampRay(direction):
        for i in range(3):
            if glm.abs(direction[i]) < EPSILON:
                direction[i] = EPSILON
        return direction

    def pointOnRay(self, t):
        return self.origin + self.direction * t 
    
class Brickmap: 
    def __init__(self):
        self.chunks = []

        self.worldSize = [CHUNK_SIZE * WORLD_SIZE] * 3
        self.worldArray = np.zeros(self.worldSize, 'u1')

        self.brickmapSize = [WORLD_SIZE] * 3 
        self.brickmapArray = np.zeros(self.brickmapSize, 'u1')

    @staticmethod
    def convertWorldIndexToPosition(worldIndex):
        return (worldIndex[X_INDEX] * CHUNK_SIZE, worldIndex[Y_INDEX] * CHUNK_SIZE, worldIndex[Z_INDEX] * CHUNK_SIZE)
    
    def generateChunks(self):
        for xIndex in range(WORLD_SIZE):
            for yIndex in range(WORLD_SIZE):
                for zIndex in range(WORLD_SIZE):
                    worldIndex = (xIndex, yIndex, zIndex)
                    chunk = Chunk(self.worldArray, self.brickmapArray, worldIndex, self.convertWorldIndexToPosition(worldIndex))

                    chunk.upload()

    def checkBrickmap(self, brickmapPos):
        if not (glm.all(glm.greaterThanEqual(brickmapPos, glm.ivec3(0))) and glm.all(glm.lessThan(brickmapPos, glm.ivec3(self.brickmapSize)))):
            return False
        return self.brickmapArray[brickmapPos.x, brickmapPos.y, brickmapPos.z] == 1
    
    def checkWorld(self, mapPosition):
        if not (glm.all(glm.greaterThanEqual(mapPosition, glm.ivec3(0))) and glm.all(glm.lessThan(mapPosition, glm.ivec3(self.worldSize)))):
            return False
        return self.worldArray[mapPosition.x, mapPosition.y, mapPosition.z] == 1

class Chunk:
    def __init__(self, worldArray, brickmapArray, worldIndex, worldPosition):
        self.worldArray = worldArray 
        self.brickmapArray = brickmapArray
        self.worldIndex = worldIndex
        self.worldPosition = worldPosition 
    
    def upload(self):
        for xIndex in range(CHUNK_SIZE):
            worldX = xIndex + self.worldPosition[X_INDEX]
            for yIndex in range(CHUNK_SIZE):
                worldY = yIndex + self.worldPosition[Y_INDEX]
                for zIndex in range(CHUNK_SIZE):
                    worldZ = zIndex + self.worldPosition[Z_INDEX]
                    self.worldArray[worldX, worldY, worldZ] = 1

        self.brickmapArray[self.worldIndex] = 1

def intersectionTest(boxMin, boxMax, ray):
    boxMin, boxMax = glm.vec3(boxMin), glm.vec3(boxMax)
    rayInvDir = 1 / ray.direction

    t1 = (boxMin.x - ray.origin.x) * rayInvDir.x 
    t2 = (boxMax.x - ray.origin.x) * rayInvDir.x

    tMin = glm.min(t1, t2)

    for i in range(3):
        t1 = (boxMin[i] - ray.origin[i]) * rayInvDir[i]
        t2 = (boxMax[i] - ray.origin[i]) * rayInvDir[i]

        tMin = glm.max(tMin, glm.min(t1, t2))
    
    return tMin

def convertToBrickmapPosition(mapPosition):
    return mapPosition / CHUNK_SIZE

brickmap = Brickmap()
brickmap.generateChunks()

ray = Ray(glm.vec3(0, -2, 1), glm.vec3(0.3, 0.5, 0.2))

invRayDir = 1 / ray.direction
rayDirSign = glm.sign(ray.direction)
deltaDist = glm.abs(glm.vec3(glm.length(ray.direction)) * invRayDir)
rayStep = glm.ivec3(rayDirSign)

rayBrickmapOrigin = convertToBrickmapPosition(ray.origin)
mapPos = glm.ivec3(glm.floor(rayBrickmapOrigin))
sideDist = (rayDirSign * (glm.vec3(mapPos) - rayBrickmapOrigin) + (rayDirSign * 0.5) + 0.5) * deltaDist

for i in range(25):
    if not brickmap.checkBrickmap(mapPos):
        mask = glm.step(sideDist.xyz, glm.min(sideDist.yzx, sideDist.zxy))

        sideDist += mask * deltaDist 
        mapPos += glm.ivec3(mask) * rayStep 
        
        continue 

    print(mapPos)

    newRay = Ray(rayBrickmapOrigin, ray.direction)
    t = intersectionTest(mapPos * CHUNK_SIZE, (mapPos + 1) * CHUNK_SIZE, newRay)
    print(ray.pointOnRay(t))
    
    mini = ((glm.vec3(mapPos) - rayBrickmapOrigin) - (rayDirSign * 0.5) + 0.5) * invRayDir
    t = glm.max(mini.x, glm.max(mini.y, mini.z))
    intersectBrickmap = ray.pointOnRay(t)

    localPosition = (intersectBrickmap - glm.vec3(mapPos)) * CHUNK_SIZE

    mapPosition = mapPos * CHUNK_SIZE + glm.ivec3(localPosition)
    
    while convertToBrickmapPosition(mapPosition) == mapPos:
        if not brickmap.checkWorld(mapPosition):
            mask = glm.step(sideDist.xyz, glm.min(sideDist.yzx, sideDist.zxy))
                
            sideDist += mask * deltaDist 
            mapPosition += glm.ivec3(mask) * rayStep 

        mini = ((glm.vec3(mapPosition) - ray.origin) - (rayDirSign * 0.5) + 0.5) * invRayDir
        t = glm.max(mini.x, glm.max(mini.y, mini.z))
        intersectWorld = ray.pointOnRay(t)
        
        break

    print(f'Intersect Point (brickmap) {intersectBrickmap}, Intersect Point (world) {mapPos}, Map Pos: {mapPosition}')

    break

ray = Ray(glm.vec3(0, -2, 1), glm.vec3(0.3, 0.5, 0.2))

invRayDir = 1 / ray.direction
rayDirSign = glm.sign(ray.direction)
mapPos = glm.ivec3(glm.floor(ray.origin))
deltaDist = glm.abs(glm.vec3(glm.length(ray.direction)) * invRayDir)
rayStep = glm.ivec3(rayDirSign)

sideDist = (rayDirSign * (glm.vec3(mapPos) - ray.origin) + (rayDirSign * 0.5) + 0.5) * deltaDist

for i in range(25):
    if not brickmap.checkWorld(mapPos):
        mask = glm.step(sideDist.xyz, glm.min(sideDist.yzx, sideDist.zxy))
        
        sideDist += mask * deltaDist 
        mapPos += glm.ivec3(mask) * rayStep 
        
        continue 
    
    mini = ((glm.vec3(mapPos) - ray.origin) - (rayDirSign * 0.5) + 0.5) * invRayDir
    t = glm.max(mini.x, glm.max(mini.y, mini.z))
    intersectWorld = ray.pointOnRay(t)

    print(f'Intersect World {intersectWorld}')

    break