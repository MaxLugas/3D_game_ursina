from ursina import *
from pathlib import Path

def init_engine():
    app = Ursina(title="Game", borderless=False, vsync=False, asset_folder=Path(__file__).parent / 'assets')
    window.show_colliders = True

    Sky(texture='sky_sunset')
    sun = DirectionalLight(shadows=True)
    sun.look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgb(0.6, 0.6, 0.6))

    ground = Entity(
        model='plane',
        scale=70,
        texture='grass',
        texture_scale=(8, 8),
        collider='mesh',
        color=color.green.tint(-0.1)
    )

    return app