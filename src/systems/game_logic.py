from ursina import *
from src.core.config import MAP_HALF_SIZE, RENDER_DISTANCE
from src.entities.npc import AnimatedNPC


class GameLogic:
    def __init__(self, player, npcs, world_entities):
        self.player = player
        self.npcs = npcs
        self.world_entities = world_entities
        self.base_speed = player.speed
        self.map_half_size = MAP_HALF_SIZE
        self.npc_update_distance = RENDER_DISTANCE * 1.5


    def update(self):
        # Сброс позиции при падении за пределы карты | Reset position when falling below map bounds
        if self.player.y < -10:
            self.player.position = (0, 10, 0)

        # Ограничение перемещения по границам карты | Constrain movement within map boundaries
        x, y, z = self.player.position
        x = clamp(x, -self.map_half_size + 1, self.map_half_size - 1)
        z = clamp(z, -self.map_half_size + 1, self.map_half_size - 1)
        self.player.set_position((x, y, z))

        # Ускорение при зажатом Shift (бег) | Sprint when Shift is held
        if held_keys['shift']:
            self.player.speed = self.base_speed * 2
        else:
            self.player.speed = self.base_speed

        # Сброс флага двойного прыжка при касании земли | Reset double jump flag when grounded
        if hasattr(self.player, 'double_jump_used') and self.player.grounded:
            self.player.double_jump_used = False

        # Удаление уничтоженных NPC | Remove destroyed NPCs
        self.npcs = [n for n in self.npcs if not getattr(n, '_destroyed', False)]

        # Обновление видимости объектов | Update object visibility
        self._update_visibility()

        # Обновление NPC (только в радиусе обновления) | Update NPCs (only within update radius)
        for npc in self.npcs:
            if distance(self.player.position, npc.get_position()) < self.npc_update_distance:
                npc.update()

    def _update_visibility(self):
        player_pos = self.player.position
        for entity in self.world_entities[:]:
            if getattr(entity, '_destroyed', False):
                self.world_entities.remove(entity)
                continue
            try:
                if isinstance(entity, AnimatedNPC):
                    dist = distance(player_pos, entity.get_position())
                    entity.set_visible(dist <= RENDER_DISTANCE)
                else:
                    dist = distance(player_pos, entity.position)
                    entity.visible = dist <= RENDER_DISTANCE
            except AssertionError:
                self.world_entities.remove(entity)