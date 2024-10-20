#version 460 core

in vec3 vertexPosition;
in vec3 vertexColor;

out vec3 fragmentColor;

void main(){
    gl_Position = vec4(vertexPosition, 1.0);
    fragmentColor = vertexColor;
}