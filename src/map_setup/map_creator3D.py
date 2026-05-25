import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from src.core.engine import init_engine
from src.core.config import GROUND_SCALE, MAP_HALF_SIZE, MODELS_DIR
from src.map_setup import map_editor_state as S
from src.map_setup.map_editor_ui import update_ui_text
from src.map_setup.map_editor_grid import create_grid_visual
from src.map_setup.map_editor_ghost import create_ghost, refresh_ghost_position
from src.map_setup.map_editor_objects import place_object, delete_object
from src.map_setup.map_editor_io import save_map, load_map

app = init_engine()

window.cursor_visible = True
print(f"Loaded object types: {list(S.OBJECT_CONFIGS.keys())}")

S.player = FirstPersonController(
    speed=8, jump_height=3, gravity=1,
    mouse_sensitivity=Vec2(40, 40),
    position=S.player_start_pos
)

S.ui_text = Text(
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
create_grid_visual()
create_ghost()


def input(key):
    if key in '123456':
        idx = int(key) - 1
        types = list(S.OBJECT_CONFIGS.keys())
        if idx < len(types):
            S.current_type[0] = types[idx]
            print(f"Selected: {S.current_type[0]}")
            create_ghost()
            update_ui_text()
            return

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
        S.height_offset = min(S.height_offset + 0.1, 10.0)
        refresh_ghost_position()
        update_ui_text()
        return

    if key == 'scroll down':
        S.height_offset = max(S.height_offset - 0.1, -10.0)
        refresh_ghost_position()
        update_ui_text()
        return

    if key == 'escape':
        application.quit()

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


def update():
    refresh_ghost_position()

    if held_keys['r'] and S.ghost_entity and S.ghost_enabled:
        S.ghost_entity.rotation_y += S.GHOST_ROTATION_SPEED * time.dt

    if mouse.left and not S.mouse_left_pressed:
        place_object()
        S.mouse_left_pressed = True
    if not mouse.left:
        S.mouse_left_pressed = False

    if mouse.right and not S.mouse_right_pressed:
        delete_object()
        S.mouse_right_pressed = True
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
