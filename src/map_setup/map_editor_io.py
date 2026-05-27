import json
from ursina import *
from src.core.config import GROUND_SCALE
from src.map_setup import map_editor_state as S
from src.map_setup.map_editor_helpers import get_model, get_scale, get_display_y, update_player_spawn
from src.map_setup.map_editor_ui import update_ui_text


def save_map():
    _save_keys = ('type', 'x', 'y', 'z', 'y_offset', 'scale', 'rot')
    clean_objects = [{k: v for k, v in obj.items() if k in _save_keys} for obj in S.placed_objects]
    clean_npcs = [{k: v for k, v in obj.items() if k in _save_keys} for obj in S.placed_npcs]

    clean_spawn = None
    if S.player_spawn_data:
        clean_spawn = {k: v for k, v in S.player_spawn_data.items() if k in _save_keys}

    data = {
        "metadata": {
            "size": GROUND_SCALE, "grid_size": S.grid_size,
            "objects_count": len(clean_objects),
            "npcs_count": len(clean_npcs),
            "has_spawn": clean_spawn is not None
        },
        "player_start": {
            "x": S.player_start_pos.x, "y": S.player_start_pos.y,
            "z": S.player_start_pos.z, "rot": S.player_start_rot
        },
        "objects": clean_objects,
        "npcs": clean_npcs,
        "spawn": clean_spawn
    }

    with open(S.MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    spawn_status = "with spawn" if clean_spawn else "without spawn"
    print(f"Map Saved! {len(clean_objects)} objects, {len(clean_npcs)} NPCs, {spawn_status}")


def load_map():
    for obj in S.placed_objects + S.placed_npcs:
        if 'entity_ref' in obj:
            destroy(obj['entity_ref'])

    if S.player_spawn_data and S.player_spawn_data.get('entity_ref'):
        destroy(S.player_spawn_data['entity_ref'])

    S.placed_objects.clear()
    S.placed_npcs.clear()
    S.player_spawn_data = None

    try:
        with open(S.MAP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Map file not found!")
        update_ui_text()
        return
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        update_ui_text()
        return

    for obj_data in data.get("objects", []):
        obj_type = obj_data.get("type", "cube")
        y_offset = obj_data.get('y_offset', 0)
        y = get_display_y(obj_type) + y_offset
        obj = Entity(
            model=get_model(obj_type),
            scale=obj_data.get('scale', get_scale(obj_type)),
            position=(obj_data['x'], y, obj_data['z']),
            rotation_y=obj_data.get('rot', 0),
            collider='box'
        )
        obj_data['entity_ref'] = obj
        S.placed_objects.append(obj_data)

    for npc_data in data.get("npcs", []):
        y_offset = npc_data.get('y_offset', 0)
        y = get_display_y('npc') + y_offset
        npc = Entity(
            model='droid.bam',
            scale=get_scale('npc'),
            position=(npc_data['x'], y, npc_data['z']),
            rotation_y=npc_data.get('rot', 0),
            collider='box',
            unlit=True,
            color=color.white
        )
        npc_data['entity_ref'] = npc
        S.placed_npcs.append(npc_data)

    spawn_data = data.get("spawn")
    if spawn_data:
        y_offset = spawn_data.get('y_offset', 0)
        y = get_display_y('player_spawn') + y_offset
        spawn = Entity(
            model='player_spawn.bam',
            scale=get_scale('player_spawn'),
            position=(spawn_data['x'], y, spawn_data['z']),
            rotation_y=spawn_data.get('rot', 0),
            collider=None,
            unlit=True,
            color=color.yellow
        )
        spawn_data['entity_ref'] = spawn
        S.player_spawn_data = spawn_data

    update_player_spawn()

    spawn_status = "with spawn" if S.player_spawn_data else "without spawn"
    print(f"Map Loaded: {len(S.placed_objects)} objects, {len(S.placed_npcs)} NPCs, {spawn_status}")

    update_ui_text()
