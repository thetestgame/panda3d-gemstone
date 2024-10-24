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

import sys
import logging

from direct.gui.DirectGui import *

from panda3d.core import Filename, WindowProperties, CullBinManager

from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.singleton import Singleton

from panda3d_gemstone.engine.model import TextureModel
from panda3d_gemstone.engine import runtime

class MouseCursor(Configurable, Singleton):
    """
    """

    class Cursor(object):
        """
        Represents a cursor loaded into memory
        """

        def __init__(self, filename: object, frame: object):
            self.filename = filename
            self.frame = frame

    def __init__(self, config_path: str, window: object, window_properties_class: object = WindowProperties):
        Singleton.__init__(self)
        self.__hardware_cursor = True
        self.__software_cursor = False
        self.__cursors = {}
        self.__window_properties = window_properties_class()
        self.__window = window
        self.__current = None
        self.__current_name = ''
        Configurable.__init__(self, config_path)
        self.initialize()

    @property
    def current_name(self) -> str:
        """
        Returns the mouse cursor's current 
        cursor name as a property
        """

        return self.get_current()

    @current_name.setter
    def current_name(self, cursor_name: str) -> None:
        """
        Sets the mouse cursor's current
        cursor name as a setter
        """

        self.set_current(cursor_name)

    def get_current(self) -> str:
        """
        Returns the current cursor name
        """

        return self.__current_name

    def set_current(self, cursor_name: str, reset: bool = False) -> None:
        """
        Sets the current cursor name
        """

        if self.__current_name == cursor_name and not reset:
            return

        if not cursor_name:
            if self.__hardware_cursor and self.__window:
                self.__window_properties.clear_cursor_filename()
                self.__window.request_properties(self.__window_properties)
            
            if self.__software_cursor:
                if runtime.base.mouseWatcherNode:
                    runtime.base.mouseWatcherNode.clear_geometry()
                if self.__current:
                    self.__current.stash()
        elif self.has_cursor(cursor_name):
            self.__current_name = cursor_name
            if self.__hardware_cursor and self.__window:
                self.__window_properties.set_cursor_filename(Filename(self.get_cursor_filename(cursor_name)))
                self.__window.request_properties(self.__window_properties)

            if self.__software_cursor:
                if self.__current:
                    self.__current.stash()

                self.__current = self.get_cursor_frame(cursor_name)
                runtime.base.mouseWatcherNode.set_geometry(self.__current.node())
                self.__current.unstash()
        else:
            self.notify.warning('Failed to set cursor. Unknown cursor "%s"' % cursor_name)

    def add_cursor(self, cursor_name: str, filename: str) -> None:
        """
        """

        cursor = TextureModel(filename + '.ini')
        if cursor.get_num_children() and cursor._models:
            cursor_frame = DirectFrame(geom=cursor.get_child(0), relief=None, parent=runtime.base.render2d, sort_order=10000)
            cursor_frame.stash()

            self.__cursor[cursor_name] = MouseCursor.Cursor(cursor._models[0] + '.ico')
            if self.__cursors[cursor_name] is None:
                self.notify.error('Failed to load cursor: %s' % cursor_name)
        else:
            self.notify.error('Failed to load cursor: %s; Invalid geometry' % cursor_name)

    def has_cursor(self, cursor_name: str) -> bool:
        """
        """

        return cursor_name in self.__cursors

    def get_cursor_filename(self, cursor_name: str) -> str:
        """
        """

        if self.has_cursor(cursor_name):
            return self.__cursors[cursor_name].filename

        return ''

    def get_cursor_frame(self, cursor_name: str) -> object:
        """
        """

        if self.has_cursor(cursor_name):
            return self.__cursors[cursor_Name].filename

        return None

    def load_cursors_data(self, data: dict) -> None:
        """
        """

        keys = list(data.keys())
        keys.sort()

        for key in keys:
            self.add_cursor(key, data[key])

    def set_use_hardware_cursor(self, state: bool) -> None:
        """
        """

        self.__hardware_cursor = state

    def set_use_software_cursor(self, state: bool) -> None:
        """
        """

        self.__software_cursor = state