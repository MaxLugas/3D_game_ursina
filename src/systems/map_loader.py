from ursina import *
import json
from src.shaders.comics_shader import comics_shaders
from src.utils.object_setup import setup_collidable_object
from src.core.config import (
    ROCK_COLLIDER_SHRINK, TREE_COLLIDER_SHRINK, STATUE_COLLIDER_SHRINK,
    ASSETS_DIR, GROUND_SCALE, COTTAGE_COLLIDER_SHRINK,
    FLASHLIGHT_COLLIDER_SHRINK, TARGET_COLLIDER_SHRINK,
    ROCK_COLOR, TREE_COLOR, COTTAGE_COLOR, FLASHLIGHT_COLOR,
    STATUE_COLOR, TARGET_COLOR, SPECULAR_FACTOR
)

statue_triggers = []                                    # Глобальный список триггеров статуй | Global list of statue triggers

def load_map(filename='map.json'):
    world_entities = []                                 # Список всех созданных игровых объектов | List of all created game entities
    statue_triggers = []                                # Локальный список триггеров для статуй | Local list of statue triggers
    filepath = ASSETS_DIR / filename

    # === Загрузка JSON-карты | JSON Map Loading ===
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Файл {filepath} не найден. | File {filepath} not found.")
        return world_entities, statue_triggers
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e} | JSON parsing error: {e}")
        return world_entities, statue_triggers

    # === Масштабирование координат под текущий размер карты | Scale coordinates to current map size ===
    base_map_size = data.get("metadata", {}).get("size", 100)  # Базовый размер из метаданных | Base size from metadata
    scale_factor = GROUND_SCALE / base_map_size                # Коэффициент масштаба | Scale factor
    map_half = GROUND_SCALE / 2.0                              # Половина размера карты (без отступа) | Half map size (no margin)


    # === Создание объектов | Entity Creation ===
    for i, obj in enumerate(data.get("objects", []), 1):
        obj_type = obj.get("type", "rock")
        x = float(obj.get("x", 0)) * scale_factor
        z = float(obj.get("z", 0)) * scale_factor
        y = float(obj.get("y", 3.0))

        # === Прижатие объектов к границам вместо пропуска | Clamp objects to boundaries instead of skipping ===
        x_clamped = clamp(x, -map_half + 2.0, map_half - 2.0)  # Отступ 2м от краёв | 2m margin from edges
        z_clamped = clamp(z, -map_half + 2.0, map_half - 2.0)

        x, z = x_clamped, z_clamped

        if obj_type == "rock":
            entity = Entity(
                model='rock',
                texture='rock',
                scale=2,                          # Применяем масштаб из карты | Apply scale from map
                position=(x, y, z),
                shader=comics_shaders,
                color=ROCK_COLOR,
                enabled=False
            )
            entity.color = entity.color.tint(0.3)
            entity.set_shader_input("specular_factor", SPECULAR_FACTOR)
            invoke(setup_collidable_object, entity, shrink_factor=ROCK_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "target":
            entity = Entity(
                model='target',
                texture='target',
                position=(x, y, z),
                shader=comics_shaders,
                color=TARGET_COLOR,
                enabled=False
            )
            entity.color = entity.color.tint(0.2)
            entity.set_shader_input("specular_factor", SPECULAR_FACTOR)
            invoke(setup_collidable_object, entity, shrink_factor=TARGET_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "tree":
            entity = Entity(
                model='tree',
                texture='tree',
                scale=2,
                position=(x, y, z),
                shader=comics_shaders,
                color=TREE_COLOR,
                enabled=False
            )
            entity.color = entity.color.tint(0.2)
            entity.set_shader_input("specular_factor", SPECULAR_FACTOR)
            invoke(setup_collidable_object, entity, shrink_factor=TREE_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "cottage":
            entity = Entity(
                model='cottage',
                texture='cottage',
                scale=5,
                position=(x, y, z),
                shader=comics_shaders,
                color=COTTAGE_COLOR,
                enabled=False
            )
            entity.color = entity.color.tint(0.4)
            entity.set_shader_input("specular_factor", SPECULAR_FACTOR)
            invoke(setup_collidable_object, entity, shrink_factor=COTTAGE_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "flashlight":
            entity = Entity(
                model='flashlight',
                texture='flashlight',
                scale=3,
                position=(x, y, z),
                shader=comics_shaders,
                color=FLASHLIGHT_COLOR,
                enabled=False
            )
            entity.color = entity.color.tint(0.3)
            entity.set_shader_input("specular_factor", SPECULAR_FACTOR)
            invoke(setup_collidable_object, entity, shrink_factor=FLASHLIGHT_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "statue":
            statue = Entity(
                model='statue',
                texture='statue',
                scale=0.5,
                position=(x, 0.5, z),                     # Статуи всегда на земле | Statues always on ground
                shader=comics_shaders,
                color=STATUE_COLOR,
                enabled=False
            )
            statue.color = statue.color.tint(0.2)
            statue.set_shader_input("specular_factor", SPECULAR_FACTOR)
            statue.collider = None                        # Коллайдер у триггера | Collider on trigger

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