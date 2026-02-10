from ursina import Shader

comics_shaders = Shader(name='comics_shaders', language=Shader.GLSL,
                        vertex='''
    #version 140
    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat4 p3d_ModelMatrix;
    in vec4 p3d_Vertex;
    in vec3 p3d_Normal;
    in vec2 p3d_MultiTexCoord0;
    out vec3 world_normal;
    out vec2 texcoord;
    out vec3 world_pos;

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
        texcoord = p3d_MultiTexCoord0;
        world_pos = (p3d_ModelMatrix * p3d_Vertex).xyz;
    }
    ''',
                        fragment='''
    #version 140
    uniform sampler2D p3d_Texture0;
    uniform vec4 p3d_ColorScale;
    in vec3 world_normal;
    in vec2 texcoord;
    in vec3 world_pos;
    out vec4 fragColor;

    void main() {
        vec3 light_dir = normalize(vec3(0.7, 0.9, 0.6));
        float ndotl = max(0.0, dot(normalize(world_normal), light_dir));

        // === CEL-SHADING С ЦВЕТНЫМИ ТЕНЯМИ (не чёрными!) ===
        // Минимальная яркость 0.7 вместо 0.2 — тени серо-фиолетовые, а не чёрные
        float toon = 0.7;
        vec3 shadow_tint = vec3(0.4, 0.35, 0.6);  // Фиолетовый оттенок для глубины

        if (ndotl > 0.4) {
            toon = 0.72;
            shadow_tint = vec3(1.0);  // Нейтральный цвет в полусвете
        }
        if (ndotl > 0.75) {
            toon = 1.0;
            shadow_tint = vec3(1.0);  // Полный свет
        }

        // Базовая текстура
        vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

        // === НАСЫЩЕННОСТЬ (+90%) ===
        vec3 intensity = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));
        vec3 saturated = mix(intensity, base.rgb, 1.5);

        // Применяем освещение с цветными тенями
        vec3 color = saturated * toon * shadow_tint;

        // === КОНТРАСТ (+35%) ===
        color = (color - 0.5) * 1.3 + 0.5;

        // === ЦВЕТОВОЙ АКЦЕНТ (розово-оранжевый градиент по высоте) ===
        float height_factor = (world_pos.y * 0.1 + 0.5) * 0.6;
        color = mix(color, color * vec3(1.45, 1.0, 0.82), height_factor);

        // === ЗАЩИТА ОТ ПЕРЕСВЕТА ===
        color = clamp(color, 0.1, 0.95);  // Минимум 0.1 вместо 0.0 — никакого чёрного!

        fragColor = vec4(color, base.a);
    }
    ''')
