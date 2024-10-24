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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from panda3d_gemstone.engine import prc

from panda3d_gemstone.editor.widgets import panda, statusbar, menu, menubar
from panda3d_gemstone.framework.internal_object import InternalObject

class EditorWindow(QMainWindow, InternalObject):
    """
    Primary window/widget for the PyQt5 editor application
    """

    def __init__(self, application: object, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        super(InternalObject, self).__init__()

        self._application = application
        self._panels = {}

        self.build_window()

    def build_window(self) -> None:
        """
        Constructs the primary editor window
        """

        # Set window info
        window_origin = prc.get_prc_string('window-origin', '0,0').split(',')
        window_size = prc.get_prc_string('window-size', '800,600').split(',')
        self.setGeometry(
            int(window_origin[0]), 
            int(window_origin[1]), 
            int(window_size[0]), 
            int(window_size[1]))
        self.setWindowIcon(QIcon('data/EditorData/images/logo.png'))

        # Load widgets
        self.menu_bar = menubar.WindowMenuBar(self)
        self.status_bar = statusbar.WindowStatusBar(self)

        self.load_menu_bar()
        self.load_panda_widget()

        # Finish construction
        self.finalize_window()

    def finalize_window(self) -> None:
        """
        Finalizes the newly created window
        """

        self.panda.force_resize()

    def load_panda_widget(self) -> None:
        """
        Loads the Panda3D based widget
        """

        self.panda = panda.QTPandaWidget()
        self.panda.setup()
        self.setCentralWidget(self.panda)

    def load_menu_bar(self) -> None:
        """
        Loads the primary window's menu bar
        """

        self.file_menu = menu.EditorFileMenu(self, self.menu_bar)
        self.edit_menu = menu.EditorEditMenu(self, self.menu_bar)
        self.view_menu = menu.EditorViewMenu(self, self.menu_bar)
        self.debug_menu = menu.EditorDebugMenu(self, self.menu_bar)
        self.help_menu = menu.EditorHelpMenu(self, self.menu_bar)

    def toggle_panel(self, panel_class: object, state: bool, dock: object = Qt.RightDockWidgetArea) -> None:
        """
        Toggles the requested panel class
        """

        panel_key = panel_class.__name__
        existing = self._panels.get(panel_key, None)
        self.notify.debug('Toggling Panel: %s' % panel_key)
        if existing and not state:
            self.removeDockWidget(existing)
            del self._panels[panel_key]
        elif not existing and state:
            widget = panel_class(self)
            self.addDockWidget(dock, widget)
            self._panels[panel_key] = widget

    def get_panel(self, panel_class: str) -> object:
        """
        Retrieves the current panel instance if one exists
        """

        panel_key = panel_class.__name__
        return self._panels.get(panel_key, None)