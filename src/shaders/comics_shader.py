from ursina import Shader
from panda3d.core import Shader as Panda3DShader

comics_shaders = Shader(
    name='comics_shaders',
    language=Shader.GLSL,
    vertex='''
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
    ''',
    fragment='''
    #version 140
    uniform sampler2D p3d_Texture0;
    uniform vec4 p3d_ColorScale;

    #ifdef P3D_ALPHA_TEST
    uniform float p3d_AlphaTest;
    #endif

    in vec3 world_normal;
    in vec2 texcoord;
    in vec3 world_pos;
    in vec3 view_pos;
    in vec4 vertex_pos;
    out vec4 fragColor;

    void main() {
        vec3 light_dir = normalize(vec3(0.5, 1.0, 0.7));

        vec3 normal = normalize(world_normal);

        float ndotl = dot(normal, light_dir);

        float light_intensity;

        if (ndotl > 0.2) {
            if (ndotl > 0.6) {
                light_intensity = 1.0;
            } else {
                light_intensity = 0.75;
            }
        } else {
            light_intensity = 0.45;
        }

        vec4 base_color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

        #ifdef P3D_ALPHA_TEST
        if (base_color.a < p3d_AlphaTest) {
            discard;
        }
        #endif

        vec3 desaturated = vec3(dot(base_color.rgb, vec3(0.3, 0.59, 0.11)));
        vec3 saturated_color = mix(desaturated, base_color.rgb, 1.4);

        vec3 final_color = saturated_color * light_intensity;

        vec2 screen_uv = vertex_pos.xy / vertex_pos.w * 0.5 + 0.5;

        vec3 color_gradient_x = dFdx(final_color);
        vec3 color_gradient_y = dFdy(final_color);
        float color_edge = length(color_gradient_x) + length(color_gradient_y);

        float depth = gl_FragCoord.z;
        float depth_gradient_x = dFdx(depth);
        float depth_gradient_y = dFdy(depth);
        float depth_edge = abs(depth_gradient_x) + abs(depth_gradient_y);

        vec3 normal_gradient_x = dFdx(normal);
        vec3 normal_gradient_y = dFdy(normal);
        float normal_edge = length(normal_gradient_x) + length(normal_gradient_y);

        float edge_intensity = color_edge * 5.0 + depth_edge * 500.0 + normal_edge * 2.0;

        edge_intensity = smoothstep(0.3, 0.8, edge_intensity);

        final_color = mix(final_color, vec3(0.0, 0.0, 0.0), edge_intensity * 0.9);

        float specular = pow(max(0.0, ndotl), 8.0) * 0.3;
        final_color += specular;

        final_color = final_color * vec3(1.05, 1.0, 0.98);

        final_color = clamp(final_color, 0.08, 0.98);

        fragColor = vec4(final_color, base_color.a);
    }
    '''
)

npc_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    '''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat4 p3d_ViewMatrix;

        uniform mat3 p3d_NormalMatrix;

        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        out vec3 world_normal;
        out vec3 world_pos;
        out vec3 view_pos;

        void main() {
            vec4 world_vertex = p3d_ModelMatrix * p3d_Vertex;
            world_pos = world_vertex.xyz;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

            texcoord = p3d_MultiTexCoord0;
            world_normal = normalize(p3d_NormalMatrix * p3d_Normal);

            vec4 view_vertex = p3d_ViewMatrix * world_vertex;
            view_pos = view_vertex.xyz;
        }
    ''',
    '''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;

        #ifdef P3D_ALPHA_TEST
        uniform float p3d_AlphaTest;
        #endif

        in vec2 texcoord;
        in vec3 world_normal;
        in vec3 world_pos;
        in vec3 view_pos;
        out vec4 fragColor;

        void main() {
            vec3 light_dir = normalize(vec3(0.6, 0.9, 0.5));
            vec3 normal = normalize(world_normal);

            float ndotl = dot(normal, light_dir);

            float light;
            if (ndotl > 0.25) {
                if (ndotl > 0.65) {
                    light = 1.0;
                } else {
                    light = 0.7;
                }
            } else {
                light = 0.4;
            }

            vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

            #ifdef P3D_ALPHA_TEST
            if (base.a < p3d_AlphaTest) {
                discard;
            }
            #endif

            vec3 gray = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));
            vec3 color = mix(gray, base.rgb, 1.35);

            color *= light;

            vec3 fdx = dFdx(color);
            vec3 fdy = dFdy(color);
            float edge = length(fdx) + length(fdy);

            vec3 view_dir = normalize(-view_pos);
            float ndotv = abs(dot(normal, view_dir));
            float silhouette = 1.0 - ndotv;
            silhouette = smoothstep(0.75, 0.92, silhouette);

            edge = edge * 5.0 + silhouette * 2.0;
            edge = clamp(edge, 0.0, 1.0);
            edge = smoothstep(0.2, 0.6, edge);

            color = mix(color, vec3(0.0, 0.0, 0.0), edge * 0.85);

            color = clamp(color, 0.1, 0.97);

            fragColor = vec4(color, base.a);
        }
    '''
)

