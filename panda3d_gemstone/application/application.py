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

from panda3d_gemstone.io.file_system import path_exists
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.service import Service, Command, ServiceManager
from panda3d_gemstone.framework.utilities import save_screenshot, start_background_thread
from panda3d_gemstone.framework.utilities import print_refcounts, print_unreachable_garbage
from panda3d_gemstone.framework.resource import ResourceManager

from panda3d_gemstone.engine.performance import toggle_profiling
from panda3d_gemstone.engine.showbase import ApplicationShowBase
from panda3d_gemstone.engine import runtime
from panda3d_gemstone.engine.http import HTTPManager
from panda3d_gemstone.engine import prc

from panda3d_gemstone.logging import utilities as _logging
from panda3d_gemstone.logging import handler as _logging_handler

from panda3d_gemstone.application.version import ApplicationVersion
from panda3d_gemstone.application import constants
from panda3d_gemstone.application.events import log_event

from panda3d.core import ConfigVariableString, WindowProperties, AntialiasAttrib

def get_home_directory() -> str:
    """
    Returns the applications current home directory
    """

    result = None
    if sys.platform == 'win32':
        result = '.%s' % os.sep
    elif sys.platform == 'darwin':
        if 'HOME' in os.environ:
            result = '%s%s' % (os.environ['HOME'], os.sep)
    else:
        result = '.%s' % os.sep

    return result

class EngineApplication(Service):
    """
    Base class for all Gemstone applications
    """

    def __init__(self):
        super().__init__()

        if runtime.is_interactive():
            print('WARNING: Running from interactive prompt. Complete compatibility is not guaranteed')

    def get_application_version(self) -> str:
        """
        Returns the application version.
        """

        return str(ApplicationVersion.instantiate_singleton())

    def get_application_name(self) -> str:
        """
        Returns the application's name. Intended to be 
        overridden by child objects
        """

        raise NotImplementedError('%s does not implement get_application_name' % self.__class__.__name__)

    def __has_panda_notify(self) -> bool:
        """
        Returns true if the object has a Panda3D notifier
        object
        """

        notify = 'notify'
        found = False
        has_attr = hasattr(self, notify)
        attr = getattr(self, notify)
        if has_attr and attr != None:
            found = not callable(attr)
        
        return found

    def __log_info(self, message: str) -> None:
        """
        Logs an info message to console if notify is available
        otherwise logs through print
        """

        has_notify = self.__has_panda_notify()
        if not has_notify:
            print(message)
        else:
            self.notify.info(message)

    def setup(self) -> None:
        """
        Performs setup operations on the application instance
        """

        self.activate()

    def destroy(self) -> None:
        """
        Performs destruction operations on the application instance
        """

        self.__log_info('Shutting down %s...' % self.get_application_name())
        self.deactivate()

    def quit(self, code: int = 0) -> None:
        """
        Exits the application with the requested code
        """

        print('Exiting with code: %d' % code)
        sys.exit(code)

