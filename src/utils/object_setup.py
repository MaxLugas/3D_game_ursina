from ursina import *


def setup_collidable_object(entity, shrink_factor=1.0, debug_color=color.rgba(255, 255, 0, 60)):
    """
    Настраивает позицию, коллайдер и (опционально) отладочный хитбокс для любого объекта.

    Параметры:
        entity (Entity): сущность, для которой настраивается коллайдер.
        shrink_factor (float): на сколько уменьшить коллайдер по X и Z (1.0 = без уменьшения).
        debug_color (color): цвет отладочного куба (только если window.show_colliders = True).
    """
    if not entity.model:
        entity.enabled = True
        return

    size = entity.bounds.size
    center = entity.bounds.center

    # Ставим объект так, чтобы его НИЗ был на y=0
    entity.y = size.y / 2 - center.y

    # Уменьшаем коллайдер по горизонтали (X и Z), если нужно
    collider_size = Vec3(
        size.x * shrink_factor,
        size.y,
        size.z * shrink_factor
    )

    # Применяем коллайдер
    entity.collider = BoxCollider(entity, center=center, size=collider_size)

    # Отладочный хитбокс (визуальный, не физический)
    if window.show_colliders:
        debug_box = Entity(
            model='cube',
            scale=size,  # полный визуальный размер
            position=entity.position + center,
            color=debug_color,
            wireframe=True,
            add_to_scene_entities=False
        )
        entity.debug_box = debug_box

    entity.enabled = True
