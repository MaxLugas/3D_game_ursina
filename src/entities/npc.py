from ursina import *
from direct.actor.Actor import Actor
from math import atan2, degrees
from src.utils.object_setup import setup_collidable_object
from src.core.config import COLLIDER_SHRINK_FACTOR, NPC_SPEED_WALK, MODELS_DIR, NPC_IDLE_DISTANCE
from src.shaders.comics_shader import comics_shaders


class AnimatedNPC:
    def __init__(self, start_pos, end_pos, player, speed=NPC_SPEED_WALK, model_path=f'{MODELS_DIR}/Droid.glb',
                 walk_anim='Walking', idle_anim='Idle', fix_orientation=True, scale=2.0, shrink_factor=COLLIDER_SHRINK_FACTOR):
        """
        Инициализация анимированного NPC с перемещением между двумя точками и остановкой при столкновении с игроком.
        | Initialize animated NPC moving between two points with stop-on-collision behavior.
        """
        self.start_pos = Vec3(start_pos)
        self.end_pos = Vec3(end_pos)
        self.player = player                                   # Ссылка на игрока для проверки столкновений | Player reference for collision checks
        self.speed = speed
        self.move_to_end = True                                # Флаг направления движения | Movement direction flag
        self._scale = scale
        self._shrink_factor = shrink_factor
        self.is_blocked = False                                # Флаг столкновения с игроком | Collision flag with player

        # === Актёр | Actor creation ===
        self.actor = Actor(model_path)
        self.actor.reparent_to(scene)
        self.actor.set_scale(self._scale)
        self.actor.set_light_off()                             # Отключаем динамическое освещение | Disable dynamic lighting
        self.actor.set_shader(comics_shaders._shader)

        if fix_orientation:
            self.actor.set_p(0)
        self.actor.set_pos(Vec3(start_pos[0], start_pos[1] + 0.1, start_pos[2]))

        # Анимации | Animations
        self.walk_anim = walk_anim
        self.idle_anim = idle_anim
        available = set(self.actor.get_anim_names())

        # Проверка доступных анимаций | Validate available animations
        if self.walk_anim not in available:
            self.walk_anim = next(iter(available)) if available else None

        if self.idle_anim not in available:
            self.idle_anim = self.walk_anim

        # Стартовая анимация | Start animation
        if self.walk_anim:
            self.actor.loop(self.walk_anim)

        # === Коллайдер | Collider setup ===
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

        # Сохраняем текущую цель для возобновления движения | Remember current target for resuming movement
        self.current_target = self.end_pos

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
        # === Проверка столкновения с игроком | Player collision check ===
        npc_pos = Vec3(self.actor.get_x(), self.actor.get_y(), self.actor.get_z())
        player_pos = self.player.position
        dist_to_player = (npc_pos - player_pos).length()

        # Остановка при близком расстоянии |  Stop at close range
        if dist_to_player < 1.8:
            if not self.is_blocked:
                self.is_blocked = True
                # Сохраняем текущую цель перед остановкой | Save current target before stopping
                self.current_target = self.end_pos if self.move_to_end else self.start_pos
                # Воспроизвести анимацию ожидания | Play idle animation
                if self.idle_anim and self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
        # Возобновление движения после отхода игрока | Start moving after player's departure
        elif dist_to_player > 2.0 and self.is_blocked:
            self.is_blocked = False
            # Вернуть анимацию ходьбы | Resume walking animation
            if self.walk_anim and self.walk_anim in self.actor.get_anim_names():
                self.actor.loop(self.walk_anim)

        # === Движение (пропускаем, если заблокирован) | Movement (skip if blocked) ===
        if not self.is_blocked:
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

            # Поворот модели по направлению движения (только по горизонтали) | Rotate model to face movement direction (horizontal only)
            if direction.x != 0 or direction.z != 0:
                angle = atan2(direction.x, direction.z)
                self.actor.set_h(degrees(angle))

        self.collider_entity.position = Vec3(self.actor.get_x(), self.actor.get_y(), self.actor.get_z())

    def get_position(self):
        return Vec3(self.actor.get_x(), self.actor.get_y(), self.actor.get_z())