from ursina import Shader
from panda3d.core import Shader as Panda3DShader
import os


class ShaderLoader:
    _shaders_dir = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def load_shader(name, vertex_path, fragment_path):
        vertex_path = os.path.join(ShaderLoader._shaders_dir, vertex_path)
        fragment_path = os.path.join(ShaderLoader._shaders_dir, fragment_path)

        with open(vertex_path, 'r', encoding='utf-8') as vf:
            vertex_code = vf.read()
        with open(fragment_path, 'r', encoding='utf-8') as ff:
            fragment_code = ff.read()

        return Shader(
            name=name,
            language=Shader.GLSL,
            vertex=vertex_code,
            fragment=fragment_code
        )

    @staticmethod
    def load_panda_shader(vertex_code, fragment_code):
        return Panda3DShader.make(
            Panda3DShader.SL_GLSL,
            vertex_code,
            fragment_code
        )

    @staticmethod
    def load_all_shaders():
        return {
            'comics': ShaderLoader.load_shader('comics_shader', 'comics_vertex.glsl', 'comics_fragment.glsl'),
            'npc': ShaderLoader.load_shader('npc_shader', 'npc_vertex.glsl', 'npc_fragment.glsl'),
            'weapon': ShaderLoader.load_shader('weapon_shader', 'weapon_vertex.glsl', 'weapon_fragment.glsl'),
            'ground': ShaderLoader.load_shader('ground_shader', 'ground_vertex.glsl', 'ground_fragment.glsl')
        }


comics_shaders = ShaderLoader.load_shader('comics_shaders', 'comics_vertex.glsl', 'comics_fragment.glsl')

with open(os.path.join(ShaderLoader._shaders_dir, 'npc_vertex.glsl'), 'r') as f:
    npc_vert = f.read()
with open(os.path.join(ShaderLoader._shaders_dir, 'npc_fragment.glsl'), 'r') as f:
    npc_frag = f.read()
npc_shader_panda = ShaderLoader.load_panda_shader(npc_vert, npc_frag)

with open(os.path.join(ShaderLoader._shaders_dir, 'weapon_vertex.glsl'), 'r') as f:
    weapon_vert = f.read()
with open(os.path.join(ShaderLoader._shaders_dir, 'weapon_fragment.glsl'), 'r') as f:
    weapon_frag = f.read()
weapon_shader_panda = ShaderLoader.load_panda_shader(weapon_vert, weapon_frag)

with open(os.path.join(ShaderLoader._shaders_dir, 'ground_vertex.glsl'), 'r') as f:
    ground_vert = f.read()
with open(os.path.join(ShaderLoader._shaders_dir, 'ground_fragment.glsl'), 'r') as f:
    ground_frag = f.read()
ground_shader_panda = ShaderLoader.load_panda_shader(ground_vert, ground_frag)