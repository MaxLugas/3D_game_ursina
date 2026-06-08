from ursina import *
from direct.actor.Actor import Actor
from src.core.destructibles import DESTRUCTIBLE_OBJECTS
from src.core.weapon_config import WEAPON_MODEL, WEAPON_SCALE
from src.shaders.shader_loader import weapon_shader_panda

class FPSWeapon:
    def __init__(self, model_path=WEAPON_MODEL, scale=WEAPON_SCALE):
        # Создаём узел-держатель для оружия в камере | Create weapon holder node attached to camera
        self.holder = camera.attach_new_node("fps_weapon")
        self.holder.set_pos(0.05, -1.25, -0.1)
        self.holder.set_hpr(185, 0, 0)

        # Загружаем анимированную модель оружия | Load animated weapon model
        self.actor = Actor(model_path)
        # print("textures:", list(self.actor.findAllTextures()))
        # print("materials:", list(self.actor.findAllMaterials()))
        self.actor.reparent_to(self.holder)
        self.actor.set_scale(scale)

        self.actor.set_shader(weapon_shader_panda)
        self.holder.set_light_off()
        from panda3d.core import MaterialAttrib, ColorScaleAttrib
        def _set_geom_colors(node):
            if node.node().is_geom_node():
                gn = node.node()
                for i in range(gn.get_num_geoms()):
                    state = gn.get_geom_state(i)
                    attrib = state.get_attrib(MaterialAttrib.get_class_type())
                    if attrib:
                        mat = attrib.get_material()
                        if mat:
                            c = mat.get_diffuse()
                            brightness = 2.0
                            max_val = max(c.x, c.y, c.z)
                            scale = min(brightness, 1.0 / max_val) if max_val > 0 else 1.0
                            r = c.x * scale
                            g = c.y * scale
                            b = c.z * scale
                            scale = ColorScaleAttrib.make(Vec4(r, g, b, c.w))
                            gn.set_geom_state(i, state.add_attrib(scale))
            for child in node.get_children():
                _set_geom_colors(child)
        _set_geom_colors(self.actor)

        available = set(self.actor.get_anim_names())
        self.available = available

        # Состояние оружия | Weapon state
        self.is_animating = False
        self.current_action = None
        self.anim_queue = []
        self.current_anim = None
        self.skip_enter = False

    def play_animation(self, action_key):
        # Блокировка новых анимаций во время воспроизведения | Block new animations during playback
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
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=100,
            ignore=(camera,)
        )
        if hit_info.hit:
            entity = hit_info.entity
            model_name = entity.model.name if entity.model else None
            if model_name in DESTRUCTIBLE_OBJECTS:
                destroy(entity)

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
                        self.actor.loop('Spell_Simple_Idle_Loop')

        if not self.is_animating:
            if mouse.left:
                self.play_animation('fire')
            if held_keys['r']:
                self.play_animation('stop')
