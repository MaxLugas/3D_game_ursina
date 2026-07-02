from ursina import *
from src.core.config import MAP_HALF_SIZE, MINIMAP_SIZE, MINIMAP_PLAYER_MARKER_SCALE, MINIMAP_VISIBILITY, ICONS_DIR, RENDER_DISTANCE


class Minimap:
    def __init__(self, player, world_entities, npcs, map_half_size=MAP_HALF_SIZE, minimap_size=MINIMAP_SIZE):
        self.player = player
        self.world_entities = world_entities
        self.npcs = npcs
        self.map_half_size = map_half_size
        self.minimap_size = minimap_size

        self.bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(minimap_size, minimap_size),
            position=(0, 0),
            color=color.rgba(0, 0, 0, MINIMAP_VISIBILITY)
        )

        self.player_marker = None
        self.markers = []

        self.icon_textures = {}
        self._load_icons()

        self._create_markers()
        self.set_visible(False)

    def _load_icons(self):
        icon_types = ['tree', 'stone', 'cottage', 'statue', 'flashlight',
                      'target', 'fence', 'npc', 'player_start']
        for name in icon_types:
            path = ICONS_DIR / f'{name}.png'
            if path.exists():
                self.icon_textures[name] = Texture(str(path))

    def _world_to_minimap(self, world_pos):
        """Преобразует мировые координаты в позицию на мини-карте. | Convert world coordinates to minimap position."""
        nx = world_pos[0] / self.map_half_size  # Нормализация по X | Normalize X
        nz = world_pos[2] / self.map_half_size  # Нормализация по Z | Normalize Z
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

    def _get_object_type(self, ent):
        obj_type = getattr(ent, 'obj_type', None)
        if obj_type in ('tree', 'stone', 'cottage', 'statue', 'flashlight', 'target', 'fence'):
            return obj_type
        return None

    def _make_marker_for_entity(self, ent):
        if getattr(ent, 'is_ground_tile', False):
            return None
        if not hasattr(ent, 'bounds'):
            return None
        obj_type = self._get_object_type(ent)
        icon = self.icon_textures.get(obj_type) if obj_type else None
        marker = Entity(
            parent=camera.ui, model='quad', scale=0.02,
            always_on_top=True
        )
        if icon:
            marker.texture = icon
        else:
            marker.color = color.white
        return marker

    def _make_marker_for_npc(self, npc):
        npc_icon = self.icon_textures.get('npc')
        marker = Entity(
            parent=camera.ui, model='quad', scale=0.025,
            always_on_top=True
        )
        if npc_icon:
            marker.texture = npc_icon
        else:
            marker.color = color.red
        return marker

    def _create_markers(self):
        scale_player = MINIMAP_PLAYER_MARKER_SCALE
        player_icon = self.icon_textures.get('player_start')
        if player_icon:
            self.player_marker = Entity(
                parent=camera.ui, model='quad', texture=player_icon,
                scale=scale_player, always_on_top=True
            )
        else:
            self.player_marker = Entity(
                parent=camera.ui, model='circle',
                color=color.green, scale=scale_player, always_on_top=True
            )

        for ent in self.world_entities:
            marker = self._make_marker_for_entity(ent)
            if marker:
                self.markers.append((ent, marker))

        for npc in self.npcs:
            marker = self._make_marker_for_npc(npc)
            if marker:
                self.markers.append((npc, marker))

    def _sync_markers(self):
        """Добавляет маркеры для новых объектов (из загруженных чанков). | Add markers for new entities (from loaded chunks)."""
        marked_ids = {id(s) for s, _ in self.markers}

        for ent in self.world_entities:
            if id(ent) in marked_ids:
                continue
            marker = self._make_marker_for_entity(ent)
            if marker:
                self.markers.append((ent, marker))
                marked_ids.add(id(ent))

        for npc in self.npcs:
            if id(npc) in marked_ids:
                continue
            marker = self._make_marker_for_npc(npc)
            if marker:
                self.markers.append((npc, marker))

    def update(self):
        """Обновление позиций всех маркеров каждый кадр. | Update all marker positions each frame."""
        # Позиция и поворот игрока | Player position and rotation
        p_pos = self._world_to_minimap(self.player.position)
        self.player_marker.position = p_pos
        self.player_marker.rotation = (0, 0, self.player.rotation_y)

        # Добавление маркеров для новых объектов из подгруженных чанков | Add markers for new chunk entities
        self._sync_markers()

        # Обновление остальных маркеров с очисткой удалённых объектов | Update other markers with cleanup
        valid_markers = []
        for source, marker in self.markers:
            # Пропуск удалённых Entity | Skip destroyed entities
            if isinstance(source, Entity) and source.is_empty():
                destroy(marker)
                continue
            # Пропуск уничтоженных NPC | Skip destroyed NPCs
            if hasattr(source, '_destroyed') and source._destroyed:
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

            # Скрыть маркеры за дистанцией рендеринга | Hide markers beyond render distance
            dist = distance(self.player.position, pos)
            marker.enabled = dist <= RENDER_DISTANCE
            valid_markers.append((source, marker))

        self.markers = valid_markers

    def destroy(self):
        """Полное уничтожение мини-карты и всех её элементов. | Completely destroy minimap and all its elements."""
        destroy(self.bg)
        destroy(self.player_marker)
        for _, m in self.markers:
            destroy(m)
