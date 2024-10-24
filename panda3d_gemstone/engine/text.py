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

from panda3d.core import NodePath, TextNode
from panda3d.core import Texture

from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.resource import Resource, ExportProperty

from panda3d_gemstone.engine.model_utilities import get_model_texture_objects

class Text(NodePath, Configurable, InternalObject):
    """
    Gemstone framework wrapper for the Panda3D TextNode object
    for displaying text in the scene graph
    """

    Alignment = {
        'left': TextNode.ALeft,
        'right': TextNode.ARight,
        'center': TextNode.ACenter,
        TextNode.ALeft: TextNode.ALeft,
        TextNode.ARight: TextNode.ARight,
        TextNode.ACenter: TextNode.ACenter
    }

    def __init__(self, config_path: str, section: str = 'Configuration'):
        NodePath.__init__(self, '')
        Configurable.__init__(self, config_path, section)

        self.__text_node = TextNode('TextBillboard')
        self.assign(self.attach_new_node(self.__text_node))
        self.set_billboard_point_eye()
        self.set_light_off()
        self.set_color_off()
        self.set_scale(0.0425)
        self.set_pos(0, 0, 0)
        self.set_color(1.0, 1.0, 1.0, 1.0)
        self.set_shadow_color(0.0, 0.0, 0.0, 1.0)
        self.set_shadow_offset(0.08, 0.08)
        self.set_text_alignment('center')
        self.set_text('')
        self.initialize()

    def set_enabled(self, enabled: bool) -> None:
        """
        Sets the Text object's enabled state
        """

        if enabled:
            self.show()
        else:
            self.hide()

    def get_shadow_color(self) -> object:
        """
        Returns the Text objects's shadow color
        """

        return self.__text_node.get_shadow_color()

    def set_shadow_color(self, *color) -> None:
        """
        Sets the Text object's shadow color
        """

        self.__text_node.set_shadow_color(*color)

    def get_color(self) -> object:
        """
        Returns this Text object's text color
        """

        return self.__text_node.get_text_color()

    def set_color(self, *color) -> None:
        """
        Sets this Text object's text color
        """

        self.__text_node.set_text_color(*color)

    def get_shadow_offset(self) -> object:
        """
        Returns this Text object's shadow offset
        """

        return self.__text_node.get_shadow()

    def set_shadow_offset(self, *offset) -> None:
        """
        Sets thie Text object's shadow offset
        """

        self.__text_node.set_shadow_color(*offset)

    def clear_shadow_color(self) -> None:
        """
        Clears the text object's shadow color
        """

        self.__text_node.clear_shadow_color()

    def clear_shadow(self) -> None:
        """
        Clears the text object's shadow
        """

        self.__text_node.clear_shadow()

    def set_font(self, font_path: str) -> None:
        """
        Sets the text object's font resource
        """

        assert font_path != None
        assert font_path != ''

        font = Font(font_path)
        if not font:
            self.notify.warning('Failed to set font. Could not open font "%s"' % font_path)
            return
        
        text_font = font.get_text_font()
        self.__text_node.set_font(text_font)

    def set_text(self, text) -> None:
        """
        Sets the text object's displayed text
        """

        self.__text_node.set_text(text)

    def get_text(self) -> str:
        """
        Gets the text object's displayed text
        """

        return self.__text_node.get_text()

    def get_text_alignment(self) -> object:
        """
        Returns the text object's text alignment
        """

        return self.__text_node.get_align()

    def get_text_alignment_name(self, align: object) -> str:
        """
        Returns the text alignment name from instance
        """

        for k, v in list(Text.Alignment.items()):
            if v == align and isinstance(k, str):
                return k
        
    def set_text_alignment(self, align: object) -> None:
        """
        Sets the text object's alignment property
        """

        if isinstance(align, str):
            align = align.lower()

        if not align in Text.Alignment:
            self.notify.warning('Failed to set alignment. Invalid alignement "%s" specified' % align)
            return
        
        self.__text_node.set_align(Text.Alignment[align])

