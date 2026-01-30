from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath

# === Настройка путей ===
model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="Покадровая анимация", borderless=False, vsync=False)

actor = Actor('weapon_Glock.glb')
actor.reparent_to(scene)
actor.set_scale(1.6)

# === Параметры анимации ===
anim_name = 'Armature|Fire|BaseLayer'
current_frame = 0
total_frames = None

# Получаем информацию об анимации
if anim_name in actor.get_anim_names():
    control = actor.get_anim_control(anim_name)
    if control and control.get_anim() and hasattr(control.get_anim(), 'get_num_frames'):
        total_frames = control.get_anim().get_num_frames()
        print(f"✅ Анимация '{anim_name}' найдена. Всего кадров: {total_frames}")
    else:
        print("⚠️ Не удалось определить количество кадров")
else:
    print(f"❌ Анимация '{anim_name}' не найдена!")

# Устанавливаем начальный кадр
if total_frames is not None:
    actor.pose(anim_name, current_frame)
    print(f"▶ Начальный кадр: {current_frame}")

# === Обновление по нажатию ===
def input(key):
    global current_frame
    if key == 'e' and total_frames is not None:
        current_frame += 1
        if current_frame >= total_frames:
            current_frame = 0
        actor.pose(anim_name, current_frame)
        print(f"🎬 Кадр: {current_frame}")

EditorCamera()
app.run()