from ursina import *
from src.map_setup import map_editor_state as S
from src.core.objects_config import OBJECT_CONFIGS

_model_bounds_cache = {}


def get_model_size(obj_type):
    if obj_type not in _model_bounds_cache:
        e = Entity(model=get_model(obj_type), visible=False)
        _model_bounds_cache[obj_type] = e.model_bounds.size
        destroy(e)
    return _model_bounds_cache[obj_type]


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


def is_placement_blocked(x: float, z: float, obj_type: str) -> bool:
    scale = get_scale(obj_type)
    model_size = get_model_size(obj_type)
    half_x = model_size.x * scale / 2
    half_z = model_size.z * scale / 2
    new_l, new_r = x - half_x, x + half_x
    new_b, new_t = z - half_z, z + half_z

    all_objs = list(S.placed_objects) + list(S.placed_npcs)
    if S.player_spawn_data:
        all_objs.append(S.player_spawn_data)

    for obj_data in all_objs:
        t = obj_data.get('type', 'cube')
        s = obj_data.get('scale', 1.0)
        ox, oz = obj_data['x'], obj_data['z']
        ms = get_model_size(t)
        oh_x = ms.x * s / 2
        oh_z = ms.z * s / 2
        if (new_l < ox + oh_x and new_r > ox - oh_x and
            new_b < oz + oh_z and new_t > oz - oh_z):
            return True
    return False
