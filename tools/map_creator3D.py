import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from src.core.config import (
    GROUND_SCALE, MAP_HALF_SIZE, ASSETS_DIR, MODELS_DIR,
    STONE_SCALE, TARGET_SCALE, STATUE_SCALE, FLASHLIGHT_SCALE,
    COTTAGE_SCALE, TREE_SCALE, NPC_SCALE
)
from src.core.engine import init_engine
from src.systems.map_loader import OBJECT_CONFIGS

application.asset_folder = MODELS_DIR

app = init_engine()

SCALE_CONFIG = {
    'tree': TREE_SCALE, 'stone': STONE_SCALE, 'cottage': COTTAGE_SCALE,
    'flashlight': FLASHLIGHT_SCALE, 'statue': STATUE_SCALE, 'target': TARGET_SCALE,
    'npc': NPC_SCALE
}
MAP_FILE = ASSETS_DIR / 'map3D.json'
GHOST_ROTATION_SPEED = 90
RAYCAST_DISTANCE = 100
DELETE_RAYCAST_DISTANCE = 50

current_type = [next(iter(OBJECT_CONFIGS.keys()), 'cube')]
mode = ['place']
ghost_enabled = True
mouse_left_pressed = False
mouse_right_pressed = False

placed_objects = []
placed_npcs = []
player_start_pos = Vec3(0, 1, 0)
player_start_rot = 0.0
ghost_entity = None

window.cursor_visible = True
print(f"Loaded object types: {list(OBJECT_CONFIGS.keys())}")

player = FirstPersonController(
    speed=8, jump_height=3, gravity=1,
    mouse_sensitivity=Vec2(40, 40),
    position=player_start_pos
)

def get_scale(obj_type: str) -> float:
    return SCALE_CONFIG.get(obj_type) or OBJECT_CONFIGS.get(obj_type, {}).get('scale', 1.0)

def get_model(obj_type: str) -> str:
    if obj_type == 'npc':
        return 'droid.bam'
    return OBJECT_CONFIGS.get(obj_type, {}).get('model', 'cube')

def get_y_offset(obj_type: str) -> float:
    return OBJECT_CONFIGS.get(obj_type, {}).get('y_offset', 0.0)

def create_ghost():
    global ghost_entity
    if ghost_entity:
        destroy(ghost_entity)

    obj_type = current_type[0]
    ghost_entity = Entity(
        model=get_model(obj_type),
        scale=get_scale(obj_type),
        color=color.yellow,
        double_sided=True,
        unlit=True,
        visible=True
    )
    refresh_ghost_position()

def refresh_ghost_position():
    global ghost_entity
    if not ghost_entity or mode[0] in ('idle', 'player_start') or not ghost_enabled:
        if ghost_entity: ghost_entity.enabled = False
        return

    ghost_entity.enabled = True

    ignore_list = [player]
    for lst in (placed_objects, placed_npcs):
        ignore_list.extend(obj['entity_ref'] for obj in lst if obj.get('entity_ref'))

    hit = raycast(camera.world_position, camera.forward, distance=RAYCAST_DISTANCE, ignore=ignore_list)

    if hit.hit:
        x, z = hit.world_point.x, hit.world_point.z
        y = 0.0 if current_type[0] == 'npc' else 1.0 + get_y_offset(current_type[0])
        ghost_entity.position = Vec3(x, y, z)
    else:
        ghost_entity.enabled = False

def place_object():
    if mode[0] == 'idle' or not ghost_entity or not ghost_entity.enabled:
        return

    if mode[0] == 'player_start':
        pos = ghost_entity.position if ghost_entity.enabled else player.position
        player.position = Vec3(pos.x, 1, pos.z)
        player_start_pos.x, player_start_pos.z = pos.x, pos.z
        print(f"Player start set to: {player.position}")
        mode[0] = 'place'
        create_ghost()
        return

    obj_type = current_type[0]
    pos = Vec3(ghost_entity.position.x, 0, ghost_entity.position.z) if obj_type == 'npc' else ghost_entity.position

    obj = Entity(
        model=get_model(obj_type),
        scale=get_scale(obj_type),
        position=pos,
        rotation_y=ghost_entity.rotation_y,
        collider='box',
        unlit=True,
        color=color.white
    )

    data = {
        'type': obj_type, 'x': pos.x, 'y': pos.y, 'z': pos.z,
        'scale': get_scale(obj_type), 'rot': ghost_entity.rotation_y,
        'entity_ref': obj
    }

    target_list = placed_npcs if obj_type == 'npc' else placed_objects
    target_list.append(data)
    print(f"{'NPC' if obj_type == 'npc' else 'Object'} placed at {pos}")

