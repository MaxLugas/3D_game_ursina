from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath

# === Настройка путей ===
model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="Тест анимации: кадры и длительность", borderless=False, vsync=False)

actor = Actor('weapon_Glock.glb')
actor.reparent_to(scene)
actor.set_scale(1.6)

def get_anim_info(actor, anim_name):
    """
    Возвращает словарь с информацией об анимации:
    - frames: количество кадров
    - fps: частота кадров
    - duration: длительность в секундах
    """
    control = actor.get_anim_control(anim_name)
    if not control:
        return None

    anim = control.get_anim()
    if not anim:
        return None

    info = {
        'frames': None,
        'fps': None,
        'duration': None
    }

    # Попытка получить количество кадров
    if hasattr(anim, 'get_num_frames'):
        try:
            info['frames'] = anim.get_num_frames()
        except:
            pass

    # Попытка получить FPS
    if hasattr(control, 'get_frame_rate'):
        try:
            info['fps'] = control.get_frame_rate()
        except:
            pass

    # Попытка получить длительность напрямую
    if hasattr(anim, 'get_duration'):
        try:
            info['duration'] = anim.get_duration()
        except:
            pass

    # Если нет duration, но есть frames и fps
    if info['duration'] is None and info['frames'] is not None and info['fps'] is not None and info['fps'] > 0:
        info['duration'] = info['frames'] / info['fps']

    return info

# === Проверка анимации ===
anim_name = 'Armature|Reload|BaseLayer'
if anim_name in actor.get_anim_names():
    actor.loop(anim_name)
    info = get_anim_info(actor, anim_name)
    if info:
        print(f"\n📊 Информация об анимации '{anim_name}':")
        if info['frames'] is not None:
            print(f"   Количество кадров: {info['frames']}")
        else:
            print("   ❌ Не удалось определить количество кадров")

        if info['fps'] is not None:
            print(f"   Частота кадров (FPS): {info['fps']:.2f}")
        else:
            print("   ❌ Не удалось определить FPS")

        if info['duration'] is not None:
            print(f"   Длительность: {info['duration']:.3f} сек")
        else:
            print("   ❌ Не удалось определить длительность")
    else:
        print("❌ Не удалось получить информацию об анимации")
else:
    print(f"⚠️ Анимация '{anim_name}' не найдена!")

EditorCamera()
app.run()