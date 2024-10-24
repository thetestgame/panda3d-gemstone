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

import logging

from panda3d_gemstone.engine import runtime
from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.runnable import Runnable

from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import Vec3

class PhysicsEngine(Singleton, Runnable):
    """
    Singleton representing bullet physics in the panda3d game 
    engine.
    """

    def __init__(self):
        Runnable.__init__(self)
        Singleton.__init__(self)

        self.__world = None
        self.__debug_node = None
        self.__debug_node_np = None
        self.setup()

    @property
    def debug_mode(self) -> bool:
        """
        Returns true when the physics engine has the debug node
        enabled
        """

        return self.__debug_node != None

    @property
    def physics_world(self) -> BulletWorld:
        """
        Returns this physics engines bullet world instance
        """

        return self.__world

    @property
    def gravity(self) -> Vec3:
        """
        Returns this physics engines current gravity configuration
        as a property
        """

        return self.get_gravity()

    @gravity.setter
    def gravity(self, gravity: Vec3) -> None:
        """
        Sets this physics engines current gravity as a setter
        """

        self.set_gravity(gravity)

    def setup(self) -> None:
        """
        Performs setup operations on the singleton
        """

        self.__world = BulletWorld()
        self.set_gravity(Vec3(0, 0, -9.81))
        self.activate()

    def destroy(self) -> None:
        """
        Performs shutdown operations on the singleton
        """

        # Remove debug node if present
        if self.__debug_node:
            self.__debug_node.remove_node()

        # Deactivate runnable
        self.deactivate()

    def toggle_debug(self) -> None:
        """
        Toggles the current debug state
        """

        assert self.__world != None
        if self.debug_mode:
            self.__world.set_debug_node(None)
            self.__debug_node_np.remove_node()
        else:
            self.__debug_node = BulletDebugNode('%s-Debug' % self.__class__.__name__)
            self.__debug_node_np = runtime.render.attach_new_node(self.__debug_node)
            self.__debug_node_np.show()
            self.__world.set_debug_node(self.__debug_node)

    async def tick(self, dt: float) -> None:
        """
        Called once per frame to perform physics world updates
        """

        if not self.__world:
            return

        self.__world.do_physics(dt, 10, 1.0/180.0)

    def __getattr__(self, key: str) -> object:
        """
        Custom attribute getter to pass through unknown attributes
        to the physics world instance
        """

        result = None
        if self.__world != None:
            if hasattr(self.__world, key):
                result = getattr(self.__world, key)
        
        if not result:
            raise AttributeError('%s instance does not have attribute %s' % (
                self.__class__.__name__, key))

        return result