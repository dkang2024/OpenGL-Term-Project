from Objects import *

class Test(mglw.WindowConfig):
    resizable = True  
    gl_version = (4, 6)
    cursor = True  
    vsync = False 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx.gc_mode = 'auto'
        self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.triangle = Triangle(self)

    def render(self, time, frameTime):
        self.ctx.clear()
        self.triangle.render()
         
        if frameTime != 0:
            self.wnd.title = f'FPS: {1 / frameTime: .2f}'

Test.run()