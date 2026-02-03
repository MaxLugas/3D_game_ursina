from ursina import *
from src.utils.object_setup import setup_collidable_object
from src.core.config import ROCK_COLLIDER_SHRINK, TREE_COLLIDER_SHRINK, STATUE_COLLIDER_SHRINK, ASSETS_DIR

statue_triggers = []

def load_map(filename=f'{ASSETS_DIR}/map.txt'):
    world_entities = []
    statue_triggers = []

    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ Файл {filename} не найден.")
        return world_entities, statue_triggers

    map_height = len(lines)
    map_width = max(len(line) for line in lines)
    scale_factor = 2
    offset_x = -(map_width // 2) * scale_factor
    offset_z = -(map_height // 2) * scale_factor

    for z, line in enumerate(lines):
        for x, char in enumerate(line):
            world_x = offset_x + x * scale_factor
            world_z = offset_z + z * scale_factor

            if char == 'R':
                rock = Entity(
                    model='rock',
                    texture='rock',
                    scale=2,
                    position=(world_x, 3, world_z),
                    enabled=False
                )
                invoke(setup_collidable_object, rock, shrink_factor=ROCK_COLLIDER_SHRINK, delay=0)
                world_entities.append(rock)

            elif char == 'T':
                tree = Entity(
                    model='tree',
                    texture='tree',
                    scale=2,
                    position=(world_x, 3, world_z),
                    enabled=False
                )
                invoke(setup_collidable_object, tree, shrink_factor=TREE_COLLIDER_SHRINK, delay=0)
                world_entities.append(tree)

            elif char == 'S':
                statue = Entity(
                    model='statue',
                    texture='statue',
                    scale=0.5,
                    position=(world_x, 0.5, world_z),
                    enabled=False
                )
                statue.collider = None
                trigger = Entity(
                    position=statue.position,
                    scale=Vec3(1, 1, 1),
                    collider='box',
                    visible=False
                )
                trigger.visual = statue
                statue_triggers.append(trigger)
                invoke(setup_collidable_object, statue, shrink_factor=STATUE_COLLIDER_SHRINK, delay=0)
                world_entities.append(statue)

    return world_entities, statue_triggers