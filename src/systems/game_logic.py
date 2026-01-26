from ursina import *

class GameLogic:
    def __init__(self, player, npcs, statue_triggers, world_entities):
        self.player = player
        self.npcs = npcs
        self.statue_triggers = statue_triggers
        self.world_entities = world_entities  # ← новое поле
        self.base_speed = player.speed
        self.map_half_size = int(70 / 2)

    def remove_statue(self, trigger):
        if trigger in self.statue_triggers:
            visual = trigger.visual
            # Удаляем из мира
            destroy(visual)
            destroy(trigger)
            # Удаляем из списков
            self.statue_triggers.remove(trigger)
            if visual in self.world_entities:
                self.world_entities.remove(visual)


    def update(self):
        # Сброс при падении
        if self.player.y < -10:
            self.player.position = (0, 10, 0)

        # Ограничение по границам
        x, y, z = self.player.position
        x = clamp(x, -self.map_half_size + 1, self.map_half_size - 1)
        z = clamp(z, -self.map_half_size + 1, self.map_half_size - 1)
        self.player.set_position((x, y, z))

        # Бег
        if held_keys['shift']:
            self.player.speed = self.base_speed * 1.75
        else:
            self.player.speed = self.base_speed

        # Сброс двойного прыжка
        if hasattr(self.player, 'double_jump_used') and self.player.grounded:
            self.player.double_jump_used = False

        # Обновление NPC
        for npc in self.npcs:
            npc.update()

        # Взаимодействие с NPC
        for npc in self.npcs:
            if distance(self.player.position, npc.get_position()) < 1.5:
                if not hasattr(npc, 'talked'):
                    msg = Text(
                        text='Беги!',
                        origin=(0, 0),
                        y=0.1,
                        scale=1.2,
                        color=color.red,
                        background=True
                    )
                    msg.animate('color', color.rgba(255, 0, 0, 0), duration=2.0, curve=curve.out_expo)
                    invoke(destroy, msg, delay=0.8)
                    npc.talked = True