import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from src.core.config import (
    GROUND_SCALE, MAP_HALF_SIZE, ASSETS_DIR, MODELS_DIR,
    STONE_SCALE, TARGET_SCALE, STATUE_SCALE, FLASHLIGHT_SCALE,
    COTTAGE_SCALE, TREE_SCALE, NPC_SCALE
)
from src.core.engine import init_engine
from src.systems.map_loader import OBJECT_CONFIGS

app = init_engine()

mouse_left_pressed = False
mouse_right_pressed = False

window.cursor_visible = True

object_types = list(OBJECT_CONFIGS.keys())
print(f"Loaded object types: {object_types}")

current_type = [object_types[0]] if object_types else ['cube']
placed_objects = []
placed_npcs = []
player_start_pos = Vec3(0, 1, 0)
player_start_rot = [0]

ghost_entity = None
ghost_enabled = True
mode = ['place']

SCALE_CONFIG = {
    'tree': TREE_SCALE,
    'stone': STONE_SCALE,
    'cottage': COTTAGE_SCALE,
    'flashlight': FLASHLIGHT_SCALE,
    'statue': STATUE_SCALE,
    'target': TARGET_SCALE,
    'npc': NPC_SCALE
}


def get_scale_for_type(obj_type):
    if obj_type in SCALE_CONFIG:
        return SCALE_CONFIG[obj_type]
    config = OBJECT_CONFIGS.get(obj_type, {})
    if 'scale' in config:
        return config['scale']
    return 1.0


def get_model_for_type(obj_type):
    config = OBJECT_CONFIGS.get(obj_type, {})
    return config.get("model", "cube")


def get_y_offset_for_type(obj_type):
    config = OBJECT_CONFIGS.get(obj_type, {})
    return config.get("y_offset", 0)


player = FirstPersonController(speed=8, jump_height=3, gravity=1, mouse_sensitivity=Vec2(40, 40),
                               position=player_start_pos)

def create_ghost():
    """Создает или обновляет модель призрака при смене типа объекта"""
    global ghost_entity
    if ghost_entity:
        destroy(ghost_entity)

    obj_type = current_type[0]
    if obj_type == 'npc':
        return

    scale = get_scale_for_type(obj_type)
    model_name = get_model_for_type(obj_type)
    y_offset = get_y_offset_for_type(obj_type)

    ghost_entity = Entity(
        model=model_name,
        scale=scale,
        color=color.rgba(255, 255, 255, 100),
        double_sided=True
    )
    refresh_ghost_position()


def refresh_ghost_position():
    """
    Обновляет позицию и вращение призрака.
    """
    global ghost_entity

    if mode[0] in ['idle', 'npc', 'player_start']:
        if ghost_entity:
            ghost_entity.enabled = False
        return

    if not ghost_enabled or not ghost_entity:
        if ghost_entity:
            ghost_entity.enabled = False
        return

    ghost_entity.enabled = True

    ignore_list = [player] + [obj['entity_ref'] for obj in placed_objects if obj.get('entity_ref')]
    hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=ignore_list)

    if hit_info.hit:
        x = hit_info.world_point.x
        z = hit_info.world_point.z
        y_offset = get_y_offset_for_type(current_type[0])
        ghost_entity.position = Vec3(x, 1 + y_offset, z)
    else:
        ghost_entity.enabled = False


def place_object():
    if mode[0] == 'idle':
        return

    if mode[0] == 'player_start':
        pos = ghost_entity.position if (ghost_entity and ghost_entity.enabled) else player.position
        player.position = Vec3(pos.x, 1, pos.z)
        player_start_pos[0] = player.position.x
        player_start_pos[2] = player.position.z
        print(f"Player start set to: {player.position}")

        mode[0] = 'place'
        if current_type[0] != 'npc':
            create_ghost()
        return

    obj_type = current_type[0]

    if mode[0] == 'npc' or obj_type == 'npc':
        hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(player,))
        if not hit_info.hit:
            return

        pos = Vec3(hit_info.world_point.x, 0, hit_info.world_point.z)
        rot_y = player.rotation_y

        placed_npcs.append({
            'type': 'npc',
            'x': pos.x,
            'y': 0,
            'z': pos.z,
            'scale': get_scale_for_type('npc'),
            'rot': rot_y
        })
        marker = Entity(model='sphere', scale=0.5, position=Vec3(pos.x, 0.5, pos.z), color=color.red)
        print(f"NPC placed at Y=0: {pos}")
        return

    # Обычный объект
    if not ghost_entity or not ghost_entity.enabled:
        return

    pos = ghost_entity.position
    rot_y = ghost_entity.rotation_y
    scale = get_scale_for_type(obj_type)
    model_name = get_model_for_type(obj_type)

    obj = Entity(
        model=model_name,
        scale=scale,
        position=pos,
        rotation_y=rot_y,
        collider='box'
    )

    placed_objects.append({
        'type': obj_type,
        'x': pos.x,
        'y': pos.y,
        'z': pos.z,
        'scale': scale,
        'rot': rot_y,
        'entity_ref': obj
    })
    print(f"Object {obj_type} placed at {pos}")


def delete_object():
    hit_info = raycast(camera.world_position, camera.forward, distance=50, ignore=(player,))

    if hit_info.hit:
        entity = hit_info.entity

        if entity == player or entity == ghost_entity:
            return

        target_id = id(entity)
        obj_to_remove = None
        for obj_data in placed_objects:
            ref = obj_data.get('entity_ref')
            if ref and id(ref) == target_id:
                obj_to_remove = obj_data
                break

        if obj_to_remove:
            destroy(entity)
            placed_objects.remove(obj_to_remove)
            print("Object deleted successfully")
            return

        if hasattr(entity, 'model') and entity.model == 'sphere':
            npc_to_remove = None
            for npc_data in placed_npcs:
                dist = distance(entity.position, Vec3(npc_data['x'], 0.5, npc_data['z']))
                if dist < 0.5:
                    npc_to_remove = npc_data
                    break

            if npc_to_remove:
                destroy(entity)
                placed_npcs.remove(npc_to_remove)
                print("NPC marker deleted")