def delete_object():
    hit = raycast(camera.world_position, camera.forward, distance=DELETE_RAYCAST_DISTANCE, ignore=(player, ghost_entity))
    if not hit.hit:
        return

    entity = hit.entity
    if entity in (player, ghost_entity):
        return

    for lst in (placed_objects, placed_npcs):
        for i, obj_data in enumerate(lst):
            if obj_data.get('entity_ref') is entity:
                destroy(entity)
                lst.pop(i)
                print(f"{'NPC' if obj_data['type'] == 'npc' else 'Object'} deleted successfully")
                return

def save_map():
    clean_objects = [{k: v for k, v in obj.items() if k != 'entity_ref'} for obj in placed_objects]
    clean_npcs = [{k: v for k, v in obj.items() if k != 'entity_ref'} for obj in placed_npcs]

    data = {
        "metadata": {
            "size": GROUND_SCALE, "grid_size": GROUND_SCALE,
            "objects_count": len(clean_objects), "npcs_count": len(clean_npcs)
        },
        "player_start": {
            "x": player_start_pos.x, "y": player_start_pos.y,
            "z": player_start_pos.z, "rot": player_start_rot
        },
        "objects": clean_objects,
        "npcs": clean_npcs
    }

    with open(MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Map Saved! {len(clean_objects)} objects, {len(clean_npcs)} NPCs")

def load_map():
    global placed_objects, placed_npcs, player_start_pos, player_start_rot

    for obj in placed_objects + placed_npcs:
        if 'entity_ref' in obj:
            destroy(obj['entity_ref'])
    placed_objects.clear()
    placed_npcs.clear()

    try:
        with open(MAP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Map file not found!")
        return
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return

    p_start = data.get("player_start", {})
    player_start_pos.x = p_start.get('x', 0)
    player_start_pos.z = p_start.get('z', 0)
    player_start_rot = p_start.get('rot', 0)
    player.position = Vec3(player_start_pos.x, 1, player_start_pos.z)

    for obj_data in data.get("objects", []):
        obj_type = obj_data.get("type", "cube")
        obj = Entity(
            model=get_model(obj_type), scale=obj_data.get('scale', get_scale(obj_type)),
            position=(obj_data['x'], obj_data.get('y', 1), obj_data['z']),
            rotation_y=obj_data.get('rot', 0), collider='box'
        )
        obj_data['entity_ref'] = obj
        placed_objects.append(obj_data)

    for npc_data in data.get("npcs", []):
        npc = Entity(
            model='droid.bam', scale=get_scale('npc'),
            position=(npc_data['x'], 0, npc_data['z']),
            collider='box', unlit=True, color=color.white
        )
        npc_data['y'] = 0
        npc_data['entity_ref'] = npc
        placed_npcs.append(npc_data)

    print(f"Map Loaded: {len(placed_objects)} objects, {len(placed_npcs)} NPCs")

def input(key):
    global ghost_enabled, mode, current_type

    if key in '1234567':
        idx = int(key) - 1
        types = list(OBJECT_CONFIGS.keys())
        if idx < len(types):
            current_type[0] = types[idx]
            mode[0] = 'place'
            print(f"Selected: {current_type[0]}")
            create_ghost()
            return

    if key == 'n':
        current_type[0] = 'npc'
        mode[0] = 'place'
        print("Selected: npc")
        create_ghost()
        return

    if key == '0':
        mode[0] = 'idle'
        if ghost_entity: ghost_entity.enabled = False
        print("Mode: IDLE")
        return

    if key == 'escape':
        application.quit()

    if key == 'g':
        ghost_enabled = not ghost_enabled
        if ghost_entity: ghost_entity.enabled = ghost_enabled
        if ghost_enabled: refresh_ghost_position()
        print(f"Ghost: {'ON' if ghost_enabled else 'OFF'}")
        return

    if key == 'p':
        mode[0] = 'player_start'
        if ghost_entity: ghost_entity.enabled = False
        print("Mode: Set Player Start")
        return

    if key == 's' and held_keys['control']:
        save_map()
    elif key == 'l' and held_keys['control']:
        load_map()

def update():
    global mouse_left_pressed, mouse_right_pressed

    refresh_ghost_position()

    if held_keys['r'] and ghost_entity and ghost_enabled:
        ghost_entity.rotation_y += GHOST_ROTATION_SPEED * time.dt

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

    player.x = clamp(player.x, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)
    player.z = clamp(player.z, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)

create_ghost()

Text(
    text="""
        MAP EDITOR
        1-6: Select Object
        N:   Place NPC
        0:   Hide Ghost
        LMB: Place
        RMB: Delete
        Ctrl+S: Save
        Ctrl+L: Load
        P: Set player start
        R: Rotate object
        G: Toggle ghost
        Q: Exit
    """,
    position=(-0.85, 0.45), scale=1, color=color.white,
    background=True, line_height=1.2
)

app.run()