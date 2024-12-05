#version 460 core 
#extension GL_ARB_bindless_texture : enable
#extension GL_ARB_gpu_shader_int64 : enable

const int CONSTCOLOR = 0;
const int GRASS = 1;
const int DIRT = 2;
const int STONE = 3;
const int SAND = 4;
const int SNOW = 5;
const int CLAY = 6;

layout(std430, binding = 2) readonly buffer TextureBuffer {
    uint64_t textures[];
};

in vec3 textureCoords;
out vec4 fragColor;

uniform int textureID;

vec4 applyTexture(int textureID, vec3 uv){
    int textureIndex = textureID - 1;
    uvec2 textureHandle = unpackUint2x32(textures[textureIndex]);
    return texture(samplerCube(textureHandle), uv);
}

void main(){
    fragColor = applyTexture(textureID, textureCoords);
}