from ursina import *
from src.utils.object_setup import setup_collidable_object

statue_triggers = []

def load_map(filename='assets/map.txt'):
    global statue_triggers
    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ Файл {filename} не найден.")
        return

    if not lines:
        return

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
                invoke(setup_collidable_object, rock, shrink_factor=0.5, delay=0)

            elif char == 'T':
                tree = Entity(
                    model='tree',
                    texture='tree',
                    scale=2,
                    position=(world_x, 3, world_z),
                    enabled=False
                )
                invoke(setup_collidable_object, tree, shrink_factor=0.5, delay=0)

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
                invoke(setup_collidable_object, statue, shrink_factor=1, delay=0)

    return statue_triggers