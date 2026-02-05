from ursina import *
from pathlib import Path
from src.core.config import MAP_HALF_SIZE, MINIMAP_SIZE, MINIMAP_PLAYER_MARKER_SCALE, MINIMAP_NPC_MARKER_SCALE, \
    MINIMAP_VISIBILITY, ASSETS_DIR


class Minimap:
    def __init__(self, player, world_entities, npcs, map_half_size=MAP_HALF_SIZE, minimap_size=MINIMAP_SIZE):
        """
        player: ссылка на игрока
        world_entities: список всех объектов (камни, деревья, статуи)
        npcs: список NPC
        map_half_size: половина размера игрового поля (ground.scale.x / 2)
        minimap_size: размер мини-карты на экране (в долях от высоты)
        """
        self.player = player
        self.world_entities = world_entities
        self.npcs = npcs
        self.map_half_size = map_half_size
        self.minimap_size = minimap_size

        # --- Фон мини-карты ---
        self.bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(minimap_size, minimap_size),
            position=(0,0),
            color=color.rgba(0, 0, 0, MINIMAP_VISIBILITY)
        )

        # --- Маркеры ---
        self.player_marker = None
        self.markers = []  # все маркеры кроме игрока

        # Загрузка PNG-маркера игрока (если есть)
        player_icon_path = ASSETS_DIR / 'textures' / 'player_minimap.png'
        if player_icon_path.exists():
            self.player_texture = Texture(str(player_icon_path))
        else:
            self.player_texture = None

        self._create_markers()
        self.set_visible(False)

    def _world_to_minimap(self, world_pos):
        nx = world_pos[0] / self.map_half_size
        nz = world_pos[2] / self.map_half_size
        offset = self.minimap_size / 2
        return Vec2(
            self.bg.position.x + nx * offset,
            self.bg.position.y + nz * offset
        )

    def set_visible(self, visible: bool):
        self.bg.enabled = visible
        self.player_marker.enabled = visible
        for _, marker in self.markers:
            marker.enabled = visible

    def _create_markers(self):
        # Игрок
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

        # Остальные объекты
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

            marker = Entity(
                parent=camera.ui,
                model='quad',
                color=col,
                scale=marker_scale,
                always_on_top=True
            )
            self.markers.append((ent, marker))

        # NPC
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
        # Обновление позиции игрока
        p_pos = self._world_to_minimap(self.player.position)
        self.player_marker.position = p_pos

        valid_markers = []
        for source, marker in self.markers:
            # Пропускаем удалённые Entity
            if isinstance(source, Entity) and source.is_empty():
                destroy(marker)
                continue

            try:
                if hasattr(source, 'position'):
                    pos = source.position
                elif hasattr(source, 'get_position'):  # NPC
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
        destroy(self.bg)
        destroy(self.player_marker)
        for _, m in self.markers:
            destroy(m)