class GemstoneApplication(EngineApplication, InternalObject):
    """
    Base class for all GemStone Panda3D Applications
    """

    PRC_FILES = []
    CONTROL_MAPPING = ''
    SHOWBASE_CLS = ApplicationShowBase

    def __init__(self, window_type: str = None, showbase_cls: object = None):
        EngineApplication.__init__(self)
        InternalObject.__init__(self)
        self.set_skip_export(prc.get_prc_bool('gs-skip-export', False))
        if runtime.has_application():
            raise Exception('Attempting to spawn more then one Gemstone Panda3D application instance')
        runtime.application = self
        self.load_prc_files(self.PRC_FILES)

        self.__base = None
        self.__http = None
        self.__showbase_cls = showbase_cls or self.SHOWBASE_CLS
        self.__window_type = window_type

        self.before_panda3d_setup()
        self.__setup_panda3d()
        self.post_panda3d_setup()

        if prc.get_prc_bool('gs-background-thread', True):
            start_background_thread()

        self.__load_control_mapping(self.CONTROL_MAPPING or prc.get_prc_string('gs-control-map', ''))

        self.add_command(Command('save screenshot', save_screenshot))
        self.add_command(Command('quit', self.quit))

    @property
    def base(self) -> ApplicationShowBase:
        """
        Applications showbase instance
        """

        return self.__base

    @property
    def http(self) -> HTTPManager:
        """
        Applications HTTPManager instance
        """

        return self.__http

    @property
    def window(self) -> object:
        """
        Applications main window instance
        """

        if not self.__base:
            return None

        return self.__base.win

    def load_prc_files(self, files: list, optional: bool = False) -> None:
        """
        Attempts to load a list of prc files
        """

        if not len(files):
            return

        for prc_file in files:
            prc.load_prc_file(prc_file, optional)

    def before_panda3d_setup(self) -> None:
        """
        Called before setting up the Panda3D game engine
        """

        prc.load_prc_file_data('gemstone', constants.GEMSTONE_PRC)

    def __setup_panda3d(self) -> None:
        """
        Performs Panda3d engine setup operations
        """

        # Initialize showbase
        self.notify.info('Setting up engine...')
        assert self.__showbase_cls != None
        self.__showbase_cls.notify = _logging.get_notify_category('showbase')
        self.__base = self.__showbase_cls(windowType=self.__window_type)
        self.__base.set_exit_callback(self.destroy)

        runtime.window = self.__base.win
        runtime.task_mgr = self.__base.task_mgr
        runtime.camera = self.__base.camera
        self.setup_window()

    def post_panda3d_setup(self) -> None:
        """
        Called after setting up the Panda3D game engine
        """

        # Replace IO access
        self.notify.info('Setting up environment...')
        from panda3d_gemstone.io import file_system
        file_system.switch_file_functions_to_vfs()

        # Setup singletons
        self.__http = HTTPManager.instantiate_singleton()
        runtime.http = self.__http

        self._logger = _logging_handler.ApplicationLogger.get_singleton()
        if self._logger:
            runtime.logger = self._logger

    def setup(self) -> None:
        """
        Performs setup operations on the application instance
        """

        EngineApplication.setup(self)

        # Log the application and version      
        self.notify.info('Starting (%s) %s - %s' % (
            self.__class__.__name__,
            self.get_application_name(),
            self.get_application_version()))

    def destroy(self) -> None:
        """
        Performs destruction operations on the application instance
        """

        EngineApplication.destroy(self)
        InternalObject.destroy(self)

    def run(self) -> None:
        """
        Runs the Geomstone application
        """

        self.base.run()

    def setup_window(self) -> None:
        """
        Performs window setup operations
        """

        self.notify.info('Performing window setup.')
        window_title = self.get_window_label()
        self.__base.set_window_title(window_title)

    def get_window_label(self) -> str:
        """
        Returns the applications window title label
        """

        return '%s - %s' % (
            self.get_application_name(),
            self.get_application_version())

    def __load_control_mapping(self, filename: str) -> None:
        """
        Loads a control map into the service manager
        """

        if not filename:
            return

        ServiceManager.get_singleton().load(filename)

    def set_skip_export(self, state: bool) -> None:
        """
        Sets the resource manager's skip export state
        """

        ResourceManager.get_singleton().set_skip_export(state)

    def get_application_name(self) -> str:
        """
        Returns the application's name. 
        """

        return ConfigVariableString('app-name', 'Gemstone Application').value
 
class HeadlessGemstoneApplication(GemstoneApplication):
    """
    Headless variant of the Panda3D Gemstone framework application
    """

    def __init__(self, *args, **kwargs):
        kwargs['window_type'] = 'none'
        super().__init__(*args, **kwargs)

class ServerGemstoneApplication(HeadlessGemstoneApplication):
    """
    Variant of the headless Panda3D Gemstone framework application
    for use in server applications
    """

    def get_public_ip(self, callback: object) -> None:
        """
        Returns the server application's public ip address
        """

        assert callback != None
        assert callable(callback)

        def wrapper(data):
            """
            Wrapper to break out the callback data
            """

            ip = data.geT('ip', 'unknown')
            callback(ip)

        url = 'https://api.ipify.org/?format=json'
        self.http.perform_json_get_Request(url, callback=wrapper)