def save_map():
    objects_to_save = []
    for obj in placed_objects:
        clean_obj = {k: v for k, v in obj.items() if k != 'entity_ref'}
        objects_to_save.append(clean_obj)

    data = {
        "metadata": {
            "size": GROUND_SCALE,
            "grid_size": GROUND_SCALE,
            "objects_count": len(objects_to_save),
            "npcs_count": len(placed_npcs)
        },
        "player_start": {
            "x": player_start_pos[0],
            "y": player_start_pos[1],
            "z": player_start_pos[2],
            "rot": player_start_rot[0]
        },
        "objects": objects_to_save,
        "npcs": placed_npcs
    }

    filepath = ASSETS_DIR / 'map3D.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Map Saved! {len(objects_to_save)} objects, {len(placed_npcs)} NPCs")


def load_map():
    global placed_objects, placed_npcs, player_start_pos

    for obj in placed_objects:
        if 'entity_ref' in obj:
            destroy(obj['entity_ref'])
    placed_objects.clear()

    for entity in scene.entities:
        if hasattr(entity, 'model') and entity.model == 'sphere':
            destroy(entity)
    placed_npcs.clear()

    filepath = ASSETS_DIR / 'map3D.json'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        player_start = data.get("player_start", {})
        player_start_pos[0] = player_start.get('x', 0)
        player_start_pos[2] = player_start.get('z', 0)
        player_start_rot[0] = player_start.get('rot', 0)
        player.position = Vec3(player_start_pos[0], 1, player_start_pos[2])

        for obj_data in data.get("objects", []):
            obj_type = obj_data.get("type", "cube")
            scale = obj_data.get('scale', get_scale_for_type(obj_type))
            model_name = get_model_for_type(obj_type)

            obj = Entity(
                model=model_name,
                scale=scale,
                position=(obj_data['x'], obj_data.get('y', 1), obj_data['z']),
                rotation_y=obj_data.get('rot', 0),
                collider='box'
            )
            obj_data['entity_ref'] = obj
            placed_objects.append(obj_data)

        for npc_data in data.get("npcs", []):
            marker = Entity(model='sphere', scale=0.5, position=(npc_data['x'], 0.5, npc_data['z']), color=color.red)
            npc_data['y'] = 0
            placed_npcs.append(npc_data)

        print(f"Map Loaded: {len(placed_objects)} objects, {len(placed_npcs)} NPCs")
    except FileNotFoundError:
        print("Map file not found!")


def input(key):
    global ghost_enabled, mode, current_type

    hotkeys = {
        '1': 0, '2': 1, '3': 2, '4': 3,
        '5': 4, '6': 5, '7': 6
    }

    if key in hotkeys:
        index = hotkeys[key]
        if index < len(object_types):
            current_type[0] = object_types[index]
            mode[0] = 'place'
            print(f"Selected: {current_type[0]}")
            if current_type[0] != 'npc':
                create_ghost()
            else:
                if ghost_entity: ghost_entity.enabled = False
            return

    elif key == '0':
        mode[0] = 'idle'
        if ghost_entity:
            ghost_entity.enabled = False
        print("Mode: IDLE (Ghost hidden, placement disabled)")
        return

    elif key == 'escape':
        application.quit()

    elif key == 'g':
        ghost_enabled = not ghost_enabled
        if ghost_entity:
            ghost_entity.enabled = ghost_enabled
        if ghost_enabled: refresh_ghost_position()
        print(f"Ghost: {'ON' if ghost_enabled else 'OFF'}")

    elif key == 's' and held_keys['control']:
        save_map()

    elif key == 'l' and held_keys['control']:
        load_map()

    elif key == 'p':
        mode[0] = 'player_start'
        if ghost_entity: ghost_entity.enabled = False
        print("Mode: Set Player Start (Click LMB to confirm)")

    elif key == 'n':
        if 'npc' in object_types:
            current_type[0] = 'npc'
            mode[0] = 'npc'
            if ghost_entity: ghost_entity.enabled = False
            print("Mode: Place NPC (Click LMB to place)")
        else:
            print("NPC type not found in config!")


ghost_rotation_speed = 90  # градусов в секунду | degrees per second

def update():
    global mouse_left_pressed, mouse_right_pressed

    refresh_ghost_position()

    if held_keys['r'] and ghost_entity and ghost_enabled:
        ghost_entity.rotation_y += ghost_rotation_speed * time.dt

    if mouse.left and not mouse_left_pressed:
        place_object()
        mouse_left_pressed = True

    if not mouse.left:
        mouse_left_pressed = False

    if mouse.right and not mouse_right_pressed:
        delete_object()
        mouse_right_pressed = True

    if not mouse.right:
        mouse_right_pressed = False

    if player.y < -10:
        player.position = Vec3(0, 5, 0)

    x, z = player.position.x, player.position.z
    player.x = clamp(x, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)
    player.z = clamp(z, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)


create_ghost()

info_text = Text(
    text=
    """
        MAP EDITOR
        1-7: Select Object
        0:   Hide Ghost (Idle)
        LMB: Place
        RMB: Delete
        Ctrl+S: Save
        Ctrl+L: Load
        P: Set player start
        N: Place NPC
        R: Rotate object
        G: Toggle ghost
        Q: Exit
    """,
    position=(-0.85, 0.45),
    scale=1,
    color=color.white,
    background=True,
    line_height=1.2
)

app.run()