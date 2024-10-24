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

from panda3d_gemstone.framework.registry import ClassRegistryMixIn
from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework import utilities
from panda3d_gemstone.framework.service import Service, Command

from panda3d_gemstone.logging.utilities import get_notify_category

from panda3d.core import NodePath

__controller_notify = get_notify_category('controller')

class Controller(Configurable, InternalObject):
    """
    Base class for all controllers in the Geomstone framework
    """

    def __init__(self, config_path: str, next_controller: object = None, section = None):
        Configurable.__init__(self, config_path, section or self.__class__.__name__)
        InternalObject.__init__(self)

        self.next_controller = next_controller
        self.moved = False
        self.turned = False
        self.update_nodepath = NodePath('')
        self.initialize()

    @property
    def changed(self) -> bool:
        """
        Value is true if the controller has changed
        """

        return self.has_changed()
    
    def destroy(self) -> None:
        """
        Called on the destruction of the controller object
        """

        self.next_controller = None
        self.update_nodepath.remove_node()
        self.update_nodepath = None

    def set_next_controller(self, next_controller: object) -> None:
        """
        """

        self.next_controller = next_controller

    def get_next_controller(self,) -> object:
        """
        """

        return self.next_controller

    def has_moved(self) -> bool:
        """
        Returns true if the controller has moved
        """

        return self.moved

    def has_turned(self) -> bool:
        """
        Returns true if the controller has turned
        """

        return self.turned

    def has_changed(self) -> bool:
        """
        Returns true if the controller has changed
        """

        return self.moved or self.turned

    def walk_controller_chain(self, ignore_self: bool = False) -> None:
        """
        """

        if ignore_self:
            controller = self.get_next_controller()
        else:
            controller = self

        while controller:
            yield controller
            controller = controller.get_next_controller()

    def foreach_get(self, attr: object) -> list:
        """
        """

        values = []
        for controller in self.walk_controller_chain():
            values.append(getattr(controller, attr, None))

        return values

    def foreach_call(self, method: object, *args, **kwargs) -> list:
        """
        """

        return utilities.foreach_call_method_by_name(self.walk_controller_chain(False), method, *args, **kwargs)

    def _foreach_call_others(self, method: object, *args, **kwargs) -> list:
        """
        """

        return utilities.foreach_call_method_by_name(self.walk_controller_chain(True), method, *args, **kwargs)

    async def update_node(self, nodepath: object, dt: float) -> object:
        """
        """

        return nodepath

    async def forward_node(self, nodepath: object, dt: float) -> object:
        """
        """

        return await self.next_controller.update(nodepath, dt)

    async def update(self, nodepath: object, dt: float) -> object:
        """
        """

        prev_direction = nodepath.get_quat()
        prev_position = nodepath.get_pos()

        new_nodepath = self.update_nodepath
        new_nodepath.set_mat(nodepath.get_mat())
        new_nodepath = await self.update_node(new_nodepath, dt)

        if self.next_controller:
            new_nodepath = await self.forward_node(new_nodepath, dt)

        direction = new_nodepath.get_quat()
        position = new_nodepath.get_pos()

        self.moved = not position.almost_equal(prev_position)
        self.turned = not direction.almost_equal(prev_direction)

        return new_nodepath

class ControllerChainMixIn(ClassRegistryMixIn):
    """
    """

    def call_controller_chain(self, controller_chain: object, function_name: object, *args, **kwargs) -> object:
        """
        """

        if controller_chain:
            return controller_chain.foreach_call(function_name, *argsm **kwargs)

    def setup_controller_chain(self, controller_chain_str: str, config_path: str) -> object:
        """
        """

        first_controller = None

        if controller_chain_str:
            controller_chain = [ c.strip() for c in controller_chain_str.split(' ') ]
            controller_chain.reverse()
            for controller_name in controller_chain:
                cls = self._get_class(controller_name + 'Controller')
                setup = self._get_class_meta(controller_name + 'Controller', 'Controller.setup')
                if cls:
                    first_controller = cls(config_path, next_controller=first_controller)
                    if setup:
                        setup(first_controller, self)
                else:
                    __controller_notify.error("Failed to setup controller '%s' (%s). Class not found" % (controller_name, self.__class__.__name__))
                    return

        return first_controller

    def find_controller(self, controller_chain: object, cls_or_name: object, as_list: bool = False) -> object:
        """
        """

        controller = []
        while controller_chain:
            if isinstance(cls_or_name, str):
                if controller_chain.section == cls_or_name:
                    controller.append(controller_chain)
            elif isinstance(controller_chain, cls_or_name):
                if isinstance(controller_chain, cls_or_name):
                    controller.append(controller_chain)
            controller_chain = controller_chain.get_next_controller()

        if as_list or len(controller) > 1:
            return controller
        elif len(controller) == 1:
            return controller[0]

        return None

class ControllerService(Controller, Service):
    """
    Base class for all controllers who also serve as a Gemstone
    framework Service object for registering commands
    """

    def __init__(self, *args, **kwargs):
        Service.__init__(self)
        Controller.__init__(self, *args, **kwargs)
