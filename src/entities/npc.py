from ursina import *
from direct.actor.Actor import Actor
from math import atan2, degrees

from src.core.config import NPC_SPEED_WALK, NPC_SPEED_RUN, NPC_ATTACK_DISTANCE, NPC_IDLE_DISTANCE, MODELS_DIR
from src.shaders.comics_shader import npc_shader_panda

class AnimatedNPC:
    def __init__(self, start_pos, player, model_path=f'{MODELS_DIR}/Droid.glb',
                 idle_anim='Idle', walk_anim='Walking', run_anim='Running', skill_anim='Skill_01',
                 fix_orientation=True, scale=2.0, speed_walk=NPC_SPEED_WALK, speed_run=NPC_SPEED_RUN):

        self.player = player
        self.speed_walk = speed_walk
        self.speed_run = speed_run

        # Состояния NPC | NPC states
        self.state = 'idle'

        # Флаг для однократного взаимодействия | One-time interaction flag
        self.talked = False

        # Создаём родительский узел для контроля позиции и поворота | Create parent node for position and rotation control
        self.npc_node = render.attach_new_node("npc_root")
        self.npc_node.set_pos(Vec3(start_pos[0], start_pos[1], start_pos[2]))

        # Загружаем актёра как дочерний объект
        # Load actor as child object
        self.actor = Actor(model_path)
        self.actor.reparent_to(self.npc_node)
        self.actor.set_scale(scale)
        self.actor.set_light_off()  # Отключаем динамическое освещение | Disable dynamic lighting
        self.actor.set_shader(npc_shader_panda)  # Применяем комикс-шейдер | Apply comic shader

        if fix_orientation:
            self.actor.set_p(0)  # Исправляем наклон | Fix pitch
        self.actor.set_pos(0, 0, 0)

        # Имена анимаций | Animation names
        self.idle_anim = idle_anim
        self.walk_anim = walk_anim
        self.run_anim = run_anim
        self.skill_anim = skill_anim

        # Проверка доступных анимаций | Check available animations
        available = set(self.actor.get_anim_names())
        for anim in [idle_anim, walk_anim, run_anim, skill_anim]:
            if anim not in available:
                print(
                    f"⚠️ Анимация '{anim}' не найдена. Доступны: {list(available)} | Animation '{anim}' not found. Available: {list(available)}")

        # Стартовая анимация | Start animation
        if self.idle_anim in available:
            self.actor.loop(self.idle_anim)

        print(f"✅ NPC создан в позиции {start_pos} | NPC created at position {start_pos}")

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

    def _move_toward(self, target, speed):
        """
        Движение к цели
        Move toward target
        """
        current = self.npc_node.get_pos()
        direction = Vec3(target.x - current.x, 0, target.z - current.z)
        if direction.length() > 0.1:
            direction = direction.normalized()
            new_pos = current + direction * speed * time.dt
            self.npc_node.set_pos(new_pos)

    def update(self):
        """
        Обновление состояния NPC (вызывается каждый кадр)
        Update NPC state (called every frame)
        """
        npc_pos = self.npc_node.get_pos()
        player_pos = self.player.position
        distance_to_player = (npc_pos - player_pos).length()

        current_anim = self.actor.getCurrentAnim()

        # Всегда поворачиваться к игроку, если он близко | Always face the player when close
        if distance_to_player < NPC_IDLE_DISTANCE:
            self._look_at_player(player_pos)

        # Логика состояний | State machine
        if self.state == 'idle':
            # Если игрок рядом - начать ходьбу | If player is close - start walking
            if distance_to_player < NPC_IDLE_DISTANCE:
                self.state = 'walking'
                if self.walk_anim in self.actor.get_anim_names():
                    self.actor.loop(self.walk_anim)

        elif self.state == 'walking':
            # Если игрок очень близко | If player is very close - attack
            if distance_to_player < NPC_ATTACK_DISTANCE:
                self.state = 'attacking'
                if self.skill_anim in self.actor.get_anim_names():
                    self.actor.play(self.skill_anim)
            # Если игрок далеко - вернуться в idle | If player is far - return to idle
            elif distance_to_player >= NPC_IDLE_DISTANCE:
                self.state = 'idle'
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                # Идти к игроку| Walk toward player
                self._move_toward(player_pos, self.speed_walk)

        elif self.state == 'attacking':
            # После анимации атаки перейти в бег| After attack animation, switch to running
            if current_anim != self.skill_anim:
                self.state = 'running'
                if self.run_anim in self.actor.get_anim_names():
                    self.actor.loop(self.run_anim)

        elif self.state == 'running':
            # Если игрок далеко - вернуться в idle | If player is far - return to idle
            if distance_to_player >= NPC_IDLE_DISTANCE:
                self.state = 'idle'
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                # Бежать к игроку | Run toward player
                self._move_toward(player_pos, self.speed_run)

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
        valid_states = ['idle', 'walking', 'attacking', 'running']
        if new_state in valid_states:
            self.state = new_state
        else:
            print(f"⚠️ Неверное состояние: {new_state} | Invalid state: {new_state}")