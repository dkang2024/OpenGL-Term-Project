from Settings import *

class LambertianMaterial:
    '''
    Class for storing all the attributes with a lambertian material and uploading the attributes to the render array
    '''
    def __init__(self, texture):
        self.texture = texture
    
    def record(self, renderArray, i):
        self.texture.record(renderArray, i)
        renderArray[i]['materialID'] = 0

class ReflectiveMaterial:
    '''
    Class for storing all the attributes with a reflective material and uploading the attributes to the render array
    '''
    def __init__(self, color, fuzz):
        self.color, self.fuzz = color, fuzz 

    def record(self, renderArray, i):
        renderArray[i]['color'] = self.color
        renderArray[i]['textureID'] = 0
        renderArray[i]['materialID'] = 1
        renderArray[i]['materialParameter'] = self.fuzz

class DielectricMaterial:
    '''
    Class for storing all the attributes with a dielectric material and uploading the attributes to the render array
    '''
    def __init__(self, refractionIndex):
        self.refractionIndex = refractionIndex 
    
    def record(self, renderArray, i):
        renderArray[i]['color'] = glm.vec3(1)
        renderArray[i]['textureID'] = 0
        renderArray[i]['materialID'] = 2 
        renderArray[i]['materialParameter'] = self.refractionIndex

class PointLight:
    '''
    Class for storing all the attributes with a point light and uploading the attributes to the render array
    '''
    def __init__(self, lightColor):
        self.lightColor = lightColor

    def record(self, renderArray, i):
        renderArray[i]['color'] = self.lightColor
        renderArray[i]['textureID'] = 0
        renderArray[i]['materialID'] = 3