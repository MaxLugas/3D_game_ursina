#version 140
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

#ifdef P3D_ALPHA_TEST
uniform float p3d_AlphaTest;
#endif

in vec2 texcoord;
in vec3 world_normal;
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
    vec3 color = gray + (base.rgb - gray) * 2.5;
    color *= light;

    vec3 view_dir = normalize(-view_pos);
    float edge = 1.0 - abs(dot(normal, view_dir));
    edge = smoothstep(0.8, 0.98, edge);
    color = mix(vec3(0.0), color, 1.0 - edge);

    color = clamp(color, 0.0, 1.0);

    fragColor = vec4(color, base.a);
}