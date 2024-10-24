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

import os
import sys

import logging
from logging import StreamHandler

from direct.directnotify.Notifier import Notifier
from panda3d.core import MultiplexStream, Filename, load_prc_file_data
from panda3d.core import Notify, ConfigVariableString, LineStream, StreamWriter

from panda3d_gemstone.engine import runtime, prc

from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.runnable import Runnable
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.exceptions import raise_not_implemented

from panda3d_gemstone.logging.utilities import *

class NotifyHandler(StreamHandler):
    """
    Custom StreamHandler for pipeing logging module based messages
    to a Panda3D notifier category
    """

    def __init__(self, name: str = 'python'):
        super().__init__()
        self.__notify = get_notify_category(name)

    def emite(self, record: object) -> None:
        """
        Processes the incoming record from the logging module
        """

        message_parts = self.format(record).split('||')
        level = message_parts[0].lower()
        message = message_parts[1]
        
        if hasattr(self.__notify, level):
            func = getattr(self.__notify, level)
        else:
            func = self.__notify.info
        
        func.info(message)

class ApplicationLogger(Singleton, InternalObject):
    """
    Singleton for managing the applications logging outputs
    """

    def __init__(self):
        Singleton.__init__(self)
        InternalObject.__init__(self)
        self.__stream = None
        self.__setup()

    def __setup(self) -> None:
        """
        Performs setup operations on the application logger
        """

        self.__stream = LineStream()
        Notify.ptr().setOstreamPtr(self.__stream, False)
        Notifier.streamWriter = StreamWriter(Notify.out(), True)
        self.__initialize_logging_module()

    def destroy(self) -> None:
        """
        Performs shutdown operations on the application logger
        """

        Singleton.destroy(self)
        InternalObject.destroy(self)
        
        if self.is_activated():
            self.deactivate()

        for handler_name in self.__handlers:
            self.remove_handler(handler_name)

    def __initialize_logging_module(self) -> None:
        """
        Initializes the Python logging module to pipe through the Panda3D notifier
        """
        level_map = {
            'spam': logging.DEBUG,
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARN,
            'error': logging.ERROR
        }

        level = level_map.get(ConfigVariableString('notify-level-python', '').value, logging.INFO)
        formatter = '%(levelname)s||%(message)s'
        logging.basicConfig(format=formatter, level=level, handlers=[NotifyHandler()])   