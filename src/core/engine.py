from ursina import *
from pathlib import Path
from ursina.shaders import lit_with_shadows_shader
from src.core.config import GROUND_SCALE, WINDOW_TITLE, WINDOW_BORDERLESS, WINDOW_VSYNC, SHOW_COLLIDERS, ASSETS_DIR, \
    DIRECTIONAL_LIGHT_DIRECTION, SKY_TEXTURE, AMBIENT_LIGHT_COLOR, DIRECTIONAL_LIGHT_COLOR, GRASS_TEXTURE


def init_engine():
    app = Ursina(
        title=WINDOW_TITLE,
        borderless=WINDOW_BORDERLESS,
        vsync=WINDOW_VSYNC,
        asset_folder=ASSETS_DIR
    )
    window.show_colliders = SHOW_COLLIDERS

    Sky(texture=SKY_TEXTURE)
    sun = DirectionalLight(shadows=True, color=DIRECTIONAL_LIGHT_COLOR)
    sun.look_at(DIRECTIONAL_LIGHT_DIRECTION)
    AmbientLight(color=AMBIENT_LIGHT_COLOR)

    ground = Entity(
        model='plane',
        scale=GROUND_SCALE,
        texture=GRASS_TEXTURE,
        texture_scale=(40, 40),
        collider='box',
        # shader=lit_with_shadows_shader,
        color=color.green.tint(-0.1)
    )

    return app