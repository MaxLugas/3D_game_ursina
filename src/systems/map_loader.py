from ursina import *
import json
from src.shaders.comics_shader import comics_shaders
from src.utils.object_setup import setup_collidable_object
from src.entities.npc import AnimatedNPC
from src.core.config import (
    ROCK_COLLIDER_SHRINK, TREE_COLLIDER_SHRINK, STATUE_COLLIDER_SHRINK,
    ASSETS_DIR, GROUND_SCALE, COTTAGE_COLLIDER_SHRINK,
    FLASHLIGHT_COLLIDER_SHRINK, TARGET_COLLIDER_SHRINK,
    ROCK_COLOR, TREE_COLOR, COTTAGE_COLOR, FLASHLIGHT_COLOR,
    STATUE_COLOR, TARGET_COLOR, SPECULAR_FACTOR,
    NPC_SPEED_WALK, NPC_SPEED_RUN, MODELS_DIR,
    NPC_IDLE_ANIM, NPC_WALK_ANIM, NPC_RUN_ANIM, NPC_SKILL_ANIM, NPC_SCALE
)

statue_triggers = []


def load_map(filename='map.json', player=None):
    world_entities = []  # Список всех созданных игровых объектов | List of all created game entities
    statue_triggers = []  # Локальный список триггеров для статуй | Local list of statue triggers
    npcs = []
    filepath = ASSETS_DIR / filename

    # === Загрузка JSON-карты | JSON Map Loading ===
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return world_entities, statue_triggers, npcs
    except json.JSONDecodeError as e:
        return world_entities, statue_triggers, npcs

    # === Масштабирование координат | Scale coordinates ===
    base_map_size = data.get("metadata", {}).get("size", 100)
    scale_factor = GROUND_SCALE / base_map_size
    map_half = GROUND_SCALE / 2.0

    print(
        f"📊 Метаданные: размер карты {base_map_size}, масштаб {scale_factor:.2f} | Metadata: map size {base_map_size}, scale {scale_factor:.2f}")

    # === Создание объектов | Entity Creation ===
    objects_data = data.get("objects", [])
    print(f"📦 Загрузка {len(objects_data)} объектов... | Loading {len(objects_data)} objects...")

    for i, obj in enumerate(objects_data, 1):
        obj_type = obj.get("type", "rock")
        x = float(obj.get("x", 0)) * scale_factor
        z = float(obj.get("z", 0)) * scale_factor
        y = float(obj.get("y", 3.0))

        # Прижатие к границам | Clamp to boundaries
        x_clamped = clamp(x, -map_half + 2.0, map_half - 2.0)
        z_clamped = clamp(z, -map_half + 2.0, map_half - 2.0)

        if x != x_clamped or z != z_clamped:
            print(
                f"⚠️ Объект {i} ({obj_type}) прижат к границе: ({x:.1f}, {z:.1f}) -> ({x_clamped:.1f}, {z_clamped:.1f}) | Object clamped to boundary")

        x, z = x_clamped, z_clamped

        # Создание объектов по типу | Create objects by type
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
                position=(x, 0.5, z),
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

    print(f"✅ Создано {len(world_entities)} объектов | Created {len(world_entities)} objects")

    # === Загрузка NPC из JSON | Load NPCs from JSON ===
    npcs_data = data.get("npcs", [])
    if npcs_data:
        print(f"👤 Загрузка {len(npcs_data)} NPC... | Loading {len(npcs_data)} NPCs...")

        for i, npc_data in enumerate(npcs_data, 1):
            try:
                # Получаем позицию из JSON | Get position from JSON
                x = float(npc_data.get("x", 0)) * scale_factor
                z = float(npc_data.get("z", 0)) * scale_factor
                y = float(npc_data.get("y", 0.0))

                # Прижатие к границам | Clamp to boundaries
                x = clamp(x, -map_half + 2.0, map_half - 2.0)
                z = clamp(z, -map_half + 2.0, map_half - 2.0)

                # Создаем NPC только если есть player
                if player:
                    npc = AnimatedNPC(
                        start_pos=(x, y, z),
                        player=player,
                        model_path=f'{MODELS_DIR}/Droid.glb',
                        idle_anim=NPC_IDLE_ANIM,
                        walk_anim=NPC_WALK_ANIM,
                        run_anim=NPC_RUN_ANIM,
                        skill_anim=NPC_SKILL_ANIM,
                        scale=npc_data.get("scale", NPC_SCALE),
                        speed_walk=NPC_SPEED_WALK,
                        speed_run=NPC_SPEED_RUN
                    )
                    npcs.append(npc)
                    world_entities.append(npc)
                    print(f"  ✅ NPC {i}: позиция ({x:.1f}, {y:.1f}, {z:.1f}) | position")
                else:
                    print(f"  ⚠️ NPC {i}: не создан (нет player) | not created (no player)")

            except Exception as e:
                print(f"  ❌ Ошибка загрузки NPC {i}: {e} | Error loading NPC {i}: {e}")

    print(
        f"📊 Итого: {len(world_entities)} объектов, {len(statue_triggers)} триггеров, {len(npcs)} NPC | Total: {len(world_entities)} objects, {len(statue_triggers)} triggers, {len(npcs)} NPCs")
    return world_entities, statue_triggers, npcs
