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

from direct.gui.OnscreenText import OnscreenText

from panda3d.core import TextNode, Vec2, Vec3, Vec4
from panda3d.core import Point2, Point3, load_prc_file_data

from panda3d_gemstone.framework.runnable import Runnable
from panda3d_gemstone.io.file_system import path_exists

from panda3d_gemstone.engine.text import Font

def create_node_debug_hud(parent: object, pos: object, scale: object, node: object, font: str = 'data/fonts/framd.ini', labels: dict = {}) -> Inspector:
    """
    Creates a new on screen debug hud for a Panda3D NodePath
    """

    inspector = Inspector(fontPath=font, updateTime=0.25, parent=parent, pos=pos, scale=scale)

    for label_key in labels:
        inspector.add_object(label_key, labels[label_key], show_label=True)

    inspector.add_object('Pos', node.get_pos)
    inspector.add_object('heading', node.get_h)
    inspector.activate()

    return inspector

class InspectObject(object):
    """
    """

    def __init__(self, always_show: bool, show_label: bool, callback: object, *args):
        self.__always_show = always_show
        self.__show_label = show_label

        if callable(callback):
            self.__callback = callback
        else:
            self.__callback = lambda callback = callback, *args: callback
        self.__args = args

    @property
    def value(self) -> tuple:
        """
        Returns the inspect object's value as a property
        """

        return self.get_value()

    def get_value(self) -> tuple:
        """
        """

        value = self.__callback(*self.__args)
        if self.__always_show or value:
            return (self.__show_label, value)

        return (False, None)

class InspectFormatter(object):
    """
    """

    @staticmethod
    def format(value: object) -> object:
        """
        """

        types = [
            Vec2,
            Vec3,
            Vec4,
            Point2, 
            Point3
        ]

        bool_values = {
            True: 'on',
            False: 'off'
        }

        if type(value) in types:
            s = '%0.2f/%0.2f' % (value.get_x(), value.get_y())
            if hasattr(value, 'get_z'):
                s += '/%0.2f' % value.get_z()
            if hasattr(value, 'get_w'):
                s += '/%0.2f' % value.get_w()
            value = s  
        elif type(value) in [bool]:
            value = bool_values[value]
        else:
            value = str(value)

        return value

 class Inspector(Runnable):
    """
    """

    def __init__(self, font_path: str= '', update_time: float = 0.1, formatter: object = InspectFormatter, show_labels: bool = False, parent: object = None, pos: tuple = (-1.32, 0.95), scale: float = 0.04, color: object = Vec4(1.0, 1.0, 1.0, 0.9)):
        super().__init__()
        self.formatter = formatter
        self.update_time = update_time
        self.show_labels = show_labels
        self.__last_update = 0.0
        self.objects = []

        font = None
        if path_exists(font_path):
            font = Font(font_path).get_text_font()

        self.onscreen_text = OnscreenText(
            fg=color, 
            align=TextNode.ALeft, 
            mayChange=True, 
            scale=scale, 
            font=font, 
            parent=parent, 
            pos=pos)

    def destroy(self) -> None:
        """
        Destroys the inspector object
        """

        Runnable.deactivate(self)
        self.onscreen_text.remove_node()
        self.objects = []

    def add_object(self, label: str, callback: object, always_show: bool = True, show_label: bool = False, *args) ->:
        """
        Adds a new object to the inspector
        """

        self.objects.append((label, InspectObject(always_show, show_label, callback, *args)))

    async def tick(self, dt: float) -> None:
        """
        Called once per tick to perform inspections
        """

        self.__last_update += dt
        if self.__last_update <= self.update_time:
            return

        txt = ''
        for label, obj in self.objects:
            show_label, value = obj.value
            if value is None:
                continue

            if show_label:
                txt += '%s: %s\n' % (label, self.formatter.format(value))
            else:
                txt += '%s\n' % self.formatter.format(value)

        self.onscreen_text.set_text(txt)
        self.__last_update = 0.0