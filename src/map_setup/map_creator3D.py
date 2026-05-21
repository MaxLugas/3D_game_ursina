import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from src.core.config import GROUND_SCALE, MAP_HALF_SIZE, ASSETS_DIR, MODELS_DIR
from src.core.npc_config import DROID_SCALE


from src.core.objects_config import PLAYER_SPAWN_SCALE, STONE_SCALE, TARGET_SCALE, STATUE_SCALE, FLASHLIGHT_SCALE, \
    COTTAGE_SCALE, TREE_SCALE

from src.core.engine import init_engine
from src.systems.map_loader import OBJECT_CONFIGS

application.asset_folder = MODELS_DIR

app = init_engine()

SCALE_CONFIG = {
    'tree': TREE_SCALE, 'stone': STONE_SCALE, 'cottage': COTTAGE_SCALE,
    'flashlight': FLASHLIGHT_SCALE, 'statue': STATUE_SCALE, 'target': TARGET_SCALE,
    'npc': DROID_SCALE, 'player_spawn': PLAYER_SPAWN_SCALE
}
MAP_FILE = ASSETS_DIR / 'map3D.json'
GHOST_ROTATION_SPEED = 90
RAYCAST_DISTANCE = 100
DELETE_RAYCAST_DISTANCE = 50

current_type = [next(iter(OBJECT_CONFIGS.keys()), 'cube')]
ghost_enabled = True
mouse_left_pressed = False
mouse_right_pressed = False
snap_to_grid = False
show_grid = True
grid_size = GROUND_SCALE
cell_size = GROUND_SCALE / grid_size
grid_entities = []

placed_objects = []
placed_npcs = []
player_spawn_data = None
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

info_panel = """
=== MAP EDITOR ===

[OBJECTS]                           [CONTROLS]
1: Stone    2: Tree    3: Cottage   LMB: Place    RMB: Delete
4: Lamp     5: Statue  6: Target    R: Rotate     G: Ghost mode
N: NPC      P: Spawn                X: Snap       H: Grid
                                    Ctrl+S: Save  Ctrl+L: Load
                                    ESC: Exit

[CURRENT]
Type: {current}
Ghost: {ghost}
Snap: {snap}
Grid: {grid}
Objects: {obj_count}
NPCs: {npc_count}
Spawn: {spawn_status}
"""


def update_ui_text():
    """Обновляет текст интерфейса"""
    ghost_status = "ON" if ghost_enabled else "OFF"
    spawn_status = "YES" if player_spawn_data else "NO"
    snap_status = "ON" if snap_to_grid else "OFF"
    grid_status = "ON" if show_grid else "OFF"

    ui_text.text = info_panel.format(
        current=current_type[0].upper(),
        ghost=ghost_status,
        snap=snap_status,
        grid=grid_status,
        obj_count=len(placed_objects),
        npc_count=len(placed_npcs),
        spawn_status=spawn_status
    )


ui_text = Text(
    text="",
    position=(-0.85, 0.45),
    scale=0.7,
    color=color.white,
    background=True,
    background_color=color.rgba(0, 0, 0, 0.7),
    line_height=1.2,
    font='VeraMono.ttf'
)

update_ui_text()

def create_grid_visual():
    global grid_entities
    for e in grid_entities:
        destroy(e)
    grid_entities.clear()

    half = GROUND_SCALE // 2
    step = 1
    grid_color = color.rgba(100, 100, 100, 60)

    for i in range(-half, half + 1, step):
        line_x = Entity(
            model='cube',
            scale=(GROUND_SCALE, 0.002, 0.002),
            position=(0, 0.005, i),
            color=grid_color,
            unlit=True,
            collider=None,
            enabled=show_grid
        )
        grid_entities.append(line_x)

        line_z = Entity(
            model='cube',
            scale=(0.002, 0.002, GROUND_SCALE),
            position=(i, 0.005, 0),
            color=grid_color,
            unlit=True,
            collider=None,
            enabled=show_grid
        )
        grid_entities.append(line_z)

def get_scale(obj_type: str) -> float:
    return SCALE_CONFIG.get(obj_type) or OBJECT_CONFIGS.get(obj_type, {}).get('scale', 1.0)

def get_model(obj_type: str) -> str:
    if obj_type == 'npc':
        return 'droid.bam'
    if obj_type == 'player_spawn':
        return 'player_spawn.bam'
    return OBJECT_CONFIGS.get(obj_type, {}).get('model', 'cube')

def get_y_offset(obj_type: str) -> float:
    return OBJECT_CONFIGS.get(obj_type, {}).get('y_offset', 0.0)

