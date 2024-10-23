#version 460 core 

in vec3 vertexPosition;
in vec2 uv;

out vec2 textureCoord; 

void main(){
    gl_Position = vec4(vertexPosition, 1.0);
    textureCoord = uv;
}