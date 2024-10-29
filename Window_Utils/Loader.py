from Settings import *

def loadVertexAndFrag(folder, vertexFileName, fragmentFileName):
    '''
    Load the vertex and fragment shader
    '''
    with open(f'{folder}/{vertexFileName}.vert', 'r') as file:
        vertexShader = file.read()
    with open(f'{folder}/{fragmentFileName}.frag', 'r') as file:
        fragmentShader = file.read()
    return vertexShader, fragmentShader

def addImports(ctx, folder, shader):
    '''
    Add the imports from the '#include' statements in the shader into the context for easy use.
    '''
    for line in shader.splitlines():
        if not line.startswith('#include'):
            continue 
            
        importFileName = line[len('#include') + 1:].strip()[1:-1] #Get rid of the quotation marks
        try: 
            with open(f'{folder}/{importFileName}.comp', 'r') as file:
                importShader = file.read().strip() #Text that is the shader that is imported
            ctx.includes[importFileName] = importShader #Add this text for the shader that is imported to the context
        except:
            raise RuntimeError('This file does not exist')
        
def loadComputeShader(ctx, folder, shader):
    '''
    Load whatever compute shader along with the other compute shaders included in the file statement to allow for cleaner abstractions.
    '''
    with open(f'{folder}/{shader}.comp', 'r') as file:
        rayTracer = file.read().strip()

    addImports(ctx, folder, rayTracer)
    return rayTracer 