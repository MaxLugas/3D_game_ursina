from panda3d.core import getModelPath
from ursina import *
from src.core.config import GROUND_SCALE, WINDOW_TITLE, WINDOW_BORDERLESS, WINDOW_VSYNC, SHOW_COLLIDERS, ASSETS_DIR, \
    DIRECTIONAL_LIGHT_DIRECTION, SKY_TEXTURE, AMBIENT_LIGHT_COLOR, DIRECTIONAL_LIGHT_COLOR, GRASS_TEXTURE, MODELS_DIR
from src.shaders.shader_loader import ground_shader_panda


GROUND_TILE_COUNT = 15


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

    # === Коллайдер земли (невидимый, вся карта) | Ground collider (invisible, full map) ===
    ground_collider = Entity(
        model='plane',
        scale=GROUND_SCALE,
        collider='box',
        visible=False,
    )

    return app


def create_ground_tiles():
    """Создаёт тайлы земли с шейдером. | Create ground tiles with shader."""
    tiles = []
    tile_size = GROUND_SCALE / GROUND_TILE_COUNT
    half = GROUND_SCALE / 2
    density = 40 / GROUND_SCALE

    for ix in range(GROUND_TILE_COUNT):
        for iz in range(GROUND_TILE_COUNT):
            x = -half + tile_size / 2 + ix * tile_size
            z = -half + tile_size / 2 + iz * tile_size
            tile = Entity(
                model='plane',
                scale=tile_size,
                position=(x, 0, z),
                texture=GRASS_TEXTURE,
                texture_scale=(tile_size * density, tile_size * density),
                texture_offset=(x * density, z * density),
                shader=ground_shader_panda,
                color=color.green.tint(-0.1),
                is_ground_tile=True,
            )
            tiles.append(tile)
    return tiles