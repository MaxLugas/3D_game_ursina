import sys
import time
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH для абсолютных импортов | Add root dir to PYTHONPATH for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.engine import init_engine
from src.systems.map_loader import load_map
from src.systems.game_logic import GameLogic
from src.entities.player import create_player
from ursina import *
import json as json_module
from src.systems.minimap import Minimap
from src.entities.weapon import FPSWeapon
from src.core.config import PLAYER_SPEED, PLAYER_SECOND_JUMP_HEIGHT, MAP_HALF_SIZE, PLAYER_GRAVITY, \
    PLAYER_MOUSE_SENSITIVITY, GLOCK_WEAPON_MODEL, GLOCK_WEAPON_SCALE, ASSETS_DIR

game_logic = None
player = None
minimap = None
weapon = None

def main():
    """Главная функция инициализации игры. | Main game initialization function."""
    global game_logic, player, minimap, weapon
    app = init_engine()
    # Временная метка для измерения времени загрузки карты и появления мира
    _start_load = time.time()

    # Читаем стартовую позицию игрока напрямую из JSON | Read player start position directly from JSON
    filepath = ASSETS_DIR / 'map.json'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json_module.load(f)
        player_start_data = data.get("player_start", {})
        player_start = {
            'x': float(player_start_data.get('x', 0)),
            'y': float(player_start_data.get('y', 1.0)),
            'z': float(player_start_data.get('z', 0)),
            'rot': float(player_start_data.get('rot', 0))
        }
    except (FileNotFoundError, json_module.JSONDecodeError):
        player_start = {'x': 0, 'y': 1.0, 'z': 0, 'rot': 0}

    player = create_player(
        speed=PLAYER_SPEED,
        second_jump_height=PLAYER_SECOND_JUMP_HEIGHT,
        gravity=PLAYER_GRAVITY,
        mouse_sensitivity=PLAYER_MOUSE_SENSITIVITY,
        position=(player_start['x'], player_start['y'], player_start['z']),
        rotation_y=player_start['rot']
    )

    # Инициализация оружия от первого лица | Initialize first-person weapon
    weapon = FPSWeapon(model_path=GLOCK_WEAPON_MODEL, scale=GLOCK_WEAPON_SCALE)

    # Загружаем карту один раз с созданным игроком | Load map once with created player
    world_entities, npcs_from_map, _ = load_map('map.json', player=player, load_npcs=True)
    # Замерение времени после загрузки карты
    _load_duration = time.time() - _start_load
    print(f"[load-time] Карта загружена за {_load_duration:.3f} сек")

    # Инициализация игровой логики | Initialize game logic
    game_logic = GameLogic(
        player=player,
        npcs=npcs_from_map,
        world_entities=world_entities
    )

    # Создание мини-карты | Create minimap
    minimap = Minimap(
        player=player,
        world_entities=world_entities,
        npcs=npcs_from_map,
        map_half_size=MAP_HALF_SIZE
    )

    app.run()


def update():
    """Обновление состояния игры каждый кадр | Update game state each frame"""
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
    """Обработка пользовательского ввода (клавиши) | Handle user input (keys)"""
    global player, game_logic, minimap
    if key == 'e' and game_logic is not None:
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=6,
            ignore=(player,)
        )

        if hit_info.hit and getattr(hit_info.entity, 'is_statue', False):
            destroy(hit_info.entity)

            # Визуальная обратная связь | Visual feedback
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