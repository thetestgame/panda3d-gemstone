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

from panda3d_gemstone.framework.exceptions import verify_thirdparty_modules
verify_thirdparty_modules(['watchdog', 'limeade'])

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.utilities import disallow_production
from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.engine import prc, runtime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import traceback
import limeade

class ReloaderFileEventHandler(FileSystemEventHandler):
    """
    Custom FileSystemEventHandler instance for performing os file watch tasks
    for the ApplicationReloader instance
    """

    def __init__(self, reloader: object, callback: object):
        assert callable(callback)
        self.__reloader = reloader
        self.__callback = callback
        super().__init__()

    def __is_valid_file(self, file_path: str) -> bool:
        """
        Returns true if the file path relates to a file type we are listening
        for. Otherwise returns False
        """

        valid = False
        for file_type in list(self.__reloader.watched_types):
            if file_path.endswith('.%s' % file_type):
                valid = True
                break

        return valid

    def on_any_event(self, event: object) -> None:
        """
        Handles all incoming events from the watchdog module and checks
        if the event relates to a file we care about before firing the 
        requested callback provided by the ApplicationReloader instance
        """

        changed_path = event.src_path
        if self.__is_valid_file(changed_path):
            ext = changed_path.split('.')[-1]
            self.__callback(changed_path, ext) 

class ApplicationReloader(Singleton, InternalObject):
    """
    Development utility object for hot reloading a Gemstone application
    when a file change is detected.
    """

    def __init__(self):
        Singleton.__init__(self)
        InternalObject.__init__(self)
        self.notify.setInfo(True)
        self.__watched_types = prc.get_prc_list('gs-reload-type')
        self.__watch_path = prc.get_prc_string('gs-reload-watch-path', '.')
        self.__reloaded = False
        self.__observer = None
        self.__setup_watchdog()
    
    @property
    def watched_types(self) -> list:
        """
        ApplicationReloader's currently watched file extensions
        """

        return self.__watched_types

    def add_watch_type(self, ext: str) -> bool:
        """
        Attempts to add a new file watch type to the reloader.
        Returning True if the type was added succesfully. Otherwise
        returning False
        """

        if ext in self.__watched_types:
            self.notify.warning('Attempted to add already registered watch type: %s' % ext)
            return False

        self.__watched_types.append(ext)
        return True

    def remove_watch_type(self, ext: str) -> None:
        """
        Attempts to remove the watch type from the reloader.
        """

        if not ext in self.__watched_types:
            return

        self.__watched_types.remove(ext)

    def destroy(self) -> None:
        """
        Destroys the ApplicationReloader instance
        """

        self.deactivate()
        Singleton.destroy(self)
        PandaBaseObject.destroy(self)

    def activate(self) -> None:
        """
        Activates the ApplicationReloader instance
        """

        # Verify we are valid
        if not self.is_valid():
            self.notify.warning('Failed to activate %s. Invalid configuration detected.' % (
                self.__class__.__name__))

        if self.__observer:
            self.__observer.start()

    def deactivate(self) -> None:
        """
        Deactivates the ApplicationReloader instance
        """

        if self.__observer:
            self.__observer.stop()

    def has_reloaded(self) -> bool:
        """
        Returns true if the application has reloaded to log any potential
        instabilities caused by the reload.
        """

        return self.__reloaded

    def is_valid(self) -> bool:
        """
        Returns true if the application reloader has a valid
        configuration
        """

        return len(self.__watched_types) > 0
    
    @disallow_production
    def send_event(self, file_path: str, ext: str) -> None:
        """
        Broadcasts a Panda Messenger event to notify other components
        that a file has changed
        """

        runtime.messenger.send('gs-file-changed', [file_path, ext])

    @disallow_production
    def on_reload(self, file_path: str, ext: str) -> None:
        """
        Default on reload handler
        """

        self.notify.info('Detecting file change: %s' % file_path)

    @disallow_production
    def on_py_reload(self, file_path: str) -> None:
        """
        Handles Python file reload events
        """

        self.notify.info('Detecting source change in file: %s. Reloading' % (
            file_path))

        # Attempt to reload source. Catching any potential errors
        # that occure during reload
        try:
            limeade.refresh()
        except Exception as e:
            print('== An Error Occured Reloading Source ==')
            print(traceback.format_exc())

    @disallow_production
    def __on_file_changed(self, file_path: str, ext: str) -> None:
        """
        Called when a file change is detected
        """

        # Attempt to call handler if present
        handler_name = 'on_%s_reload' % ext
        has_handler = hasattr(self, handler_name)
        if has_handler:
            getattr(self, handler_name)(file_path)
        else:
            self.on_reload(file_path, ext)

        # Flag that we have reloaded
        if not self.__reloaded:
            self.__reloaded = True

        # Send application wide event
        self.send_event(file_path, ext)

    @disallow_production
    def __setup_watchdog(self) -> None:
        """
        Performs Watchdog setup operations
        """

        event_handler = ReloaderFileEventHandler(
            reloader=self,
            callback=self.__on_file_changed)
        self.__observer = Observer()
        self.__observer.schedule(event_handler, self.__watch_path, recursive=True)
