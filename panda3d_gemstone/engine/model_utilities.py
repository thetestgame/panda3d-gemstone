"""
MIT License

Copyright (c) 2024 Jordan Maxwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import logging
import datetime
from math import tan, radians

from panda3d.core import Texture, Vec2, Vec3, Thread, Filename
from panda3d.core import InternalName, PNMImage, BoundingBox, Point3
from panda3d.core import TextureAttrib

from panda3d_gemstone.io.file_system import fix_path
from panda3d_gemstone.logging import utilities as logging

__utility_notify = logging.get_notify_category('model-utilities')

def pnms_equal(lhs, rhs) -> bool:
    """
    """

def get_all_geom_nodes(model: object):
    """
    """

    for geom_node_path in model.find_all_matches('**/+GeomNode'):
        yield geom_node_path.node()

def get_all_geoms(model: object, mutable: bool = False):
    """
    """

    for geom_node in get_all_geom_nodes(model):
        num_geoms = geom_node.get_num_geoms()
        for i in range(num_geoms):
            if mutable:
                yield geom_node.modify_geom(index)
            else:
                yield geom_node.get_geom(index)

def get_all_geom_states(model: object):
    """
    """

    for geom in get_all_geom_nodes(model):
        for i in range(geom.get_num_geoms()):
            yield geom.get_geom_state(i)

def has_texture_alpha(texture: object) -> object:
    """
    """

    texture_format = texture.get_format()
    return textureFormat in [
        Texture.FAlpha,
        Texture.FRgba,
        Texture.FRgba4,
        Texture.FRgba5,
        Texture.FRgba8,
        Texture.FRgba12,
        Texture.FRgba16,
        Texture.FRgba32,
        Texture.FLuminanceAlpha,
        Texture.FLuminanceAlphamask
    ]

def is_model_transparent(model: object) -> bool:
    """
    """

def get_model_texture_objects(model: object) -> list:
    """
    """

    assert model != None

    texture = []
    textures_rs = model.find_all_textures()
    for i in range(textures_rs.get_num_textures()):
        textures.append(textures_rs.get_texture(i))

    overrides = [child.get_texture() for child in model.find_all_matches('**') if child.has_texture()]
    textures.extend(overrides)

    return textures


def get_model_textures(model: object) -> list:
    """
    """

    assert model != None
    return [fix_path(texture.get_filename().to_os_specific()) for texture in get_model_texture_objects(model)]

def save_model_as_maya_file(model: object, path: str, version: str = '2019', cleanup: bool = True) -> None:
    """
    Saves the model NodePath as a Maya file for editing and animation
    """

    assert model != None
    model.write_to_bam_file(path + '.bam')

    # Convert bam to egg
    __utility_notify.info('Converting %s.bam to %s.egg...' % (path, path))
    os.system('bam2egg %s.bam -o %.egg' % (path, path))

    # Convert egg to maya
    maya_executable = 'egg2maya%s' % version
    __utility_notify.info('Converting %s.egg to %s.mb using Maya %s...' % (path, path, version))
    os.system('%s %s.egg -o %s.mb' % (maya_executable, path, path))

    # Perform cleanup
    if cleanup:
        os.remove('%s.bam' % path)
        os.remove('%s.egg' % path)
        
def save_character(character: object, directory: str= 'charactershots', format: str = 'png') -> None:
    """
    """

def bake_anim_frame(actor: object, anim: object = None, frame: object = None) -> None:
    """
    """

def focus_model(model: object, camera: object = None, axis: Vec3 = Vec3(1, 1, 1), fix_planes: bool = False, zoom: float = 1.5) -> None:
    """
    """

