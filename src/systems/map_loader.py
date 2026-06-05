from ursina import *
import json
from src.shaders.shader_loader import comics_shaders
from src.utils.object_setup import setup_collidable_object
from src.entities.npc import AnimatedNPC
from src.core.config import ASSETS_DIR, GROUND_SCALE, MAP_FILENAME


from src.core.npc_config import DROID_IDLE_ANIM, DROID_WALK_ANIM, DROID_RUN_ANIM_1, DROID_SKILL_ANIM, DROID_SCALE, DROID_SKILL_SOUND, DROID_WALK_SOUND, \
    DROID_ATTACK_1_SOUND, DROID_SPEED_WALK, DROID_SPEED_RUN_1
from src.core.objects_config import OBJECT_CONFIGS


def _clamp_coords(x, z, half_size, offset=2.0):
    """Ограничивает координаты в пределах границ карты. | Clamps coordinates within map boundaries."""
    return clamp(x, -half_size + offset, half_size - offset), clamp(z, -half_size + offset, half_size - offset)


def _setup_with_offset(entity, shrink_factor, y_offset):
    setup_collidable_object(entity, shrink_factor=shrink_factor)
    if y_offset:
        entity.y += y_offset


def create_world_object(obj_type, x, y, z, rot, y_offset=0, verbose=True):
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
        invoke(_setup_with_offset, entity, config["shrink_factor"], y_offset, delay=0)
    elif config.get("collider"):
        entity.collider = config["collider"]
        if y_offset:
            entity.y += y_offset

    if config.get("is_statue"):
        entity.is_statue = True

    return entity


def get_player_start(filename=MAP_FILENAME):
    filepath = ASSETS_DIR / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        player_start_data = data.get("player_start", {})
        return {
            'x': float(player_start_data.get('x', 0)),
            'y': float(player_start_data.get('y', 1.0)),
            'z': float(player_start_data.get('z', 0)),
            'rot': float(player_start_data.get('rot', 0))
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return {'x': 0, 'y': 1.0, 'z': 0, 'rot': 0}


def load_map(filename=MAP_FILENAME, player=None, load_npcs=True, verbose=True):
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

    filepath = ASSETS_DIR / filename

    # === Загрузка JSON-карты | JSON Map Loading ===
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        if verbose:
            print(
                f"❌ Файл {filepath} не найден. Используются настройки по умолчанию. | File {filepath} not found. Using default settings.")
        return world_entities, npcs, get_player_start()
    except json.JSONDecodeError as e:
        if verbose:
            print(f"❌ Ошибка парсинга JSON: {e} | JSON parsing error: {e}")
        return world_entities, npcs, get_player_start()

    # === Загрузка стартовой позиции игрока | Load player start position ===
    player_start = get_player_start(filename)
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
        y_offset = float(obj.get("y_offset", 0))

        # === Загрузка поворота | Load rotation ===
        rot = float(obj.get("rot", 0))

        # Прижатие к границам | Clamp to boundaries
        x, z = _clamp_coords(x, z, map_half)

        # Создание объекта через фабрику | Create object via factory
        entity = create_world_object(obj_type, x, y, z, rot, y_offset, verbose)
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
                y = float(npc_data.get("y", 0.0)) + float(npc_data.get("y_offset", 0)) - DROID_SCALE

                # Прижатие к границам | Clamp to boundaries
                x, z = _clamp_coords(x, z, map_half)

                if player:
                    npc = AnimatedNPC(
                        start_pos=(x, y, z),
                        player=player,
                        model_path='droid.glb',
                        idle_anim=DROID_IDLE_ANIM,
                        walk_anim=DROID_WALK_ANIM,
                        run_anim_1=DROID_RUN_ANIM_1,
                        skill_anim=DROID_SKILL_ANIM,
                        scale=npc_data.get("scale", DROID_SCALE),
                        speed_walk=DROID_SPEED_WALK,
                        speed_run_1=DROID_SPEED_RUN_1,
                        skill_sound=DROID_SKILL_SOUND,
                        walk_sound=DROID_WALK_SOUND,
                        attack_sound_1=DROID_ATTACK_1_SOUND
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
