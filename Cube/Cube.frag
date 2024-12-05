#version 460 core 

const int CONSTCOLOR = 0;
const int GRASS = 1;
const int DIRT = 2;
const int STONE = 3;
const int SAND = 4;
const int SNOW = 5;
const int CLAY = 6;

layout(binding = 2) uniform samplerCube grassTexture;
layout(binding = 3) uniform samplerCube dirtTexture;
layout(binding = 4) uniform samplerCube stoneTexture;
layout(binding = 5) uniform samplerCube sandTexture;
layout(binding = 6) uniform samplerCube snowTexture;
layout(binding = 7) uniform samplerCube clayTexture;

in vec3 textureCoords;
out vec4 fragColor;

uniform int textureID;

vec4 applyTexture(int textureID, vec3 uv){
    if (textureID == GRASS){
        return texture(grassTexture, uv);
    } else if (textureID == DIRT){
        return texture(dirtTexture, uv);
    } else if (textureID == STONE){
        return texture(stoneTexture, uv);
    } else if (textureID == SAND){
        return texture(sandTexture, uv);
    } else if (textureID == SNOW){
        return texture(snowTexture, uv);
    } else if (textureID == CLAY){
        return texture(clayTexture, uv);
    }
}
void main(){
    fragColor = applyTexture(textureID, textureCoords);
}