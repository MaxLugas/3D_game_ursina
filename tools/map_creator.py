"""
Простой редактор карты на Pygame с прокручиваемой информационной панелью слева
Simple Pygame map editor with scrollable info panel on the left
"""

import pygame
import json
import sys
from pathlib import Path

# Добавляем путь к проекту | Add project path to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.config import GROUND_SCALE


class SimpleMapEditor:
    def __init__(self):
        pygame.init()

        # Настройки окна | Window settings
        self.panel_width = 280
        self.map_width = 800
        self.screen_width = self.map_width + self.panel_width
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Simple Map Editor")

        # Параметры карты | Map parameters
        self.map_size = GROUND_SCALE
        self.grid_size = GROUND_SCALE  # количество клеток | number of grid cells
        self.cell_size = self.map_size / self.grid_size

        # Данные карты | Map data
        self.objects = []  # список объектов {type, x, z, y, scale} | list of objects
        self.npcs = []  # список NPC {type, x, z, y, scale} | list of NPCs
        self.current_type = 'tree'  # текущий тип объекта | current object type
        self.selected_object = None  # выделенный объект | selected object

        # Цвета для объектов | Colors for objects
        self.colors = {
            'tree': (34, 170, 34),
            'rock': (170, 85, 34),
            'cottage': (170, 68, 170),
            'statue': (170, 170, 255),
            'flashlight': (255, 255, 170),
            'target': (255, 85, 85),
            'npc': (255, 0, 0)  # красный для NPC | red for NPC
        }

        # Иконки для объектов (emoji) | Object icons
        self.icons = {
            'tree': '🌲',
            'rock': '🪨',
            'cottage': '🏠',
            'statue': '🗿',
            'flashlight': '🔦',
            'target': '🎯',
            'npc': '👤'  # человечек для NPC | person icon for NPC
        }

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

        # Прокрутка панели | Panel scrolling
        self.scroll_y = 0  # текущая позиция прокрутки | current scroll position
        self.scroll_speed = 30  # скорость прокрутки | scroll speed
        self.panel_height_total = 900  # общая высота содержимого панели | total panel content height
        self.max_scroll = 0  # максимальная прокрутка | maximum scroll

        self.running = True
        self.clock = pygame.time.Clock()

    def screen_to_world(self, screen_x, screen_y):
        """Конвертация экранных координат в мировые | Convert screen coordinates to world coordinates"""
        # Учитываем отступ для панели | Account for panel offset
        map_screen_x = screen_x - self.panel_width
        if map_screen_x < 0:
            map_screen_x = 0

        world_x = (map_screen_x / self.map_width - 0.5) * self.map_size
        world_z = (screen_y / self.screen_height - 0.5) * self.map_size

        # Привязка к сетке (если включена) | Snap to grid (if enabled)
        if self.snap_to_grid:
            grid_x = round((world_x + self.map_size / 2) / self.cell_size)
            grid_z = round((world_z + self.map_size / 2) / self.cell_size)
            world_x = grid_x * self.cell_size - self.map_size / 2
            world_z = grid_z * self.cell_size - self.map_size / 2

        return world_x, world_z

    def world_to_screen(self, world_x, world_z):
        """Конвертация мировых координат в экранные | Convert world coordinates to screen coordinates"""
        screen_x = (world_x / self.map_size + 0.5) * self.map_width + self.panel_width
        screen_y = (world_z / self.map_size + 0.5) * self.screen_height
        return int(screen_x), int(screen_y)

    def draw_grid(self):
        """Рисуем сетку | Draw grid"""
        if not self.show_grid:
            return

        cell_size_px = self.map_width / self.grid_size

        for i in range(self.grid_size + 1):
            x = i * cell_size_px + self.panel_width
            # Вертикальные линии | Vertical lines
            pygame.draw.line(self.screen, (100, 100, 100), (x, 0), (x, self.screen_height), 1)

            y = i * cell_size_px
            # Горизонтальные линии | Horizontal lines
            pygame.draw.line(self.screen, (100, 100, 100), (self.panel_width, y), (self.screen_width, y), 1)

    def draw_objects(self):
        """Рисуем все объекты и NPC | Draw all objects and NPCs"""
        # Рисуем обычные объекты | Draw regular objects
        for obj in self.objects:
            x, z = obj['x'], obj['z']
            screen_x, screen_y = self.world_to_screen(x, z)

            # Подсветка выделенного объекта | Highlight selected object
            if self.selected_object == obj:
                pygame.draw.circle(self.screen, (255, 255, 0), (screen_x, screen_y), 15, 3)

            # Маркер объекта | Object marker
            color = self.colors.get(obj['type'], (255, 255, 255))
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), 10)
            pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), 10, 1)

            # Подпись (первая буква) | Label (first letter)
            text = self.font.render(obj['type'][0].upper(), True, (255, 255, 255))
            self.screen.blit(text, (screen_x - 5, screen_y - 15))

        # Рисуем NPC | Draw NPCs
        for npc in self.npcs:
            x, z = npc['x'], npc['z']
            screen_x, screen_y = self.world_to_screen(x, z)

            # Подсветка выделенного NPC | Highlight selected NPC
            if self.selected_object == npc:
                pygame.draw.circle(self.screen, (255, 255, 0), (screen_x, screen_y), 20, 3)

            # Маркер NPC (красный квадрат) | NPC marker (red square)
            pygame.draw.rect(self.screen, (255, 0, 0), (screen_x - 12, screen_y - 12, 24, 24))
            pygame.draw.rect(self.screen, (255, 255, 255), (screen_x - 12, screen_y - 12, 24, 24), 2)

            # Иконка NPC | NPC icon
            text = self.font.render("👤", True, (255, 255, 255))
            self.screen.blit(text, (screen_x - 8, screen_y - 12))

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
        title = self.big_font.render("MAP EDITOR", True, (255, 215, 0))
        panel_surface.blit(title, (20, y_offset))
        y_offset += 40

        # Разделитель | Separator
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 20

        # Информация о карте | Map information
        info_items = [
            f"Map size: {self.map_size}x{self.map_size}",
            f"Grid: {self.grid_size}x{self.grid_size}",
            f"Cell: {self.cell_size:.1f}",
            f"Objects: {len(self.objects)}",
            f"NPCs: {len(self.npcs)}"
        ]

        for item in info_items:
            text = self.small_font.render(item, True, (200, 200, 200))
            panel_surface.blit(text, (20, y_offset))
            y_offset += 20

        y_offset += 10
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 20

        # Режим | Mode
        mode_text = self.font.render("NPC Mode: " + ("ON" if self.npc_mode else "OFF"), True,
                                     (0, 255, 0) if self.npc_mode else (255, 0, 0))
        panel_surface.blit(mode_text, (20, y_offset))
        y_offset += 30

        # Текущий объект | Current object
        if not self.npc_mode:
            current_text = self.font.render("Current object:", True, (255, 255, 255))
            panel_surface.blit(current_text, (20, y_offset))
            y_offset += 25

            color = self.colors[self.current_type]
            pygame.draw.rect(panel_surface, color, (20, y_offset, 30, 30))
            pygame.draw.rect(panel_surface, (255, 255, 255), (20, y_offset, 30, 30), 1)

            obj_text = self.font.render(f"{self.icons[self.current_type]} {self.current_type}", True, (255, 255, 255))
            panel_surface.blit(obj_text, (60, y_offset + 5))
            y_offset += 40
        else:
            current_text = self.font.render("Current: NPC", True, (255, 0, 0))
            panel_surface.blit(current_text, (20, y_offset))
            pygame.draw.rect(panel_surface, (255, 0, 0), (20, y_offset + 25, 30, 30))
            pygame.draw.rect(panel_surface, (255, 255, 255), (20, y_offset + 25, 30, 30), 2)
            npc_text = self.font.render("👤 NPC", True, (255, 255, 255))
            panel_surface.blit(npc_text, (60, y_offset + 30))
            y_offset += 60

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
        for i, (obj_type, color) in enumerate(self.colors.items()):
            if obj_type == 'npc':
                continue  # NPC показываем отдельно | NPC shown separately
            # Цветной индикатор | Color indicator
            pygame.draw.rect(panel_surface, color, (20, y_offset + i * 25, 15, 15))
            pygame.draw.rect(panel_surface, (255, 255, 255), (20, y_offset + i * 25, 15, 15), 1)

            # Название объекта | Object name
            obj_text = self.small_font.render(f"{self.icons[obj_type]} {obj_type}", True,
                                              (255, 255,
                                               255) if obj_type == self.current_type and not self.npc_mode else (150,
                                                                                                                 150,
                                                                                                                 150))
            panel_surface.blit(obj_text, (40, y_offset + i * 25))

            # Номер клавиши | Key number
            key_text = self.small_font.render(f"[{i + 1}]", True, (200, 200, 200))
            panel_surface.blit(key_text, (self.panel_width - 70, y_offset + i * 25))

        y_offset += len(self.colors) * 25 - 25

        # NPC секция | NPC section
        npc_y = y_offset
        pygame.draw.rect(panel_surface, (255, 0, 0), (20, npc_y, 15, 15))
        pygame.draw.rect(panel_surface, (255, 255, 255), (20, npc_y, 15, 15), 1)
        npc_text = self.small_font.render("👤 NPC", True, (255, 255, 255) if self.npc_mode else (150, 150, 150))
        panel_surface.blit(npc_text, (40, npc_y))
        key_text = self.small_font.render("[N]", True, (200, 200, 200))
        panel_surface.blit(key_text, (self.panel_width - 70, npc_y))

        y_offset += 40
        pygame.draw.line(panel_surface, (100, 100, 100), (10, y_offset), (self.panel_width - 30, y_offset), 1)
        y_offset += 15

        # Горячие клавиши | Hotkeys
        hotkeys_title = self.font.render("Hotkeys:", True, (255, 255, 255))
        panel_surface.blit(hotkeys_title, (20, y_offset))
        y_offset += 20

        hotkeys1 = [
            ("Left click", "Place"),
            ("Right click", "Delete"),
            ("Ctrl+Right", "Select"),
            ("N", "Toggle NPC mode"),
        ]

        for key, desc in hotkeys1:
            key_text = self.small_font.render(key, True, (255, 215, 0))
            panel_surface.blit(key_text, (30, y_offset))
            desc_text = self.small_font.render(desc, True, (200, 200, 200))
            panel_surface.blit(desc_text, (140, y_offset))
            y_offset += 15

        y_offset += 5

        hotkeys2 = [
            ("G", "Toggle grid"),
            ("X", "Snap to grid"),
            ("S", "Save"),
            ("L", "Load"),
            ("ESC", "Exit"),
            ("↑/↓", "Scroll panel")
        ]

        for key, desc in hotkeys2:
            key_text = self.small_font.render(key, True, (255, 215, 0))
            panel_surface.blit(key_text, (30, y_offset))
            desc_text = self.small_font.render(desc, True, (200, 200, 200))
            panel_surface.blit(desc_text, (100, y_offset))
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
            "objects": self.objects,
            "npcs": self.npcs  # Добавляем NPC в JSON | Add NPCs to JSON
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
            self.npcs = data.get("npcs", [])  # Загружаем NPC | Load NPCs
            self.show_message(f"✅ Loaded {len(self.objects)} objects, {len(self.npcs)} NPCs", 90)
        except FileNotFoundError:
            self.show_message("❌ File not found", 90)

    def handle_events(self):
        """Обработка событий | Handle events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.handle_scroll(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_s:
                    self.save_map()
                elif event.key == pygame.K_l:
                    self.load_map()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                    self.show_message(f"Grid: {'ON' if self.show_grid else 'OFF'}", 60)
                elif event.key == pygame.K_x:
                    self.snap_to_grid = not self.snap_to_grid
                    self.show_message(f"Snap to grid: {'ON' if self.snap_to_grid else 'OFF'}", 60)
                elif event.key == pygame.K_n:
                    self.npc_mode = not self.npc_mode
                    self.show_message(f"NPC Mode: {'ON' if self.npc_mode else 'OFF'}", 60)
                elif event.key == pygame.K_1 and not self.npc_mode:
                    self.current_type = 'tree'
                elif event.key == pygame.K_2 and not self.npc_mode:
                    self.current_type = 'rock'
                elif event.key == pygame.K_3 and not self.npc_mode:
                    self.current_type = 'cottage'
                elif event.key == pygame.K_4 and not self.npc_mode:
                    self.current_type = 'statue'
                elif event.key == pygame.K_5 and not self.npc_mode:
                    self.current_type = 'flashlight'
                elif event.key == pygame.K_6 and not self.npc_mode:
                    self.current_type = 'target'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверяем, что клик был по области карты
                # Check if click was on map area
                if event.pos[0] > self.panel_width:
                    if event.button == 1:  # Левая кнопка - разместить | Left click - place
                        if self.npc_mode:
                            # Размещаем NPC | Place NPC
                            self.npcs.append({
                                'type': 'npc',
                                'x': self.mouse_world_x,
                                'z': self.mouse_world_z,
                                'y': 0,
                                'scale': 2.0
                            })
                            self.selected_object = None
                            self.show_message("👤 NPC placed", 30)
                        else:
                            # Размещаем обычный объект | Place regular object
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
                                    'scale': 1.0
                                })
                                self.selected_object = None

                    elif event.button == 3:  # Правая кнопка - удалить/выделить | Right click - delete/select
                        # Ищем ближайший объект среди обычных объектов и NPC
                        # Find closest object among regular objects and NPCs
                        closest_obj = None
                        closest_dist = float('inf')
                        all_items = self.objects + self.npcs

                        for obj in all_items:
                            dist = ((obj['x'] - self.mouse_world_x) ** 2 +
                                    (obj['z'] - self.mouse_world_z) ** 2) ** 0.5
                            if dist < closest_dist and dist < 5.0:
                                closest_dist = dist
                                closest_obj = obj

                        if closest_obj:
                            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl + клик - выделить | Ctrl+click - select
                                self.selected_object = closest_obj
                                obj_type = closest_obj.get('type', 'npc')
                                self.show_message(f"Selected: {obj_type}", 60)
                            else:  # Просто правый клик - удалить | Just right click - delete
                                if closest_obj in self.objects:
                                    self.objects.remove(closest_obj)
                                elif closest_obj in self.npcs:
                                    self.npcs.remove(closest_obj)
                                if self.selected_object == closest_obj:
                                    self.selected_object = None
                                self.show_message(f"Deleted", 60)

    def run(self):
        """Главный цикл | Main loop"""
        while self.running:
            # Получаем позицию мыши | Get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.mouse_world_x, self.mouse_world_z = self.screen_to_world(mouse_x, mouse_y)

            # Обработка событий | Handle events
            self.handle_events()

            # Отрисовка | Drawing
            self.screen.fill((50, 50, 50))  # Темно-серый фон | Dark gray background

            # Фон карты (светлее, чтобы выделялась) | Map background (lighter to stand out)
            pygame.draw.rect(self.screen, (60, 60, 60),
                             (self.panel_width, 0, self.map_width, self.screen_height))

            self.draw_grid()
            self.draw_objects()
            self.draw_info_panel()

            # Маркер мыши (только если мышь над картой) | Mouse marker (only if mouse over map)
            if mouse_x > self.panel_width:
                screen_x, screen_y = self.world_to_screen(self.mouse_world_x, self.mouse_world_z)

                # Разный цвет маркера в зависимости от режима | Different marker color based on mode
                marker_color = (255, 0, 0) if self.npc_mode else (255, 255, 255)
                pygame.draw.circle(self.screen, marker_color, (screen_x, screen_y), 8, 2)

                # Координаты рядом с курсором | Coordinates near cursor
                coord_text = self.small_font.render(f"{self.mouse_world_x:.1f}, {self.mouse_world_z:.1f}",
                                                    True, (255, 255, 255))
                self.screen.blit(coord_text, (screen_x + 15, screen_y - 10))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    editor = SimpleMapEditor()
    editor.run()