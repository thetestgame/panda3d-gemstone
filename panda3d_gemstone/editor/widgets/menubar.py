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

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from direct.directnotify.DirectNotifyGlobal import directNotify

class Menu(object):
    """
    """

    notify = directNotify.newCategory('Menu')

    def __init__(self, window, menu):
        self.window = window
        self.menu = menu

    def add_action(self, display_name, theme_icon=None, icon=None, shortcut=None, tooltip=None, connect=None, **kwargs):
        """
        """

        if theme_icon and False:
            #icon = QIcon(editor_globals.app.styles.get_icon(theme_icon))
            action = QAction(icon, display_name, self.window, **kwargs)
        elif icon:
            icon = QIcon(icon)
            action = QAction(icon, display_name, self.window, **kwargs)
        else:
            action = QAction(display_name, self.window, **kwargs)

        if shortcut:
            action.setShortcut(shortcut)

        if tooltip:
            action.setStatusTip(tooltip)

        if connect:
            action.triggered.connect(connect)

        self.menu.addAction(action)
        return action

class WindowMenuBar(object):
    """
    """

    notify = directNotify.newCategory('WindowMenuBar')

    def __init__(self, window):
        self.window = window
        self.menu_bar = window.menuBar()
        self.menus = {}

    def add_menu(self, display_name):
        """
        """

        if display_name in self.menus:
            return self.menus[display_name]

        menu = Menu(self.window, self.menu_bar.addMenu(display_name))
        self.menus[display_name] = menu
        return self.menus[display_name]

    def get_menu(self, display_name):
        """
        """

        return self.menus.get(display_name, None)

