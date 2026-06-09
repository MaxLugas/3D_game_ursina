from ursina import Vec3, color
from pathlib import Path

# ================ Пути | Paths ================
BASE_DIR = Path(__file__).parent.parent.parent          # Корневая директория проекта | Project root directory
ASSETS_DIR = Path(__file__).parent.parent / 'assets'    # Директория с игровыми ресурсами | Game assets directory
MODELS_DIR = ASSETS_DIR / 'models'                      # Директория 3D-моделей | 3D models directory
AUDIO_DIR = ASSETS_DIR / 'audio'                        # Директория аудиофайлов | Audio files directory
ICONS_DIR = ASSETS_DIR / 'icons'                        # Директория иконок | Icons directory
MAP_FILENAME = ASSETS_DIR/ 'map3D.json'

# ================ Игровые параметры | Game Parameters ================
GROUND_SCALE = 75                                      # Размер игрового поля | Game field size
MAP_HALF_SIZE = int(GROUND_SCALE // 2)
PLAYER_SPEED = 10                                        # Базовая скорость игрока | Player base speed
PLAYER_JUMP_HEIGHT = 2.0                                # Высота прыжка | Height of the jump
PLAYER_SECOND_JUMP_HEIGHT = 3.0                         # Высота второго прыжка | Height of the second jump
PLAYER_GRAVITY = 1                                      # Гравитации | Gravity
PLAYER_MOUSE_SENSITIVITY = (40, 40)

# ================ Мини-карта | Minimap ================
MINIMAP_SIZE = 0.3                                      # Размер мини-карты | Minimap size as fraction of screen height
MINIMAP_PLAYER_MARKER_SCALE = 0.015                     # Масштаб маркера игрока | Player marker scale
MINIMAP_NPC_MARKER_SCALE = 0.012                        # Масштаб маркера NPC | NPC marker scale
MINIMAP_VISIBILITY = 0.65                               # Прозрачность фона мини-карты | Minimap background transparency

# ================ Настройки Ursina | Ursina Settings ================
WINDOW_TITLE = "Game"                                   # Заголовок игрового окна | Game window title
WINDOW_BORDERLESS = False                               # Безрамочное окно (False = обычное окно) | Borderless window (False = standard window)
WINDOW_VSYNC = False                                    # Вертикальная синхронизация (отключена для производительности) | Vertical sync (disabled for performance)
SHOW_COLLIDERS = False                                   # Отображение отладочных коллайдеров | Show debug colliders

# ================ Освещение и окружение | Lighting and Environment ================
SKY_TEXTURE = 'sky_sunset'                              # Имя текстуры неба | Sky texture name
GRASS_TEXTURE = 'grass'                                 # Имя текстуры травы | Grass texture name
DIRECTIONAL_LIGHT_DIRECTION = Vec3(1, -1, -1)           # Направление основного света | Direction of main light source
AMBIENT_LIGHT_COLOR = color.rgb(90, 70, 140)            # Цвет фонового освещения | Ambient light color
DIRECTIONAL_LIGHT_COLOR = color.rgb(240, 230, 200)      # Цвет направленного света | Directional light color
SPECULAR_FACTOR = 0.0                                   # Отключение спекулярных бликов | Disable specular highlights

RENDER_DISTANCE = 35                                    # Дистанция рендеринга объектов | Object render distance