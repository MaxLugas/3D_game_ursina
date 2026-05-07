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