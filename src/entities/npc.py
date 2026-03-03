from ursina import *
from direct.actor.Actor import Actor
from math import atan2, degrees
import math
import random
from collections import deque

from src.core.config import (
    NPC_SPEED_WALK, NPC_SPEED_RUN_1, NPC_ATTACK_DISTANCE, NPC_IDLE_DISTANCE, NPC_ATTACK_TRIGGER_DISTANCE,
    MODELS_DIR, COLLIDER_SHRINK_FACTOR, NPC_MIN_CHASE_DISTANCE, NPC_WALK_ANIM, NPC_RUN_ANIM_1, NPC_SKILL_ANIM,
    NPC_IDLE_ANIM, NPC_ATTACK_ANIM_1, NPC_RUN_ANIM_2, NPC_SPEED_RUN_2

)
from src.shaders.comics_shader import npc_shader_panda
from src.utils.object_setup import setup_collidable_object


class AnimatedNPC:
    def __init__(self, start_pos, player, model_path=f'{MODELS_DIR}/droid.glb',
                 idle_anim=NPC_IDLE_ANIM, walk_anim=NPC_WALK_ANIM, run_anim_1=NPC_RUN_ANIM_1, run_anim_2=NPC_RUN_ANIM_2,
                 skill_anim=NPC_SKILL_ANIM, attack_anim_1=NPC_ATTACK_ANIM_1, fix_orientation=True, scale=2.0,
                 speed_walk=NPC_SPEED_WALK, speed_run_1=NPC_SPEED_RUN_1, speed_run_2=NPC_SPEED_RUN_2,
                 shrink_factor=COLLIDER_SHRINK_FACTOR):

        self.player = player
        self.speed_walk = speed_walk
        self.speed_run_1 = speed_run_1
        self.speed_run_2 = speed_run_2
        self._scale = scale
        self._shrink_factor = shrink_factor
        self.model_path = model_path

        # Состояния NPC | NPC states
        self.state = idle_anim

        # Флаг для однократного взаимодействия | One-time interaction flag
        self.talked = False

        self.skill_used = False

        # === Память препятствий | Obstacle memory===
        self.obstacle_memory = {}  # Словарь: позиция -> время запоминания | Dictionary: position -> memorization time
        self.memory_duration = 5.0
        self.last_obstacle_pos = None
        self.stuck_time = 0
        self.stuck_threshold = 2.0
        self.last_positions = deque(maxlen=10)

        # === Параметры поиска пути | Path Search Parameters===
        self.path_nodes = []
        self.current_path_index = 0
        self.path_update_timer = 0
        self.path_update_interval = 1.0

        # === Предсказание позиции игрока | Predicting the player's position ===
        self.last_player_pos = self.player.position if player else Vec3(0, 0, 0)
        self.player_velocity = Vec3(0, 0, 0)
        self.player_prediction_time = 0.5  # Предсказывать на 0.5 секунд вперед | Predict 0.5 seconds ahead

        # Создаём родительский узел для контроля позиции и поворота | Create parent node for position and rotation control
        self.npc_node = render.attach_new_node("npc_root")
        self.npc_node.set_pos(Vec3(start_pos[0], start_pos[1], start_pos[2]))

        # Загружаем актёра как дочерний объект | Load actor as child object
        self.actor = Actor(model_path)
        self.actor.reparent_to(self.npc_node)
        self.actor.set_scale(self._scale)
        self.actor.set_light_off()  # Отключаем динамическое освещение | Disable dynamic lighting
        self.actor.set_shader(npc_shader_panda)  # Применяем комикс-шейдер | Apply comic shader

        if fix_orientation:
            self.actor.set_p(0)  # Исправляем наклон | Fix pitch
        self.actor.set_pos(0, 0, 0)

        # Имена анимаций | Animation names
        self.idle_anim = idle_anim
        self.walk_anim = walk_anim
        self.run_anim_1 = run_anim_1
        self.run_anim_2 = run_anim_2
        self.skill_anim = skill_anim
        self.attack_anim_1 = attack_anim_1

        # Проверка доступных анимаций | Check available animations
        available = set(self.actor.get_anim_names())

        for anim in [idle_anim, walk_anim, run_anim_1, run_anim_2, skill_anim, attack_anim_1]:
            if anim not in available:
                print(
                    f"⚠️ Анимация '{anim}' не найдена. Доступны: {list(available)} | Animation '{anim}' not found. Available: {list(available)}")

        # Стартовая анимация | Start animation
        if self.idle_anim in available:
            self.actor.loop(self.idle_anim)

        # === СОЗДАНИЕ КОЛЛАЙДЕРА | CREATE COLLIDER ===
        self._create_collider()

        print(f"✅ NPC создан в позиции {start_pos} | NPC created at position {start_pos}")

    def _create_collider(self):
        """Создание коллайдера для NPC | Create collider for NPC"""
        temp_ent = Entity(
            model=self.model_path,
            scale=self._scale,
            position=self.npc_node.get_pos(),
            enabled=False,
            visible=False
        )

        setup_collidable_object(temp_ent, shrink_factor=self._shrink_factor)

        self.collider_entity = temp_ent
        self.collider_entity.reparent_to(self.npc_node)
        self.collider_entity.visible = False
        self.collider_entity.texture = None

    def _look_at_player(self, player_pos):
        """
        Поворачивает NPC к игроку
        Rotates NPC to face the player
        """
        npc_pos = self.npc_node.get_pos()
        direction = Vec3(player_pos.x - npc_pos.x, 0, player_pos.z - npc_pos.z)
        if direction.length() > 0.1:
            angle = atan2(direction.x, direction.z)
            self.npc_node.set_h(-degrees(angle) + 180)

    def _predict_player_position(self):
        """
        Предсказывает будущую позицию игрока
        Predicts future player position
        """
        if not self.player:
            return Vec3(0, 0, 0)

        current_player_pos = self.player.position
        self.player_velocity = current_player_pos - self.last_player_pos
        self.last_player_pos = current_player_pos

        predicted_pos = current_player_pos + self.player_velocity * self.player_prediction_time
        return predicted_pos

    def _is_stuck(self):
        """
        Проверяет, застрял ли NPC
        Checks if NPC is stuck
        """
        current_pos = self.npc_node.get_pos()
        self.last_positions.append(current_pos)

        if len(self.last_positions) < self.last_positions.maxlen:
            return False

        # Проверяем, двигался ли NPC за последние N кадров | Checking if the NPC has moved in the last N frames
        avg_movement = 0
        for i in range(1, len(self.last_positions)):
            avg_movement += (self.last_positions[i] - self.last_positions[i - 1]).length()

        avg_movement /= len(self.last_positions)

        if avg_movement < 0.1:
            self.stuck_time += time.dt
            return self.stuck_time > self.stuck_threshold
        else:
            self.stuck_time = 0
            return False

    def _find_alternative_path(self, target_pos):
        """
        Находит альтернативный путь к цели
        Finds alternative path to target
        """
        current = self.npc_node.get_pos()

        strategies = []

        # Стратегия 1 | Strategy 1
        # Двигаться в сторону цели с небольшим отклонением | Move towards the target with a slight deviation
        base_dir = (target_pos - current).normalized()
        for angle in [0, 30, -30, 45, -45, 60, -60, 90, -90]:
            rad = math.radians(angle)
            test_dir = Vec3(
                base_dir.x * math.cos(rad) - base_dir.z * math.sin(rad),
                0,
                base_dir.x * math.sin(rad) + base_dir.z * math.cos(rad)
            ).normalized()
            strategies.append(test_dir)

        # Стратегия 2 | Strategy 2
        # Двигаться в сторону от последнего препятствия | Move away from the last obstacle
        if self.last_obstacle_pos:
            away_dir = (current - self.last_obstacle_pos).normalized()
            strategies.append(away_dir)

        # Стратегия 3 | Strategy 3
        # Случайное направление (чтобы выйти из тупика) | Random direction (to break the deadlock)
        random_angle = random.uniform(0, 360)
        rad = math.radians(random_angle)
        random_dir = Vec3(math.sin(rad), 0, math.cos(rad)).normalized()
        strategies.append(random_dir)

        # Пробуем каждую стратегию | Try every strategy
        tested_positions = []
        for test_dir in strategies:
            # Пробуем разные дистанции | Try different distances
            for distance_mult in [1, 2, 3]:
                test_pos = current + test_dir * self.speed_walk * time.dt * distance_mult
                if not self._check_collision(test_pos):
                    # Оцениваем позицию | Evaluating the position
                    dist_to_target = (target_pos - test_pos).length()
                    dist_to_current = (target_pos - current).length()

                    if dist_to_target < dist_to_current * 1.5:
                        tested_positions.append((dist_to_target, test_pos, test_dir))

        # Сортируем по близости к цели | Sorting by proximity
        tested_positions.sort()

        if tested_positions:
            _, best_pos, best_dir = tested_positions[0]
            self.npc_node.set_pos(best_pos)
            angle = atan2(best_dir.x, best_dir.z)
            self.npc_node.set_h(-degrees(angle) + 180)
            return True

        return False

    def _update_obstacle_memory(self):
        """
        Обновляет память препятствий (забывает старые)
        Updates obstacle memory (forgets old ones)
        """
        current_time = time.time()
        to_remove = []

        for pos, timestamp in self.obstacle_memory.items():
            if current_time - timestamp > self.memory_duration:
                to_remove.append(pos)

        for pos in to_remove:
            del self.obstacle_memory[pos]

    def _move_toward(self, target, speed):
        """
        Движение к цели с проверкой коллизий и поиском пути
        Move toward target with collision detection and pathfinding
        """
        current = self.npc_node.get_pos()

        distance_to_target = (target - current).length()
        if distance_to_target <= NPC_MIN_CHASE_DISTANCE:
            return

        if self._is_stuck():
            if self._find_alternative_path(target):
                self.stuck_time = 0
                return
            else:
                return

        # Предсказываем позицию игрока | Predicting the player's position
        predicted_target = self._predict_player_position()

        # Направление к предсказанной позиции | The direction to the predicted position
        direction = Vec3(predicted_target.x - current.x, 0, predicted_target.z - current.z)

        if direction.length() > 0.1:
            direction = direction.normalized()

            new_pos = current + direction * speed * time.dt

            # Проверяем коллизии перед движением | Check for collisions before moving
            if not self._check_collision(new_pos):
                self.npc_node.set_pos(new_pos)
            else:
                # Запоминаем препятствие | Remembering the obstacle
                hit_info = raycast(
                    origin=current,
                    direction=direction,
                    distance=1.0,
                    ignore=(self.npc_node, self.actor, self.collider_entity, self.player)
                )
                if hit_info.hit:
                    self.last_obstacle_pos = hit_info.point
                    self.obstacle_memory[tuple(hit_info.point)] = time.time()

                if not self._avoid_obstacle(direction, speed, predicted_target):
                    self._find_alternative_path(predicted_target)

    def _check_collision(self, target_pos):
        """
        Проверка коллизии с другими объектами используя raycast
        Check collision with other objects using raycast
        """
        # Используем raycast от текущей позиции к целевой | Use a raycast from the current position to the target
        current_pos = self.npc_node.get_pos()
        direction = target_pos - current_pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalized()

            hit_info = raycast(
                origin=current_pos,
                direction=direction,
                distance=distance,
                ignore=(self.npc_node, self.actor, self.collider_entity, self.player)
            )

            return hit_info.hit

        return False

    def _avoid_obstacle(self, desired_direction, speed, target_pos):
        """
        Умный обход препятствия с выбором оптимального направления
        Smart obstacle avoidance with optimal direction selection
        """
        current = self.npc_node.get_pos()

        # Обновляем память препятствий | Updating the memory of obstacles
        self._update_obstacle_memory()

        direct_path_free = not self._check_collision(target_pos)
        if direct_path_free:
            new_dir = (target_pos - current).normalized()
            new_pos = current + new_dir * speed * time.dt
            if not self._check_collision(new_pos):
                self.npc_node.set_pos(new_pos)
                return True

        available_directions = []

        # Проверяем 16 направлений | Check 16 directions
        for angle in range(0, 360, 22):
            rad = math.radians(angle)
            test_dir = Vec3(math.sin(rad), 0, math.cos(rad)).normalized()

            test_pos = current + test_dir * speed * time.dt * 2

            if not self._check_collision(test_pos):
                obstacle_penalty = 0
                for obs_pos, _ in self.obstacle_memory.items():
                    obs_vec = Vec3(obs_pos[0], obs_pos[1], obs_pos[2])
                    dir_to_obstacle = (obs_vec - test_pos).normalized()
                    if test_dir.dot(dir_to_obstacle) > 0.8:
                        dist_to_obstacle = (obs_vec - test_pos).length()
                        if dist_to_obstacle < 3.0:
                            obstacle_penalty += 10 * (1 - dist_to_obstacle / 3.0)

                score = self._evaluate_direction(test_dir, test_pos, current, target_pos, desired_direction)
                score -= obstacle_penalty

                available_directions.append((score, test_dir, test_pos))

        available_directions.sort(reverse=True)

        for score, test_dir, test_pos in available_directions[:5]:
            if not self._check_collision(test_pos):
                self.npc_node.set_pos(test_pos)
                angle = atan2(test_dir.x, test_dir.z)
                self.npc_node.set_h(-degrees(angle) + 180)
                return True

        return self._slide_along_obstacle(desired_direction, speed, target_pos)

    def _evaluate_direction(self, direction, new_pos, current_pos, target_pos, desired_direction):
        """
        Оценивает направление по нескольким критериям
        Evaluates direction based on multiple criteria
        """
        score = 0

        dot_product = direction.dot(desired_direction)
        score += dot_product * 10

        current_dist = (target_pos - current_pos).length()
        new_dist = (target_pos - new_pos).length()
        if new_dist < current_dist:
            score += 5 * (1 - new_dist / current_dist)
        else:
            score -= 3 * (new_dist / current_dist)

        if not self._check_collision_line(new_pos, target_pos):
            score += 8

        openness = 0
        for test_angle in [0, 90, -90, 180]:
            rad = math.radians(test_angle)
            check_dir = Vec3(
                direction.x * math.cos(rad) - direction.z * math.sin(rad),
                0,
                direction.x * math.sin(rad) + direction.z * math.cos(rad)
            ).normalized()
            check_pos = new_pos + check_dir * 2
            if not self._check_collision(check_pos):
                openness += 1
        score += openness * 2

        return score

    def _slide_along_obstacle(self, desired_direction, speed, target_pos):
        """
        Скольжение вдоль препятствия с выбором направления
        Slide along obstacle with direction selection
        """
        current = self.npc_node.get_pos()

        # Вычисляем перпендикулярные направления | Calculate the perpendicular directions
        left_dir = Vec3(
            desired_direction.x * math.cos(math.radians(90)) - desired_direction.z * math.sin(math.radians(90)),
            0,
            desired_direction.x * math.sin(math.radians(90)) + desired_direction.z * math.cos(math.radians(90))
        ).normalized()

        right_dir = Vec3(
            desired_direction.x * math.cos(math.radians(-90)) - desired_direction.z * math.sin(math.radians(-90)),
            0,
            desired_direction.x * math.sin(math.radians(-90)) + desired_direction.z * math.cos(math.radians(-90))
        ).normalized()

        # Выбираем направление, которое лучше ведет к цели | Choosing the direction the best direction
        left_score = self._evaluate_direction(left_dir, current + left_dir, current, target_pos, desired_direction)
        right_score = self._evaluate_direction(right_dir, current + right_dir, current, target_pos, desired_direction)

        directions = [(left_score, left_dir), (right_score, right_dir)]
        directions.sort(reverse=True)

        for score, direction in directions:
            for step in range(1, 4):
                test_pos = current + direction * speed * time.dt * step
                if not self._check_collision(test_pos):

                    new_dist = (target_pos - test_pos).length()
                    current_dist = (target_pos - current).length()

                    if new_dist < current_dist * 2:
                        self.npc_node.set_pos(test_pos)
                        angle = atan2(direction.x, direction.z)
                        self.npc_node.set_h(-degrees(angle) + 180)
                        return True

        return False

    def _check_collision_line(self, start_pos, end_pos):
        """
        Проверка, есть ли прямая видимость между двумя точками
        Check if there's line of sight between two points
        """
        direction = end_pos - start_pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalized()
            hit_info = raycast(
                origin=start_pos,
                direction=direction,
                distance=distance,
                ignore=(self.npc_node, self.actor, self.collider_entity, self.player)
            )
            return hit_info.hit

        return False

    def update(self):
        """
        Обновление состояния NPC (вызывается каждый кадр)
        Update NPC state (called every frame)
        """
        if not self.player:
            return

        npc_pos = self.npc_node.get_pos()
        player_pos = self.player.position
        distance_to_player = (npc_pos - player_pos).length()

        current_anim = self.actor.getCurrentAnim()

        # Всегда поворачиваться к игроку, если он близко | Always face the player when close
        if distance_to_player < NPC_IDLE_DISTANCE:
            self._look_at_player(player_pos)

        RUN_TRIGGER_DISTANCE = 15

        if self.skill_used and distance_to_player < RUN_TRIGGER_DISTANCE and self.state == self.idle_anim:
            self.state = self.run_anim_2
            if self.run_anim_2 in self.actor.get_anim_names():
                self.actor.loop(self.run_anim_2)

        # Логика состояний | State machine
        if self.state == self.idle_anim:
            if distance_to_player < NPC_IDLE_DISTANCE:
                self.state = self.walk_anim
                if self.walk_anim in self.actor.get_anim_names():
                    self.actor.loop(self.walk_anim)

        elif self.state == self.walk_anim:
            if distance_to_player < NPC_ATTACK_DISTANCE:
                self.state = self.skill_anim
                if self.skill_anim in self.actor.get_anim_names():
                    self.actor.play(self.skill_anim)
            elif distance_to_player >= NPC_IDLE_DISTANCE:
                self.state = self.idle_anim
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                # Идти к игроку| Walk toward player
                self._move_toward(player_pos, self.speed_walk)

        elif self.state == self.skill_anim:
            if current_anim != self.skill_anim:
                self.skill_used = True
                self.state = self.run_anim_1
                if self.run_anim_1 in self.actor.get_anim_names():
                    self.actor.loop(self.run_anim_1)
            elif distance_to_player >= NPC_IDLE_DISTANCE:
                self.state = self.idle_anim
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)

        elif self.state == self.run_anim_1:
            if distance_to_player < NPC_ATTACK_TRIGGER_DISTANCE:
                self.state = self.attack_anim_1
                if self.attack_anim_1 in self.actor.get_anim_names():
                    self.actor.play(self.attack_anim_1)
            elif distance_to_player >= NPC_IDLE_DISTANCE:
                self.state = self.idle_anim
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                # Бежать к игроку со скоростью run_1 | Run to player with run_1
                self._move_toward(player_pos, self.speed_run_1)

        # === Вторая анимация бега с увеличенной скоростью | Second run animation ===
        elif self.state == self.run_anim_2:
            if distance_to_player < NPC_ATTACK_TRIGGER_DISTANCE:
                self.state = self.attack_anim_1
                if self.attack_anim_1 in self.actor.get_anim_names():
                    self.actor.play(self.attack_anim_1)
            elif distance_to_player >= NPC_IDLE_DISTANCE:
                self.state = self.idle_anim
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                # Бежать к игроку с увеличенной скоростью run_2 | Run to player with run_2
                self._move_toward(player_pos, self.speed_run_2)

        elif self.state == self.attack_anim_1:
            if current_anim != self.attack_anim_1:
                if distance_to_player < NPC_IDLE_DISTANCE:
                    if self.skill_used:
                        self.state = self.run_anim_2
                        if self.run_anim_2 in self.actor.get_anim_names():
                            self.actor.loop(self.run_anim_2)
                    else:
                        self.state = self.run_anim_1
                        if self.run_anim_1 in self.actor.get_anim_names():
                            self.actor.loop(self.run_anim_1)
                else:
                    self.state = self.idle_anim
                    if self.idle_anim in self.actor.get_anim_names():
                        self.actor.loop(self.idle_anim)

    def get_position(self):
        """
        Возвращает текущую позицию NPC
        Returns current NPC position
        """
        return self.npc_node.get_pos()

    def get_state(self):
        """
        Возвращает текущее состояние NPC
        Returns current NPC state
        """
        return self.state

    def set_state(self, new_state):
        """
        Устанавливает состояние NPC
        Sets NPC state
        """
        valid_states = [self.idle_anim, self.walk_anim, self.skill_anim, self.run_anim_1, self.run_anim_2,
                        self.attack_anim_1]
        if new_state in valid_states:
            self.state = new_state
        else:
            print(f"⚠️ Неверное состояние: {new_state} | Invalid state: {new_state}")

    def reset_skill_flag(self):
        """
        Сброс флага использования скилла (если нужно)
        Reset skill usage flag (if needed)
        """
        self.skill_used = False