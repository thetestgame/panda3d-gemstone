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

from panda3d.core import *

from panda3d_gemstone.framework.internal_object import InternalObject

class QTPandaWidget(QWidget, InternalObject):
    """
    """

    def __init__(self , *args, **kwargs):
        super(InternalObject, self).__init__()
        super(QWidget, self).__init__(*args, **kwargs)

        self.win = None
        self.wp = None

    def setup(self) -> None:
        """
        """
        
        self.notify.info('Setting up %s widget' % self.__class__.__name__)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.createWindow()
        self.startTaskMgr()

    def force_resize(self) -> None:
        """
        """

        wp = WindowProperties()
        wp.setOrigin(0, 0)
        wp.setSize(self.width(), self.height())
        base.win.requestProperties(wp)

    def resizeEvent(self, evt) -> None:
        """
        """
        
        size = evt.size()
        wp = WindowProperties()
        wp.setOrigin(0, 0)
        wp.setSize(size.width(), size.height())
        base.win.requestProperties(wp)

    def minimumSizeHint(self) -> None:
        """
        """
        
        return QSize(400,300)

    def createWindow(self) -> None:
        """
        """
        
        wp = WindowProperties.getDefault()
        wp.setSize(self.width(), self.height())
        wp.setOrigin(0, 0)
        wp.setParentWindow(int(self.winId()))
        wp.setUndecorated(True)
        base.windowType = 'onscreen'
        base.openDefaultWindow(props=wp)
        self.wp = wp

    def startTaskMgr(self) -> None:
        """
        """
        
        pandaTimer = QTimer(self)
        pandaTimer.timeout.connect(taskMgr.step)
        pandaTimer.start(0)

    def cleanup(self) -> None:
        """
        """

        self.notify.info('Cleaning up widget')
        if base.win:
            base.closeWindow(base.win)
