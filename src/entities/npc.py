from ursina import *
from direct.actor.Actor import Actor
from math import atan2, degrees
from src.utils.object_setup import setup_collidable_object

class AnimatedNPC:
    def __init__(self, start_pos, end_pos, speed=1, model_path='assets/models/Droid.glb',
                 anim_name=None, fix_orientation=True, scale=2.0, shrink_factor=0.8):
        self.start_pos = Vec3(start_pos)
        self.end_pos = Vec3(end_pos)
        self.speed = speed
        self.move_to_end = True
        self._scale = scale
        self._shrink_factor = shrink_factor

        # === Актёр ===
        self.actor = Actor(model_path)
        self.actor.reparent_to(scene)
        self.actor.set_scale(self._scale)
        self.actor.set_light_off()

        if fix_orientation:
            self.actor.set_p(0)

        self.actor.set_pos(Vec3(start_pos[0], start_pos[1] + 0.1, start_pos[2]))

        # Анимация
        if anim_name is None:
            anims = self.actor.get_anim_names()
            anim_name = anims[0] if anims else None
        if anim_name:
            self.actor.loop(anim_name)

        # === Коллайдер ===
        temp_ent = Entity(
            model=model_path,
            scale=self._scale,
            position=self.actor.get_pos(),
            enabled=False,
            visible=False
        )
        setup_collidable_object(temp_ent, shrink_factor=self._shrink_factor)
        self.collider_entity = temp_ent
        self.collider_entity.visible = False
        self.collider_entity.texture = None

    def set_scale(self, value):
        self._scale = value
        self.actor.set_scale(value)

        old_pos = self.collider_entity.position
        destroy(self.collider_entity)

        temp_ent = Entity(
            model=self.actor.get_model(),
            scale=value,
            position=old_pos,
            enabled=False,
            visible=False
        )
        setup_collidable_object(temp_ent, shrink_factor=self._shrink_factor)
        self.collider_entity = temp_ent
        self.collider_entity.visible = False

    def update(self):
        target = self.end_pos if self.move_to_end else self.start_pos
        current = Vec3(self.actor.get_x(), self.actor.get_y(), self.actor.get_z())
        direction = target - current

        if direction.length() <= self.speed * time.dt:
            self.move_to_end = not self.move_to_end
            new_pos = target
        else:
            direction = direction.normalized()
            new_pos = current + direction * self.speed * time.dt

        self.actor.set_pos(new_pos)

        # Поворот по направлению движения
        if direction.x != 0 or direction.z != 0:
            angle = atan2(direction.x, direction.z)
            self.actor.set_h(degrees(angle))

        # Синхронизация коллайдера с актёром
        self.collider_entity.position = Vec3(self.actor.get_x(), self.actor.get_y(), self.actor.get_z())

    def get_position(self):
        return Vec3(self.actor.get_x(), self.actor.get_y(), self.actor.get_z())