def update_player_spawn():
    global player_start_pos, player_start_rot, player_spawn_data
    if player_spawn_data:
        player_start_pos = Vec3(player_spawn_data['x'], 1, player_spawn_data['z'])
        player_start_rot = player_spawn_data.get('rot', 0)
        print(f"Player spawn updated to: {player.position}, rotation: {player_start_rot}")
    else:
        player_start_pos = Vec3(0, 1, 0)
        player_start_rot = 0
        print("No spawn point, using default position (0, 1, 0)")

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
        visible=ghost_enabled
    )
    refresh_ghost_position()


def get_display_y(obj_type: str) -> float:
    scale = get_scale(obj_type)

    if obj_type in ('npc', 'player_spawn'):
        return scale

    base_y = scale if scale != 1.0 else 1.0
    return base_y + get_y_offset(obj_type)


def get_save_y(obj_type: str) -> float:
    if obj_type in ('npc', 'player_spawn'):
        return 0.0

    scale = get_scale(obj_type)
    base_y = scale if scale != 1.0 else 1.0
    return base_y + get_y_offset(obj_type)

def refresh_ghost_position():
    global ghost_entity
    if not ghost_entity or not ghost_enabled:
        if ghost_entity:
            ghost_entity.enabled = False
        return

    ghost_entity.enabled = True

    ignore_list = [player]
    for lst in (placed_objects, placed_npcs):
        ignore_list.extend(obj['entity_ref'] for obj in lst if obj.get('entity_ref'))

    if player_spawn_data and player_spawn_data.get('entity_ref'):
        ignore_list.append(player_spawn_data['entity_ref'])

    hit = raycast(camera.world_position, camera.forward, distance=RAYCAST_DISTANCE, ignore=ignore_list)

    if hit.hit:
        x, z = hit.world_point.x, hit.world_point.z

        if snap_to_grid:
            half = GROUND_SCALE // 2
            gx = round((x + half) / cell_size)
            gz = round((z + half) / cell_size)
            x = gx * cell_size - half
            z = gz * cell_size - half

        y = get_display_y(current_type[0])
        ghost_entity.position = Vec3(x, y, z)
    else:
        ghost_entity.enabled = False

def place_object():
    global player_spawn_data

    if not ghost_entity or not ghost_entity.enabled:
        return

    obj_type = current_type[0]

    pos = Vec3(ghost_entity.position.x, get_display_y(obj_type), ghost_entity.position.z)

    obj_color = color.white

    obj = Entity(
        model=get_model(obj_type),
        scale=get_scale(obj_type),
        position=pos,
        rotation_y=ghost_entity.rotation_y,
        collider='box' if obj_type not in ('player_spawn',) else None,
        unlit=True,
        color=obj_color
    )

    save_y = get_save_y(obj_type)
    data = {
        'type': obj_type, 'x': pos.x, 'y': save_y, 'z': pos.z,
        'scale': get_scale(obj_type), 'rot': ghost_entity.rotation_y,
        'entity_ref': obj
    }

    if obj_type == 'npc':
        placed_npcs.append(data)
    elif obj_type == 'player_spawn':
        if player_spawn_data:
            if player_spawn_data.get('entity_ref'):
                destroy(player_spawn_data['entity_ref'])
            print("Old spawn point replaced")
        player_spawn_data = data
        update_player_spawn()
    else:
        placed_objects.append(data)

    update_ui_text()

def delete_object():
    global player_spawn_data

    hit = raycast(camera.world_position, camera.forward, distance=DELETE_RAYCAST_DISTANCE,
                  ignore=(player, ghost_entity))
    if not hit.hit:
        return

    entity = hit.entity
    if entity in (player, ghost_entity):
        return

    if player_spawn_data and player_spawn_data.get('entity_ref') is entity:
        destroy(entity)
        player_spawn_data = None
        update_player_spawn()
        print("Spawn point deleted")
        update_ui_text()
        return

    for lst, lst_name in [(placed_objects, 'Object'), (placed_npcs, 'NPC')]:
        for i, obj_data in enumerate(lst):
            if obj_data.get('entity_ref') is entity:
                destroy(entity)
                lst.pop(i)
                print(f"{lst_name} deleted successfully")
                update_ui_text()
                return

