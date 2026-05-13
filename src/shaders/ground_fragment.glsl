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