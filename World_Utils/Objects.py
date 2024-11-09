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