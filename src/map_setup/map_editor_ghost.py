from ursina import *
from src.map_setup import map_editor_state as S
from src.map_setup.map_editor_helpers import get_model, get_scale, get_display_y, is_placement_blocked
from src.core.config import GROUND_SCALE


def create_ghost():
    if S.ghost_entity:
        destroy(S.ghost_entity)

    obj_type = S.current_type[0]
    S.ghost_entity = Entity(
        model=get_model(obj_type),
        scale=get_scale(obj_type),
        color=color.yellow,
        double_sided=True,
        unlit=True,
        visible=S.ghost_enabled
    )
    refresh_ghost_position()


def refresh_ghost_position():
    if not S.ghost_entity or not S.ghost_enabled:
        if S.ghost_entity:
            S.ghost_entity.enabled = False
        return

    S.ghost_entity.enabled = True

    ignore_list = [S.player]
    for lst in (S.placed_objects, S.placed_npcs):
        ignore_list.extend(obj['entity_ref'] for obj in lst if obj.get('entity_ref'))

    if S.player_spawn_data and S.player_spawn_data.get('entity_ref'):
        ignore_list.append(S.player_spawn_data['entity_ref'])

    hit = raycast(camera.world_position, camera.forward, distance=S.RAYCAST_DISTANCE, ignore=ignore_list)

    if hit.hit:
        x, z = hit.world_point.x, hit.world_point.z

        if S.snap_to_grid:
            half = GROUND_SCALE // 2
            gx = round((x + half) / S.cell_size)
            gz = round((z + half) / S.cell_size)
            x = gx * S.cell_size - half
            z = gz * S.cell_size - half

        y = get_display_y(S.current_type[0]) + S.height_offset
        S.ghost_entity.position = Vec3(x, y, z)

        if is_placement_blocked(x, z, S.current_type[0]):
            S.ghost_entity.color = color.red
        else:
            S.ghost_entity.color = color.yellow
    else:
        S.ghost_entity.enabled = False
