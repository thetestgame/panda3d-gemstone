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

from panda3d_gemstone.framework.controller import Controller
from panda3d.core import Vec3, Point3

class FixedController(Controller):
    """
    """

    def __init__(self, config_path: str, next_controller: object = None, section: str = None):
        self.__position = Vec3(0, 0, 50)
        self.__look_at_offset = Vec3(0, 0, 0)
        self.__follow_mode = False
        self.__target = None
        Controller.__init__(self, config_path, next_controller, section or 'Fixed')

    def set_position(self, position: Vec3) -> None:
        """
        """
        self.__position = position

    def get_position(self) -> Vec3:
        """
        """

        return self.__position

    def set_look_at_offset(self, look_at_offset: Vec3) -> None:
        """
        """

        self.__look_at_offset = look_at_offset

    def get_look_at_offset(self) -> Vec3:
        """
        """

        return self.__look_at_offset

    def set_follow_mode(self, follow: bool) -> None:
        """
        """

        self.__follow_mode = follow

    def get_follow_mode(self) -> bool:
        """
        """

        return self.__follow_mode

    def set_target(self, target: object) -> None:
        """
        """

        self.__target = target

    def get_target(self) -> object:
        """
        """

        return self.__target

    async def update(self, nodepath: object, dt: float) -> object:
        """
        """

        nodepath.set_pos(self.__position)
        if self.__target and self.__follow_mode:
            if hasattr(self.__target, '__getitem__'):
                look_at = Point3(self.__target[0], self.__target[1], self.__target[2])
            else:
                look_at = Point3(self.__target.getX(), self.__target.getY(), self.__target.getZ())
        else:
            look_at = Point3(0, 0, 0)


        nodepath.look_at(look_at + self.__look_at_offset, Vec3(0, 0, 1))
        return nodepath
