from ursina import Vec3, color
from pathlib import Path

# ================ Пути ================
BASE_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
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
GLOCK_WEAPON_MODEL = 'weapon_Glock.glb'
GLOCK_WEAPON_SCALE = 0.8
GLOCK_MAGAZINE_SIZE = 5
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
NPC_IDLE_DISTANCE = 15
NPC_ATTACK_DISTANCE = 10

# ================ Коллайдеры ================
COLLIDER_SHRINK_FACTOR = 0.8
ROCK_COLLIDER_SHRINK = 0.5
TREE_COLLIDER_SHRINK = 0.5
COTTAGE_COLLIDER_SHRINK = 0.2
FLASHLIGHT_COLLIDER_SHRINK = 0.2
TARGET_COLLIDER_SHRINK = 0.3
STATUE_COLLIDER_SHRINK = 1

# ================ Мини-карта ================
MINIMAP_SIZE = 0.3
MINIMAP_PLAYER_MARKER_COLOR = 'lime'
MINIMAP_NPC_MARKER_COLOR = 'crimson'
MINIMAP_PLAYER_MARKER_SCALE = 0.015
MINIMAP_NPC_MARKER_SCALE = 0.012
MINIMAP_VISIBILITY = 0.85

# ================ Ursina Engine (КРИТИЧНО ДЛЯ 60+ FPS) ================
WINDOW_TITLE = "Game"
WINDOW_BORDERLESS = False
WINDOW_VSYNC = False      # ← Отключён для максимальной производительности
SHOW_COLLIDERS = False

# ================ Цвета в стиле комикса ================
BORDERLANDS_SKY_COLOR = color.rgba(210, 240, 255, 255)  # Ярко-голубой с розовым оттенком
GRASS_COLOR = color.rgb(100, 180, 100)    # Зелёный
ROCK_COLOR = color.rgb(230, 110, 80)    # Оранжево-коричневый
TREE_COLOR = color.rgb(40, 250, 100)    # Кислотно-зелёный
COTTAGE_COLOR = color.rgb(250, 130, 70) # Ярко-оранжевый
FLASHLIGHT_COLOR = color.rgb(255, 255, 100)  # Солнечный жёлтый
STATUE_COLOR = color.rgb(150, 150, 255) # Лавандовый
TARGET_COLOR = color.rgb(255, 70, 70)   # Кроваво-красный

# ================ Окружение (БЕЗ БЛИКОВ!) ================
SKY_TEXTURE = 'sky_sunset'
GRASS_TEXTURE = 'grass'
DIRECTIONAL_LIGHT_DIRECTION = Vec3(1, -1, -1)
AMBIENT_LIGHT_COLOR = color.rgb(90, 70, 140)   # Фиолетовый для глубины
DIRECTIONAL_LIGHT_COLOR = color.rgb(240, 230, 200)  # Слегка приглушённый солнечный свет (не белый!)
SPECULAR_FACTOR = 0.0  # ← Ключевой параметр: отключаем блики