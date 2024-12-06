#version 460 core 
#extension GL_ARB_bindless_texture : enable
#extension GL_ARB_gpu_shader_int64 : enable

const int CONSTCOLOR = 0;

// General material structure to hold important information (so that each voxel doesn't hold this information but rather an index to this material)
struct Material {
    vec3 color;
    int materialID;
    float materialParameter;
    int textureID;
    vec2 padding;
};

layout(std430, binding = 0) buffer MatBuffer {
    Material materials[];
};
layout(std430, binding = 2) readonly buffer TextureBuffer {
    uint64_t textures[];
};

in vec3 textureCoords;
out vec4 fragColor;

uniform int voxelID;

// Apply the cube texure with bindless handles
vec4 applyTexture(int textureID, vec3 color, vec3 uv){
    if (textureID == CONSTCOLOR){
        return vec4(color, 1);
    }

    int textureIndex = textureID - 1;
    uvec2 textureHandle = unpackUint2x32(textures[textureIndex]);
    return texture(samplerCube(textureHandle), uv);
}

void main(){
    Material currMaterial = materials[voxelID - 1];
    fragColor = applyTexture(currMaterial.textureID, currMaterial.color, textureCoords);
}