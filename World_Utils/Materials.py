from Settings import *

class lambertianMaterial:
    '''
    Class for storing all the attributes with a lambertian material and uploading the attributes to the render array
    '''
    def __init__(self, color):
        self.color = color 
    
    def record(self, renderArray, i):
        renderArray[i]['color'] = glm.vec4(self.color, 0)
        renderArray[i]['materialID'] = 0

class reflectiveMaterial:
    '''
    Class for storing all the attributes with a reflective material and uploading the attributes to the render array
    '''
    def __init__(self, color, fuzz):
        self.color, self.fuzz = color, fuzz 

    def record(self, renderArray, i):
        renderArray[i]['color'] = glm.vec4(self.color, 0)
        renderArray[i]['materialID'] = 1
        renderArray[i]['materialParameter'] = self.fuzz

class dielectricMaterial:
    '''
    Class for storing all the attributes with a dielectric material and uploading the attributes to the render array
    '''
    def __init__(self, refractionIndex):
        self.refractionIndex = refractionIndex 
    
    def record(self, renderArray, i):
        renderArray[i]['color'] = glm.vec4(1, 1, 1, 0)
        renderArray[i]['materialID'] = 2 
        renderArray[i]['materialParameter'] = self.refractionIndex