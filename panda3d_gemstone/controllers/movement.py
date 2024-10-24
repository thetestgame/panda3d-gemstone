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

from panda3d_gemstone.framework.controller import Controller, ControllerService
from panda3d_gemstone.framework.service import State

from panda3d.core import Vec3

class FollowController(ControllerService):
    """
    """

    def __init__(self, config_path: str, next_controller: object = None, section: str = None):
        self.__fixed_direction = None
        self.__position_offset = Vec3(0, 25, 7)
        self.__look_at_offset = Vec3(0, 2.5, 5)
        self.__look_at_offset_zoom0 = None
        self.__zoom = 0.0
        self.__zoom_factor = 1.2
        self.__zoom_minimum = 0.0
        self.__zoom_maximum = 0.0

        super().__init__(config_path, next_controller, section)
        self.addCommand(State('zoom in', False))
        self.addCommand(State('zoom out', False))

    def set_fixed_direction(self, direction: object) -> None:
        """
        Sets the controllers fixed direction
        """

        self.__fixed_direction = direction

    def get_fixed_direction(self) -> object:
        """
        Returns the controller's fixed direction
        """

        return self.__fixed_direction 

    

    
