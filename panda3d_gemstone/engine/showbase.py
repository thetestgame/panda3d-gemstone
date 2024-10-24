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

import builtins

from direct.showbase.ShowBase import ShowBase

from panda3d_gemstone.framework.service import Service, Command
from panda3d_gemstone.logging import utilities as logging
from panda3d_gemstone.engine import runtime, prc

from panda3d.core import WindowProperties, AntialiasAttrib

class GemstoneShowBase(Service, ShowBase):
    """
    Custom Gemstone framework varient of the stock
    Panda3D ShowBase object
    """ 

    def __init__(self, *args, **kwargs):
        Service.__init__(self, initialize_handle_attributes_as_commands=False)
        ShowBase.__init__(self, *args, **kwargs)

        self.config = prc.ShowbaseConfig()
        builtins.config = self.config
        runtime.config = self.config

    def setup(self) -> None:
        """
        Performs setup operations on the showbase instance
        """

    def destroy(self) -> None:
        """
        Performs destruction operations on the showbase instance
        """

        Service.destroy(self)
        ShowBase.destroy(self)

    def set_exit_callback(self, func: object) -> None:
        """
        Sets the showbase's shutdown callback
        """

        assert func != None
        assert callable(func)

        self.exitFunc = func

class ApplicationShowBase(GemstoneShowBase):
    """
    Standard ShowBase instance for the Gemstone framework.
    Used by most application use cases
    """

    notify = logging.get_notify_category('showbase')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup()

        self.set_antialias(prc.get_prc_bool('gs-panda-antialias', True))
        self.__showing_frame_rate = prc.get_prc_bool('show-frame-rate-meter', False)

        self.add_command(Command('toggle frame rate', self.toggle_frame_rate))

    def setup(self) -> None:
        """
        Performs setup operations on the showbase instance
        """

        super().setup()

        self.__setup_runtime()

    def destroy(self) -> None:
        """
        Performs destruction operations on the showbase instance
        """

        super().destroy()

    def __setup_runtime(self) -> None:
        """
        Performs runtime variable setup operations
        """

        runtime.base = self
        runtime.task_mgr = self.task_mgr
        runtime.loader = self.loader
        runtime.cam = self.cam
        runtime.camera = self.camera
    
    def set_window_title(self, window_title: str) -> None:
        """
        Sets the primary window's title
        """

        # Verify we have a window instance
        if not self.win:
            return

        props = WindowProperties()
        props.set_title(window_title)
        self.win.request_properties(props)

    def set_window_dimensions(self, origin: tuple, size: tuple) -> None:
        """
        Sets the current window dimensions
        """

        if not self.win:
            return

        props = WindowProperties()
        props.set_origin(*origin)
        props.set_size(*size)
        self.win.request_properties(props)

    def get_window_dimensions(self) -> tuple:
        """
        Returns the current windows dimensions
        """

        origin = (-1, -1)
        size = (-1, -1)

        if not self.win:
            return (origin, size)

        props = self.win.get_properties()
        if sys.platform == 'darwin':
            origin = (25, 50)
        elif props.has_origin():
            origin = (props.get_x_origin(), props.get_y_origin())
        
        if props.has_size():
            size = (props.get_x_size(), props.get_y_size())

        return (origin, size)

    def set_clear_color(self, clear_color: object) -> None:
        """
        Sets the primary window's clear color
        """

        # Verify we have a window instance
        if not self.win:
            return

        self.win.set_clear_color(clear_color)

    def set_antialias(self, antialias: bool) -> None:
        """
        Sets the graphics library based antialiasing state
        """

        if not prc.get_prc_bool('framebuffer-mutlisample', False):
            prc.set_prc_value('framebuffer-multisample', True)

        if prc.get_prc_int('multisamples', 0) < 2:
            self.notify.warning('Multisamples not set. Defaulting to a value of 2')
            prc.set_prc_value('multisamples', 2)

        if antialias:
            self.render.set_antialias(AntialiasAttrib.MAuto)
        else:
            self.render.clear_antialias()

    def post_window_setup(self) -> None:
        """
        Performs setup operations after the window has succesfully
        opened
        """

    def open_default_window(self) -> object:
        """
        Opens a window with the default configuration
        options
        """

        props = WindowProperties.get_default()
        return self.openMainWindow(props = props)

    def openMainWindow(self, *args, **kwargs) -> object:
        """
        Custom override of the ShowBase openMainWindow function
        for handling runtime registering
        """

        result = ShowBase.openMainWindow(self, *args, **kwargs)

        if result:
            runtime.window = self.win
            runtime.render = self.render

            self.post_window_setup()

        return self.win

    def toggle_frame_rate(self) -> None:
        """
        Toggles the application's frame rate meter
        """

        self.__showing_frame_rate = not self.__showing_frame_rate
        self.set_frame_rate_meter(self.__showing_frame_rate)

    def is_oobe(self) -> bool:
        """
        Returns true if the ShowBase instance is in oobe mode
        """

        if not hasattr(self, 'oobeMode'):
            return False

        return self.oobeMode

class HeadlessApplicationShowbase(ApplicationShowBase):
    """
    Headless varient of the ApplicationShowBase object. Creates
    without a primary window instance
    """

    def __init__(self, *args, **kwargs):
        kwargs['window_type'] = 'none'
        super().__init__(*args, **kwargs)