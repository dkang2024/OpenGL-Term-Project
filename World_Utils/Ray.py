class Ray:
    '''
    Ray used for raymarching
    '''
    def __init__(self, origin, direction):
        self.origin = origin 
        self.direction = direction 

    def pointOnRay(self, t):
        return self.origin + self.direction * t 