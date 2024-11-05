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