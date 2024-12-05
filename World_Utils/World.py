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

        self.voxelPlaceID = GRASS 

        self.worldSize = (WORLD_SIZE_XZ * CHUNK_SIZE, WORLD_SIZE_Y * CHUNK_SIZE, WORLD_SIZE_XZ * CHUNK_SIZE)
        self.worldArray = np.zeros(self.worldSize, 'u1')

        self.heightMap = generateHeightMap()
        self.generateChunks()
        
        self.initMaterials()

        self.lights = []

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
    
    def removeVoxel(self, mapPos):
        '''
        Remove a voxel from the world given a mapPosition
        '''
        if mapPos == None:
            return 
        
        self.writeToMapPos(mapPos, EMPTY_VOXEL)

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
        self.rayTracer['numLights'] = len(self.lights)