class Font(Resource, InternalObject):
    """
    Represents a Font resource in the Gemstone framework. Wrapping the
    native Panda3D font objects
    """

    def __init__(self, config_path: str, force_export: bool = False):
        self.__name = ''
        self.__fonts = []
        self.__font_data = {}
        self.__text_font = None
        self.__line_height = None
        self.__font_textures = []
        self.set_disable_filtering(False)

        Resource.__init__(self, config_path, force_export)
        InternalObject.__init__(self)

    @property
    def text_font(self) -> object:
        """
        Returns the font resource as a Panda3D text font object
        through a property
        """

        return self.get_text_font()

    def get_text_font(self) -> object:
        """
        Returns the font resource as a Panda3D text font object
        """

        return self.__text_font

    def load_font_data(self, data: dict) -> None:
        """
        Loads the font data dictionary into the resource 
        object
        """

        self.__font_data = data

    def set_line_height(self, data: object) -> None:
        """
        Sets the font resource's line height
        """

        self.__line_height = data

    def disable_texture_filtering(self, disable_filtering: bool) -> None:
        """
        Sets the text filtering state as either true or false
        """

        if disable_filtering:
            mag_filter = Texture.FTNearest
        else:
            mag_filter = Texture.FTLinear

        for tex in self.__font_textures:
            tex.set_mag_filter(mag_filter)

    def export(self, force_export: bool) -> None:
        """
        Attempts to export the font resource
        """

        if len(self.__font_data) == 1:
            params = list(list(self.__font_data.items())[0])
            params.append('MakeFont')
            export = ExportProperty(*params)
            self.add_export_step(export)
            self.add_export_step(export.generate_post_egg2bam)
            self.__fonts.append(self.get_export_step(-1).output_filename)
            Resource.export(self, force_export)
        elif len(self.__font_data) > 1:
            self.notify.error('%s does not support multipart models' % self.__class__.__name__)

    def set_name(self, name: str) -> None:
        """
        Sets the font resource's name
        """

        self.__name = name

    def get_name(self) -> str:
        """
        Retrieves the font resource's name
        """

        return self.__name

    def _load(self, force_export: bool) -> bool:
        """
        Loads the font resource into memory
        """

    def _unload(self) -> None:
        """
        Unloads the font resource from memory
        """

        if self.loaded:

            if len(self.__fonts):
                self.notify.warning('Font unloading not yet implemented. Attempted to unload font: %s' % self.__fonts[0])
            return True

        return False

class TextBillboard(Configurable, InternalObject):
    """
    Represents a billboard text node in the Gemstone framework
    """

    Alignment = {
        'left': TextNode.ALeft,
        'right': TextNode.ARight,
        'center': TextNode.ACenter,
        TextNode.ALeft: TextNode.ALeft,
        TextNode.ARight: TextNode.ARight,
        TextNode.ACenter: TextNode.ACenter
    }

    def __init__(self, config_path: str, parent: object):
        InternalObject.__init__(self)
        self.__text_node = TextNode(self.__class__.__name__)
        self.__nodepath = parent.attach_new_node(self.__text_node)
        self.__nodepath.set_billboard_point_eye()
        self.__nodepath.set_light_off()
        self.__nodepath.set_color_off()
        self.set_enabled(True)
        self.set_color(Vec4(1, 1, 1, 1))
        self.set_align(TextNode.ACenter)
        self.set_text_size(0.7)
        self.set_position(Vec3(0, 0, 4.2))
        self.set_font(None)
        self.set_text('')
        
        Configurable.__init__(self, config_path)
        self.initialize()

    def set_enabled(self, enabled: bool) -> None:
        """
        Sets the object's enabled visibility state
        """

        if enabled:
            self.__nodepath.show()
        else:
            self.__nodepath.hide()

    def set_color(self, color: object) -> None:
        """
        Sets the object's text color
        """

        self.__text_node.set_text_color(color)

    def get_color(self) -> object:
        """
        Returns the object's text color
        """

        return self.__text_node.get_text_color()

    def set_shadow_color(self, color: object) -> None:
        """
        Sets the object's shadow color
        """

        self.__text_node.set_shadow_color(color)

    def get_shadow_color(self) -> object:
        """
        Returns the object's shadow color
        """

        return self.__text_node.get_shadow_color()

    def set_font(self, font: object) -> None:
        """
        Sets the billboard's font object
        """

        if not font:
            return

        f = Font(font)
        tf = f.get_text_font()
        if tf:
            self.__text_node.set_font(tf)

    def set_text(self, text: str) -> None:
        """
        Sets the billboard's text value
        """

        self.__text_node.set_text(text)

    def get_text(self) -> str:
        """
        Returns this billboard's text value
        """

        return self.__text_node.get_text()

    def set_shadow_offset(self, offset: object) -> None:
        """
        Sets the text shadow offset
        """

        self.__text_node.set_shadow(offset)

    def get_shadow_offset(self) -> object:
        """
        Returns the text shadow offset
        """

        return self.__text_node.get_shadow(offset)

    def set_align(self, align: object) -> None:
        """
        Sets the object's text alignment
        """

        a = TextBillboard.Alignment.get(align.lower(), None)
        if not a:
            self.notify.warning('Failed to align. Invalid alignment specified: %s' % str(align))

        self.__text_node.set_align(a)

    def reparent_to(self, nodepath: object) -> None:
        """
        Reparents the object to the node path
        """

        self.__nodepath.reparent_to(nodepath)