from ursina import *
import json
from src.shaders.shader_loader import comics_shaders
from src.utils.object_setup import setup_collidable_object
from src.entities.npc import AnimatedNPC
from src.core.config import (
    STONE_COLLIDER_SHRINK, TREE_COLLIDER_SHRINK, STATUE_COLLIDER_SHRINK,
    ASSETS_DIR, GROUND_SCALE, COTTAGE_COLLIDER_SHRINK,
    FLASHLIGHT_COLLIDER_SHRINK, TARGET_COLLIDER_SHRINK, SPECULAR_FACTOR,
    NPC_SPEED_WALK, NPC_SPEED_RUN_1, MODELS_DIR,
    NPC_IDLE_ANIM, NPC_WALK_ANIM, NPC_RUN_ANIM_1, NPC_SKILL_ANIM, NPC_SCALE, NPC_SKILL_SOUND, NPC_WALK_SOUND,
    NPC_ATTACK_1_SOUND, STONE_SCALE, TARGET_SCALE, STATUE_SCALE, FLASHLIGHT_SCALE, COTTAGE_SCALE, TREE_SCALE
)

# === Конфигурация объектов мира | World objects configuration ===
OBJECT_CONFIGS = {
    "stone": {
        "model": "stone",
        "scale": STONE_SCALE,
        "shrink_factor": STONE_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "target": {
        "model": "target",
        "scale": TARGET_SCALE,
        "shrink_factor": TARGET_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "tree": {
        "model": "tree",
        "scale": TREE_SCALE,
        "shrink_factor": TREE_COLLIDER_SHRINK,
        "y_offset": 0,
        "has_specular": True,
        "enabled": False
    },
    "cottage": {
        "model": "cottage",
        "scale": COTTAGE_SCALE,
        "shrink_factor": COTTAGE_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "flashlight": {
        "model": "flashlight",
        "scale": FLASHLIGHT_SCALE,
        "shrink_factor": FLASHLIGHT_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "statue": {
        "model": "statue",
        "scale": STATUE_SCALE,
        "shrink_factor": None,
        "collider": "box",
        "y_offset": -0.5,
        "is_statue": True,
        "enabled": True
    }
}


def create_world_object(obj_type, x, y, z, rot, verbose=True):
    """
    Создание объекта мира по типу
    Create world object by type

    Returns:
        Entity or None: созданный объект или None при ошибке
    """
    if obj_type not in OBJECT_CONFIGS:
        if verbose:
            print(f"⚠️ Неизвестный тип объекта: {obj_type} | Unknown object type: {obj_type}")
        return None

    config = OBJECT_CONFIGS[obj_type]

    entity = Entity(
        model=config["model"],
        scale=config["scale"],
        position=(x, y + config.get("y_offset", 0), z),
        rotation=(0, rot, 0),
        shader=comics_shaders,
        enabled=config.get("enabled", False)
    )

    if config.get("shrink_factor") is not None:
        invoke(setup_collidable_object, entity, shrink_factor=config["shrink_factor"], delay=0)
    elif config.get("collider"):
        entity.collider = config["collider"]

    if config.get("is_statue"):
        entity.is_statue = True

    return entity


def load_map(filename='map.json', player=None, load_npcs=True, verbose=True):
    """
    Загрузка карты из JSON файла
    Load map from JSON file

    Параметры | Parameters:
        filename (str): имя файла карты | map filename
        player (Entity): ссылка на игрока (для NPC) | reference to player (for NPCs)

    Возвращает | Returns:
        tuple: (world_entities, npcs, player_start) - списки объектов, NPC и стартовая позиция игрока
    """
    world_entities = []  # Список всех созданных игровых объектов | List of all created game entities
    npcs = []  # Список созданных NPC | List of created NPCs
    player_start = {'x': 0, 'z': 0, 'y': 1.0}  # Стартовая позиция по умолчанию | Default player start position

    filepath = ASSETS_DIR / filename

    # === Загрузка JSON-карты | JSON Map Loading ===
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        if verbose:
            print(
                f"❌ Файл {filepath} не найден. Используются настройки по умолчанию. | File {filepath} not found. Using default settings.")
        return world_entities, npcs, player_start
    except json.JSONDecodeError as e:
        if verbose:
            print(f"❌ Ошибка парсинга JSON: {e} | JSON parsing error: {e}")
        return world_entities, npcs, player_start

    # === Загрузка стартовой позиции игрока | Load player start position ===
    player_start_data = data.get("player_start", {})
    if player_start_data:
        player_start = {
            'x': float(player_start_data.get('x', 0)),
            'z': float(player_start_data.get('z', 0)),
            'y': float(player_start_data.get('y', 1.0))
        }
        if verbose:
            print(
                f"🚩 Загружена стартовая позиция игрока: ({player_start['x']:.1f}, {player_start['y']:.1f}, {player_start['z']:.1f}) | Player start position loaded")

    # === Масштабирование координат | Scale coordinates ===
    base_map_size = data.get("metadata", {}).get("size", 100)
    scale_factor = GROUND_SCALE / base_map_size
    map_half = GROUND_SCALE / 2.0
    if verbose:
        print(
            f"📊 Метаданные: размер карты {base_map_size}, масштаб {scale_factor:.2f} | Metadata: map size {base_map_size}, scale {scale_factor:.2f}")

    # === Создание объектов | Entity Creation ===
    objects_data = data.get("objects", [])
    if verbose:
        print(f"📦 Загрузка {len(objects_data)} объектов... | Loading {len(objects_data)} objects...")

    for i, obj in enumerate(objects_data, 1):
        obj_type = obj.get("type", "stone")
        x = float(obj.get("x", 0)) * scale_factor
        z = float(obj.get("z", 0)) * scale_factor
        y = float(obj.get("y", 3.0))

        # === Загрузка поворота | Load rotation ===
        rot = float(obj.get("rot", 0))

        # Прижатие к границам | Clamp to boundaries
        x_clamped = clamp(x, -map_half + 2.0, map_half - 2.0)
        z_clamped = clamp(z, -map_half + 2.0, map_half - 2.0)

        if (x != x_clamped or z != z_clamped) and verbose:
            print(
                f"⚠️ Объект {i} ({obj_type}) прижат к границе: ({x:.1f}, {z:.1f}) -> ({x_clamped:.1f}, {z_clamped:.1f}) | Object clamped to boundary")

        x, z = x_clamped, z_clamped

        # Создание объекта через фабрику | Create object via factory
        entity = create_world_object(obj_type, x, y, z, rot, verbose)
        if entity:
            world_entities.append(entity)

    if verbose:
        print(f"✅ Создано {len(world_entities)} объектов | Created {len(world_entities)} objects")

    # === Загрузка NPC из JSON | Load NPCs from JSON ===
    npcs_data = data.get("npcs", [])
    if load_npcs and npcs_data:
        if verbose:
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

                if player:
                    npc = AnimatedNPC(
                        start_pos=(x, y, z),
                        player=player,
                        model_path='droid.glb',
                        idle_anim=NPC_IDLE_ANIM,
                        walk_anim=NPC_WALK_ANIM,
                        run_anim_1=NPC_RUN_ANIM_1,
                        skill_anim=NPC_SKILL_ANIM,
                        scale=npc_data.get("scale", NPC_SCALE),
                        speed_walk=NPC_SPEED_WALK,
                        speed_run_1=NPC_SPEED_RUN_1,
                        skill_sound=NPC_SKILL_SOUND,
                        walk_sound=NPC_WALK_SOUND,
                        attack_sound_1=NPC_ATTACK_1_SOUND
                    )
                    npcs.append(npc)
                    world_entities.append(npc)
                else:
                    if verbose:
                        print(f"  ⚠️ NPC {i}: не создан (нет player) | not created (no player)")

            except Exception as e:
                if verbose:
                    print(f"  ❌ Ошибка загрузки NPC {i}: {e} | Error loading NPC {i}: {e}")
    if verbose:
        print(
            f"📊 Итого: {len(world_entities)} объектов, {len(npcs)} NPC | Total: {len(world_entities)} objects, {len(npcs)} NPCs")

    return world_entities, npcs, player_start