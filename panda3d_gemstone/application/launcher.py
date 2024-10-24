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
import base64
import traceback
from collections import defaultdict

from panda3d_gemstone.engine import runtime, prc
from panda3d_gemstone.framework.internal_object import InternalObject

class LauncherExitCodes(object):
    """
    Contains all possible exit codes for the 
    Geomstone launcher
    """

    SUCCESS = 0
    FAILED_STARTUP_CHECK = 1
    INTERNAL_ERROR = 2

class GemstoneLauncher(InternalObject):
    """
    Base class for all Geomstone launchers
    """

    APPLICATION_CLS = None

    def __init__(self, application_cls: object = None):
        self._application_cls = application_cls or self.APPLICATION_CLS
        assert self._application_cls != None
        super().__init__()
        self.exit_code = 0
        runtime.launcher = self

        self.__application = None
        self._launch_arguments = defaultdict(list)
        self.__parse_command_line()

    @property
    def application(self) -> object:
        """
        Launchers current application instance
        """

        return self.get_application()

    def get_application(self) -> object:
        """
        Returns the launcher's current application instance
        """

        return self.__application

    def get_environment_variable(self, key: str, default: str) -> str:
        """
        Returns the environment variable defined at the time of launch if present.
        Otherwise returns the value of default
        """

        return os.environ.get(key, default)

    def has_launch_arg(self, key: str) -> bool:
        """
        Returns true if the launch argument key was present at the time
        of launch via command line
        """

        return self.get_launch_arg(key, None) != None

    def get_launch_arg(self, key: str, default: str) -> str:
        """
        Retrieves a command line launch argument if present.
        Otherwise returns default
        """

        value = self._launch_arguments.get(key, default)
        if isinstance(value, list):
            if len(value) > 0:
                return value[0]

        return value

    def get_encoded_launch_arg(self, key: str, default: str, bypass: bool=True) -> str:
        """
        Retrieves an encoded command line launch argument if present.
        Otherwise returns default
        """

        value = self.get_launch_arg(key, default)
        result = None
        try:
            decoded = base64.b64decode(value)
            result = decoded.decode('utf-8')
        except:
            pass

        if bypass and runtime.is_developer_build():
            result = value

        return result

    def set_development_launch(self) -> None:
        """
        Flags the current application launch as a development 
        launch. Must be performed before starting the application
        """

        if runtime.has_base():
            self.notify.warning('Failed to set as development launch. Application already started')
            return 

        self.notify.warning('Launching as a development build of the Gemstone application (%s)' % self._application_cls.__name__)
        prc.load_prc_file_data('want-dev #t')
        runtime.dev = True

    def __parse_command_line(self) -> None:
        """
        Parses the output of the command line arguments
        """

        self.notify.debug('Parsing command line arguments')
        for k, v in ((k.lstrip('-'), v) for k,v in (a.split('=') for a in sys.argv[1:])):
            self._launch_arguments[k].append(v)

    def attempt_start(self) -> None:
        """
        Attempts to start the Geomstone application
        """

        # Verify we can start
        if not self.can_start():
            self.exit_code = LauncherExitCodes.FAILED_STARTUP_CHECK
            return
        
        self.launch()

    def can_start(self) -> bool:
        """
        Returns true when the launcher can start. Intended to be overriden by 
        a child launcher object
        """

        raise NotImplementedError('%s does not implement can_start!' % self.__class__.__name__)

    def launch(self) -> None:
        """
        Launches the gemstone application
        """

        if runtime.has_application():
            self.notify.warning('Failed to launch application. An application is already running!')
            return

        try:
            self.__application = self._application_cls()
            self.__application.setup()
            self.__application.run()
        except SystemExit:
            pass
        except Exception as e:
            self.exit_code = LauncherExitCodes.INTERNAL_ERROR
            exe_cls, exe, tb = sys.exc_info()
            print('An unexpected error has occured. %s (%s)' % (str(exe), exe_cls.__name__))
            if runtime.is_developer_build():
                print(traceback.format_exc())
            
            self.handle_application_error(exe_cls, exe, traceback.format_exc())

    def handle_application_error(self, error_cls: object, error: Exception, traceback: object) -> None:
        """
        Called when the application encounters an error for custom
        launcher processing
        """

    def start(self) -> int:
        """
        Starts the application launch process
        """

        self.attempt_start()
        self.destroy()

        return self.exit_code

class DeveloperLauncher(GemstoneLauncher):
    """
    Basic developer launcher that will always launch immediately and permits hot reloads
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notify.setInfo(True)
        self.set_development_launch()

    def can_start(self) -> bool:
        """
        Returns true when the launcher can start. Intended to be overriden by 
        a child launcher object
        """

        return True
    
def application_main(launcher_cls: object) -> int:
    """
    Handler to process the startup of a Gemstone application
    """

    assert launcher_cls != None
    launcher = launcher_cls()
    launcher.start()

    return launcher.exit_code
