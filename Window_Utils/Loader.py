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

def removeComments(shader):
    '''
    Remove the comments from the shader to avoid any shenanigans with "import" statements in comments
    '''
    return [line for line in shader if not line.startswith('//')]

def addImports(folder, shader):
    '''
    Add the imports from the 'import' statements in the shader into the shader's string
    '''
    for i, line in enumerate(shader):
        if not line.startswith('import'):
            continue 
            
        importFileName = line[len('import') + 1:].strip()
        try: 
            with open(f'{folder}/{importFileName}.comp', 'r') as file:
                shader[i] = file.read().strip()
        except:
            raise RuntimeError('This file does not exist')
        
def loadComputeShader(folder, shader):
    '''
    Load whatever compute shader along with the other compute shaders "imported" in the file beforehand to allow cleaner abstractions
    '''
    with open(f'{folder}/{shader}.comp', 'r') as file:
        rayTracer = file.read().strip().split('\n')

    rayTracer = removeComments(rayTracer)
    addImports(folder, rayTracer)
    return '\n'.join(rayTracer) 