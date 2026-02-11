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
        print(f"⚠️ Файл {filepath} не найден.")
        return world_entities, statue_triggers
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return world_entities, statue_triggers

    world_radius = (GROUND_SCALE * 0.9) / 2.0           # Радиус игрового мира (с отступом от краёв) | Game world radius (with margin from edges)

    # === Создание объектов | Entity Creation ===
    for obj in data.get("objects", []):
        obj_type = obj.get("type")
        # Нормализованные координаты из JSON | Normalized coordinates from JSON
        nx = float(obj.get("nx", 0))
        nz = float(obj.get("nz", 0))
        world_x = nx * world_radius                     # Преобразование в мировую координату X | Convert to world X coordinate
        world_z = nz * world_radius                     # Преобразование в мировую координату Z | Convert to world Z coordinate

        if obj_type == "rock":
            entity = Entity(
                model='rock',
                texture='rock',
                scale=2,
                position=(world_x, 3, world_z),         # Y=3 — поднят над землёй | Y=3 — raised above ground
                shader=comics_shaders,
                color=ROCK_COLOR,
                enabled=False                           # Отложенная активация для оптимизации | Deferred activation for optimization
            )
            entity.color = entity.color.tint(0.3)
            # Отключаем блики | Disable specular highlights
            entity.set_shader_input("specular_factor", SPECULAR_FACTOR)
            invoke(setup_collidable_object, entity, shrink_factor=ROCK_COLLIDER_SHRINK, delay=0)
            world_entities.append(entity)

        elif obj_type == "target":
            entity = Entity(
                model='target',
                texture='target',
                scale=1,
                position=(world_x, 3, world_z),
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
                position=(world_x, 3, world_z),
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
                position=(world_x, 3, world_z),
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
                position=(world_x, 3, world_z),
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
                position=(world_x, 0.5, world_z),
                shader=comics_shaders,
                color=STATUE_COLOR,
                enabled=False
            )
            statue.color = statue.color.tint(0.2)
            statue.set_shader_input("specular_factor", SPECULAR_FACTOR)
            statue.collider = None                      # Коллайдер у триггера | Collider on trigger

            # Невидимый триггер для взаимодействия | Invisible trigger for player interaction
            trigger = Entity(
                position=statue.position,
                scale=Vec3(1, 1, 1),
                collider='box',
                visible=False
            )
            # Связываем триггер с визуальной моделью | Link trigger to visual model
            trigger.visual = statue
            statue_triggers.append(trigger)

            invoke(setup_collidable_object, statue, shrink_factor=STATUE_COLLIDER_SHRINK, delay=0)
            world_entities.append(statue)

    return world_entities, statue_triggers