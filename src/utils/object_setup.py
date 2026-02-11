from ursina import *


def setup_collidable_object(entity, shrink_factor=1.0, debug_color=color.rgba(255, 255, 0, 60)):

    """

    Параметры | Parameters:
        entity (Entity): сущность с моделью | entity with a model
        shrink_factor (float): уменьшение коллайдера по X/Z (1.0 = без изменений) | collider shrink on X/Z (1.0 = no shrink)
        debug_color (color): цвет отладочного куба при включённых коллайдерах | debug cube color when colliders visible

    """

    if not entity.model:
        entity.enabled = True
        return

    size = entity.bounds.size
    center = entity.bounds.center

    # Ставим объект так, чтобы его НИЗ был на y=0 | Raise object so its BOTTOM rests on ground level (y=0)
    entity.y = size.y / 2 - center.y

    # Уменьшаем коллайдер по горизонтали для более точного взаимодействия | Shrink collider horizontally for better interaction
    collider_size = Vec3(
        size.x * shrink_factor,
        size.y,
        size.z * shrink_factor
    )

    # Применяем коллайдер | Create collider
    entity.collider = BoxCollider(entity, center=center, size=collider_size)

    # Отладочный хитбокс | Visual debug hitbox
    if window.show_colliders:
        debug_box = Entity(
            model='cube',
            scale=size,
            position=entity.position + center,
            color=debug_color,
            wireframe=True,
            add_to_scene_entities=False
        )
        entity.debug_box = debug_box

    entity.enabled = True
