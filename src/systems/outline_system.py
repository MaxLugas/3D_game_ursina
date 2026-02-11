from ursina import *


class ComicsOutline:
    """Чёрные контуры вокруг объектов | Black outlines around objects"""

    def __init__(self, entities, thickness=0.08):
        self.outlines = []

        # Фильтруем только валидные сущности с моделью и включённым состоянием | Filter only valid entities with model and enabled state
        self.entities = [e for e in entities if hasattr(e, 'model') and e.model and e.enabled]
        self.thickness = thickness
        self._create_outlines()

    def _create_outlines(self):
        for entity in self.entities:
            """Создаёт контуры через рендеринг ТОЛЬКО задних граней увеличенной копии модели. | Create outlines by rendering ONLY backfaces of an enlarged model copy."""
            outline = Entity(
                model=entity.model,
                scale=entity.scale * (1.0 + self.thickness),
                position=entity.position,
                rotation=entity.rotation,
                color=color.black,
                ouble_sided=False,              # КРИТИЧНО: рендерим только невидимые снаружи грани | CRITICAL: render only back-facing polygons
                render_queue=0,
                shader=None,
                always_on_top=False,
                parent=entity              # Привязка к родителю для автоматической синхронизации | Parenting for automatic position sync
            )
            self.outlines.append(outline)

    def update(self):
        pass

    def destroy(self):
        """Уничтожение всех контуров для очистки памяти. | Destroy all outlines for memory cleanup."""
        for outline in self.outlines:
            destroy(outline)
        self.outlines.clear()