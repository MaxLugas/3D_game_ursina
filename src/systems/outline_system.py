from ursina import *


class ComicsOutline:
    """Чёрные контуры вокруг объектов (ключевой элемент стиля Borderlands)"""

    def __init__(self, entities, thickness=0.08):
        self.outlines = []
        # Фильтруем только валидные сущности с моделью
        self.entities = [e for e in entities if hasattr(e, 'model') and e.model and e.enabled]
        self.thickness = thickness
        self._create_outlines()

    def _create_outlines(self):
        for entity in self.entities:
            # Создаём контур как копию модели с увеличенным размером
            outline = Entity(
                model=entity.model,
                scale=entity.scale * (1.0 + self.thickness),
                position=entity.position,
                rotation=entity.rotation,
                color=color.black,
                double_sided=False,  # Рендерим ТОЛЬКО задние грани
                render_queue=0,  # Рендерим ДО основных объектов
                shader=None,
                always_on_top=False,
                parent=entity  # Привязываем к родителю для синхронизации
            )
            self.outlines.append(outline)

    def update(self):
        # Позиции синхронизируются автоматически благодаря parent=entity
        pass

    def destroy(self):
        for outline in self.outlines:
            destroy(outline)
        self.outlines.clear()