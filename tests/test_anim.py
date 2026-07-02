from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath
from panda3d.core import AmbientLight, DirectionalLight

model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="Animation Inspector", borderless=False, vsync=False)

ambient = AmbientLight('ambient')
ambient.set_color((0.55, 0.55, 0.55, 1))
ambient_np = render.attach_new_node(ambient)
render.set_light(ambient_np)

directional = DirectionalLight('directional')
directional.set_color((1, 1, 1, 1))
directional_np = render.attach_new_node(directional)
directional_np.set_hpr(35, -60, 0)
render.set_light(directional_np)

actor = Actor('UAL1_Standard.glb')
actor.reparent_to(render)
actor.set_scale(1.6)

avail = list(actor.get_anim_names())
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
Right: Next anim     Left: Prev anim
Up: Next frame       Down: Prev frame
1: Play              2: Frame mode

[CURRENT]
Animation: {anim_name}
Frames: {frames}
FPS: {fps}
Duration: {duration}
Frame: {current_frame}
"""

right_template = """[ANIMATIONS]
{anim_list}
"""


def get_anim_info(actor, anim_name):
    ctrl = actor.get_anim_control(anim_name)
    if not ctrl:
        return None

    anim = ctrl.get_anim()
    if not anim:
        return None

    info = {'frames': None, 'fps': None, 'duration': None}

    try:
        if hasattr(anim, 'get_num_frames'):
            info['frames'] = anim.get_num_frames()
    except:
        pass

    try:
        if hasattr(ctrl, 'get_frame_rate'):
            info['fps'] = ctrl.get_frame_rate()
    except:
        pass

    try:
        if hasattr(anim, 'get_duration'):
            info['duration'] = anim.get_duration()
    except:
        pass

    if info['duration'] is None and info['frames'] and info['fps']:
        info['duration'] = info['frames'] / info['fps']

    return info


def update_panel():
    if not anim_name:
        return

    info = get_anim_info(actor, anim_name)

    anim_lines = []
    for name in avail:
        prefix = '> ' if name == anim_name else '  '
        anim_lines.append(f'{prefix}{name}')

    column_left.text = left_template.format(
        anim_name=anim_name,
        frames=info['frames'] if info and info['frames'] else 'N/A',
        fps=f'{info["fps"]:.2f}' if info and info['fps'] else 'N/A',
        duration=f'{info["duration"]:.3f}s' if info and info['duration'] else 'N/A',
        current_frame=f'{current_frame}/{total_frames}' if mode == 'frame' else '-',
    )

    column_right.text = right_template.format(
        anim_list="\n".join(anim_lines)
    )


def start_duration():
    global mode, control

    mode = 'duration'
    actor.stop()

    if anim_name in actor.get_anim_names():
        actor.loop(anim_name)
        control = None


def start_frame():
    global mode, control, current_frame, total_frames

    mode = 'frame'
    current_frame = 0
    actor.stop()

    if anim_name in actor.get_anim_names():
        control = actor.get_anim_control(anim_name)

        if control and control.get_anim():
            anim = control.get_anim()

            if hasattr(anim, 'get_num_frames'):
                total_frames = anim.get_num_frames()
                control.pose(0)


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
    global current_frame, control, mode, total_frames

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

    elif key == 'up arrow' and mode == 'frame' and control and total_frames:
        current_frame = (current_frame + 1) % total_frames
        control.pose(float(current_frame))
        update_panel()

    elif key == 'down arrow' and mode == 'frame' and control and total_frames:
        current_frame = (current_frame - 1) % total_frames
        control.pose(float(current_frame))
        update_panel()


start_duration()
update_panel()

EditorCamera()
app.run()