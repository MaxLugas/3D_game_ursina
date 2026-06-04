from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath

model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="Animation Inspector", borderless=False, vsync=False)

actor = Actor('UAL1_Standard.glb')
actor.reparent_to(scene)
actor.set_scale(1.6)
actor.set_light_off()
# actor.set_color_off()

avail = list(actor.get_anim_names())
# print(f"Available animations: {avail}")
anim_index = 0
anim_name = avail[anim_index] if avail else None
current_frame = 0
total_frames = None
mode = 'duration'
control = None


column_left = Text(
    text="",
    position=(-0.85, 0.45),
    origin=(-0.5, 0.5),
    scale=0.7,
    color=color.white,
    background_color=color.rgba(0, 0, 0, 0.7),
    line_height=1.2,
    font='VeraMono.ttf',
)

column_right = Text(
    text="",
    position=(0.75, 0.45),
    origin=(0.5, 0.5),
    scale=0.55,
    color=color.white,
    background_color=color.rgba(0, 0, 0, 0.7),
    line_height=1.2,
    font='VeraMono.ttf',
)

left_template = """
[CONTROLS]
Right: Next amin        Left: Previous anim
Up: Next frame          Down: Prev frame
1: Animated             2: By frame


[CURRENT]
Animation: {anim_name}
Frames: {frames}
FPS: {fps}
Duration: {duration}
Frame: {current_frame}"""

right_template = """[ANIMATIONS]
{anim_list}"""

def update_panel():
    if not anim_name:
        return
    info = get_anim_info(actor, anim_name)
    anim_lines = []
    for i, name in enumerate(avail):
        prefix = '> ' if name == anim_name else '  '
        anim_lines.append(f'{prefix}{name}')
    anim_list_str = '\n'.join(anim_lines)
    column_left.text = left_template.format(
        anim_name=anim_name,
        frames=info['frames'] if info and info['frames'] is not None else 'N/A',
        fps=f'{info["fps"]:.2f}' if info and info['fps'] is not None else 'N/A',
        duration=f'{info["duration"]:.3f}s' if info and info['duration'] is not None else 'N/A',
        current_frame=f'{current_frame} / {total_frames}' if mode == 'frame' else '-',
    )
    column_right.text = right_template.format(
        anim_list=anim_list_str,
    )

def get_anim_info(actor, anim_name):
    ctrl = actor.get_anim_control(anim_name)
    if not ctrl:
        return None
    anim = ctrl.get_anim()
    if not anim:
        return None
    info = {'frames': None, 'fps': None, 'duration': None}
    if hasattr(anim, 'get_num_frames'):
        try:
            info['frames'] = anim.get_num_frames()
        except:
            pass
    if hasattr(ctrl, 'get_frame_rate'):
        try:
            info['fps'] = ctrl.get_frame_rate()
        except:
            pass
    if hasattr(anim, 'get_duration'):
        try:
            info['duration'] = anim.get_duration()
        except:
            pass
    if info['duration'] is None and info['frames'] is not None and info['fps'] is not None and info['fps'] > 0:
        info['duration'] = info['frames'] / info['fps']
    return info

def start_duration():
    global mode, control, current_frame
    mode = 'duration'
    actor.stop()
    if anim_name in actor.get_anim_names():
        actor.loop(anim_name)
        control = None
        info = get_anim_info(actor, anim_name)
        # if info:
        #     print(f"\nMode: duration — Animation '{anim_name}':")
        #     if info['frames'] is not None:
        #         print(f"  Frames: {info['frames']}")
        #     else:
        #         print("  Frames: N/A")
        #     if info['fps'] is not None:
        #         print(f"  FPS: {info['fps']:.2f}")
        #     else:
        #         print("  FPS: N/A")
        #     if info['duration'] is not None:
        #         print(f"  Duration: {info['duration']:.3f}s")
        #     else:
        #         print("  Duration: N/A")
        # else:
        #     print("Could not get anim info")
    # else:
    #     print(f"Animation '{anim_name}' not found")

def start_frame():
    global mode, control, current_frame, total_frames
    mode = 'frame'
    current_frame = 0
    actor.stop()
    if anim_name in actor.get_anim_names():
        control = actor.get_anim_control(anim_name)
        if control and control.get_anim() and hasattr(control.get_anim(), 'get_num_frames'):
            total_frames = control.get_anim().get_num_frames()
            # print(f"\nMode: frame — Animation '{anim_name}'. Total frames: {total_frames}")
            control.pose(float(current_frame))
            # print(f"Frame: {current_frame}")
        # else:
            # print("Could not determine frame count")
    # else:
        # print(f"Animation '{anim_name}' not found")

start_duration()
update_panel()

def switch_anim(delta):
    global anim_index, anim_name, current_frame
    if not avail:
        return
    anim_index = (anim_index + delta) % len(avail)
    anim_name = avail[anim_index]
    current_frame = 0
    if mode == 'duration':
        start_duration()
    else:
        start_frame()
    update_panel()

def input(key):
    global current_frame, total_frames, control, mode, anim_index, anim_name
    if key == '1':
        start_duration()
        update_panel()
    elif key == '2':
        start_frame()
        update_panel()
    elif key == 'left arrow':
        switch_anim(-1)
    elif key == 'right arrow':
        switch_anim(1)
    elif key == 'up arrow' and mode == 'frame' and control is not None and total_frames is not None:
        current_frame += 1
        if current_frame >= total_frames:
            current_frame = 0
        control.pose(float(current_frame))
        update_panel()
    elif key == 'down arrow' and mode == 'frame' and control is not None and total_frames is not None:
        current_frame -= 1
        if current_frame < 0:
            current_frame = total_frames - 1
        control.pose(float(current_frame))
        update_panel()

EditorCamera()
app.run()