weapon_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    '''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;

        uniform mat3 p3d_NormalMatrix;

        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        out vec3 world_normal;
        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
            world_normal = normalize(p3d_NormalMatrix * p3d_Normal);
        }
    ''',
    '''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        in vec3 world_normal;
        out vec4 fragColor;
        void main() {
            vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

            vec3 gray = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));
            vec3 color = gray + (base.rgb - gray) * 2.5;

            vec3 view_dir = normalize(vec3(0.0, 0.0, 1.0));
            float edge = 1.0 - abs(dot(normalize(world_normal), view_dir));
            edge = smoothstep(0.8, 0.98, edge);
            color = mix(vec3(0.0), color, 1.0 - edge);

            color = clamp(color, 0.0, 1.0);

            fragColor = vec4(color, base.a);
        }
    '''
)

ground_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    '''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat4 p3d_ViewMatrix;

        uniform mat3 p3d_NormalMatrix;

        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;

        out vec2 texcoord;
        out vec3 world_normal;
        out vec3 world_pos;
        out vec3 view_pos;
        out vec4 vertex_pos;

        void main() {
            vec4 world_vertex = p3d_ModelMatrix * p3d_Vertex;
            world_pos = world_vertex.xyz;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            vertex_pos = gl_Position;

            texcoord = p3d_MultiTexCoord0 * 40.0;
            world_normal = normalize(p3d_NormalMatrix * p3d_Normal);

            vec4 view_vertex = p3d_ViewMatrix * world_vertex;
            view_pos = view_vertex.xyz;
        }
    ''',
    '''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;

        #ifdef P3D_ALPHA_TEST
        uniform float p3d_AlphaTest;
        #endif

        in vec2 texcoord;
        in vec3 world_normal;
        in vec3 world_pos;
        in vec3 view_pos;
        in vec4 vertex_pos;
        out vec4 fragColor;

        void main() {
            vec3 light_dir = normalize(vec3(0.5, 1.0, 0.7));
            vec3 normal = normalize(world_normal);

            float ndotl = dot(normal, light_dir);

            float light_intensity;

            if (ndotl > 0.15) {
                if (ndotl > 0.55) {
                    light_intensity = 1.0;
                } else {
                    light_intensity = 0.7;
                }
            } else {
                light_intensity = 0.4;
            }

            vec4 base_color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

            #ifdef P3D_ALPHA_TEST
            if (base_color.a < p3d_AlphaTest) {
                discard;
            }
            #endif

            float height_factor = clamp(world_pos.y * 0.2, 0.0, 0.3);
            vec3 height_tint = mix(vec3(1.0, 1.0, 1.0), vec3(0.9, 1.0, 0.8), height_factor);

            vec3 desaturated = vec3(dot(base_color.rgb, vec3(0.3, 0.59, 0.11)));
            vec3 saturated_color = mix(desaturated, base_color.rgb, 1.25);

            vec3 final_color = saturated_color * light_intensity * height_tint;

            vec3 color_gradient_x = dFdx(final_color);
            vec3 color_gradient_y = dFdy(final_color);
            float color_edge = length(color_gradient_x) + length(color_gradient_y);

            float depth = gl_FragCoord.z;
            float depth_gradient_x = dFdx(depth);
            float depth_gradient_y = dFdy(depth);
            float depth_edge = abs(depth_gradient_x) + abs(depth_gradient_y);

            float edge_intensity = color_edge * 3.0 + depth_edge * 200.0;
            edge_intensity = smoothstep(0.4, 0.9, edge_intensity);

            final_color = mix(final_color, vec3(0.0, 0.0, 0.0), edge_intensity * 0.3);

            float noise = fract(sin(dot(texcoord, vec2(12.9898, 78.233))) * 43758.5453);
            final_color = mix(final_color, final_color * 1.1, noise * 0.1);

            final_color = clamp(final_color, 0.1, 0.98);

            fragColor = vec4(final_color, base_color.a);
        }
    '''
)
