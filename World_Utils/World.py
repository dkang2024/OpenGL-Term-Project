from Settings import *
from Chunk import *
from Materials import *
from Noise import * 
from Ray import *
from World_Utils.Textures import Texture

class World:
    '''
    Create the scene with a list of hittables that are passed as a Shader Storage Buffer Object (SSBO) to the ray tracing compute shader
    '''
    def __init__(self, ctx, rayTracer, camera):
        self.ctx, self.rayTracer, self.camera = ctx, rayTracer, camera

        START_INDEX = WOOD
        self.voxels = np.arange(START_INDEX, START_INDEX + 10) # Numpy array of voxels that can be selected using the number keys
        self.voxelPlaceID = self.voxels[0]

        self.worldSize = (WORLD_SIZE_XZ * CHUNK_SIZE, WORLD_SIZE_Y * CHUNK_SIZE, WORLD_SIZE_XZ * CHUNK_SIZE)
        self.worldArray = np.zeros(self.worldSize, 'u1')

        self.heightMap = generateHeightMap()
        self.generateChunks()
        
        self.initMaterials()

        self.lights = {}
        self.lightIDs = {RED_LIGHT, GREEN_LIGHT, BLUE_LIGHT}

    def setVoxel(self, keyIndex):
        '''
        Set the current voxel place id based on the key number pressed
        '''
        self.voxelPlaceID = self.voxels[keyIndex]

    def setTime(self, time):
        '''
        Set the time of the day in the renderer (background color)
        '''
        if time == 'Night':
            self.rayTracer['topColor'] = glm.vec3(0.001)
            self.rayTracer['botColor'] = glm.vec3(0.01)
        elif time == 'Day':
            self.rayTracer['topColor'] = glm.vec3(1)
            self.rayTracer['botColor'] = glm.vec3(0.5, 0.7, 1.0)
        elif time == 'Dawn':
            self.rayTracer['topColor'] = glm.vec3(0.3)
            self.rayTracer['botColor'] = glm.vec3(0.98, 0.48, 0.38)
        else:
            raise RuntimeError('This day-night time does not exist!')

    @staticmethod
    def initRayMarchVars(ray):
        '''
        Initialize all the ray march variables and return them
        '''
        rayDirSign = glm.sign(ray.direction)
        mapPos = glm.ivec3(glm.floor(ray.origin))
        deltaDist = glm.abs(glm.vec3(glm.length(ray.direction)) / ray.direction)
        rayStep = glm.ivec3(rayDirSign)

        sideDist = (rayDirSign * (glm.vec3(mapPos) - ray.origin) + (rayDirSign * 0.5) + 0.5) * deltaDist
        mask = glm.vec3(0)
        
        return rayDirSign, mapPos, deltaDist, rayStep, sideDist, mask
    
    @staticmethod 
    def ddaStep(mapPos, sideDist, deltaDist, rayStep):
        '''
        Perform a DDA step 
        '''
        mask = glm.step(sideDist.xyz, glm.min(sideDist.yzx, sideDist.zxy))

        mapPos += glm.ivec3(mask) * rayStep 
        sideDist += mask * deltaDist 

        return mapPos, sideDist, mask 
    
    def checkInWorld(self, mapPos):
        '''
        Check whether a map position is within the world
        '''
        return glm.all(glm.greaterThanEqual(mapPos, glm.ivec3(0))) and glm.all(glm.lessThan(mapPos, glm.ivec3(self.worldSize)))

    def checkVoxelEmpty(self, mapPos):
        '''
        Check if a voxel is empty 
        '''
        return self.worldArray[mapPos.x, mapPos.y, mapPos.z] == EMPTY_VOXEL
    
    @staticmethod
    def getCenterOfVoxel(mapPos):
        '''
        Get the center of the voxel given a map position 
        '''
        return glm.vec3(mapPos) + glm.vec3(0.5)

    def rayMarch(self, ray, maxRange):
        '''
        Ray march the world with branchless raymarching and then return the intersection map position and the normal vector. Help from https://www.shadertoy.com/view/4dX3zl and https://www.shadertoy.com/view/mtyfRV
        '''

        rayDirSign, mapPos, deltaDist, rayStep, sideDist, mask = self.initRayMarchVars(ray)
        mask = glm.vec3(0)

        while glm.distance(ray.origin, self.getCenterOfVoxel(mapPos)) < maxRange:
            if not self.checkInWorld(mapPos) or self.checkVoxelEmpty(mapPos): #If the voxel is empty or we're outside the world, continue raymarching
                mapPos, sideDist, mask = self.ddaStep(mapPos, sideDist, deltaDist, rayStep)
                continue 
            
            normal = -rayDirSign * mask 
            return mapPos, glm.ivec3(normal)
        
        return None, None # Didn't intersect anything so return None 
    
    def writeToMapPos(self, mapPos, voxelID):
        '''
        Write to a specific map position  for the worldArray and then update the world
        '''
        self.worldArray[mapPos.x, mapPos.y, mapPos.z] = voxelID
        self.world.write(self.worldArray)
        self.rayTracer['updatedVoxel'] = True 

    def writeLightsToSSBO(self):
        '''
        Write the lights array to the SSBO 
        '''
        lenLights = len(self.lights)
        self.rayTracer['numLights'] = lenLights

        lightDType = np.dtype([
            ('mapPos', 'i4', 3),
            ('voxelID', 'i4')
        ])
        
        if lenLights == 0:
            self.lightArray = np.ones(1, lightDType)
        else: 
            self.lightArray = np.empty(lenLights, lightDType)

            for i, (mapPos, voxelID) in zip(range(lenLights), self.lights.items()):
                self.lightArray[i]['mapPos'] = mapPos 
                self.lightArray[i]['voxelID'] = voxelID 

        self.lightBuffer = self.ctx.buffer(self.lightArray)
        self.lightBuffer.bind_to_storage_buffer(1)

    def writeToLights(self, mapPos, voxelID):
        '''
        Write to the light dictionary if the voxelID is a light
        '''
        if (mapPos not in self.lights and voxelID == EMPTY_VOXEL) or (voxelID not in self.lightIDs and voxelID != EMPTY_VOXEL):
            return 
        
        if voxelID == EMPTY_VOXEL:
            self.lights.pop(mapPos)
        else:
            self.lights[mapPos] = voxelID 
        
        self.writeLightsToSSBO()

    def removeVoxel(self, mapPos):
        '''
        Remove a voxel from the world given a mapPosition
        '''
        if mapPos == None:
            return 
        
        self.writeToMapPos(mapPos, EMPTY_VOXEL)
        self.writeToLights(mapPos, EMPTY_VOXEL)

    def placeVoxel(self, mapPos, normal):
        '''
        Place a voxel in the world given a mapPos and a normal vector
        '''
        if mapPos == None: 
            return 
        
        mapPos += normal 
        if not self.checkInWorld(mapPos):
            return 
        
        self.writeToMapPos(mapPos, self.voxelPlaceID)
        self.writeToLights(mapPos, self.voxelPlaceID)
        
    def initMaterials(self):
        '''
        Initialize the materials list
        '''
        self.materialList = []

        self.materialList.append(LambertianMaterial(Texture('Grass')))
        self.materialList.append(LambertianMaterial(Texture('Dirt')))
        self.materialList.append(LambertianMaterial(Texture('Stone')))
        self.materialList.append(LambertianMaterial(Texture('Sand')))
        self.materialList.append(ReflectiveMaterial(Texture('Snow'), 0.5))
        self.materialList.append(LambertianMaterial(Texture('Clay')))
        self.materialList.append(LambertianMaterial(Texture('Wood')))
        self.materialList.append(ReflectiveMaterial(Texture(glm.vec3(0.5)), 0))

        self.materialList.append(PointLight(glm.vec3(15, 0.9, 0.9)))
        self.materialList.append(PointLight(glm.vec3(0.9, 15, 0.9)))
        self.materialList.append(PointLight(glm.vec3(0.9, 0.9, 15)))

        self.materialList.append(DielectricMaterial(Texture(glm.vec3(1, 0.8, 0.8)), 1.52))
        self.materialList.append(DielectricMaterial(Texture(glm.vec3(0.8, 1, 0.8)), 1.52))
        self.materialList.append(DielectricMaterial(Texture(glm.vec3(0.8, 0.8, 1)), 1.52))
        self.materialList.append(DielectricMaterial(Texture(glm.vec3(1)), 1.52))

    @staticmethod
    @njit(cache = True)
    def convertWorldIndexToPosition(worldIndex):
        '''
        Convert the world index position to a world position (chunk position to world map position)
        '''
        return (worldIndex[X_INDEX] * CHUNK_SIZE, worldIndex[Y_INDEX] * CHUNK_SIZE, worldIndex[Z_INDEX] * CHUNK_SIZE)
    
    def generateChunks(self):
        '''
        Generate the chunks for the world
        '''
        for worldXIndex in range(WORLD_SIZE_XZ):
            for worldYIndex in range(WORLD_SIZE_Y):
                for worldZIndex in range(WORLD_SIZE_XZ):
                    chunkIndex = (worldXIndex, worldYIndex, worldZIndex)
                    chunkPosition = self.convertWorldIndexToPosition(chunkIndex)
                    
                    chunk = Chunk(self.worldArray, self.heightMap, chunkIndex, chunkPosition)
                    chunk.upload()
    
    def assignMaterials(self):
        '''
        Assign all the materials to a numpy array and bind it to an OpenGL SSBO
        '''
        materialDType = np.dtype([
            ('color', 'f4', 3),
            ('materialID', 'i4'),
            ('materialParameter', 'f4'),
            ('textureID', 'i4'),
            ('padding', 'f4', 2)
        ])

        self.materialArray = np.empty(len(self.materialList), materialDType)

        for i, material in enumerate(self.materialList):
            material.record(self.materialArray, i)

        self.materials = self.ctx.buffer(self.materialArray)
        self.materials.bind_to_storage_buffer(0)

    def assignWorld(self):
        '''
        Assign the world image texture
        '''
        self.world = self.ctx.texture3d(self.worldSize, 1, self.worldArray, dtype = 'u1')
        self.world.bind_to_image(2)

    def assignRender(self):
        '''
        Assign the render values to the compute shader in order to render all the hittables
        '''
        self.assignMaterials()        
        self.assignWorld()
        self.writeLightsToSSBO()