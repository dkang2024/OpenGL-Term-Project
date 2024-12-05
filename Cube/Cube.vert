#version 460 core 

in vec3 vertexPosition;

uniform vec3 cubeCenter;
uniform mat4 proj;

out vec3 textureCoords;

void main(){
    textureCoords = vertexPosition - cubeCenter;
    gl_Position = proj * vec4(vertexPosition, 1.0);
}