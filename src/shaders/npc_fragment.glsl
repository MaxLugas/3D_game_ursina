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