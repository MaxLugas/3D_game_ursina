from ursina import *
from direct.actor.Actor import Actor
from src.core.destructibles import DESTRUCTIBLE_OBJECTS
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
from src.shaders.comics_shader import comics_shaders
from src.core.config import SPECULAR_FACTOR

class FPSWeapon:
    def __init__(self, model_path=MODELS_DIR/GLOCK_WEAPON_MODEL, scale=GLOCK_WEAPON_SCALE):
        self.holder = camera.attach_new_node("fps_weapon")
        self.holder.set_pos(0.25, -1.36, 0.7)
        self.holder.set_hpr(190, 0, 0)

        self.actor = Actor(model_path)
        self.actor.reparent_to(self.holder)
        self.actor.set_scale(scale)
        self.actor.set_light_off(True)

        # === ПРИМЕНЯЕМ КОМИКСНЫЙ ШЕЙДЕР ===
        self.actor.set_shader(comics_shaders._shader)
        # self.actor.set_shader_input("specular_factor", SPECULAR_FACTOR)

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

        self.ammo_text = Text(
            text=self._get_ammo_text(),
            origin=(0, 0),
            position=window.bottom_right + Vec2(-0.13, 0.1),
            scale=1,
            color=color.white,
            background=True,
            parent=camera.ui
        )

        # Начальная поза
        if 'fire' in self.anim_names and self.anim_names['fire'] in self.available:
            self.actor.pose(self.anim_names['fire'], FIRE_ANIM_END_FRAME)

        # Звуки
        self.fire_sound = Audio(SOUND_GLOCK_FIRE, autoplay=False)
        self.reload_sound = Audio(SOUND_GLOCK_RELOAD, autoplay=False, pitch=RELOAD_PITCH)


    def _get_ammo_text(self):
        remaining = self.magazine_size - self.shots_fired
        return f"Патроны: {remaining}/{self.magazine_size}"

    def _update_ammo_display(self):
        if self.ammo_text:
            self.ammo_text.text = self._get_ammo_text()

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
            from_frame = FIRE_ANIM_START_FRAME
            to_frame = FIRE_ANIM_END_FRAME
            self.actor.play(anim_name, fromFrame=from_frame, toFrame=to_frame)

            num_frames = to_frame - from_frame
            duration = num_frames / ANIM_FPS
            invoke(self._on_fire_animation_end, anim_name, delay=duration)

            self.shots_fired += 1
            self._update_ammo_display()

            if self.shots_fired >= self.magazine_size:
                invoke(self._start_reload_after_empty, delay=duration + 0.1)

            self.fire_sound.play()

            # === Проверка попадания в разрушаемые объекты ===
            hit_info = raycast(
                origin=camera.world_position,
                direction=camera.forward,
                distance=100,
                ignore=(camera,)
            )
            if hit_info.hit:
                entity = hit_info.entity
                model_name = entity.model.name if entity.model else None
                if model_name in DESTRUCTIBLE_OBJECTS:
                    destroy(entity)

        else:
            self.actor.play(anim_name)
            frame_count = self.actor.get_num_frames(anim_name)
            duration = frame_count / ANIM_FPS
            invoke(self._on_animation_end, anim_name, delay=duration)

            if action_key == 'reload':
                self.reload_sound.play()

    def _start_reload_after_empty(self):
        self.play_animation('reload')

    def _on_fire_animation_end(self, anim_name):
        self.actor.pose(anim_name, FIRE_ANIM_END_FRAME)
        self.is_animating = False

    def _on_animation_end(self, anim_name):
        self.is_animating = False
        if anim_name == self.anim_names.get('reload'):
            self.shots_fired = 0
            self._update_ammo_display()

    def update(self):
        if not self.is_animating:
            if mouse.left:
                self.play_animation('fire')
            if held_keys['r']:
                self.play_animation('reload')