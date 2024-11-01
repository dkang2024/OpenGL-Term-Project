class sphere3:
    '''
    Class for storing basic necessary attributes about a sphere to render
    '''
    def __init__(self, center, radius, color, materialID, materialParameter):
        self.center, self.radius, self.color, self.materialID, self.materialParameter = center, radius, color, materialID, materialParameter 
