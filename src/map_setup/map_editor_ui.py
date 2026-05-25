from ursina import *
from src.map_setup import map_editor_state as S

info_panel = """
=== MAP EDITOR ===

[OBJECTS]                           [CONTROLS]
1: Stone    2: Target    3: Tree    LMB: Place    RMB: Delete
4: Cottage  5: Lamp      6: Statue  R: Rotate     G: Ghost mode
N: NPC      P: Spawn                X: Snap       H: Grid
                                    Ctrl+S: Save  Ctrl+L: Load
                                    ESC: Exit

[CURRENT]
Type: {current}
Ghost: {ghost}
Snap: {snap}
Grid: {grid}
Height: {height}
Objects: {obj_count}
NPCs: {npc_count}
Spawn: {spawn_status}
"""


def update_ui_text():
    ghost_status = "ON" if S.ghost_enabled else "OFF"
    spawn_status = "YES" if S.player_spawn_data else "NO"
    snap_status = "ON" if S.snap_to_grid else "OFF"
    grid_status = "ON" if S.show_grid else "OFF"

    S.ui_text.text = info_panel.format(
        current=S.current_type[0].upper(),
        ghost=ghost_status,
        snap=snap_status,
        grid=grid_status,
        height=f"{S.height_offset:.1f}",
        obj_count=len(S.placed_objects),
        npc_count=len(S.placed_npcs),
        spawn_status=spawn_status
    )
