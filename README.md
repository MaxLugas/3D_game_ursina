# 🎮 Comic-Style Game

![Ursina Engine](https://img.shields.io/badge/Ursina-Python%20Game%20Engine-ff6b6b?logo=python&logoColor=white)
![Style](https://img.shields.io/badge/Art%20Style-Comic%20Book%20Cel--Shading-4ecdc4)
![License](https://img.shields.io/badge/License-MIT-blue)

**Комиксная игра с анимированным оружием и разрушаемыми объектами**  
*A comic-book styled game with animated weapons and destructible objects*

---

## 🛠️ Технологии / Tech Stack

| Русский | English |
|---------|---------|
| **Python**: 3.11 | **Python**: 3.11 
| **Движок**: [Ursina Engine](https://www.ursinaengine.org/) (Python + Panda3D) | **Engine**: [Ursina Engine](https://www.ursinaengine.org/) (Python + Panda3D) |
| **Графика**: Кастомный GLSL-шейдер для стиля комикса | **Graphics**: Custom GLSL shader for comic-book visual style |
| **Анимации**: Panda3D Actor system (FBX/GLB) | **Animation**: Panda3D Actor system (FBX/GLB) |
| **Аудио**: Встроенный аудио-менеджер Ursina | **Audio**: Built-in Ursina audio manager |
| **Карта**: JSON с нормализованными координатами (-1..1) | **Map format**: JSON with normalized coordinates (-1..1) |
| **Коллайдеры**: Автоматическая настройка под каждый тип объекта | **Colliders**: Auto-configured per object type |
| **Стилизация**: Чёрные контуры через рендеринг обратных граней | **Styling**: Black outlines via backface rendering |


## 🌟 Особенности / Features

| Русский                                                       | English                                      |
|---------------------------------------------------------------|----------------------------------------------|
| ✨ Стиль комикса с кастомным шейдером                          | ✨ Comic-book visual style with custom shader |
| 🔫 Анимация оружия                                            | 🔫 Frame-accurate weapon animations          |
| 🦘 Двойной прыжок для динамичного геймплея                    | 🦘 Double jump for dynamic movement          |
| 💥 Разрушаемые объекты при попадании                          | 💥 Destructible targets on bullet impact     |
| 🗺️ Мини-карта с маркерами                                    | 🗺️ Minimap with object markers              |
| 🗿 Сбор коллекционных предметов                               | 🗿 Collectible items                         |
| 👥 Анимированные NPC с перемещением между точками             | 👥 Animated NPCs with patrol movement        |
| 🎨 Автоматическая настройка коллайдеров под каждый тип объекта | 🎨 Auto-configured colliders per object type |


## ⚙️ Централизованная конфигурация / Centralized Configuration

| Русский | English |
|---------|---------|
| **Все настройки игры находятся в одном файле** `src/core/config.py` | **All game settings centralized in a single file** `src/core/config.py` |
| Изменяйте параметры без правки основного кода | Tweak gameplay without touching core logic |
| Поддержка быстрой балансировки и прототипирования | Fast balancing and prototyping support |
| Группировка по категориям: пути, геймплей, оружие, NPC, визуал | Categorized sections: paths, gameplay, weapons, NPCs, visuals |

**Примеры настроек / Configuration examples:**
```python
# Геймплей | Gameplay
PLAYER_SPEED = 8
PLAYER_JUMP_HEIGHT = 2.0
PLAYER_SECOND_JUMP_HEIGHT = 3.0
GROUND_SCALE = 100

# Оружие | Weapon
GLOCK_MAGAZINE_SIZE = 5
FIRE_ANIM_START_FRAME = 86
FIRE_ANIM_END_FRAME = 105
RELOAD_ANIM_START_FRAME = 106

# NPC
NPC_SPEED_WALK = 3.0
NPC_IDLE_DISTANCE = 15

# Визуал | Visual
MINIMAP_SIZE = 0.3
MINIMAP_VISIBILITY = 0.85
SPECULAR_FACTOR = 0.0
```

## 🚀 Установка и запуск / Setup & Run

### Требования / Requirements
- Python 3.8+
- Ursina Engine 4.0+

### Инструкция / Instructions

```bash
# 1. Клонировать репозиторий | Clone repo
git clone ...
cd project_folder

# 2. Создать виртуальное окружение | Create venv
python -m venv venv

# 3. Активировать виртуальное окружение | Activate venv
Windows:      venv\Scripts\activate
Linux:        . venv/bin/activate

# 4. Установить зависимости | Install dependencies
pip install -r requirements.txt

# 5. Запустить программу | Launch programm
python src/main.py
```

## 📂 Структура проекта / Project Structure
```
project/
├── src/
│   ├── assets/               # Игровые ресурсы | Game assets
│   │   ├── models/           # 3D-модели (.glb) | 3D models (.glb)
│   │   ├── textures/         # Текстуры и иконки | Textures and icons
│   │   ├── audio/            # Звуковые эффекты | Sound effects
│   │   └── map.json          # Карта с нормализованными координатами объектов (-1..1) | Map with normalized object coordinates (-1..1) 
│   ├── core/                 # Ядро движка | Engine core
│   │   ├── config.py         # Все настройки в одном файле | Centralized configuration
│   │   ├── engine.py         # Инициализация сцены | Scene initialization
│   │   ├── destructibles.py  # Список разрушаемых объектов | Destructible objects list
│   │   └── comics_shader.py  # Кастомный шейдер | Custom shader
│   ├── entities/             # Игровые сущности | Game entities
│   │   ├── player.py         # Игрок с двойным прыжком | Double-jump player
│   │   ├── weapon.py         # FPS-оружие с анимациями | FPS weapon with animations
│   │   └── npc.py            # Анимированные NPC | Animated NPCs
│   ├── systems/              # Игровые системы | Game systems
│   │   ├── game_logic.py     # Границы, падение, взаимодействия | Boundaries, fall reset, interactions
│   │   ├── map_loader.py     # Загрузка карты из JSON | JSON map loader
│   │   ├── minimap.py        # Система мини-карты | Minimap system
│   │   └── outline_system.py # Чёрные контуры | Black outlines system
│   └── utils/                # Вспомогательные утилиты | Utilities
│       └── object_setup.py   # Настройка коллайдеров | Collider setup
├── tests/                    # Тесты отдельных систем | System tests
├── features/                 # Прототипы механик | Feature prototypes
├── docs/                     # Документация проекта | Project documentation
├── tools/                    # Вспомогательные утилиты для разработки | Development utilities
└── main.py                   # Точка входа | Entry point
```

---

## 📜 Лицензия / License

Этот проект распространяется под лицензией **MIT**.

📄 Полный текст лицензии: [LICENSE](LICENSE)

This project is licensed under the **MIT License**.

📄 Full license text: [LICENSE](LICENSE)

---

## 📬 Контакты / Contact


📧 **Email**: [maxim.lugovsky@gmail.com](mailto:maxim.lugovsky@gmail.com)  
💬 **Telegram**: [@mxm_lugas](https://t.me/mxm_lugas)  
📱 **WhatsApp**: [+972 55-257-5915](https://wa.me/972552575915)


