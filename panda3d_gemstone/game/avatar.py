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

from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.runnable import Runnable
from panda3d_gemstone.framework.controller import ControllerChainMixIn
from panda3d_gemstone.controllers.avatar import AvatarController
from panda3d_gemstone.engine.model import AnimatedModel


class Avatar(AnimatedModel, Configurable, Runnable, ControllerChainMixIn):
    """
    Represents an avatar in the Gemstone framework
    """

    def __init__(self, config_path: str):
        Configurable.__init__(self, config_path)
        self.controller = None
        name = self.pop('name')
        self.__setup_model_path_and_controller()
        AnimatedModel.__init__(self, self.model_path, have_anim_in_node=False)
        if name:
            self.set_name(name)

        Runnable.__init__(self, priority=5)

    def destroy(self) -> None:
        """
        Called on avatar destruction
        """

        if self.controller:
            self.controller.destroy()
        self.controller = None

        self.deactive()
        AnimatedModel.destroy(self)

    def make_copy_to(self, destination: object, copy_controller_chain: bool = True, callback: object = None, extra_args: list = [], task_chain_name: str = None) -> None:
        """
        """

        super(AnimatedModel, self).make_copy_to(destination, callback=callback, extra_args=extra_args, task_chain_name=task_chain_name)
        destination.set_name(self.get_name())
        destination.model_path = self.model_path

        if copy_controller_chain:
            destination.__setup_model_path_and_controller()

    def configure_controller(self, config_path: str = None) -> None:
        """
        """

        if config_path is None:
            config_path = self.path

        configuration = Configurable(config_path)
        controller = self.setup_controller_chain(configuration.pop('controller'), config_path)

        if isinstance(controller, AvatarController) or controller is None:
            self.controller = controller
        else:
            self.notify.warning('Failed to configure controller: %s does not inherit AvatarController!' % controller.__class__.__name__)
            self.controller = None

    def __setup_model_path_and_controller(self) -> None:
        """
        """

        self.model_path = self.pop('model')
        self.configure_controller()
        self.pop('controller')
        self.initialize()

    def get_controller(self) -> object:
        """
        """

        return self.controller

    def activate(self) -> None:
        """
        Activates the avatar object
        """

        if self.is_activated():
            Runnable.deactivate(self)

        if self.controller:
            self.controller.foreach_call('activate')
        
        return Runnable.activate(self)

    def deactivate(self) -> None:
        """
        Deactivates the avatar object
        """

        if self.is_activated():
            return super(Runnable, self).dectivate()

        if self.controller:
            self.controller.foreach_call('dectivate')
        
        return super(Runnable, self).dectivate()

    def reload(self) -> None:
        """
        Reloads the avatar object
        """

        super(Configurable, self).reload()
        self.__setup_model_path_and_controller()
        super(AnimatedModel, self).reload(True)

    def relooad_model(self, model_path: str) -> None:
        """
        Reloads the avatar's model
        """

        self.model_path = model_path
        super(AnimatedModel, self).__init__(self.model_path)

    def get_state(self, name: str) -> object:
        """
        Retrieves an avatar's state
        """

        if self.controller:
            return self.controller.get_state(name)

        return False

    def get_running(self) -> bool:
        """
        Retrieves the avatar's running state
        """

        if self.controller:
            return self.controller.get_running()

        return False

    def set_running(self, running: bool) -> None:
        """
        Sets the avatar's running state
        """

        if self.controller:
            self.controller.set_running(running)

    async def update_controller(self, nodepath: object, dt: float) -> None:
        """
        Called once per frame to perform controller update operations
        """

        if not self.controller or not nodepath:
            return
        
        np = await self.controller.update(nodepath, dt)
        nodepath.set_quat(np.get_quat())
        nodepath.set_fluid_pos(np.get_pos())

    async def tick(self, dt: float) -> None:
        """
        Called once per frame to perform tick operations
        """

        if not self.controller:
            return

        await self.update_controller(self, dt)

    def play_emote(self, anim: object) -> None:
        """
        Plays an emotion animation on the avatar
        """

        if not self.controller:
            return

        self.controller.play_emote(anim)