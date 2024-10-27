#version 460 core 

in vec2 textureCoord;

out vec4 fragColor; 

uniform sampler2D screen;

void main(){
    fragColor = texture(screen, textureCoord);
}