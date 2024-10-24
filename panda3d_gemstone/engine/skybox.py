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

from panda3d_gemstone.engine import runtime, shader
from panda3d_gemstone.engine.model import StaticModel

from panda3d_gemstone.framework.runnable import Runnable


class Skybox(StaticModel, Runnable):
    """
    Base class for all skybox models
    """

    def __init__(self, config_path: str):
        StaticModel.__init__(self, config_path)
        Runnable.__init__(self, 15)
        
        self.set_bin('background', 0)
        self.set_depth_test(False)
        self.set_compass()
        self.activate()

    def set_lights_enabled(self, state: bool) -> None:
        """
        Sets the lights enable state of the SkyBox
        """

        if not state:
            self.set_light_off()

    def activate(self) -> None:
        """
        Custom activate handle to control the clear color active 
        state with the Panda3D game window
        """

        active = Runnable.activate(self)
        if active and runtime.base.win:
            runtime.base.win.set_clear_color_active(False)

    def deactivate(self) -> None:
        """
        Custom deactivate handle to control the clear color active 
        state with the Panda3D game window
        """

        active = Runnable.deactivate(self)
        if active and runtime.base.win:
            runtime.base.win.set_clear_color_active(True)

    async def tick(self, dt: float) -> int:
        """
        Custom tick handler. Updates the position of the skybox to match
        the position of the users camera
        """

        camera = runtime.camera
        if runtime.base.is_oobe():
            camera = runtime.base.oobeCamera
        self.set_pos(camera.get_pos(self.get_parent()))