import os
from panda3d.core import Shader as Panda3DShader

_shaders_dir = os.path.dirname(os.path.abspath(__file__))


def _read_shader_file(filename):
    path = os.path.join(_shaders_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def load_shader(name, vertex_path, fragment_path):
    vertex_code = _read_shader_file(vertex_path)
    fragment_code = _read_shader_file(fragment_path)
    return Panda3DShader.make(Panda3DShader.SL_GLSL, vertex_code, fragment_code)


comics_shaders = load_shader('comics_shaders', 'comics_vertex.glsl', 'comics_fragment.glsl')
npc_shader_panda = load_shader('npc_shader', 'npc_vertex.glsl', 'npc_fragment.glsl')
weapon_shader_panda = load_shader('weapon_shader', 'weapon_vertex.glsl', 'weapon_fragment.glsl')
ground_shader_panda = load_shader('ground_shader', 'ground_vertex.glsl', 'ground_fragment.glsl')