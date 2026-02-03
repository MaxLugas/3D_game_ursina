from ursina import *
from pathlib import Path
from src.core.config import GROUND_SCALE, WINDOW_TITLE, WINDOW_BORDERLESS, WINDOW_VSYNC, SHOW_COLLIDERS, ASSETS_DIR


def init_engine():
    app = Ursina(
        title=WINDOW_TITLE,
        borderless=WINDOW_BORDERLESS,
        vsync=WINDOW_VSYNC,
        asset_folder=ASSETS_DIR
    )
    window.show_colliders = SHOW_COLLIDERS

    Sky(texture='sky_sunset')
    sun = DirectionalLight(shadows=True)
    sun.look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgb(0.6, 0.6, 0.6))

    ground = Entity(
        model='plane',
        scale=GROUND_SCALE,
        texture='grass',
        texture_scale=(8, 8),
        collider='mesh',
        color=color.green.tint(-0.1)
    )

    return app