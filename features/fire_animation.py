from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import application

from src.core.config import PLAYER_SPEED, PLAYER_JUMP_HEIGHT, PLAYER_GRAVITY, GLOCK_WEAPON_MODEL, GLOCK_MAGAZINE_SIZE, \
    SKY_TEXTURE, GRASS_TEXTURE, DIRECTIONAL_LIGHT_DIRECTION, AMBIENT_LIGHT_COLOR

application.asset_folder = Path(__file__).parent.parent / 'src' / 'assets'

# === Настройка путей ===
model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="FPS Weapon Test", borderless=False, vsync=True)

# Небо и освещение
Sky(texture=SKY_TEXTURE)
DirectionalLight(shadows=True).look_at(DIRECTIONAL_LIGHT_DIRECTION)
AmbientLight(color=AMBIENT_LIGHT_COLOR)

# Пол
ground = Entity(
    model='plane',
    scale=50,
    texture=GRASS_TEXTURE,
    collider='mesh',
    color=color.green.tint(-0.1)
)

# Игрок
player = FirstPersonController(speed=PLAYER_SPEED, jump_height=PLAYER_JUMP_HEIGHT, gravity=PLAYER_GRAVITY, position=(0, 1, 0))

# === Класс FPS Weapon ===
class FPSWeapon:
    def __init__(self, model_path=GLOCK_WEAPON_MODEL, scale=2):
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
        self.shots_fired = 0
        self.magazine_size = GLOCK_MAGAZINE_SIZE        # ← максимум N выстрелов

        # Сразу достаём
        if 'fire' in self.anim_names and self.anim_names['fire'] in self.available:
            self.actor.pose(self.anim_names['fire'], 105)

        self.fire_sound = Audio('audio/Glock_fire', autoplay=False)
        self.reload_sound = Audio('audio/Glock_reload', autoplay=False, pitch=0.62)

    def play_animation(self, action_key):
        if self.is_animating:
            return

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

            self.fire_sound.play()

        else:
            self.actor.play(anim_name)
            frame_count = self.actor.get_num_frames(anim_name)
            duration = frame_count / 60
            invoke(self._on_animation_end, anim_name, delay=duration)

            if action_key in 'reload':
                self.reload_sound.play()

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
weapon = FPSWeapon(model_path=GLOCK_WEAPON_MODEL, scale=0.8)

def update():
    weapon.update()

# Скрыть курсор
window.cursor_hidden = True

app.run()