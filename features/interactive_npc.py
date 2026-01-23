from ursina import Vec3, time, distance
from direct.actor.Actor import Actor
from math import atan2, degrees

class AnimatedNPC:
    def __init__(self, start_pos, player, model_path='Droid.glb',
                 idle_anim='Idle', walk_anim='Walking', run_anim='Running', skill_anim='Skill_01',
                 fix_orientation=True, scale=2.0, speed_walk=2.0, speed_run=5.0):
        self.player = player
        self.speed_walk = speed_walk
        self.speed_run = speed_run

        # Состояния
        self.state = 'idle'

        # Создаём родительский узел для контроля позиции и поворота
        self.npc_node = render.attach_new_node("npc_root")
        self.npc_node.set_pos(Vec3(start_pos[0], start_pos[1], start_pos[2]))

        # Загружаем актёра как дочерний объект
        self.actor = Actor(model_path)
        self.actor.reparent_to(self.npc_node)
        self.actor.set_scale(scale)
        self.actor.set_light_off()
        if fix_orientation:
            self.actor.set_p(0)
        self.actor.set_pos(0, 0.1, 0)  # чуть выше земли

        # Имена анимаций
        self.idle_anim = idle_anim
        self.walk_anim = walk_anim
        self.run_anim = run_anim
        self.skill_anim = skill_anim

        # Проверка анимаций
        available = set(self.actor.get_anim_names())
        for anim in [idle_anim, walk_anim, run_anim, skill_anim]:
            if anim not in available:
                print(f"⚠️ Анимация '{anim}' не найдена. Доступны: {list(available)}")

        # Старт
        if self.idle_anim in available:
            self.actor.loop(self.idle_anim)

    def _look_at_player(self, player_pos):
        # Поворачиваем ВЕСЬ узел к игроку
        npc_pos = self.npc_node.get_pos()
        direction = Vec3(player_pos.x - npc_pos.x, 0, player_pos.z - npc_pos.z)
        if direction.length() > 0.1:
            angle = atan2(direction.x, direction.z)
            self.npc_node.set_h(-degrees(angle)+180)

    def update(self):
        npc_pos = self.npc_node.get_pos()
        player_pos = self.player.position
        distance_to_player = (npc_pos - player_pos).length()

        current_anim = self.actor.getCurrentAnim()

        # === ВСЕГДА поворачиваться к игроку, если он близко ===
        if distance_to_player < 15:
            self._look_at_player(player_pos)

        # === Логика состояний ===
        if self.state == 'idle':
            if distance_to_player < 15:
                self.state = 'walking'
                if self.walk_anim in self.actor.get_anim_names():
                    self.actor.loop(self.walk_anim)

        elif self.state == 'walking':
            if distance_to_player < 10:
                self.state = 'attacking'
                if self.skill_anim in self.actor.get_anim_names():
                    self.actor.play(self.skill_anim)
            elif distance_to_player >= 15:
                self.state = 'idle'
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                self._move_toward(player_pos, self.speed_walk)

        elif self.state == 'attacking':
            if current_anim != self.skill_anim:
                self.state = 'running'
                if self.run_anim in self.actor.get_anim_names():
                    self.actor.loop(self.run_anim)

        elif self.state == 'running':
            if distance_to_player >= 15:
                self.state = 'idle'
                if self.idle_anim in self.actor.get_anim_names():
                    self.actor.loop(self.idle_anim)
            else:
                self._move_toward(player_pos, self.speed_run)

    def _move_toward(self, target, speed):
        current = self.npc_node.get_pos()
        direction = Vec3(target.x - current.x, 0, target.z - current.z)
        if direction.length() > 0.1:
            direction = direction.normalized()
            new_pos = current + direction * speed * time.dt
            self.npc_node.set_pos(new_pos)
        # Поворот уже обрабатывается в update → не нужен здесь

    def get_position(self):
        return self.npc_node.get_pos()


# Создание NPC

npc = AnimatedNPC(
    start_pos=(-5, 0, 0),
    # player=player,
    model_path='Droid.glb',
    idle_anim='Idle',
    walk_anim='Walking',
    run_anim='Running',
    skill_anim='Skill_01',
    speed_walk=2.0,
    speed_run=5.0
)