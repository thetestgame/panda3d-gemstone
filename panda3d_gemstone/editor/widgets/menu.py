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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from direct.directnotify.DirectNotifyGlobal import directNotify

#from anvil.core import editor_globals
#from anvil.widget import properties, layers, asset_library

from functools import partial
import sys

class MenuBase(object):
    """
    Base class for all window menus
    """

    def __init__(self, window, menu_bar):
        self.window = window
        self.menu_bar = menu_bar
        self.notify = directNotify.newCategory(self.__class__.__name__)
        self.build_menu()

    def build_menu(self):
        """
        Constructs the menu object on the window
        """

class EditorFileMenu(MenuBase):
    """
    File menu for the primary editor window
    """

    def build_menu(self):
        """
        Constructs the menu object on the window
        """

        self.file_menu = self.menu_bar.add_menu('&File')
        self.file_menu.add_action('&New', theme_icon='star.png', tooltip='Creates a new level project')
        self.file_menu.add_action('&Save', theme_icon='save.png', tooltip='Saves current project')
        self.file_menu.add_action('&Settings', theme_icon='wrench.png', tooltip='User settings')
        self.file_menu.add_action('&Quit', theme_icon='exit.png', tooltip='Closes the editor', connect=sys.exit)

class EditorEditMenu(MenuBase):
    """
    Edit menu for the primary editor window
    """

    def build_menu(self):
        """
        Constructs the menu object on the window
        """

        self.edit_menu = self.menu_bar.add_menu('&Edit')

class EditorViewMenu(MenuBase):
    """
    View menu for the primary editor window
    """

    def build_menu(self):
        """
        Constructs the menu object on the window
        """

        self.view_menu = self.menu_bar.add_menu('&View')
        #self.view_menu.add_action(
        #    '&Properties Panel', 
        #    tooltip='Opens/Closes the properties panel', 
        #    checkable=True, 
        #    connect=partial(
        #        self.toggle_panel, 
        #        properties.QPropertiesWidget))
        #self.view_menu.add_action(
        #    '&Layers Panel', 
        #    tooltip='Opens/Closes the layers panel', 
        #    checkable=True, 
        #    connect=partial(
        #        self.toggle_panel, 
        #        layers.QLayersWidget))
        #self.view_menu.add_action(
        #    '&Asset Library', 
        #    tooltip='Opens/Closes the asset library', 
        #    checkable=True, 
        #    connect=partial(
        #        self.toggle_panel, 
        #        asset_library.QObjectLibraryWidget,
        #        dock=Qt.LeftDockWidgetArea))

    def toggle_panel(self, *args, **kwargs):
        """
        Toggles the requested panel class
        """

        self.window.toggle_panel(*args, **kwargs)

class EditorHelpMenu(MenuBase):
    """
    Help menu for the primary editor window
    """

    def build_menu(self):
        """
        Constructs the menu object on the window
        """

        self.help_menu = self.menu_bar.add_menu('&Help')
        self.help_menu.add_action('&Docs', theme_icon='question.png', tooltip='Editor documentation', connect=self.open_docs)
        self.help_menu.add_action('&About', theme_icon='information.png', tooltip='About this application', connect=self.open_about)
        #self.help_menu.add_action('&Qt', theme_icon='information.png', tooltip="About this application's Qt version", connect=editor_globals.app.aboutQt)

    def open_docs(self):
        """
        Opens the editor's documentation page
        """

    def open_about(self):
        """
        Opens the editor's about dialog box
        """

        self.notify.info('Opening about dialog box.')
        about_message = """
        %(app_name)s - Gemstone Editor (%(app_version)s)

        Written by:
        Jordan Maxwell <me@jordan-maxwell.info>

        Copyright %(org_name)s, 2020
        %(org_domain)s
        """

        about_info = {
            'app_name': config.GetString('app-name', 'Anvil Level Editor'),
            'app_version': config.GetString('app-version', '1.0.0'),
            'org_name': config.GetString('org-name', 'Digital Descent, LLC'),
            'org_domain': config.GetString('org-domain', 'https://www.digitaldescent.co')
        }

        about_message = about_message % about_info
        response = QMessageBox.about(self.window, 'About Anvil', about_message)

class EditorDebugMenu(MenuBase):
    """
    Debug menu for the primary editor window
    """

    def build_menu(self):
        """
        Constructs the menu object on the window
        """

        self.debug_menu = self.menu_bar.add_menu('&Debug')
        self.debug_menu.add_action(
            '&Print Scene', 
            theme_icon='information.png', 
            tooltip='Prints the entire scene graph to console',
            connect=self.print_scene)
        self.debug_menu.add_action(
            '&Analyze', 
            theme_icon='information.png', 
            tooltip='Analyzes the entire scene graph in console',
            connect=self.analyze_scene)
        self.debug_menu.add_action(
            '&Dump Scene', 
            theme_icon='save.png', 
            tooltip='Dumps the entire scene graph to a file',
            connect=self.dump_scene)

    def print_scene(self):
        """
        Prints the current scene to console
        """

        base.render.ls()
        self.window.status_bar.show_temp_message('Scene printed. Check console for results')

    def analyze_scene(self):
        """
        Analyzes the current scene to console
        """

        base.render.analyze()
        self.window.status_bar.show_temp_message('Scene Analyzed. Check console for results')

    def dump_scene(self):
        """
        Dumps the current editor scene to a file
        """

        base.render.writeBamFile('dump.bam')
        self.window.status_bar.show_temp_message('Scene dumped to `dump.bam`')