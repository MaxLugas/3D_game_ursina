from ursina import Shader
from panda3d.core import Shader as Panda3DShader


comics_shaders = Shader(name='comics_shaders', language=Shader.GLSL,
                        vertex='''
    #version 140
    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat4 p3d_ModelMatrix;
    in vec4 p3d_Vertex;
    in vec3 p3d_Normal;
    in vec2 p3d_MultiTexCoord0;
    out vec3 world_normal;      // Нормаль в мировых координатах | Normal in world space
    out vec2 texcoord;          // UV-координаты текстуры | Texture UV coordinates
    out vec3 world_pos;         // Позиция вершины в мире | Vertex position in world space

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;  // Преобразование в экранные координаты | Transform to screen space
        world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);  // Перевод нормали в мировое пространство | Transform normal to world space
        texcoord = p3d_MultiTexCoord0;
        world_pos = (p3d_ModelMatrix * p3d_Vertex).xyz;  // Мировая позиция для цветовых акцентов | World position for color accents
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
        vec3 light_dir = normalize(vec3(0.7, 0.9, 0.6));          // Направление основного света | Main light direction
        float ndotl = max(0.0, dot(normalize(world_normal), light_dir));  // Интенсивность освещения | Lighting intensity

        // === СТИЛИЗОВАННОЕ ОСВЕЩЕНИЕ | STYLIZED LIGHTING ===
        // | STYLIZED LIGHTING (non-black shadows)
        float toon = 0.7;
        vec3 shadow_tint = vec3(0.4, 0.35, 0.6);  // Фиолетовый оттенок в тенях | Purple tint in shadows

        if (ndotl > 0.4) {
            toon = 0.72;
            shadow_tint = vec3(1.0);  // Полутень — нейтральный цвет | Mid-tone — neutral color
        }
        if (ndotl > 0.75) {
            toon = 1.0;               // Яркий свет | Bright light
            shadow_tint = vec3(1.0);
        }

        // === Базовая текстура с цветом материала | Base texture with material color ===
        vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

        // === ПОВЫШЕННАЯ НАСЫЩЕННОСТЬ (+50%) | INCREASED SATURATION (+50%) ===
        // 
        vec3 intensity = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));  // Яркость серого | Grayscale luminance
        vec3 saturated = mix(intensity, base.rgb, 1.5);  // Усиление цвета | Color boost

        // === Применение стилизованного освещения | Apply stylized lighting ===
        vec3 color = saturated * toon * shadow_tint;

        // === ПОВЫШЕННЫЙ КОНТРАСТ (+30%) | INCREASED CONTRAST (+30%) ===
        color = (color - 0.5) * 1.3 + 0.5;

        // === ВЕРТИКАЛЬНЫЙ ЦВЕТОВОЙ АКЦЕНТ (розово-оранжевый градиент) | VERTICAL COLOR ACCENT (pink-orange gradient) ===
        float height_factor = (world_pos.y * 0.1 + 0.5) * 0.6;  // Зависимость от высоты объекта | Height-dependent factor
        color = mix(color, color * vec3(1.45, 1.0, 0.82), height_factor);  // Теплый оттенок сверху | Warm tint on top

        // === ЗАЩИТА ОТ ПЕРЕСВЕТА И ЧЁРНОГО | CLAMP TO AVOID OVEREXPOSURE AND BLACK ===

        color = clamp(color, 0.1, 0.95);  // Минимум 0.1 — никакого чёрного | Minimum 0.1 — no pure black

        fragColor = vec4(color, base.a);  // Финальный цвет с прозрачностью | Final color with alpha
    }
    ''')

npc_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    vertex='''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat4 p3d_NormalMatrix;
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        out vec3 world_normal;
        out vec3 world_pos;
        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
            world_pos = (p3d_ModelMatrix * p3d_Vertex).xyz;
            world_normal = normalize(mat3(p3d_NormalMatrix) * p3d_Normal);
        }
    ''',
    fragment='''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        in vec3 world_normal;
        in vec3 world_pos;
        out vec4 fragColor;
        void main() {
            vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

            // === МАКСИМАЛЬНАЯ НАСЫЩЕННОСТЬ (+150%) ===
            vec3 intensity = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));
            vec3 saturated = mix(intensity, base.rgb, 2.5);  // +150% saturation

            // === ЭКСТРЕМАЛЬНЫЙ КОНТРАСТ (+80%) ===
            vec3 color = (saturated - 0.5) * 1.8 + 0.53;  // +0.03 яркости

            // === ЧЁРНЫЕ КОНТУРЫ ЧЕРЕЗ НОРМАЛИ (стиль комиксов) ===
            vec3 view_dir = normalize(vec3(0.0, 0.0, 1.0));  // упрощённое направление камеры
            float ndotv = abs(dot(normalize(world_normal), view_dir));
            float edge = 1.0 - ndotv;
            edge = smoothstep(0.75, 0.98, edge);  // резкие чёрные линии на краях

            // Применяем контуры: смешиваем с чёрным по краям
            color = mix(vec3(0.0), color, 1.0 - edge * 0.95);

            // === ФИНАЛЬНАЯ ЗАЩИТА ===
            color = clamp(color, 0.0, 1.0);

            fragColor = vec4(color, base.a);
        }
    '''
)

from panda3d.core import Shader as Panda3DShader

weapon_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    vertex='''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat4 p3d_NormalMatrix;
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        out vec3 world_normal;
        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
            world_normal = normalize(mat3(p3d_NormalMatrix) * p3d_Normal);
        }
    ''',
    fragment='''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        in vec3 world_normal;
        out vec4 fragColor;
        void main() {
            vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

            // === ЧИСТАЯ НАСЫЩЕННОСТЬ БЕЗ ИСКАЖЕНИЯ ЦВЕТОВ ===
            // Сохраняет оригинальный цвет, только усиливает его
            vec3 gray = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));
            vec3 color = gray + (base.rgb - gray) * 2.5;  // +150% saturation

            // === ЧЁРНЫЕ КОНТУРЫ ЧЕРЕЗ НОРМАЛИ ===
            vec3 view_dir = normalize(vec3(0.0, 0.0, 1.0));
            float edge = 1.0 - abs(dot(normalize(world_normal), view_dir));
            edge = smoothstep(0.8, 0.98, edge);
            color = mix(vec3(0.0), color, 1.0 - edge);

            // === ФИНАЛЬНАЯ ЗАЩИТА ===
            color = clamp(color, 0.0, 1.0);

            fragColor = vec4(color, base.a);
        }
    '''
)