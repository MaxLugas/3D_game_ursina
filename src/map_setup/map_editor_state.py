import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ursina import *

from src.core.config import GROUND_SCALE, MAP_HALF_SIZE, ASSETS_DIR, MODELS_DIR
from src.core.npc_config import DROID_SCALE
from src.core.objects_config import PLAYER_SPAWN_SCALE, STONE_SCALE, TARGET_SCALE, STATUE_SCALE, FLASHLIGHT_SCALE, \
    COTTAGE_SCALE, TREE_SCALE, OBJECT_CONFIGS

application.asset_folder = MODELS_DIR

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
height_offset = 0.0

occupied_cells: set[tuple[int, int]] = set()

player = None
ui_text = None
