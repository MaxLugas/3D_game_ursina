from ursina import *
from src.map_setup import map_editor_state as S
from src.map_setup.map_editor_helpers import get_model, get_scale, get_display_y, update_player_spawn
from src.map_setup.map_editor_ui import update_ui_text



def place_object():
    if not S.ghost_entity or not S.ghost_entity.enabled:
        return

    obj_type = S.current_type[0]

    pos = Vec3(S.ghost_entity.position.x, S.ghost_entity.position.y, S.ghost_entity.position.z)

    obj = Entity(
        model=get_model(obj_type),
        scale=get_scale(obj_type),
        position=pos,
        rotation_y=S.ghost_entity.rotation_y,
        collider='box' if obj_type not in ('player_spawn',) else None,
        unlit=True,
        color=color.white
    )

    y_offset = round(pos.y - get_display_y(obj_type), 1)
    data = {
        'type': obj_type, 'x': pos.x, 'y': pos.y, 'z': pos.z,
        'y_offset': y_offset,
        'scale': get_scale(obj_type), 'rot': S.ghost_entity.rotation_y,
        'entity_ref': obj
    }

    if obj_type == 'npc':
        S.placed_npcs.append(data)
    elif obj_type == 'player_spawn':
        if S.player_spawn_data:
            if S.player_spawn_data.get('entity_ref'):
                destroy(S.player_spawn_data['entity_ref'])
            print("Old spawn point replaced")
        S.player_spawn_data = data
        update_player_spawn()
    else:
        S.placed_objects.append(data)

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
        destroy(entity)
        S.player_spawn_data = None
        update_player_spawn()
        print("Spawn point deleted")
        update_ui_text()
        return

    for lst, lst_name in [(S.placed_objects, 'Object'), (S.placed_npcs, 'NPC')]:
        for i, obj_data in enumerate(lst):
            if obj_data.get('entity_ref') is entity:
                destroy(entity)
                lst.pop(i)
                print(f"{lst_name} deleted successfully")
                update_ui_text()
                return
