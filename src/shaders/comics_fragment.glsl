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

    float ambient_strength = 0.6;
    float diffuse_step_1 = 0.85;
    float diffuse_step_2 = 1.2;

    float light_intensity;

    if (ndotl > 0.3) {
        if (ndotl > 0.7) {
            light_intensity = diffuse_step_2;
        } else {
            light_intensity = diffuse_step_1;
        }
    } else {
        light_intensity = ambient_strength;
    }

    vec4 base_color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

    #ifdef P3D_ALPHA_TEST
    if (base_color.a < p3d_AlphaTest) {
        discard;
    }
    #endif

    vec3 desaturated = vec3(dot(base_color.rgb, vec3(0.3, 0.59, 0.11)));
    vec3 saturated_color = mix(desaturated, base_color.rgb, 1.6);

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

    float edge_intensity = color_edge * 4.0 + depth_edge * 300.0 + normal_edge * 1.5;

    edge_intensity = smoothstep(0.2, 0.6, edge_intensity);

    vec3 outline_color = vec3(0.05, 0.05, 0.1);
    final_color = mix(final_color, outline_color, edge_intensity * 0.75);

    if (light_intensity > 1.0) {
        float specular = pow(max(0.0, ndotl), 16.0) * 0.5;
        final_color += vec3(specular);
    }

    final_color = final_color * vec3(1.1, 1.05, 1.0);
    final_color = clamp(final_color, 0.0, 1.2);

    fragColor = vec4(final_color, base_color.a);
}