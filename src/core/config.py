from ursina import Vec3, color
from pathlib import Path

# ================ Пути | Paths ================
BASE_DIR = Path(__file__).parent.parent.parent          # Корневая директория проекта | Project root directory
ASSETS_DIR = Path(__file__).parent.parent / 'assets'    # Директория с игровыми ресурсами | Game assets directory
MODELS_DIR = ASSETS_DIR / 'models'                      # Директория 3D-моделей | 3D models directory
AUDIO_DIR = ASSETS_DIR / 'audio'                        # Директория аудиофайлов | Audio files directory
ICONS_DIR = ASSETS_DIR / 'icons'                        # Директория иконок | Icons directory

# ================ Игровые параметры | Game Parameters ================
GROUND_SCALE = 100                                      # Размер игрового поля | Game field size
MAP_HALF_SIZE = int(GROUND_SCALE // 2)
PLAYER_SPEED = 10                                        # Базовая скорость игрока | Player base speed
PLAYER_JUMP_HEIGHT = 2.0                                # Высота прыжка | Height of the jump
PLAYER_SECOND_JUMP_HEIGHT = 3.0                         # Высота второго прыжка | Height of the second jump
PLAYER_GRAVITY = 1                                      # Гравитации | Gravity
PLAYER_MOUSE_SENSITIVITY = (40, 40)

# ================ Оружие | Weapon ================
GLOCK_WEAPON_MODEL = 'weapon_Glock.glb'                 # Имя файла 3D-модели | 3D model filename
GLOCK_WEAPON_SCALE = 0.8                                # Масштаб модели оружия от первого лица | First-person weapon model scale
GLOCK_MAGAZINE_SIZE = 5                                 # Вместимость магазина | Magazine capacity
ANIM_FPS = 60                                           # Частота кадров для анимаций оружия | Weapon animation frame rate
FIRE_ANIM_START_FRAME = 86                              # Начальный кадр анимации стрельбы | Fire animation start frame
FIRE_ANIM_END_FRAME = 105                               # Конечный кадр анимации стрельбы | Fire animation end frame
RELOAD_ANIM_START_FRAME = 106                           # Начальный кадр анимации перезарядки | Reload animation start frame
RELOAD_ANIM_END_FRAME = 150                             # Конечный кадр анимации перезарядки | Reload animation end frame
SOUND_GLOCK_FIRE = 'Glock_fire'                         # Имя звукового файла выстрела | Fire sound filename
SOUND_GLOCK_RELOAD = 'Glock_reload'                     # Имя звукового файла перезарядки | Reload sound filename
RELOAD_PITCH = 0.62                                     # Замедление звука перезарядки | Reload sound pitch slowdown factor

# ================ NPC | NPC ================
NPC_SPEED_WALK = 4.0                                    # Скорость ходьбы NPC | NPC walking speed
NPC_SPEED_RUN_1 = 8                                       # Скорость бега NPC при преследовании | NPC running speed when chasing
NPC_SPEED_RUN_2 = 13
NPC_IDLE_DISTANCE = 15                                  # Дистанция активации преследования | Distance to trigger chase behavior
NPC_ATTACK_DISTANCE = 10                                # Дистанция начала бега к игроку | Distance to start running toward player
NPC_MIN_CHASE_DISTANCE = 2.0
NPC_ATTACK_TRIGGER_DISTANCE = 2.0

# Звуки NPC | NPC sounds
NPC_SKILL_SOUND = 'Berserker_Call_2'
NPC_SKILL_SOUND_PITCH=2.27
NPC_WALK_SOUND='Walking'
NPC_ATTACK_1_SOUND='Attack_1'

# Анимации NPC | NPC animations
NPC_IDLE_ANIM = 'Idle'                                  # Анимация бездействия | Idle animation
NPC_WALK_ANIM = 'Walking'                               # Анимация ходьбы | Walking animation
NPC_RUN_ANIM_1 = 'Running_01'                           # Анимация бега | Running animation
NPC_RUN_ANIM_2= 'Running_02'
NPC_SKILL_ANIM = 'Berserker_Call'                       # Анимация навыка/атаки | Skill/attack animation
NPC_ATTACK_ANIM_1 = 'Attack_01'
NPC_SCALE = 2.0                                         # Масштаб NPC | NPC scale

# ================ Коллайдеры | Colliders ================
COLLIDER_SHRINK_FACTOR = 0.8                            # Базовый коэффициент уменьшения коллайдера | Base collider shrink factor
STONE_COLLIDER_SHRINK = 0.5                              # Уменьшение коллайдера для камней (по X/Z) | Collider shrink for STONEs (X/Z axes)
TREE_COLLIDER_SHRINK = 0.5                              # Уменьшение коллайдера для деревьев | Collider shrink for trees
COTTAGE_COLLIDER_SHRINK = 0.2                           # Уменьшение коллайдера для домиков | Collider shrink for cottages
FLASHLIGHT_COLLIDER_SHRINK = 0.2                        # Уменьшение коллайдера для фонариков | Collider shrink for flashlights
TARGET_COLLIDER_SHRINK = 1                              # Уменьшение коллайдера для мишеней | Collider shrink for targets
STATUE_COLLIDER_SHRINK = 1                              # Коллайдер статуи = размер модели | Statue collider matches model size

# ================ Мини-карта | Minimap ================
MINIMAP_SIZE = 0.3                                      # Размер мини-карты | Minimap size as fraction of screen height
MINIMAP_PLAYER_MARKER_COLOR = 'lime'                    # Цвет маркера игрока | Player marker color
MINIMAP_NPC_MARKER_COLOR = 'crimson'                    # Цвет маркера NPC | NPC marker color
MINIMAP_PLAYER_MARKER_SCALE = 0.015                     # Масштаб маркера игрока | Player marker scale
MINIMAP_NPC_MARKER_SCALE = 0.012                        # Масштаб маркера NPC | NPC marker scale
MINIMAP_VISIBILITY = 0.85                               # Прозрачность фона мини-карты | Minimap background transparency

# ================ Настройки Ursina | Ursina Settings ================
WINDOW_TITLE = "Game"                                   # Заголовок игрового окна | Game window title
WINDOW_BORDERLESS = False                               # Безрамочное окно (False = обычное окно) | Borderless window (False = standard window)
WINDOW_VSYNC = False                                    # Вертикальная синхронизация (отключена для производительности) | Vertical sync (disabled for performance)
SHOW_COLLIDERS = True                                   # Отображение отладочных коллайдеров | Show debug colliders

# ================ Цвета объектов в стиле комикс | Comic-Style Object Colors ================
STONE_COLOR = color.rgb(230, 110, 80)
TREE_COLOR = color.rgb(40, 250, 100)
COTTAGE_COLOR = color.rgb(250, 130, 70)
FLASHLIGHT_COLOR = color.rgb(255, 255, 100)
STATUE_COLOR = color.rgb(150, 150, 255)
TARGET_COLOR = color.rgb(255, 70, 70)

# ================ Освещение и окружение | Lighting and Environment ================
SKY_TEXTURE = 'sky_sunset'                              # Имя текстуры неба | Sky texture name
GRASS_TEXTURE = 'grass'                                 # Имя текстуры травы | Grass texture name
DIRECTIONAL_LIGHT_DIRECTION = Vec3(1, -1, -1)           # Направление основного света | Direction of main light source
AMBIENT_LIGHT_COLOR = color.rgb(90, 70, 140)            # Цвет фонового освещения | Ambient light color
DIRECTIONAL_LIGHT_COLOR = color.rgb(240, 230, 200)      # Цвет направленного света | Directional light color
SPECULAR_FACTOR = 0.0                                   # Отключение спекулярных бликов | Disable specular highlights