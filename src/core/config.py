# src/core/config.py
from pathlib import Path

# ================ Пути ================
BASE_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = BASE_DIR / 'assets'
MODELS_DIR = ASSETS_DIR / 'models'
AUDIO_DIR = ASSETS_DIR / 'audio'

# ================ Игровые параметры ================
GROUND_SCALE = 100
MAP_HALF_SIZE = int(GROUND_SCALE // 2)

PLAYER_SPEED = 8
PLAYER_JUMP_HEIGHT = 2.0
PLAYER_SECOND_JUMP_HEIGHT = 3.0
PLAYER_GRAVITY = 1
PLAYER_MOUSE_SENSITIVITY = (40, 40)

# ================ Оружие ================
WEAPON_MODEL = 'weapon_Glock.glb'
WEAPON_SCALE = 0.8
MAGAZINE_SIZE = 5
ANIM_FPS = 60

FIRE_ANIM_START_FRAME = 86
FIRE_ANIM_END_FRAME = 105
RELOAD_ANIM_START_FRAME = 106
RELOAD_ANIM_END_FRAME = 150

SOUND_GLOCK_FIRE = 'Glock_fire'
SOUND_GLOCK_RELOAD = 'Glock_reload'
RELOAD_PITCH = 0.62

# ================ NPC ================
NPC_SPEED_WALK = 3.0
NPC_SPEED_RUN = 5.0
NPC_IDLE_DISTANCE = 15  # переключение из idle в follow
NPC_ATTACK_DISTANCE = 10  # переключение в attack

# ================ Коллайдеры ================
COLLIDER_SHRINK_FACTOR = 0.8
ROCK_COLLIDER_SHRINK = 0.5
TREE_COLLIDER_SHRINK = 0.5
STATUE_COLLIDER_SHRINK = 1

# ================ Мини-карта ================
MINIMAP_SIZE = 0.3
MINIMAP_PLAYER_MARKER_COLOR = 'green'
MINIMAP_NPC_MARKER_COLOR = 'red'
MINIMAP_PLAYER_MARKER_SCALE = 0.015
MINIMAP_NPC_MARKER_SCALE = 0.012

# ================ Ursina Engine ================
WINDOW_TITLE = "Game"
WINDOW_BORDERLESS = False
WINDOW_VSYNC = False
SHOW_COLLIDERS = True
