from ursina import *
from direct.actor.Actor import Actor
from pathlib import Path
from panda3d.core import getModelPath
from ursina.prefabs.first_person_controller import FirstPersonController

model_dir = (Path(__file__).parent.parent / 'src' / 'assets' / 'models').resolve()
getModelPath().append_directory(str(model_dir))

app = Ursina(title="FPS Weapon Test", borderless=False, vsync=True)

Sky(texture='sky_sunset')
DirectionalLight(shadows=True).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgb(0.6, 0.6, 0.6))

ground = Entity(
    model='plane',
    scale=50,
    texture='grass',
    collider='mesh',
    color=color.green.tint(-0.1)
)

player = FirstPersonController(speed=8, jump_height=2, gravity=1, position=(0, 1, 0))

target_cube = Entity(
    model='cube',
    color=color.red,
    scale=1,
    position=(5, 1, 5),
    collider='box'
)

class FPSWeapon:
    def __init__(self, model_path='UAL1_Standard.glb', scale=2):
        self.holder = camera.attach_new_node("fps_weapon")
        self.holder.set_pos(0.05, -1.25, -0.1)
        self.holder.set_hpr(185, 0, 0)

        self.actor = Actor(model_path)
        # print("textures:", list(self.actor.findAllTextures()))
        # print("materials:", list(self.actor.findAllMaterials()))
        self.actor.reparent_to(self.holder)
        self.actor.set_scale(scale)
        # Available animations: ['A_TPose', 'Crouch_Fwd_Loop', 'Crouch_Idle_Loop', 'Dance_Loop', 'Death01', 'Driving_Loop',
        #              'Fixing_Kneeling', 'Hit_Chest', 'Hit_Head', 'Idle_Loop', 'Idle_Talking_Loop', 'Idle_Torch_Loop',
        #              'Interact', 'Jog_Fwd_Loop', 'Jump_Land', 'Jump_Loop', 'Jump_Start', 'PickUp_Table',
        #              'Pistol_Aim_Down', 'Pistol_Aim_Neutral', 'Pistol_Aim_Up', 'Pistol_Idle_Loop', 'Pistol_Reload',
        #              'Pistol_Shoot', 'Punch_Cross', 'Punch_Jab', 'Push_Loop', 'Roll', 'Roll_RM', 'Sitting_Enter',
        #              'Sitting_Exit', 'Sitting_Idle_Loop', 'Sitting_Talking_Loop', 'Spell_Simple_Enter',
        #              'Spell_Simple_Exit', 'Spell_Simple_Idle_Loop', 'Spell_Simple_Shoot', 'Sprint_Loop',
        #              'Swim_Fwd_Loop', 'Swim_Idle_Loop', 'Sword_Attack', 'Sword_Attack_RM', 'Sword_Idle',
        #              'Walk_Formal_Loop', 'Walk_Loop']

        available = set(self.actor.get_anim_names())
        self.available = available

        self.is_animating = False
        self.current_action = None
        self.anim_queue = []
        self.current_anim = None
        self.skip_enter = False

    def play_animation(self, action_key):
        if self.is_animating:
            return

        self._prev_anim = self.actor.get_current_anim()
        self.actor.stop()

        if action_key == 'fire':
            if self.skip_enter:
                anims = ['Spell_Simple_Shoot']
            else:
                anims = ['Spell_Simple_Enter']
                self.skip_enter = True
            anims = [a for a in anims if a in self.available]
            if not anims:
                return
            self.anim_queue = []
            self.is_animating = True
            self.current_action = action_key
            self.current_anim = anims[0]
            self.actor.play(anims[0])
            if anims[0] == 'Spell_Simple_Shoot':
                self._perform_shot()

        elif action_key == 'enter_exit':
            if self._prev_anim == 'Spell_Simple_Idle_Loop':
                anims = ['Spell_Simple_Exit']
            else:
                anims = ['Spell_Simple_Enter', 'Spell_Simple_Exit']
            anims = [a for a in anims if a in self.available]
            if not anims:
                return
            self.anim_queue = anims[1:]
            self.is_animating = True
            self.current_action = action_key
            self.current_anim = anims[0]
            self.actor.play(anims[0])

        elif action_key == 'stop':
            anim_name = 'Spell_Simple_Exit'
            if anim_name not in self.available:
                return
            self.is_animating = True
            self.current_action = action_key
            self.current_anim = anim_name
            self.actor.play(anim_name)
            self.skip_enter = False

    def _perform_shot(self):
        """Выполняет луч от камеры и уничтожает попавший куб."""
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=100,
            ignore=(player,)
        )
        if hit_info.hit:
            if hit_info.entity == target_cube:
                destroy(target_cube)
                print("🎯 Куб уничтожен!")

    def update(self):
        if self.is_animating and self.current_anim:
            ctrl = self.actor.get_anim_control(self.current_anim)
            if ctrl and not ctrl.is_playing():
                if self.anim_queue:
                    self.current_anim = self.anim_queue.pop(0)
                    self.actor.play(self.current_anim)
                else:
                    self.is_animating = False
                    finished_action = self.current_action
                    self.current_action = None
                    self.current_anim = None

                    if finished_action == 'fire' and 'Spell_Simple_Idle_Loop' in self.available:
                        self.actor.play('Spell_Simple_Idle_Loop')


        if not self.is_animating:
            if mouse.left:
                self.play_animation('fire')
            if held_keys['r']:
                self.play_animation('stop')
            if held_keys['e']:
                self.play_animation('enter_exit')

weapon = FPSWeapon(model_path='UAL1_Standard.glb', scale=0.8)

def update():
    weapon.update()


window.cursor_hidden = True

app.run()
