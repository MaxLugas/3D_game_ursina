from ursina import *
import json
from src.utils.object_setup import setup_collidable_object
from src.core.config import ROCK_COLLIDER_SHRINK, TREE_COLLIDER_SHRINK, STATUE_COLLIDER_SHRINK, ASSETS_DIR, \
    GROUND_SCALE, COTTAGE_COLLIDER_SHRINK, FLASHLIGHT_COLLIDER_SHRINK, TARGET_COLLIDER_SHRINK

statue_triggers = []

def load_map(filename='map.json'):
    world_entities = []
    statue_triggers = []

    filepath = ASSETS_DIR / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Файл {filepath} не найден.")
        return world_entities, statue_triggers
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return world_entities, statue_triggers

    world_radius = (GROUND_SCALE * 0.9) / 2.0  # 90% от поля

    # === Создание объектов ===
    for obj in data.get("objects", []):
        obj_type = obj.get("type")
        nx = float(obj.get("nx", 0))
        nz = float(obj.get("nz", 0))

        world_x = nx * world_radius
        world_z = nz * world_radius

        if obj_type == "rock":
            entity = Entity(
                model='rock',
                texture='rock',
                scale=2,
                position=(world_x, 3, world_z),
                enabled=False
            )
            invoke(setup_collidable_object, entity, shrink_factor=ROCK_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "target":
            entity = Entity(
                model='target',
                texture='target',
                scale=1,
                position=(world_x, 3, world_z),
                enabled=False
            )
            invoke(setup_collidable_object, entity, shrink_factor=TARGET_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "tree":
            entity = Entity(
                model='tree',
                texture='tree',
                scale=2,
                position=(world_x, 3, world_z),
                enabled=False
            )
            invoke(setup_collidable_object, entity, shrink_factor=TREE_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "cottage":
            entity = Entity(
                model='cottage',
                texture='cottage',
                scale=5,
                position=(world_x, 3, world_z),
                enabled=False
            )
            invoke(setup_collidable_object, entity, shrink_factor=COTTAGE_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "flashlight":
            entity = Entity(
                model='flashlight',
                texture='flashlight',
                scale=3,
                position=(world_x, 3, world_z),
                enabled=False
            )
            invoke(setup_collidable_object, entity, shrink_factor=FLASHLIGHT_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "statue":
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