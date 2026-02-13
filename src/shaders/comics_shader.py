from ursina import Shader
from panda3d.core import Shader as Panda3DShader

comics_shaders = Shader(name='comics_shaders', language=Shader.GLSL,
                        vertex='''
    #version 140
    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat4 p3d_ModelMatrix;
    uniform mat4 p3d_NormalMatrix;
    uniform vec3 camera_position;
    in vec4 p3d_Vertex;
    in vec3 p3d_Normal;
    in vec2 p3d_MultiTexCoord0;
    out vec3 world_normal;
    out vec2 texcoord;
    out vec3 world_pos;
    out vec3 view_dir;

    void main() {
        vec4 world_vertex = p3d_ModelMatrix * p3d_Vertex;
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        world_normal = normalize(mat3(p3d_NormalMatrix) * p3d_Normal);
        texcoord = p3d_MultiTexCoord0;
        world_pos = world_vertex.xyz;
        view_dir = normalize(camera_position - world_pos);
    }
    ''',
                        fragment='''
    #version 140
    uniform sampler2D p3d_Texture0;
    uniform vec4 p3d_ColorScale;
    uniform vec3 camera_position;
    in vec3 world_normal;
    in vec2 texcoord;
    in vec3 world_pos;
    in vec3 view_dir;
    out vec4 fragColor;

    void main() {
        vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
        if (base.a < 0.01) discard;

        // === CEL-SHADING: 3 ДИСКРЕТНЫХ УРОВНЯ ОСВЕЩЕНИЯ | 3 DISCRETE LIGHT LEVELS ===
        vec3 light_dir = normalize(vec3(0.7, 0.9, 0.6));
        float ndotl = dot(normalize(world_normal), light_dir);

        // Ступенчатая функция вместо плавных переходов
        float toon = 0.45;  // Тень
        if (ndotl > 0.4) toon = 0.85;  // Полутень
        if (ndotl > 0.8) toon = 1.0;   // Свет

        // === БАЗОВЫЙ ЦВЕТ БЕЗ ПЛАВНЫХ ГРАДИЕНТОВ | FLAT BASE COLOR ===
        vec3 color = base.rgb * toon;

        // === ЧЁРНЫЕ КОНТУРЫ (толщина зависит от угла к камере) | BLACK OUTLINES ===
        float ndotv = abs(dot(normalize(world_normal), normalize(view_dir)));
        float edge = 1.0 - ndotv;
        if (edge > 0.85) color = vec3(0.0, 0.0, 0.0);  // Резкий чёрный контур

        // === ЗАЩИТА ОТ ПЕРЕСВЕТА | CLAMP ===
        color = clamp(color, 0.0, 1.0);

        fragColor = vec4(color, base.a);
    }
    ''')

npc_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    vertex='''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat4 p3d_NormalMatrix;
        uniform vec3 camera_position;
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        out vec3 world_normal;
        out vec3 world_pos;
        out vec3 view_dir;

        void main() {
            vec4 world_vertex = p3d_ModelMatrix * p3d_Vertex;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
            world_pos = world_vertex.xyz;
            world_normal = normalize(mat3(p3d_NormalMatrix) * p3d_Normal);
            view_dir = normalize(camera_position - world_pos);
        }
    ''',
    fragment='''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        in vec3 world_normal;
        in vec3 world_pos;
        in vec3 view_dir;
        out vec4 fragColor;

        void main() {
            vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
            if (base.a < 0.01) discard;

            // === CEL-SHADING: 2 УРОВНЯ (тень/свет) | 2-LEVEL CEL-SHADING ===
            vec3 light_dir = normalize(vec3(0.7, 0.9, 0.6));
            float ndotl = dot(normalize(world_normal), light_dir);
            float toon = step(0.5, ndotl);  // 0.0 или 1.0 — резкий переход

            // Плоский цвет без насыщенности/контраста
            vec3 color = base.rgb * mix(0.5, 1.0, toon);  // Тень = 50%, Свет = 100%

            // === ЧЁРНЫЕ КОНТУРЫ | BLACK OUTLINES ===
            float ndotv = abs(dot(normalize(world_normal), normalize(view_dir)));
            if (1.0 - ndotv > 0.82) color = vec3(0.0);

            color = clamp(color, 0.0, 1.0);
            fragColor = vec4(color, base.a);
        }
    '''
)

weapon_shader_panda = Panda3DShader.make(
    Panda3DShader.SL_GLSL,
    vertex='''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat4 p3d_NormalMatrix;
        uniform vec3 camera_position;
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        out vec3 world_normal;
        out vec3 view_dir;

        void main() {
            vec4 world_vertex = p3d_ModelMatrix * p3d_Vertex;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
            world_normal = normalize(mat3(p3d_NormalMatrix) * p3d_Normal);
            view_dir = normalize(camera_position - world_vertex.xyz);
        }
    ''',
    fragment='''
        #version 140
        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        in vec3 world_normal;
        in vec3 view_dir;
        out vec4 fragColor;

        void main() {
            vec4 base = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
            if (base.a < 0.01) discard;

            // === CEL-SHADING: МИНИМАЛИСТИЧНЫЙ (2 уровня) | MINIMALIST CEL-SHADING ===
            vec3 light_dir = normalize(vec3(0.0, 0.0, 1.0));  // Свет сверху для оружия
            float ndotl = dot(normalize(world_normal), light_dir);
            float toon = step(0.3, ndotl) * 0.7 + 0.3;  // 30% тень, 100% свет

            vec3 color = base.rgb * toon;

            // === ТОЛСТЫЕ ЧЁРНЫЕ КОНТУРЫ | THICK BLACK OUTLINES ===
            float ndotv = abs(dot(normalize(world_normal), normalize(view_dir)));
            if (1.0 - ndotv > 0.75) color = vec3(0.0);  // Более толстые линии

            color = clamp(color, 0.0, 1.0);
            fragColor = vec4(color, base.a);
        }
    '''
)