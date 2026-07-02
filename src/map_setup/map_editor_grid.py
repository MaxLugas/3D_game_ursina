from ursina import *
from src.map_setup import map_editor_state as S
from src.core.config import GROUND_SCALE


def create_grid_visual():
    for e in S.grid_entities:
        destroy(e)
    S.grid_entities.clear()

    half = GROUND_SCALE // 2
    step = S.cell_size
    grid_color = color.rgba(100, 100, 100, 60)
    num_lines = int(GROUND_SCALE // 2 / step)

    for idx in range(-num_lines, num_lines + 1):
        i = idx * step
        line_x = Entity(
            model='cube',
            scale=(GROUND_SCALE, 0.002, 0.002),
            position=(0, 0.005, i),
            color=grid_color,
            unlit=True,
            collider=None,
            enabled=S.show_grid
        )
        S.grid_entities.append(line_x)

        line_z = Entity(
            model='cube',
            scale=(0.002, 0.002, GROUND_SCALE),
            position=(i, 0.005, 0),
            color=grid_color,
            unlit=True,
            collider=None,
            enabled=S.show_grid
        )
        S.grid_entities.append(line_z)
