import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.engine import init_engine
from src.systems.map_loader import load_map
from src.systems.game_logic import GameLogic
from src.entities.player import create_player
from src.entities.npc import AnimatedNPC
from ursina import *
from src.systems.minimap import Minimap
from src.entities.weapon import FPSWeapon
from src.core.config import PLAYER_SPEED, PLAYER_SECOND_JUMP_HEIGHT, MAP_HALF_SIZE, PLAYER_GRAVITY, \
    PLAYER_MOUSE_SENSITIVITY, NPC_SPEED_WALK, MODELS_DIR, GLOCK_WEAPON_MODEL

game_logic = None
player = None
minimap = None
weapon=None

def main():
    global game_logic, player, minimap, weapon
    app = init_engine()
    player = create_player(
        speed=PLAYER_SPEED,
        second_jump_height=PLAYER_SECOND_JUMP_HEIGHT,
        gravity=PLAYER_GRAVITY,
        mouse_sensitivity=PLAYER_MOUSE_SENSITIVITY,
        position=(0, 1, 0)
    )
    weapon = FPSWeapon(model_path=GLOCK_WEAPON_MODEL, scale=0.8)
    world_entities, statue_triggers_list = load_map('map.json')

    npcs = [
        AnimatedNPC(
            start_pos=(3, 0, 0),
            end_pos=(15, 0, 0),
            speed=NPC_SPEED_WALK,
            model_path='assets/models/Droid.glb',
            anim_name='Walking'
        )
    ]

    game_logic = GameLogic(
        player=player,
        npcs=npcs,
        statue_triggers=statue_triggers_list,
        world_entities=world_entities
    )

    # === Мини-карта ===
    minimap = Minimap(
        player=player,
        world_entities=world_entities,
        npcs=npcs,
        map_half_size= MAP_HALF_SIZE
    )

    app.run()


def update():
    if game_logic is not None:
        game_logic.update()
    if weapon is not None:
        weapon.update()
    if minimap is not None:
        is_tab_held = held_keys['tab']
        minimap.set_visible(is_tab_held)
        if is_tab_held:
            minimap.update()


def input(key):
    global player, game_logic, minimap
    if key == 'e' and game_logic is not None:
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=6,
            ignore=(player,)
        )
        if hit_info.hit and hit_info.entity in game_logic.statue_triggers:
            game_logic.remove_statue(hit_info.entity)

            msg = Text(
                text='Статуя подобрана!',
                origin=(0, 0),
                y=0.4,
                scale=1.5,
                color=color.white,
                background=True
            )
            msg.animate('color', color.rgba(255, 255, 255, 0), duration=2.0, curve=curve.out_expo)
            invoke(destroy, msg, delay=1.6)


if __name__ == '__main__':
    main()