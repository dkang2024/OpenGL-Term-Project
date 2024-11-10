from Settings import *

class Texture:
    '''
    Class for dealing with constant color textures and image textures both in materials 
    '''
    def __init__(self, texture):
        if isinstance(texture, str):
            self.color = glm.vec4(0)
            self.textureID = self.convertToIndex(texture)
        else:
            self.color = glm.vec4(texture, 0) 
            self.textureID = 0
    
    @staticmethod 
    def convertToIndex(texture):
        '''
        Convert a texture string to a texture index 
        '''
        if texture == 'Brick Wall':
            return 1 
        elif texture == 'Earth':
            return 2
        raise RuntimeError('This texture does not exist!')
        
    def record(self, renderArray, i):
        '''
        Record the texture to the render array
        '''
        renderArray[i]['color'] = self.color 
        renderArray[i]['textureID'] = self.textureID