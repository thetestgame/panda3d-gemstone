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

from panda3d_gemstone.framework import exceptions

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    raise exceptions.MissingThirdpartySupportError('PyQt5')

from panda3d_gemstone.application.application import GemstoneApplication

from panda3d_gemstone.editor.showbase import EditorShowbase
from panda3d_gemstone.editor.window import EditorWindow
from panda3d_gemstone.editor.styles import StyleManager
from panda3d_gemstone.editor.level import EditorWorldManager, EditorScene

from panda3d_gemstone.engine import runtime, prc
from panda3d_gemstone.framework.progress import RenderController

from panda3d.core import WindowProperties

class EditorQApplication(QApplication):
    """
    Custom QApplication instance for use inside the Gemstone Editor application
    """

    def __init__(self, application: object):
        self._application = application
        super().__init__(sys.argv)

    def setup(self) -> None:
        """
        Performs setup operations on the QApplication instnace
        """

        # Sync PyQT application information with Gemstone application
        # information.
        self.setApplicationDisplayName(self._application.get_application_name())
        self.setApplicationName(self._application.get_application_name())
        self.setApplicationVersion(self._application.get_application_version())

    def run(self) -> int:
        """
        Runs the QApplication instance
        """

        return self.exec_()

class EditorApplication(GemstoneApplication):
    """
    Base class for all Gemstone editor applications
    """

    SHOWBASE_CLS = EditorShowbase
    
    def __init__(self, showbase_cls: object = None):
        super().__init__(window_type='none', showbase_cls=showbase_cls)
        self.world_manager = EditorWorldManager.instantiate_singleton()
        self.editor_scene = EditorScene.instantiate_singleton()
        self.editor_controller = RenderController()
        self.q_application = EditorQApplication(self)
        self.editor_window = None

    def load_prc_files(self, files: list, optional: bool = False) -> None:
        """
        Attempts to load a list of prc files
        """

        if not len(files):
            return

        for prc_file in files:
            prc.load_prc_file(prc_file, optional)

    def setup(self) -> None:
        """
        Performs setup operations on the application instance
        """

        super().setup()

        # Setup PyQT components
        self.q_application.setup()
        self.styles = StyleManager(self)
        self.styles.set_dark_theme()

        # Create the editor window
        self.editor_window = EditorWindow(self)

    def run(self) -> int:
        """
        Runs the editor application
        """

        if not self.window:
            self.notify.error('Failed to start editor. Could not open window')
            return

        self.notify.info('Opening primary editor window.')
        self.editor_window.show()

        self.notify.info('Starting application loop.')
        return self.q_application.run()

    def get_application_name(self) -> str:
        """
        Returns the application's name. 
        """

        return '%s - Level Editor' % (
            prc.get_prc_string('app-name', 'Gemstone Application'))


