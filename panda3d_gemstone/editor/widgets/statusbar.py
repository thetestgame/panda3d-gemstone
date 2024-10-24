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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from panda3d.core import SceneGraphAnalyzer

from panda3d_gemstone.framework.internal_object import InternalObject

class QStatusUpdater(QTimer, InternalObject):
    """
    """

    def __init__(self, status_bar: object):
        QThread.__init__(self)
        InternalObject.__init__(self)
        fps = config.GetInt('status-update-fps', 10)
        self.setInterval(int(1000/fps))
        self.status_bar = status_bar
        self.scene_analyzer = SceneGraphAnalyzer()
        self.scene_analyzer.add_node(base.render.node())
        self.timeout.connect(self.update_status)

    def update_status(self) -> None:
        """
        """

        self.scene_analyzer.clear()
        status_text = self.status_bar.status_text
        status_parts = [
            self.status_bar.status_message,
            'FPS: %s' % round(globalClock.get_average_frame_rate(), 1),
            'Geoms: %s' % self.scene_analyzer.get_num_geoms(),
            'Vertices: %s' % self.scene_analyzer.get_num_vertices()
        ]

        status_message = ' | '.join(status_parts)
        status_text.setText(status_message)

class WindowStatusBar(InternalObject):
    """
    """

    def __init__(self, window: object, status_message: str = 'Ready'):
        super().__init__()
        self.window = window
        self.status_message = status_message
        self.status_bar = QStatusBar()
        self.status_text = QLabel()
        self.status_bar.addPermanentWidget(self.status_text)
        self.window.setStatusBar(self.status_bar)
        self.updater = QStatusUpdater(self)
        self.updater.start()

    def set_status_message(self, status_message: str) -> None:
        """
        """

        self.status_message = status_message
        self.updater.update_status()

    def show_temp_message(self, status_message: str) -> None:
        """
        """

        self.status_bar.showMessage(status_message)