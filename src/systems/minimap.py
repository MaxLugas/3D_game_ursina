from ursina import *
from pathlib import Path
from src.core.config import MAP_HALF_SIZE, MINIMAP_SIZE, MINIMAP_PLAYER_MARKER_SCALE, MINIMAP_NPC_MARKER_SCALE, \
    MINIMAP_VISIBILITY, ASSETS_DIR


class Minimap:
    def __init__(self, player, world_entities, npcs, map_half_size=MAP_HALF_SIZE, minimap_size=MINIMAP_SIZE):
        """
        Инициализация мини-карты | Minimap initialization
        Параметры / Parameters:
            player: ссылка на игрока | reference to player entity
            world_entities: все объекты мира | all world objects
            npcs: список NPC | list of NPC
            map_half_size: половина размера игрового поля | half of game field size
            minimap_size: размер мини-карты на экране (доля от высоты) | minimap size on screen (fraction of height)
        """
        self.player = player
        self.world_entities = world_entities
        self.npcs = npcs
        self.map_half_size = map_half_size
        self.minimap_size = minimap_size

        # === Фон мини-карты | Minimap background ===
        self.bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(minimap_size, minimap_size),
            position=(0, 0),                              # Центрировано на экране | Centered on screen
            color=color.rgba(0, 0, 0, MINIMAP_VISIBILITY)
        )

        # === Маркеры | Object markers  ===
        self.player_marker = None
        self.markers = []                                 # Все маркеры кроме игрока | All markers except player

        # Загрузка иконки игрока | Load player icon
        player_icon_path = ASSETS_DIR / 'textures' / 'player_minimap.png'
        if player_icon_path.exists():
            self.player_texture = Texture(str(player_icon_path))
        else:
            self.player_texture = None

        self._create_markers()
        self.set_visible(False)                           # Скрыта по умолчанию | Hidden by default

    def _world_to_minimap(self, world_pos):
        """Преобразует мировые координаты в позицию на мини-карте. | Convert world coordinates to minimap position."""
        nx = world_pos[0] / self.map_half_size            # Нормализация по X | Normalize X
        nz = world_pos[2] / self.map_half_size            # Нормализация по Z | Normalize Z
        offset = self.minimap_size / 2
        return Vec2(
            self.bg.position.x + nx * offset,
            self.bg.position.y + nz * offset
        )

    def set_visible(self, visible: bool):
        """Переключение видимости мини-карты. | Toggle minimap visibility."""
        self.bg.enabled = visible
        self.player_marker.enabled = visible
        for _, marker in self.markers:
            marker.enabled = visible

    def _create_markers(self):
        """Создание визуальных маркеров для всех объектов. | Create visual markers for all objects."""
        # Маркер игрока | Player marker
        scale_player = MINIMAP_PLAYER_MARKER_SCALE
        if self.player_texture:
            self.player_marker = Entity(
                parent=camera.ui,
                model='quad',
                texture=self.player_texture,
                scale=scale_player,
                always_on_top=True
            )
        else:
            self.player_marker = Entity(
                parent=camera.ui,
                model='circle',
                color=color.green,
                scale=scale_player,
                always_on_top=True
            )

        # Маркеры статических объектов | Static object markers
        for ent in self.world_entities:
            if not hasattr(ent, 'bounds'):
                continue
            size_factor = max(ent.bounds.size.x, ent.bounds.size.z) / (2 * self.map_half_size)
            marker_scale = max(0.005, size_factor * 0.3)

            col = color.white
            if hasattr(ent, 'visual') or (hasattr(ent, 'model') and 'statue' in str(ent.model)):
                col = color.orange
            elif 'rock' in str(ent.model):
                col = color.gray
            elif 'tree' in str(ent.model):
                col = color.green
            elif 'cottage' in str(ent.model):
                col = color.brown
            elif 'flashlight' in str(ent.model):
                col = color.yellow
            elif 'target' in str(ent.model):
                col = color.azure

            marker = Entity(
                parent=camera.ui,
                model='quad',
                color=col,
                scale=marker_scale,
                always_on_top=True
            )
            self.markers.append((ent, marker))

        # Маркеры NPC | NPC markers
        for npc in self.npcs:
            marker = Entity(
                parent=camera.ui,
                model='circle',
                color=color.red,
                scale=MINIMAP_NPC_MARKER_SCALE,
                always_on_top=True
            )
            self.markers.append((npc, marker))

    def update(self):
        """Обновление позиций всех маркеров каждый кадр. | Update all marker positions each frame."""
        # Позиция игрока | Player position
        p_pos = self._world_to_minimap(self.player.position)
        self.player_marker.position = p_pos

        # Обновление остальных маркеров с очисткой удалённых объектов | Update other markers with cleanup
        valid_markers = []
        for source, marker in self.markers:
            # Пропуск удалённых Entity | Skip destroyed entities
            if isinstance(source, Entity) and source.is_empty():
                destroy(marker)
                continue

            try:
                # Получение позиции | Get position
                if hasattr(source, 'position'):
                    pos = source.position
                elif hasattr(source, 'get_position'):  # Для NPC | For NPC
                    pos = source.get_position()
                else:
                    destroy(marker)
                    continue
            except Exception:
                destroy(marker)
                continue

            m_pos = self._world_to_minimap(pos)
            marker.position = m_pos
            valid_markers.append((source, marker))

        self.markers = valid_markers

    def destroy(self):
        """Полное уничтожение мини-карты и всех её элементов. | Completely destroy minimap and all its elements."""
        destroy(self.bg)
        destroy(self.player_marker)
        for _, m in self.markers:
            destroy(m)
