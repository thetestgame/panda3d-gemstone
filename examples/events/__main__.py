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

from panda3d_gemstone.application import launcher, application
from panda3d_gemstone.framework.service import ServiceManager, Command
from panda3d_gemstone.engine import prc

EXAMPLE_PRC = """
gs-v-major 0
gs-v-minor 0
gs-v-release 1
"""

class EventsApplication(application.GemstoneApplication):
    """
    Gemstone application instance for the events example
    application
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(Command('print-hello', self.print_hello_world))

    def before_panda3d_setup(self) -> None:
        """
        Called before setting up the Panda3D game engine
        """

        super().before_panda3d_setup()
        prc.load_prc_file_data(EXAMPLE_PRC, 'example')

        service_mgr = ServiceManager.get_singleton()
        service_mgr.register_event('f8', self.get_service_name(), 'print-hello')
        ServiceManager.analyze_services()

    def print_hello_world(self) -> None:
        """
        Prints hello world to console when the print-hello command is sent
        """

        print('Hello World!')

    def get_application_name(self) -> str:
        """
        Returns the application's name. 
        """

        return 'Gemstone Example - Events'

class EventsLauncher(launcher.DeveloperLauncher):
    """
    Variant of the developer launcher to launch the demo 
    instantly
    """

    APPLICATION_CLS = EventsApplication

# Main entry point for the application
if __name__ == '__main__':
    sys.exit(launcher.application_main(EventsLauncher))