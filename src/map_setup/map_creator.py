"""
Простой редактор карты на Pygame с прокручиваемой информационной панелью слева
Simple Pygame map editor with scrollable info panel on the left
"""

import pygame
import json
import sys
from pathlib import Path
import math
from src.core.config import GROUND_SCALE, ICONS_DIR

# Добавляем путь к проекту | Add project path to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))


class MapEditor:
    def __init__(self):
        pygame.init()

        # Настройки окна | Window settings
        self.panel_width = 280
        self.map_width = 780  # Уменьшили с 800 до 750
        self.map_offset = 20  # Добавили отступ
        self.screen_width = self.map_width + self.panel_width + self.map_offset * 2  # 750 + 280 + 80 = 1110
        self.screen_height = 600 + self.map_offset * 2  # 600 + 80 = 680
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Map Editor")

        # Параметры карты | Map parameters
        self.map_size = GROUND_SCALE
        self.grid_size = GROUND_SCALE  # количество клеток | number of grid cells
        self.cell_size = self.map_size / self.grid_size

        # Данные карты | Map data
        self.objects = []  # список объектов {type, x, z, y, scale, rot} | list of objects
        self.npcs = []  # список NPC {type, x, z, y, scale, rot} | list of NPCs

        # Стартовая позиция игрока | Player start position
        self.player_start = {
            'x': 0,
            'z': 0,
            'y': 1.0,
            'rot': 0  # начальное направление взгляда (в градусах) | initial view direction (in degrees)
        }
        self.show_player_start = True  # показывать маркер старта игрока | show player start marker

        self.current_type = 'tree'  # текущий тип объекта | current object type
        self.selected_object = None  # выделенный объект | selected object

        # === Параметры поворота | Rotation parameters ===
        self.rotation_mode = False  # режим поворота | rotation mode
        self.rotation_amount = 0  # текущий поворот для нового объекта | current rotation for new object
        self.rotation_step = 15  # шаг поворота в градусах | rotation step in degrees

        # === Для поворота с помощью мыши | For mouse rotation ===
        self.rotating_object = None  # объект, который сейчас поворачиваем | object currently being rotated
        self.rotation_start_angle = 0  # начальный угол при начале поворота | starting angle when rotation begins
        self.rotation_start_mouse = (0, 0)  # начальная позиция мыши | starting mouse position

        # Цвета для объектов | Colors for objects
        self.colors = {
            'tree': (34, 170, 34),
            'stone': (170, 85, 34),
            'cottage': (170, 68, 170),
            'statue': (170, 170, 255),
            'flashlight': (255, 255, 170),
            'target': (255, 85, 85),
            'npc': (255, 0, 0),  # красный для NPC | red for NPC
            'player_start': (0, 255, 255)  # голубой для старта игрока | cyan for player start
        }

        self.icon_images = {}
        self.icon_images_large = {}
        self.load_icon_images()

        # Шрифты | Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 32)

        # Координаты мыши в мировых координатах | Mouse world coordinates
        self.mouse_world_x = 0
        self.mouse_world_z = 0

        # Состояние интерфейса | Interface state
        self.show_grid = True  # показывать сетку | show grid
        self.snap_to_grid = False  # привязка к сетке | snap to grid
        self.message = ""  # текущее сообщение | current message
        self.message_timer = 0  # таймер сообщения | message timer
        self.npc_mode = False  # режим размещения NPC | NPC placement mode
        self.player_start_mode = False  # режим редактирования старта игрока | player start edit mode

        # Прокрутка панели | Panel scrolling
        self.scroll_y = 0  # текущая позиция прокрутки | current scroll position
        self.scroll_speed = 30  # скорость прокрутки | scroll speed
        self.panel_height_total = 1050  # общая высота содержимого панели | total panel content height
        self.max_scroll = 0  # максимальная прокрутка | maximum scroll

        self.running = True
        self.clock = pygame.time.Clock()

    def load_icon_images(self):
        icon_types = ['tree', 'stone', 'cottage', 'statue', 'flashlight',
                      'target', 'npc', 'player_start']

        print(f"Загрузка иконок из папки | Load icons from folder: {ICONS_DIR}")

        if not ICONS_DIR.exists():
            print(f"⚠️ Папка с иконками не найдена | No icons folder: {ICONS_DIR}")
            return

        loaded_count = 0
        for icon_type in icon_types:
            try:
                icon_path = ICONS_DIR / f"{icon_type}.png"
                if icon_path.exists():
                    # Загружаем иконку | Load icon
                    icon = pygame.image.load(str(icon_path)).convert_alpha()
                    # Иконки для бокового меню | Icons for menu
                    self.icon_images[icon_type] = pygame.transform.scale(icon, (18, 18))
                    # Иконки для карты | Icons for map
                    self.icon_images_large[icon_type] = pygame.transform.scale(icon, (24, 24))
                    loaded_count += 1
                    print(f"Загружена иконка | Icon loaded: {icon_type}.png")
                else:
                    print(f"Иконка не найдена | No icon: {icon_type}.png")
            except Exception as e:
                print(f"Ошибка загрузки | Load error {icon_type}.png: {e}")

        print(f"Загружено иконок | Loaded icons: {loaded_count}/{len(icon_types)}")

    def screen_to_world(self, screen_x, screen_y):
        """Конвертация экранных координат в мировые | Convert screen coordinates to world coordinates"""
        # Учитываем отступ для панели | Account for panel offset
        map_left = self.panel_width + self.map_offset
        map_right = map_left + self.map_width
        map_top = self.map_offset
        map_bottom = self.screen_height - self.map_offset

        if screen_x < map_left or screen_x > map_right or screen_y < map_top or screen_y > map_bottom:
            return self.mouse_world_x, self.mouse_world_z

        map_x = screen_x - map_left
        map_y = screen_y - map_top

        world_x = (map_x / self.map_width - 0.5) * self.map_size
        world_z = -((map_y / (self.screen_height - self.map_offset * 2) - 0.5) * self.map_size)

        if self.snap_to_grid:
            grid_x = round((world_x + self.map_size / 2) / self.cell_size)
            grid_z = round((world_z + self.map_size / 2) / self.cell_size)
            world_x = grid_x * self.cell_size - self.map_size / 2
            world_z = grid_z * self.cell_size - self.map_size / 2

        return world_x, world_z

    def world_to_screen(self, world_x, world_z):
        """Конвертация мировых координат в экранные | Convert world coordinates to screen coordinates"""
        map_left = self.panel_width + self.map_offset
        map_top = self.map_offset
        map_height = self.screen_height - self.map_offset * 2

        screen_x = (world_x / self.map_size + 0.5) * self.map_width + map_left
        screen_y = (-world_z / self.map_size + 0.5) * map_height + map_top
        return int(screen_x), int(screen_y)

    def draw_grid(self):
        """Рисуем сетку | Draw grid"""
        if not self.show_grid:
            return

        cell_size_px = self.map_width / self.grid_size

        map_left = self.panel_width + self.map_offset
        map_right = map_left + self.map_width
        map_top = self.map_offset
        map_bottom = self.screen_height - self.map_offset

        for i in range(self.grid_size + 1):
            x = i * cell_size_px + map_left
            # Вертикальные линии | Vertical lines
            if map_left <= x <= map_right:
                pygame.draw.line(self.screen, (100, 100, 100), (x, map_top), (x, map_bottom), 1)

        for i in range(self.grid_size + 1):
            y = i * cell_size_px + map_top
            # Горизонтальные линии | Horizontal lines
            if map_top <= y <= map_bottom:
                pygame.draw.line(self.screen, (100, 100, 100), (map_left, y), (map_right, y), 1)

        pygame.draw.line(self.screen, (100, 100, 100), (map_left, map_bottom), (map_right, map_bottom), 1)

    def draw_objects(self):
        """Рисуем все объекты, NPC и стартовую позицию игрока | Draw all objects, NPCs and player start position"""
        # Рисуем стартовую позицию игрока (поверх всего, но под выделением) | Draw player start position
        if self.show_player_start:
            screen_x, screen_y = self.world_to_screen(self.player_start['x'], self.player_start['z'])

            if 'player_start' in self.icon_images_large:
                icon_rect = self.icon_images_large['player_start'].get_rect(center=(screen_x, screen_y - 3))
                self.screen.blit(self.icon_images_large['player_start'], icon_rect)

            # Рисуем направление взгляда игрока | Draw player view direction
            rot = self.player_start.get('rot', 0)
            end_x = screen_x + 15 * math.cos(math.radians(rot))
            end_y = screen_y - 15 * math.sin(math.radians(rot))
            pygame.draw.line(self.screen, (255, 255, 255), (screen_x, screen_y), (end_x, end_y), 3)
            rot_text = self.small_font.render(f"{rot}°", True, (255, 255, 255))
            self.screen.blit(rot_text, (screen_x + 30, screen_y - 20))

        # Рисуем обычные объекты | Draw regular objects
        for obj in self.objects:
            x, z = obj['x'], obj['z']
            screen_x, screen_y = self.world_to_screen(x, z)

            # Подсветка выделенного объекта | Highlight selected object
            if self.selected_object == obj or self.rotating_object == obj:
                pygame.draw.circle(self.screen, (255, 255, 0), (screen_x, screen_y), 15, 3)

                if 'rot' in obj:
                    rot = obj.get('rot', 0)
                    end_x = screen_x + 20 * math.cos(math.radians(rot))
                    end_y = screen_y - 20 * math.sin(math.radians(rot))
                    pygame.draw.line(self.screen, (255, 255, 0), (screen_x, screen_y), (end_x, end_y), 3)
                    rot_text = self.small_font.render(f"{rot}°", True, (255, 255, 0))
                    self.screen.blit(rot_text, (screen_x + 25, screen_y - 15))

            # Проверяем, есть ли PNG иконка для объекта | Check PNG icon for object
            if obj['type'] in self.icon_images_large:
                self.screen.blit(self.icon_images_large[obj['type']], (screen_x - 16, screen_y - 16))

                if 'rot' in obj and obj['rot'] != 0:
                    rot = obj.get('rot', 0)
                    arrow_x = screen_x + 8 * math.cos(math.radians(rot))
                    arrow_y = screen_y - 8 * math.sin(math.radians(rot))
                    pygame.draw.line(self.screen, (255, 255, 255), (screen_x, screen_y), (arrow_x, arrow_y), 2)
            else:
                # Если нет PNG иконки, рисуем только цветной маркер | Draw marker if not icon
                color = self.colors.get(obj['type'], (255, 255, 255))
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), 10)
                pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), 10, 1)

                if 'rot' in obj and obj['rot'] != 0:
                    rot = obj.get('rot', 0)
                    arrow_x = screen_x + 8 * math.cos(math.radians(rot))
                    arrow_y = screen_y - 8 * math.sin(math.radians(rot))
                    pygame.draw.line(self.screen, (255, 255, 255), (screen_x, screen_y), (arrow_x, arrow_y), 2)

        # Рисуем NPC | Draw NPCs
        for npc in self.npcs:
            x, z = npc['x'], npc['z']
            screen_x, screen_y = self.world_to_screen(x, z)

            # Подсветка выделенного NPC | Highlight selected NPC
            if self.selected_object == npc or self.rotating_object == npc:
                pygame.draw.circle(self.screen, (255, 255, 0), (screen_x, screen_y), 20, 3)

            if 'npc' in self.icon_images_large:
                self.screen.blit(self.icon_images_large['npc'], (screen_x - 16, screen_y - 16))
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), (screen_x - 12, screen_y - 12, 24, 24))
                pygame.draw.rect(self.screen, (255, 255, 255), (screen_x - 12, screen_y - 12, 24, 24), 2)

    def draw_info_panel(self):
        """Рисуем прокручиваемую информационную панель слева | Draw scrollable info panel on the left"""
        # Фон панели | Panel background
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, self.panel_width, self.screen_height))
        pygame.draw.line(self.screen, (100, 100, 100), (self.panel_width, 0),
                         (self.panel_width, self.screen_height), 2)

        # Индикатор прокрутки | Scroll indicator
        if self.max_scroll > 0:
            scroll_indicator_height = int((self.screen_height / self.panel_height_total) * self.screen_height)
            scroll_indicator_y = int((self.scroll_y / self.max_scroll) * (self.screen_height - scroll_indicator_height))
            pygame.draw.rect(self.screen, (100, 100, 100),
                             (self.panel_width - 10, scroll_indicator_y, 5, scroll_indicator_height))

        # Создаем поверхность для панели | Create panel surface
        panel_surface = pygame.Surface((self.panel_width - 20, self.panel_height_total))
        panel_surface.fill((40, 40, 40))

        y_offset = 20

        # Заголовок | Title
        title = self.big_font.render("INFO", True, (255, 215, 0))
        panel_surface.blit(title, (20, y_offset))
        y_offset += 40

        # Разделитель | Separator
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 20

        # Информация о карте | Map information
        info_items = [
            f"Map size: {self.map_size}x{self.map_size}",
            f"Cell: {self.cell_size:.1f}",
            f"Objects: {len(self.objects)}",
            f"NPCs: {len(self.npcs)}",
            f"Player start: ({self.player_start['x']:.1f}, {self.player_start['z']:.1f})",
            f"Player rot: {self.player_start.get('rot', 0)}°"
        ]

        for item in info_items:
            text = self.small_font.render(item, True, (200, 200, 200))
            panel_surface.blit(text, (20, y_offset))
            y_offset += 20

        y_offset += 10
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 20

        # Секция поворота | Rotation section
        if (self.selected_object or self.rotating_object) and not self.player_start_mode:
            current_obj = self.rotating_object if self.rotating_object else self.selected_object
            rot_text = self.font.render("Rotation:", True, (255, 255, 255))
            panel_surface.blit(rot_text, (20, y_offset))
            y_offset += 25

            current_rot = current_obj.get('rot', 0)
            rot_value = self.small_font.render(f"Current: {current_rot}°", True, (200, 200, 200))
            panel_surface.blit(rot_value, (30, y_offset))
            y_offset += 20

            pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
            y_offset += 15

        # Режимы редактирования | Edit modes
        mode_text = self.font.render("Edit Modes:", True, (255, 255, 255))
        panel_surface.blit(mode_text, (20, y_offset))
        y_offset += 25

        # Кнопка для стартовой позиции игрока | Player start button
        pygame.draw.rect(panel_surface, (40, 40, 40), (20, y_offset, 30, 30))
        pygame.draw.rect(panel_surface, (60, 60, 60), (20, y_offset, 30, 30), 1)

        if 'player_start' in self.icon_images:
            icon_rect = self.icon_images['player_start'].get_rect(center=(35, y_offset + 15))
            panel_surface.blit(self.icon_images['player_start'], icon_rect)

        start_text = self.small_font.render("Start", True, (255, 255, 255))
        panel_surface.blit(start_text, (60, y_offset + 5))
        key_text = self.small_font.render("[P]", True, (255, 215, 0))
        panel_surface.blit(key_text, (self.panel_width - 70, y_offset + 5))
        y_offset += 40

        # Режим NPC | NPC mode
        pygame.draw.rect(panel_surface, (40, 40, 40), (20, y_offset, 30, 30))
        pygame.draw.rect(panel_surface, (60, 60, 60), (20, y_offset, 30, 30), 1)

        if 'npc' in self.icon_images:
            icon_rect = self.icon_images['npc'].get_rect(center=(35, y_offset + 15))
            panel_surface.blit(self.icon_images['npc'], icon_rect)

        npc_text = self.small_font.render("NPC", True, (255, 255, 255))
        panel_surface.blit(npc_text, (60, y_offset + 5))
        key_text = self.small_font.render("[N]", True, (255, 215, 0))
        panel_surface.blit(key_text, (self.panel_width - 70, y_offset + 5))
        y_offset += 40

        # Текущий объект | Current object
        current_text = self.font.render("Current object:", True, (255, 255, 255))
        panel_surface.blit(current_text, (20, y_offset))
        y_offset += 25

        if self.player_start_mode:
            display_type = 'player_start'
            display_name = "Player Start"
            display_icon = self.icon_images.get('player_start')
        elif self.npc_mode:
            display_type = 'npc'
            display_name = "NPC"
            display_icon = self.icon_images.get('npc')
        else:
            display_type = self.current_type
            display_name = self.current_type.capitalize()
            display_icon = self.icon_images.get(self.current_type)

        pygame.draw.rect(panel_surface, (40, 40, 40), (20, y_offset, 30, 30))
        pygame.draw.rect(panel_surface, (100, 100, 100), (20, y_offset, 30, 30), 1)

        if display_icon:
            icon_rect = display_icon.get_rect(center=(35, y_offset + 15))
            panel_surface.blit(display_icon, icon_rect)

        obj_text = self.font.render(display_name, True, (255, 255, 255))
        panel_surface.blit(obj_text, (60, y_offset + 5))
        y_offset += 40

        # Координаты мыши | Mouse coordinates
        mouse_text = self.font.render("Mouse position:", True, (255, 255, 255))
        panel_surface.blit(mouse_text, (20, y_offset))
        y_offset += 20

        coord_text = self.small_font.render(f"X: {self.mouse_world_x:.1f}", True, (200, 200, 200))
        panel_surface.blit(coord_text, (30, y_offset))
        y_offset += 15

        coord_text = self.small_font.render(f"Z: {self.mouse_world_z:.1f}", True, (200, 200, 200))
        panel_surface.blit(coord_text, (30, y_offset))
        y_offset += 25

        # Настройки | Settings
        settings_title = self.font.render("Settings:", True, (255, 255, 255))
        panel_surface.blit(settings_title, (20, y_offset))
        y_offset += 20

        grid_text = self.small_font.render(f"Grid: {'ON' if self.show_grid else 'OFF'}", True,
                                           (0, 255, 0) if self.show_grid else (255, 0, 0))
        panel_surface.blit(grid_text, (30, y_offset))
        y_offset += 15

        snap_text = self.small_font.render(f"Snap to grid: {'ON' if self.snap_to_grid else 'OFF'}", True,
                                           (0, 255, 0) if self.snap_to_grid else (255, 0, 0))
        panel_surface.blit(snap_text, (30, y_offset))
        y_offset += 25

        # Разделитель | Separator
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 15

        # Выбор объектов | Object selection
        objects_title = self.font.render("Object types:", True, (255, 255, 255))
        panel_surface.blit(objects_title, (20, y_offset))
        y_offset += 25

        # Список объектов | Object list
        obj_list = [(k, v) for k, v in self.colors.items() if k not in ['npc', 'player_start']]
        for i, (obj_type, color) in enumerate(obj_list):
            if obj_type in self.icon_images:
                icon_rect = self.icon_images[obj_type].get_rect(topleft=(20, y_offset + i * 25))
                panel_surface.blit(self.icon_images[obj_type], icon_rect)

            # Название объекта | Object name
            is_selected = obj_type == self.current_type and not self.npc_mode and not self.player_start_mode
            obj_text = self.small_font.render(obj_type, True,
                                              (255, 255, 255) if is_selected else (150, 150, 150))
            panel_surface.blit(obj_text, (45, y_offset + i * 25))

            # Номер клавиши | Key number
            key_text = self.small_font.render(f"[{i + 1}]", True, (200, 200, 200))
            panel_surface.blit(key_text, (self.panel_width - 70, y_offset + i * 25))

        y_offset += len(obj_list) * 25 + 15
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 15

        # Горячие клавиши | Hotkeys
        hotkeys_title = self.font.render("Hotkeys:", True, (255, 255, 255))
        panel_surface.blit(hotkeys_title, (20, y_offset))
        y_offset += 20


        hotkeys = [
            ("Left click", "Place"),
            ("Right click", "Delete"),
            ("Ctrl+LMB drag", "Rotate object"),
            ("G", "Toggle grid"),
            ("X", "Snap to grid"),
            ("S", "Save"),
            ("L", "Load"),
            ("ESC", "Exit"),
        ]

        for key, desc in hotkeys:
            key_text = self.small_font.render(key, True, (255, 215, 0))
            panel_surface.blit(key_text, (30, y_offset))
            desc_text = self.small_font.render(desc, True, (200, 200, 200))
            panel_surface.blit(desc_text, (140, y_offset))
            y_offset += 15

        # Обновляем общую высоту панели | Update total panel height
        self.panel_height_total = y_offset + 50
        self.max_scroll = max(0, self.panel_height_total - self.screen_height)

        # Накладываем panel_surface на экран с учетом прокрутки | Blit panel surface with scroll offset
        self.screen.blit(panel_surface, (10, 10 - self.scroll_y))

        # Сообщение | Message
        if self.message and self.message_timer > 0:
            msg_text = self.font.render(self.message, True, (255, 255, 0))
            msg_rect = msg_text.get_rect(center=(self.panel_width // 2, self.screen_height - 30))
            self.screen.blit(msg_text, msg_rect)
            self.message_timer -= 1

    def handle_scroll(self, event):
        """Обработка прокрутки панели | Handle panel scrolling"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)

    def show_message(self, text, duration=60):
        """Показать сообщение | Show message"""
        self.message = text
        self.message_timer = duration

    def save_map(self):
        """Сохранить карту в JSON | Save map to JSON"""
        data = {
            "metadata": {
                "size": self.map_size,
                "grid_size": self.grid_size,
                "objects_count": len(self.objects),
                "npcs_count": len(self.npcs)
            },
            "player_start": self.player_start,
            "objects": self.objects,
            "npcs": self.npcs
        }

        filename = "../src/assets/map.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.show_message(f"✅ Saved {len(self.objects)} objects, {len(self.npcs)} NPCs", 90)

    def load_map(self):
        """Загрузить карту из JSON | Load map from JSON"""
        filename = "../src/assets/map.json"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.objects = data.get("objects", [])
            self.npcs = data.get("npcs", [])
            self.player_start = data.get("player_start", {'x': 0, 'z': 0, 'y': 1.0, 'rot': 0})
            self.show_message(f"✅ Loaded {len(self.objects)} objects, {len(self.npcs)} NPCs", 90)
        except FileNotFoundError:
            self.show_message("❌ File not found", 90)

    def get_angle_between_points(self, p1, p2):
        """Вычисляет угол между двумя точками в градусах | Calculate angle between two points in degrees"""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.degrees(math.atan2(-dy, dx)) % 360

    def handle_events(self):
        """Обработка событий | Handle events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.handle_scroll(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.scancode == 22:
                    self.save_map()
                elif event.scancode == 15:
                    self.load_map()
                elif event.scancode == 10:
                    self.show_grid = not self.show_grid
                    self.show_message(f"Grid: {'ON' if self.show_grid else 'OFF'}", 60)
                elif event.scancode == 27:
                    self.snap_to_grid = not self.snap_to_grid
                    self.show_message(f"Snap to grid: {'ON' if self.snap_to_grid else 'OFF'}", 60)
                elif event.scancode == 19:
                    self.player_start_mode = not self.player_start_mode
                    self.npc_mode = False
                    self.rotation_mode = False
                    self.selected_object = None
                    self.rotating_object = None
                    self.show_message(f"Player start mode: {'ON' if self.player_start_mode else 'OFF'}", 60)
                elif event.scancode == 17:
                    self.npc_mode = not self.npc_mode
                    self.player_start_mode = False
                    self.rotation_mode = False
                    self.selected_object = None
                    self.rotating_object = None
                    self.show_message(f"NPC Mode: {'ON' if self.npc_mode else 'OFF'}", 60)
                elif event.key == pygame.K_1:
                    if not self.npc_mode and not self.player_start_mode:
                        self.current_type = 'tree'
                        self.show_message(f"Selected: tree", 30)
                elif event.key == pygame.K_2:
                    if not self.npc_mode and not self.player_start_mode:
                        self.current_type = 'stone'
                        self.show_message(f"Selected: stone", 30)
                elif event.key == pygame.K_3:
                    if not self.npc_mode and not self.player_start_mode:
                        self.current_type = 'cottage'
                        self.show_message(f"Selected: cottage", 30)
                elif event.key == pygame.K_4:
                    if not self.npc_mode and not self.player_start_mode:
                        self.current_type = 'statue'
                        self.show_message(f"Selected: statue", 30)
                elif event.key == pygame.K_5:
                    if not self.npc_mode and not self.player_start_mode:
                        self.current_type = 'flashlight'
                        self.show_message(f"Selected: flashlight", 30)
                elif event.key == pygame.K_6:
                    if not self.npc_mode and not self.player_start_mode:
                        self.current_type = 'target'
                        self.show_message(f"Selected: target", 30)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] < self.panel_width:
                    pass
                elif event.pos[0] > self.panel_width:
                    if event.button == 1:
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            closest_obj = None
                            closest_dist = float('inf')
                            all_items = self.objects + self.npcs

                            for obj in all_items:
                                dist = ((obj['x'] - self.mouse_world_x) ** 2 +
                                        (obj['z'] - self.mouse_world_z) ** 2) ** 0.5
                                if dist < closest_dist and dist < 3.0:
                                    closest_dist = dist
                                    closest_obj = obj

                            if self.show_player_start:
                                dist_to_player = ((self.player_start['x'] - self.mouse_world_x) ** 2 +
                                                  (self.player_start['z'] - self.mouse_world_z) ** 2) ** 0.5
                                if dist_to_player < 3.0 and dist_to_player < closest_dist:
                                    closest_dist = dist_to_player
                                    closest_obj = self.player_start

                            if closest_obj:
                                self.rotating_object = closest_obj
                                self.selected_object = closest_obj if closest_obj != self.player_start else None
                                screen_x, screen_y = self.world_to_screen(closest_obj['x'], closest_obj['z'])
                                self.rotation_start_mouse = (event.pos[0], event.pos[1])
                                self.rotation_start_angle = self.get_angle_between_points(
                                    (screen_x, screen_y),
                                    self.rotation_start_mouse
                                )
                                obj_type = "player start" if closest_obj == self.player_start else closest_obj.get(
                                    'type', 'object')
                                self.show_message(f"Rotating {obj_type}", 30)
                        else:
                            if self.player_start_mode:
                                self.player_start['x'] = self.mouse_world_x
                                self.player_start['z'] = self.mouse_world_z
                                self.selected_object = None
                                self.rotating_object = None
                            elif self.npc_mode:
                                self.npcs.append({
                                    'type': 'npc',
                                    'x': self.mouse_world_x,
                                    'z': self.mouse_world_z,
                                    'y': 0,
                                    'scale': 2.0,
                                    'rot': 0
                                })
                                self.selected_object = None
                                self.rotating_object = None
                            else:
                                occupied = False
                                for obj in self.objects:
                                    dist = ((obj['x'] - self.mouse_world_x) ** 2 +
                                            (obj['z'] - self.mouse_world_z) ** 2) ** 0.5
                                    if dist < 2.0:
                                        occupied = True
                                        break

                                if not occupied:
                                    self.objects.append({
                                        'type': self.current_type,
                                        'x': self.mouse_world_x,
                                        'z': self.mouse_world_z,
                                        'y': 1.0,
                                        'scale': 1.0,
                                        'rot': 0
                                    })
                                    self.selected_object = None
                                    self.rotating_object = None

                    elif event.button == 3:
                        closest_obj = None
                        closest_dist = float('inf')
                        all_items = self.objects + self.npcs
                        if self.show_player_start:
                            all_items_with_start = all_items + [self.player_start]
                        else:
                            all_items_with_start = all_items
                        for obj in all_items_with_start:
                            dist = ((obj['x'] - self.mouse_world_x) ** 2 +
                                    (obj['z'] - self.mouse_world_z) ** 2) ** 0.5
                            if dist < closest_dist and dist < 5.0:
                                closest_dist = dist
                                closest_obj = obj
                        if closest_obj:
                            if closest_obj == self.player_start:
                                self.player_start['x'] = 0
                                self.player_start['z'] = 0
                                self.player_start['rot'] = 0
                                self.show_message(f"Player start reset to center", 60)
                            elif closest_obj in self.objects:
                                self.objects.remove(closest_obj)
                                if self.selected_object == closest_obj:
                                    self.selected_object = None
                                self.show_message(f"Deleted", 60)
                            elif closest_obj in self.npcs:
                                self.npcs.remove(closest_obj)
                                if self.selected_object == closest_obj:
                                    self.selected_object = None
                                self.show_message(f"Deleted", 60)
                            if self.rotating_object == closest_obj:
                                self.rotating_object = None

                            else:
                                if closest_obj == self.player_start:
                                    self.player_start['x'] = 0
                                    self.player_start['z'] = 0
                                    self.player_start['rot'] = 0
                                    self.show_message(f"Player start reset to center", 60)
                                elif closest_obj in self.objects:
                                    self.objects.remove(closest_obj)
                                    if self.selected_object == closest_obj:
                                        self.selected_object = None
                                    self.show_message(f"Deleted", 60)
                                elif closest_obj in self.npcs:
                                    self.npcs.remove(closest_obj)
                                    if self.selected_object == closest_obj:
                                        self.selected_object = None
                                    self.show_message(f"Deleted", 60)

                                if self.rotating_object == closest_obj:
                                    self.rotating_object = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.rotating_object:
                    self.rotating_object = None
                    self.show_message("Rotation finished", 30)

            elif event.type == pygame.MOUSEMOTION:
                if self.rotating_object and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    screen_x, screen_y = self.world_to_screen(
                        self.rotating_object['x'],
                        self.rotating_object['z']
                    )
                    current_mouse = (event.pos[0], event.pos[1])
                    current_angle = self.get_angle_between_points(
                        (screen_x, screen_y),
                        current_mouse
                    )

                    angle_diff = current_angle - self.rotation_start_angle
                    self.rotation_start_angle = current_angle

                    if self.rotating_object == self.player_start:
                        self.player_start['rot'] = int((self.player_start.get('rot', 0) + angle_diff) % 360)
                    else:
                        current_rot = self.rotating_object.get('rot', 0)
                        self.rotating_object['rot'] = int((current_rot + angle_diff) % 360)

    def run(self):
        """Главный цикл | Main loop"""
        while self.running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.mouse_world_x, self.mouse_world_z = self.screen_to_world(mouse_x, mouse_y)

            self.handle_events()

            self.screen.fill((50, 50, 50))

            map_left = self.panel_width + self.map_offset
            map_top = self.map_offset
            map_height = self.screen_height - self.map_offset * 2
            pygame.draw.rect(self.screen, (60, 60, 60),
                             (map_left, map_top, self.map_width, map_height))

            self.draw_grid()
            self.draw_objects()
            self.draw_info_panel()

            map_left = self.panel_width + self.map_offset
            map_right = map_left + self.map_width
            map_top = self.map_offset
            map_bottom = self.screen_height - self.map_offset

            if mouse_x > map_left and mouse_x < map_right and mouse_y > map_top and mouse_y < map_bottom:
                screen_x, screen_y = self.world_to_screen(self.mouse_world_x, self.mouse_world_z)

                if self.player_start_mode:
                    marker_color = (0, 255, 255)
                elif self.npc_mode:
                    marker_color = (255, 0, 0)
                elif self.rotating_object:
                    marker_color = (255, 255, 0)
                elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                    marker_color = (255, 255, 0)
                else:
                    marker_color = (255, 255, 255)

                pygame.draw.circle(self.screen, marker_color, (screen_x, screen_y), 8, 2)

                coord_text = self.small_font.render(f"{self.mouse_world_x:.1f}, {self.mouse_world_z:.1f}",
                                                    True, (255, 255, 255))
                text_width = coord_text.get_width()

                if screen_x + 15 + text_width > map_right:
                    text_x = screen_x - 15 - text_width
                else:
                    text_x = screen_x + 15

                if text_x < map_left:
                    text_x = map_left + 5

                self.screen.blit(coord_text, (text_x, screen_y - 10))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    editor =MapEditor()
    editor.run()