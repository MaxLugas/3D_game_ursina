from panda3d.core import Shader as Panda3DShader
import os


class ShaderLoader:
    _shaders_dir = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def _read_shader_file(filename):
        path = os.path.join(ShaderLoader._shaders_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def load_shader(name, vertex_path, fragment_path):
        vertex_code = ShaderLoader._read_shader_file(vertex_path)
        fragment_code = ShaderLoader._read_shader_file(fragment_path)

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
npc_shader_panda = ShaderLoader.load_shader('npc_shader', 'npc_vertex.glsl', 'npc_fragment.glsl')
weapon_shader_panda = ShaderLoader.load_shader('weapon_shader', 'weapon_vertex.glsl', 'weapon_fragment.glsl')
ground_shader_panda = ShaderLoader.load_shader('ground_shader', 'ground_vertex.glsl', 'ground_fragment.glsl')