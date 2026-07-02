from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath
from ursina.prefabs.first_person_controller import FirstPersonController

# === Настройка путей ===
model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="Pickup Test", borderless=False, vsync=True)

Sky(texture='sky_sunset')
DirectionalLight(shadows=True).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgb(0.6, 0.6, 0.6))

ground = Entity(
    model='plane',
    scale=50,
    texture='grass',
    collider='mesh',
    color=color.green.tint(-0.1)
)

cube = Entity(
    model='cube',
    color=color.orange,
    position=(0, 1, 5),
    scale=(1, 1, 1),
    collider='box'
)

player = FirstPersonController(speed=8, jump_height=2, gravity=1, position=(0, 1, 0))


def update():
    # Проверяем нажатие E
    if held_keys['e']:
        # Пускаем луч из центра экрана
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=5,  # Дистанция взаимодействия
            ignore=(player, ground)
            # Игнорируем игрока и землю, чтобы луч проходил сквозь них или не бился в землю сразу
        )

        if hit_info.hit:
            # Если попали в куб
            if hit_info.entity == cube:
                print("Куб подобран!")
                destroy(cube)


# Скрыть курсор
window.cursor_hidden = True

app.run()