#version 460 core 

in vec2 textureCoord;

out vec4 fragColor; 

uniform int frameCount;
uniform sampler2D screen1;
uniform sampler2D screen2;

void main(){
    if (frameCount == 0){
        fragColor = texture(screen1, textureCoord);
    } else if (frameCount % 2 == 0){
        fragColor = texture(screen1, textureCoord);
    } else {
        fragColor = texture(screen2, textureCoord);
    }
}