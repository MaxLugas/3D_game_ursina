from ursina import *
from src.core.config import MAP_HALF_SIZE


class GameLogic:
    def __init__(self, player, npcs, world_entities):
        self.player = player
        self.npcs = npcs
        self.world_entities = world_entities
        self.base_speed = player.speed
        self.map_half_size = MAP_HALF_SIZE


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
            self.player.speed = self.base_speed * 1.75
        else:
            self.player.speed = self.base_speed

        # Сброс флага двойного прыжка при касании земли | Reset double jump flag when grounded
        if hasattr(self.player, 'double_jump_used') and self.player.grounded:
            self.player.double_jump_used = False

        # Обновление NPC | Update NPCs
        for npc in self.npcs:
            npc.update()

        # # Взаимодействие с NPC | NPC interaction
        # for npc in self.npcs:
        #     if distance(self.player.position, npc.get_position()) < 1.5:
        #         npc.trigger_interaction()