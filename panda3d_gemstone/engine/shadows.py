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

from panda3d.core import NodePath, CardMaker, Texture
from panda3d.core import TransparencyAttrib

from panda3d_gemstone.engine import runtime
from panda3d_gemstone.framework.internal_object import InternalObject

class GeometryShadow(NodePath, InternalObject):
    """
    """

    def __init__(self, obj: object, texture_path: str, height: float = 0.001, scale_x: float = 1.0, scale_y: float = 1.0):
        NodePath.__init__(self, '')
        InternalObject.__init__(self)
        card_maker = CardMaker(self.__class__.__name__)
        card_maker.set_frame(-0.5 * scale_x, 0.5 * scale_x, -0.5 * scale_y, 0.5 * scale_y)
        self.assign(obj.attach_new_node(card_maker.generate()))
        self.set_p(-90)

        try:
            texture = runtime.loader.load_texture(texture_path)
            if texture:
                self.set_texture(texture)
            else:
                self.notify.error('%s: Failed to read texture file "%s"' % (self.__class__.__name__, texture_path))
        except IOError:
            self.notify.error('%s: Failed to read texture file "%s"' % (self.__class__.__name__, texture_path))

        self.set_z(height)
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.set_depth_write(False)