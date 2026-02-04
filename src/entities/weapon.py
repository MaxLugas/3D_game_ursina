from ursina import *
from direct.actor.Actor import Actor
from src.core.config import (
    GLOCK_WEAPON_MODEL,
    GLOCK_MAGAZINE_SIZE,
    GLOCK_WEAPON_SCALE,
    ANIM_FPS,
    FIRE_ANIM_START_FRAME,
    FIRE_ANIM_END_FRAME,
    SOUND_GLOCK_FIRE,
    SOUND_GLOCK_RELOAD,
    RELOAD_PITCH, MODELS_DIR
)

class FPSWeapon:
    def __init__(self, model_path=MODELS_DIR/GLOCK_WEAPON_MODEL, scale=2):
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
        self.magazine_size = GLOCK_MAGAZINE_SIZE

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
