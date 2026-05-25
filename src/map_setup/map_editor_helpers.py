import math
from ursina import *
from src.map_setup import map_editor_state as S
from src.core.objects_config import OBJECT_CONFIGS


def get_scale(obj_type: str) -> float:
    return S.SCALE_CONFIG.get(obj_type) or OBJECT_CONFIGS.get(obj_type, {}).get('scale', 1.0)


def get_model(obj_type: str) -> str:
    if obj_type == 'npc':
        return 'droid.bam'
    if obj_type == 'player_spawn':
        return 'player_spawn.bam'
    return OBJECT_CONFIGS.get(obj_type, {}).get('model', 'cube')


def get_y_offset(obj_type: str) -> float:
    return OBJECT_CONFIGS.get(obj_type, {}).get('y_offset', 0.0)


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


def update_player_spawn():
    if S.player_spawn_data:
        S.player_start_pos = Vec3(S.player_spawn_data['x'], 1, S.player_spawn_data['z'])
        S.player_start_rot = S.player_spawn_data.get('rot', 0)
        print(f"Player spawn updated to: {S.player.position}, rotation: {S.player_start_rot}")
    else:
        S.player_start_pos = Vec3(0, 1, 0)
        S.player_start_rot = 0
        print("No spawn point, using default position (0, 1, 0)")


def get_footprint_cells(x: float, z: float, scale: float) -> list[tuple[int, int]]:
    """Returns grid cell coordinates occupied by an object centered at (x, z) with given scale."""
    radius = max(1, math.ceil(scale / 2))
    cx, cz = round(x), round(z)
    return [(cx + dx, cz + dz) for dx in range(-radius, radius + 1) for dz in range(-radius, radius + 1)]


def is_placement_blocked(x: float, z: float, scale: float) -> bool:
    """Returns True if the area for an object is already occupied."""
    cells = get_footprint_cells(x, z, scale)
    return any(cell in S.occupied_cells for cell in cells)
