from ursina import *
from direct.actor.Actor import Actor
from panda3d.core import getModelPath

model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(
    title="Тест анимации",
    borderless=False,
    vsync=False
)

print("Доступные анимации:")
try:
    temp_actor = Actor('Droid.glb')
    anims = temp_actor.get_anim_names()
    for name in anims:
        print(f" - '{name}'")
    temp_actor.cleanup()
    temp_actor.remove_node()
except Exception as e:
    print("❌ Ошибка при проверке:", e)

# Основной актёр
actor = Actor('Droid.glb')
actor.reparent_to(scene)
actor.set_scale(1.6)

anim_name = 'Idle'
if anim_name in actor.get_anim_names():
    actor.loop(anim_name)
else:
    print(f"⚠️ Анимация '{anim_name}' не найдена!")

EditorCamera()
app.run()