def save_map():
    clean_objects = [{k: v for k, v in obj.items() if k != 'entity_ref'} for obj in placed_objects]
    clean_npcs = [{k: v for k, v in obj.items() if k != 'entity_ref'} for obj in placed_npcs]

    clean_spawn = None
    if player_spawn_data:
        clean_spawn = {k: v for k, v in player_spawn_data.items() if k != 'entity_ref'}

    data = {
        "metadata": {
            "size": GROUND_SCALE, "grid_size": GROUND_SCALE,
            "objects_count": len(clean_objects),
            "npcs_count": len(clean_npcs),
            "has_spawn": clean_spawn is not None
        },
        "player_start": {
            "x": player_start_pos.x, "y": player_start_pos.y,
            "z": player_start_pos.z, "rot": player_start_rot
        },
        "objects": clean_objects,
        "npcs": clean_npcs,
        "spawn": clean_spawn
    }

    with open(MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    spawn_status = "with spawn" if clean_spawn else "without spawn"
    print(f"Map Saved! {len(clean_objects)} objects, {len(clean_npcs)} NPCs, {spawn_status}")

def load_map():
    global placed_objects, placed_npcs, player_spawn_data, player_start_pos, player_start_rot

    for obj in placed_objects + placed_npcs:
        if 'entity_ref' in obj:
            destroy(obj['entity_ref'])

    if player_spawn_data and player_spawn_data.get('entity_ref'):
        destroy(player_spawn_data['entity_ref'])

    placed_objects.clear()
    placed_npcs.clear()
    player_spawn_data = None

    try:
        with open(MAP_FILE, 'r', encoding='utf-8') as f:
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
        visual_y = get_display_y(obj_type)
        obj = Entity(
            model=get_model(obj_type),
            scale=obj_data.get('scale', get_scale(obj_type)),
            position=(obj_data['x'], visual_y, obj_data['z']),
            rotation_y=obj_data.get('rot', 0),
            collider='box'
        )
        obj_data['entity_ref'] = obj
        placed_objects.append(obj_data)

    for npc_data in data.get("npcs", []):
        visual_y = get_display_y('npc')
        npc = Entity(
            model='droid.bam',
            scale=get_scale('npc'),
            position=(npc_data['x'], visual_y, npc_data['z']),
            rotation_y=npc_data.get('rot', 0),
            collider='box',
            unlit=True,
            color=color.white
        )
        npc_data['y'] = 0
        npc_data['entity_ref'] = npc
        placed_npcs.append(npc_data)

    spawn_data = data.get("spawn")
    if spawn_data:
        visual_y = get_display_y('player_spawn')
        spawn = Entity(
            model='player_spawn.bam',
            scale=get_scale('player_spawn'),
            position=(spawn_data['x'], visual_y, spawn_data['z']),
            rotation_y=spawn_data.get('rot', 0),
            collider=None,
            unlit=True,
            color=color.yellow
        )
        spawn_data['entity_ref'] = spawn
        player_spawn_data = spawn_data

    update_player_spawn()

    spawn_status = "with spawn" if player_spawn_data else "without spawn"
    print(f"Map Loaded: {len(placed_objects)} objects, {len(placed_npcs)} NPCs, {spawn_status}")

    update_ui_text()

def input(key):
    global ghost_enabled, current_type, snap_to_grid, show_grid

    if key in '123456':
        idx = int(key) - 1
        types = list(OBJECT_CONFIGS.keys())
        if idx < len(types):
            current_type[0] = types[idx]
            print(f"Selected: {current_type[0]}")
            create_ghost()
            update_ui_text()
            return

    if key == 'n':
        current_type[0] = 'npc'
        create_ghost()
        update_ui_text()
        return

    if key == 'p':
        current_type[0] = 'player_spawn'
        create_ghost()
        update_ui_text()
        return

    if key == 'x':
        snap_to_grid = not snap_to_grid
        print(f"Snap to grid: {'ON' if snap_to_grid else 'OFF'}")
        update_ui_text()
        return

    if key == 'h':
        show_grid = not show_grid
        for e in grid_entities:
            e.enabled = show_grid
        print(f"Grid: {'ON' if show_grid else 'OFF'}")
        update_ui_text()
        return

    if key == 'escape':
        application.quit()

    if key == 'g':
        ghost_enabled = not ghost_enabled
        if ghost_entity:
            ghost_entity.enabled = ghost_enabled
        if ghost_enabled:
            refresh_ghost_position()
        print(f"Ghost: {'ON' if ghost_enabled else 'OFF'}")
        update_ui_text()
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
        if player_spawn_data:
            player.position = Vec3(player_spawn_data['x'], 1, player_spawn_data['z'])
        else:
            player.position = Vec3(0, 5, 0)

    player.x = clamp(player.x, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)
    player.z = clamp(player.z, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)

create_grid_visual()
create_ghost()

app.run()