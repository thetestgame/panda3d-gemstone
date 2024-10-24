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

from PyQt5.QtGui import QIcon, QPixmap

from panda3d_gemstone.framework.internal_object import InternalObject

class StyleManager(InternalObject):
    """
    Styling manager for the PyQt5 editor application
    """

    def __init__(self, application):
        super().__init__()
        self._application = application
        self._icon_path = 'assets/icons/black'

    def get_icon(self, path):
        """
        Retrieves the icon related to the requested style
        """

        final_path = '%s/%s' % (self._icon_path, path)
        return QIcon(final_path)

    def get_pixmap(self, path):
        """
        Retrieves the pixmap related to the requested style
        """

        final_path = '%s/%s' % (self._icon_path, path)
        return QPixmap(final_path)

    def set_dark_theme(self):
        """
        Attempts to set the editor's dark theme if the required module is available
        """

        has_dark = True
        try:
            import qdarkstyle
        except:
            has_dark = False

        if not has_dark:
            self.notify.warning('Failed to set dark theme; qdarkstyle not installed')
            return

        stylesheet = qdarkstyle.load_stylesheet_pyqt5()
        self._icon_path = 'assets/icons/white'
        self._application.q_application.setStyleSheet(stylesheet)
        self.notify.info('Configured dark theme')    