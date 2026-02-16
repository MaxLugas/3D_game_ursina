from panda3d.core import getModelPath
from ursina import *
from src.core.config import GROUND_SCALE, WINDOW_TITLE, WINDOW_BORDERLESS, WINDOW_VSYNC, SHOW_COLLIDERS, ASSETS_DIR, \
    DIRECTIONAL_LIGHT_DIRECTION, SKY_TEXTURE, AMBIENT_LIGHT_COLOR, DIRECTIONAL_LIGHT_COLOR, GRASS_TEXTURE, MODELS_DIR
from src.shaders.comics_shader import comics_shaders, ground_shader_panda


def init_engine():
    """Инициализация игрового движка и базовой сцены. | Initialize game engine and base scene."""
    app = Ursina(
        title=WINDOW_TITLE,
        borderless=WINDOW_BORDERLESS,
        vsync=WINDOW_VSYNC,
        asset_folder=ASSETS_DIR
    )
    getModelPath().append_directory(str(MODELS_DIR))   # Путь к моделям для загрузчика Panda3D | Add models path for Panda3D loader

    window.show_colliders = SHOW_COLLIDERS             # Отладка: отображение коллайдеров | Debug: show colliders
    window.cursor_hidden = True                        # Скрыть курсор мыши | Hide mouse cursor

    # === Окружение | Environment ===
    Sky(texture=SKY_TEXTURE)                           # Текстура неба | Sky texture
    sun = DirectionalLight(shadows=True, color=DIRECTIONAL_LIGHT_COLOR)  # Направленный свет с тенями | Directional light with shadows
    sun.look_at(DIRECTIONAL_LIGHT_DIRECTION)           # Ориентация солнца | Sun direction
    AmbientLight(color=AMBIENT_LIGHT_COLOR)            # Фоновое освещение для заполнения теней | Ambient light to fill shadows

    # === Игровая площадка | Ground plane ===
    ground = Entity(
        model='plane',
        scale=GROUND_SCALE,
        texture=GRASS_TEXTURE,
        texture_scale=(40, 40),                        # Повторение текстуры для естественного вида | Texture tiling for natural look
        collider='box',                                # Коллайдер для земли | Ground collider
        shader=ground_shader_panda,                         # Кастомный шейдер для стилизации | Custom shader
        color=color.green.tint(-0.1)
    )

    return app