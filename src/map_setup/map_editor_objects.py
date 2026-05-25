from ursina import *
from src.map_setup import map_editor_state as S
from src.map_setup.map_editor_helpers import get_model, get_scale, get_display_y, update_player_spawn, \
    is_placement_blocked, get_footprint_cells
from src.map_setup.map_editor_ui import update_ui_text



def place_object():
    if not S.ghost_entity or not S.ghost_entity.enabled:
        return

    obj_type = S.current_type[0]
    scale = get_scale(obj_type)

    pos = Vec3(S.ghost_entity.position.x, S.ghost_entity.position.y, S.ghost_entity.position.z)

    if is_placement_blocked(pos.x, pos.z, scale):
        print(f"Cannot place {obj_type}: area already occupied!")
        return

    obj = Entity(
        model=get_model(obj_type),
        scale=scale,
        position=pos,
        rotation_y=S.ghost_entity.rotation_y,
        collider='box' if obj_type not in ('player_spawn',) else None,
        unlit=True,
        color=color.white
    )

    footprint_cells = get_footprint_cells(pos.x, pos.z, scale)
    base_y = get_display_y(obj_type)
    y_offset = round(pos.y - base_y, 1)
    data = {
        'type': obj_type, 'x': pos.x, 'y': base_y, 'z': pos.z,
        'y_offset': y_offset,
        'scale': scale, 'rot': S.ghost_entity.rotation_y,
        'entity_ref': obj,
        'footprint_cells': footprint_cells
    }

    if obj_type == 'npc':
        S.placed_npcs.append(data)
    elif obj_type == 'player_spawn':
        if S.player_spawn_data:
            old_cells = S.player_spawn_data.get('footprint_cells', [])
            for cell in old_cells:
                S.occupied_cells.discard(cell)
            if S.player_spawn_data.get('entity_ref'):
                destroy(S.player_spawn_data['entity_ref'])
            print("Old spawn point replaced")
        S.player_spawn_data = data
        update_player_spawn()
    else:
        S.placed_objects.append(data)

    for cell in footprint_cells:
        S.occupied_cells.add(cell)

    update_ui_text()


def delete_object():
    hit = raycast(camera.world_position, camera.forward, distance=S.DELETE_RAYCAST_DISTANCE,
                  ignore=(S.player, S.ghost_entity))
    if not hit.hit:
        return

    entity = hit.entity
    if entity in (S.player, S.ghost_entity):
        return

    if S.player_spawn_data and S.player_spawn_data.get('entity_ref') is entity:
        old_cells = S.player_spawn_data.get('footprint_cells', [])
        for cell in old_cells:
            S.occupied_cells.discard(cell)
        destroy(entity)
        S.player_spawn_data = None
        update_player_spawn()
        print("Spawn point deleted")
        update_ui_text()
        return

    for lst, lst_name in [(S.placed_objects, 'Object'), (S.placed_npcs, 'NPC')]:
        for i, obj_data in enumerate(lst):
            if obj_data.get('entity_ref') is entity:
                old_cells = obj_data.get('footprint_cells', [])
                for cell in old_cells:
                    S.occupied_cells.discard(cell)
                destroy(entity)
                lst.pop(i)
                print(f"{lst_name} deleted successfully")
                update_ui_text()
                return
