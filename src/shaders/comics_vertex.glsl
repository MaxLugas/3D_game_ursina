#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;
out vec3 world_normal;
out vec2 texcoord;
out vec3 world_pos;
out vec3 view_pos;
out vec4 vertex_pos;

void main() {
    vec4 world_vertex = p3d_ModelMatrix * p3d_Vertex;
    world_pos = world_vertex.xyz;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    vertex_pos = gl_Position;

    world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
    texcoord = p3d_MultiTexCoord0;

    vec4 view_vertex = p3d_ViewMatrix * world_vertex;
    view_pos = view_vertex.xyz;
}