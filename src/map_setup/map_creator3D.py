import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from src.core.engine import init_engine
from src.core.config import MAP_HALF_SIZE
from src.core.objects_config import OBJECT_CONFIGS
from src.map_setup import map_editor_state as S
from src.map_setup.map_editor_ui import update_ui_text
from src.map_setup.map_editor_grid import create_grid_visual
from src.map_setup.map_editor_ghost import create_ghost, refresh_ghost_position
from src.map_setup.map_editor_objects import place_object, delete_object
from src.map_setup.map_editor_io import save_map, load_map

ALL_TYPES = list(S.OBJECT_CONFIGS.keys()) + ['npc', 'player_spawn']

app = init_engine()

window.cursor_visible = True
print(f"Loaded object types: {ALL_TYPES}")

S.player = FirstPersonController(
    speed=8, jump_height=3, gravity=1,
    mouse_sensitivity=Vec2(40, 40),
    position=S.player_start_pos
)

S.ui_text = Text(
    text="",
    position=(-0.85, 0.45),
    scale=0.7,
    color=color.black,
    background_color=color.rgba(0, 0, 0, 0.7),
    line_height=1.2,
    font='VeraMono.ttf'
)

update_ui_text()
create_grid_visual()
create_ghost()

show_colliders = False
_collider_debug_entities = []


def _get_collider_box(entity, obj_type):
    if not entity.collider or not entity.model:
        return None
    size = entity.bounds.size
    center = entity.bounds.center
    config = OBJECT_CONFIGS.get(obj_type)
    if config:
        shrink = config.get('shrink_factor')
        if shrink is not None:
            size = Vec3(size.x * shrink, size.y, size.z * shrink)
    return Entity(
        model='cube',
        scale=size,
        position=entity.position + center,
        rotation=entity.rotation,
        color=color.rgba(255, 255, 0, 80),
        wireframe=True,
        unlit=True,
        add_to_scene_entities=False
    )


def _refresh_collider_debug():
    global _collider_debug_entities
    for e in _collider_debug_entities:
        destroy(e)
    _collider_debug_entities.clear()
    if not show_colliders:
        return
    for obj_data in S.placed_objects + S.placed_npcs:
        ent = obj_data.get('entity_ref')
        if ent:
            db = _get_collider_box(ent, obj_data.get('type', ''))
            if db:
                _collider_debug_entities.append(db)
    if S.player_spawn_data and S.player_spawn_data.get('entity_ref'):
        db = _get_collider_box(S.player_spawn_data['entity_ref'], 'player_spawn')
        if db:
            _collider_debug_entities.append(db)


def _toggle_colliders():
    global show_colliders
    show_colliders = not show_colliders
    if show_colliders:
        _refresh_collider_debug()
    else:
        for e in _collider_debug_entities:
            destroy(e)
        _collider_debug_entities.clear()
    print(f"Colliders: {'ON' if show_colliders else 'OFF'}")


def input(key):
    if key == 'n':
        S.current_type[0] = 'npc'
        create_ghost()
        update_ui_text()
        return

    if key == 'p':
        S.current_type[0] = 'player_spawn'
        create_ghost()
        update_ui_text()
        return

    if key == 'x':
        S.snap_to_grid = not S.snap_to_grid
        print(f"Snap to grid: {'ON' if S.snap_to_grid else 'OFF'}")
        update_ui_text()
        return

    if key == 'h':
        S.show_grid = not S.show_grid
        for e in S.grid_entities:
            e.enabled = S.show_grid
        print(f"Grid: {'ON' if S.show_grid else 'OFF'}")
        update_ui_text()
        return

    if key == 'scroll up':
        if held_keys['shift']:
            idx = (ALL_TYPES.index(S.current_type[0]) + 1) % len(ALL_TYPES)
            S.current_type[0] = ALL_TYPES[idx]
            print(f"Selected: {S.current_type[0]}")
            create_ghost()
            update_ui_text()
        else:
            S.height_offset = min(S.height_offset + 0.1, 10.0)
            refresh_ghost_position()
            update_ui_text()
        return

    if key == 'scroll down':
        if held_keys['shift']:
            idx = (ALL_TYPES.index(S.current_type[0]) - 1) % len(ALL_TYPES)
            S.current_type[0] = ALL_TYPES[idx]
            print(f"Selected: {S.current_type[0]}")
            create_ghost()
            update_ui_text()
        else:
            S.height_offset = max(S.height_offset - 0.1, -10.0)
            refresh_ghost_position()
            update_ui_text()
        return

    if key == 'escape':
        application.quit()

    if key == 'c':
        _toggle_colliders()
        return

    if key == 'g':
        S.ghost_enabled = not S.ghost_enabled
        if S.ghost_entity:
            S.ghost_entity.enabled = S.ghost_enabled
        if S.ghost_enabled:
            refresh_ghost_position()
        print(f"Ghost: {'ON' if S.ghost_enabled else 'OFF'}")
        update_ui_text()
        return

    if key == 's' and held_keys['control']:
        save_map()
    elif key == 'l' and held_keys['control']:
        load_map()
        if show_colliders:
            _refresh_collider_debug()


def update():
    refresh_ghost_position()

    if held_keys['r'] and S.ghost_entity and S.ghost_enabled:
        S.ghost_entity.rotation_y += S.GHOST_ROTATION_SPEED * time.dt

    if mouse.left and not S.mouse_left_pressed:
        place_object()
        S.mouse_left_pressed = True
        if show_colliders:
            _refresh_collider_debug()
    if not mouse.left:
        S.mouse_left_pressed = False

    if mouse.right and not S.mouse_right_pressed:
        delete_object()
        S.mouse_right_pressed = True
        if show_colliders:
            _refresh_collider_debug()
    if not mouse.right:
        S.mouse_right_pressed = False

    if S.player.y < -10:
        if S.player_spawn_data:
            S.player.position = Vec3(S.player_spawn_data['x'], 1, S.player_spawn_data['z'])
        else:
            S.player.position = Vec3(0, 5, 0)

    S.player.x = clamp(S.player.x, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)
    S.player.z = clamp(S.player.z, -MAP_HALF_SIZE + 1, MAP_HALF_SIZE - 1)


app.run()
