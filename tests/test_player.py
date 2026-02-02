from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath
from ursina.prefabs.first_person_controller import FirstPersonController

# === Настройка путей ===
model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="FPS Weapon Test", borderless=False, vsync=True)

# Небо и освещение
Sky(texture='sky_sunset')
DirectionalLight(shadows=True).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgb(0.6, 0.6, 0.6))

# Пол
ground = Entity(
    model='plane',
    scale=50,
    texture='grass',
    collider='mesh',
    color=color.green.tint(-0.1)
)

# Игрок
player = FirstPersonController(speed=8, jump_height=2, gravity=1, position=(0, 1, 0))

# === Класс FPS Weapon ===
class FPSWeapon:
    def __init__(self, model_path='weapon_Glock.glb', scale=2):
        self.holder = camera.attach_new_node("fps_weapon")
        self.holder.set_pos(0.25, -1.36, 0.7)
        self.holder.set_hpr(190, 0, 0)

        self.actor = Actor(model_path)
        self.actor.reparent_to(self.holder)
        self.actor.set_scale(scale)
        self.actor.set_light_off(True)

        self.anim_names = {
            'draw': 'Armature|Draw|BaseLayer',
            'holster': 'Armature|Holster|BaseLayer',
            'fire': 'Armature|Fire|BaseLayer',
            'reload': 'Armature|Reload|BaseLayer',
            'reload_empty': 'Armature|ReloadEmpty|BaseLayer',
            'slide_back': 'Armature|SlideBack|BaseLayer'
        }

        available = set(self.actor.get_anim_names())
        for name, anim in self.anim_names.items():
            if anim not in available:
                print(f"⚠️ Анимация '{name}' ('{anim}') не найдена!")
        self.available = available

        # Состояние оружия
        self.is_animating = False
        self.shots_fired = 0          # ← добавлено
        self.magazine_size = 5        # ← максимум 5 выстрелов

        # Сразу достаём
        if 'fire' in self.anim_names and self.anim_names['fire'] in self.available:
            self.actor.pose(self.anim_names['fire'], 105)

    def play_animation(self, action_key):
        if self.is_animating:
            return

        # ←←← ДОБАВЛЕНО: блокируем стрельбу, если магазин пуст
        if action_key == 'fire' and self.shots_fired >= self.magazine_size:
            return

        anim_name = self.anim_names.get(action_key)
        if not (anim_name and anim_name in self.available):
            return

        self.is_animating = True

        if action_key == 'fire':
            from_frame = 86
            to_frame = 105
            self.actor.play(anim_name, fromFrame=from_frame, toFrame=to_frame)

            num_frames = to_frame - from_frame
            fps = 60
            duration = num_frames / fps

            invoke(self._on_fire_animation_end, anim_name, delay=duration)

            self.shots_fired += 1
            if self.shots_fired >= self.magazine_size:
                invoke(self._start_reload_after_empty, delay=duration + 0.1)

        else:
            self.actor.play(anim_name)
            frame_count = self.actor.get_num_frames(anim_name)
            duration = frame_count / 60
            invoke(self._on_animation_end, anim_name, delay=duration)

    def _start_reload_after_empty(self):
        self.play_animation('reload')

    def _on_fire_animation_end(self, anim_name):
        self.actor.pose(anim_name, 105)
        self.is_animating = False

    def _on_animation_end(self, anim_name):
        self.is_animating = False
        # Если завершилась перезарядка — сбросить счётчик
        if anim_name == self.anim_names.get('reload'):
            self.shots_fired = 0

    def update(self):
        if not self.is_animating:
            if mouse.left:
                self.play_animation('fire')
            if held_keys['r']:
                self.play_animation('reload')

# Создаём оружие
weapon = FPSWeapon(model_path='weapon_Glock.glb', scale=0.8)

def update():
    weapon.update()

# Скрыть курсор
window.cursor_hidden = True

app.run()