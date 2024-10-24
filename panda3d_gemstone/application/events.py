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

import json
import os

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.exceptions import raise_not_implemented

from panda3d_gemstone.logging.utilities import get_log_directory, get_log_filename, get_notify_category

class EventHandler(InternalObject):
    """
    Base class for all Gemstone event handlers
    """

    def __init__(self):
        super().__init__()
        self.setup()

    def __del__(self, *args, **kwargs) -> None:
        """
        Called on object deletion
        """

        self.destroy()

    def setup(self) -> None:
        """
        Called on event handler setup
        """

    def destroy(self) -> None:
        """
        Called on event handler destruction
        """

        super().destroy()

    def consume_event(self, type=None, **data) -> None:
        """
        Consumes the incoming event from the EventsManager
        """

        raise_not_implemented(self, 'consume_event')

class ConsoleEventHandler(EventHandler):
    """
    Console printout event handler for Gemstone
    """

    def consume_event(self, type=None, **data) -> None:
        """
        Consumes the incoming event from the EventsManager
        """

        if not hasattr(self, '_notify'):
            self._notify = get_notify_category('events')
            self._notify.setInfo(True)

        event_message = '%s: %s' % (type, json.dumps(data))
        self._notify.info(event_message)

class FileEventHandler(EventHandler):
    """
    File base file handler for Gemstone
    """

    def setup(self) -> None:
        """
        Performs setup operations on the FileEventHandler
        """

        log_directory = get_log_directory()
        log_filename = 'events_' + get_log_filename()
        if not os.path.exists(log_directory):
            os.mkdir(log_directory)

        log_path = os.path.join(log_directory, log_filename)
        self.notify.debug('Opening event log: %s' % log_path)
        self._log_file = open(log_path, 'w')

    def destroy(self) -> None:
        """
        Destroys the FileEventHandler instance
        """

        if hasattr(self, '_log_file'):
            self._log_file.close()
            del self._log_file

    def consume_event(self, type=None, **data) -> None:
        """
        Consumes the incoming event from the EventsManager
        """

        assert hasattr(self, '_log_file')
        assert self._log_file != None

        message = '[%s]' % type
        parts = []
        for data_key, data_value in data.items():
            parts.append('%s: %s' % (data_key, data_value))

        message = '%s (%s)\n' % (message, ', '.join(parts))
        self.notify.debug('Logging Event: %s' % message)
        self._log_file.write(message)

class EventsManager(Singleton, InternalObject):
    """
    Handles all events in the Gemstone framework
    """

    def __init__(self):
        Singleton.__init__(self)
        InternalObject.__init__(self)
        self.notify.setInfo(True)
        self.__handlers = []
        self.add_handler(ConsoleEventHandler())

    def destroy(self) -> None:
        """
        Called on the destruction of the events manager
        """

        Singleton.destroy(self)
        InternalObject.destroy(self)

    def add_handler(self, handler: EventHandler) -> bool:
        """
        Adds a new event handler to the EventsManager. Returning True on success
        """

        if handler in self.__handlers:
            self.notify.warning('Failed to add event handler %s. Handler already exists in EventsManager' % (
                handler.__class__.__name__))

            return False

        self.notify.info('Registering event handler: %s' % handler.__class__.__name__)
        self.__handlers.append(handler)

        return True

    def consume_event(self, type=None, **data) -> None:
        """
        Consumes an application event and routes it to the available handlers
        """

        # Verify we have handlers present
        if not len(self.__handlers):
            self.notify.warning('Failed to consume %s event. No handlers registered!' % type)
            return

        for handler in self.__handlers:
            handler.consume_event(type, **data)

def log_event(type='GenericEvent', **data) -> None:
    """
    Logs an application event with the EventsManager instance
    """

    em = EventsManager.get_singleton()
    if not em:
        return
    
    em.consume_event(type, **data)

def add_event_handler(*args, **kwargs) -> bool:
    """
    Adds an event handler to the EventsManager singleton. Returns
    true if the operation was a success
    """

    em = EventsManager.get_singleton()
    if not em:
        return False

    return em.add_handler(*args, **kwargs)

    
