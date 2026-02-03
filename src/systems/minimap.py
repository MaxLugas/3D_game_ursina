from ursina import *
from pathlib import Path
from src.core.config import GROUND_SCALE, MINIMAP_SIZE, MINIMAP_PLAYER_MARKER_SCALE, MINIMAP_NPC_MARKER_SCALE


class Minimap:
    def __init__(self, player, world_entities, npcs, map_half_size=(GROUND_SCALE // 2), minimap_size=MINIMAP_SIZE):
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
        margin_x = -0.36  # отступ от левого края
        margin_y = 0.02  # отступ от нижнего края
        self.bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(minimap_size, minimap_size),
            position=(-0.5 + margin_x + minimap_size / 2, -0.5 + margin_y + minimap_size / 2),
            color=color.rgba(0, 0, 0, 180)
        )

        # --- Маркеры ---
        self.player_marker = None
        self.markers = []  # все маркеры кроме игрока

        # Загрузка PNG-маркера игрока (если есть)
        player_icon_path = Path(__file__).parent.parent / 'assets' / 'textures' / 'player_minimap.png'
        if player_icon_path.exists():
            self.player_texture = Texture(str(player_icon_path))
        else:
            self.player_texture = None

        self._create_markers()

    def _world_to_minimap(self, world_pos):
        nx = world_pos[0] / self.map_half_size  # [-1, 1]
        nz = world_pos[2] / self.map_half_size  # [-1, 1]
        offset = self.minimap_size / 2
        return Vec2(
            self.bg.position.x + nx * offset,
            self.bg.position.y + nz * offset
        )

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
                col = color.yellow
            elif 'rock' in str(ent.model):
                col = color.gray
            elif 'tree' in str(ent.model):
                col = color.green

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
