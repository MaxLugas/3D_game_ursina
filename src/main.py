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

game_logic=None
player=None
minimap=None

def main():
    global game_logic, player, minimap
    app = init_engine()

    player = create_player(
        speed=8,
        second_jump_height=3,
        gravity=1,
        mouse_sensitivity=Vec2(40, 40),
        position=(0, 1, 0)
    )

    world_entities, statue_triggers_list = load_map('assets/map.txt')

    npcs = [
        AnimatedNPC(
            start_pos=(3, 0, 0),
            end_pos=(15, 0, 0),
            speed=3,
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
        map_half_size=35  # = ground.scale.x / 2
    )

    app.run()

def update():
    if game_logic is not None:
        game_logic.update()
    if minimap is not None:
        minimap.update()

def input(key):
    global player, game_logic
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