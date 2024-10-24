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

from panda3d_gemstone.engine import runtime, prc

from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.runnable import Runnable
from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.service import Service, Command
from panda3d_gemstone.framework.controller import ControllerChainMixIn
from panda3d_gemstone.controllers.basic import FixedController

class Camera(Configurable, Runnable):
    """
    Represents the base class of all cameras in
    the Gemstone framework
    """

    def __init__(self, config_path: str):
        self.__name = ''
        self.__fov = prc.get_prc_double('default-fov', 30.0)
        self.__near = prc.get_prc_double('default-near', 1.0)
        self.__far = prc.get_prc_double('default-far', 100000)
        Configurable.__init__(self, config_path)
        Runnable.__init__(self, priority=10)
        CameraManager.get_singleton()._register(self)

    @property
    def camera_id(self) -> object:
        """
        Returns the camera's id as a property
        """

        return self.get_camera_id()

    @property
    def name(self) -> str:
        """
        Returns the camera's name as a property
        """

        return self.get_name()

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets the camera's name as a setter
        """

        self.set_name(name)

    @property
    def camera(self) -> object:
        """
        Returns the showbase camera object
        """

        return runtime.camera

    @property
    def camera_lens(self) -> object:
        """
        Returns the showbase camera lens object
        """

        return runtime.base.camLens

    def get_id(self) -> object:
        """
        Returns this camera's id 
        """

        return id(self)

    def get_name(self) -> str:
        """
        Returns the cameras name
        """

        return self.__name
    
    def set_name(self, name: str) -> None:
        """
        Sets the camera's name
        """

        self.__name = name

    def destroy(self) -> None:
        """
        Called on the destruction of the camera
        """

        camera_mgr = CameraManager.get_singleton()
        if self in camera_mgr.get_cameras():
            cam_mgr._unregister(self)

    def activate(self) -> None:
        """
        Activates the camera object
        """

        if self.is_activated():
            return False

        activated = Runnable.activate(self)
        CameraManager.get_singleton()._activate_camera(self)

        self.set_fov(self.__fov)
        self.set_near(self.__near)
        self.set_far(self.__far)

        return activated

    def deactivate(self): 
        """
        Deactivates the camera object
        """

        if self.is_activated():
            CameraManager.get_singleton()._deactivate_camera(self)

        return Runnable.deactivate(self)

    def reload(self):
        """
        Reloads the camera object
        """

        self.load()
        self.initialize()

    def set_fov(self, fov: float) -> None:
        """
        """

        self.__fov = fov
        if self.camera_lens and self.is_activated():
            self.camera_lens.set_fov(fov)

    def get_fov(self) -> float:
        """
        """

        return self.__fov

    def set_far(self, far: float) -> None:
        """
        """

        self.__far = far
        if self.camera_lens and self.is_activated():
            self.camera_lens.set_far(far)

    def get_far(self) -> None:
        """
        """

        return self.__far

    def set_near(self, near: float) -> None:
        """
        """
    
        self.__near = near
        if self.camera_lens and self.is_activated():
            self.camera_lens.set_near(near)

    def get_near(self) -> None:
        """
        """

        return self.__near

    def __getattr__(self, name) -> object:
        """
        Custom attribute for briding the Gemstone camera object
        to the native Panda3D camera lens and camera object created
        by the application's showbase instance
        """

        base = runtime.base
        if hasattr(base.camLens, name):
            return getattr(base.camLens, name)
        elif hasattr(base.camera, name):
            return getattr(base.camera)
        else:
            raise AttributeError('%s does not have attribute: %s!' % (
                self.__class__.__name__, name))

    def __del__(self) -> None:
        """
        Calls destroy on object deletion
        """

        self.destroy()

class FixedCamera(Camera):
    """
    """

    def __init__(self, config_path: str, target: object):
        super().__init__(config_path)
        self.__controller = FixedController(config_path)
        self.__target = None
        self.set_target(target)
        self.initialize()

    @property
    def controller(self) -> object:
        """
        Returns this camera's controller
        """

        return self.__controller

    @property
    def target(self) -> object:
        """
        Returns this camera's target point as a
        property
        """

        return self.get_target()

    @target.setter
    def target(self, target: object) -> None:
        """
        Sets this camera's target point as a 
        setter
        """

        self.set_target(target)

    def destory(self) -> None:
        """
        Called on camera destruction
        """

        if self.__controller != None:
            self.__controller.destroy()
            self.__controller = None

        Camera.destroy(self)

    def set_target(self, target: object) -> None:
        """
        Set's this camera's target point
        """

        self.__target = target
        self.__controller.foreach_call('set_target', target)

    def get_target(self) -> object:
        """
        Returns this camera's target point
        """

        return self.__target

    async def tick(self, dt: float) -> None:
        """
        Performs camera tick operations once per frame
        """

        np = await self.__controller.update(camera, dt)
        self.camera.set_quat(np.get_quat())
        self.camera.set_fluid_pos(np.get_pos())

class FollowCamera(Camera, ControllerChainMixIn):
    """
    """

    def __init__(self, config_path: str, target: object):
        super().__init__(config_path)
        self.__target = None
        self.__target_pos = None
        self.__target_hpr = None
        self.__mouse_rotating_handling = True
        self.__update_target_look_at = False
        self.__controller = self.setup_controller_chain(self.pop('controller'), config_path)
        self.__mouse_controller = self.find_controller(self.controller, MouseRotationController)
        self.set_target(target)
        self.initialize()

    def set_mouse_rotation_handling(self, mouse_rotation_handling: bool) -> None:
        """
        """

        self.__mouse_rotating_handling = mouse_rotation_handling

    def get_mouse_rotation_handling(self) -> bool:
        """
        """

        return self.__mouse_rotating_handling

    def set_update_target_look_at(self, update_target_look_at: bool) -> None:
        """
        """

        self.__update_target_look_at = update_target_look_at

    def get_update_target_look_at(self) -> bool:
        """
        """

        return self.__update_target_look_at

    def set_target(self, target: object) -> None:
        """
        Sets the follow camera's target NodePath
        """

        self.__target = target
        self.__target_pos = target.get_pos()
        self.__target_hpr = target.get_hpr()
        self.call_controller_chain(self.__controller, 'set_target', target)

    def get_target(self) -> object:
        """
        Returns the follow camera's target NodePath
        """

        return self.__target

    def activate(self) -> bool:
        """
        Attempts to activate the follow camera
        """

        result = Camera.activate(self)
        if result:
            self.call_controller_chain(self.controller, 'activate')

        return result

    def deactivate(self) -> bool:
        """
        Attempts to adeactivate the follow camera
        """

        result = Camera.deactivate(self)
        if result:
            self.call_controller_chain(self.controller, 'aeactivate')

        return result

    async def tick(self, dt: float) -> None:
        """
        Called once per frame to perform tick operations on the FollowCamera
        object instance
        """

        # Verify we have a controller instance
        if self.__controller is None:
            return

        np = await self.__controller.update(self.__target, dt)
        if self.__mouse_controller and self.__mouse_rotating_handling:
            should_lerp = self.__target_pos.almost_equal(self.__target.get_pos()) or self.__target_hpr.almost_equal(self.__target.get_hpr())
            if should_lerp:
                self.__mouse_controller.set_mode(MouseRotationController.LERP_ROTATION)
            else:
                self.__mouse_controller.set_mode(MouseRotationController.SAVE_ROTATION)

        look_at = np.get_quat()
        position = np.get_pos()

        if camera:
            camera.set_quat(look_at)
            camera.set_fluid_pos(position)

        if self.__update_target_look_at:
            if self.__mouse_controller.dragging:
                if not self.__target.get_quat().almost_equal(look_at):
                    self.__mouse_controller._reset_position()
                    self.__target.set_quat(look_at)
            else:
                self.__mouse_controller._reset_angle()

        self.__target_pos = self.__target.get_pos()
        self.__target_hpr = self.__target.get_hpr()

class CameraManager(Singleton, Service):
    """
    """

    def __init__(self):
        Singleton.__init__(self)
        Service.__init__(self)
        self.__cameras = []
        self.__last_camera_index = 0
        self.__active_camera = None
        self.__last_active_camera = None
        self.add_command(Command('reload cameras', self.reload))
        self.add_command(Command('toggle active camera', self.toggle_active_camera))
        self.add_command(Command('toggle culling camera', self.toggle_culling_camera))
        self.add_command(Command('toggle oobe camera', self.toggle_oobe_camera))
        self.activate()

    @property
    def cameras(self) -> list:
        """
        Complete list of all cameras known by the CameraManager
        """

        return self.get_cameras()

    @property
    def active_camera(self) -> Camera:
        """
        Currently active camera instance
        """

        return self.get_active_camera()

    def has_camera(self, camera: Camera) -> bool:
        """
        Returns true if the camera is found in the camera manager instance
        """

        return camera in self.__cameras

    def _register(self, camera: Camera) -> None:
        """
        Registers a new camera object with the CameraManager singleton
        """

        # Verify the camera is not already registered
        if self.has_camera(camera):
            self.notify.warning('Tried to register already registered camera (%s)' % camera.get_name())
            return
        
        self.__cameras.append(camera)
        camera._Camera__id = self.__last_camera_index
        self.__last_camera_index += 1

        #self.add_command(Command('activate camera <%d>' % camera.get_id()))
        #self.add_command(Command('activate camera <%s>' % camera.get_name()))

    def _unregister(self, camera: Camera) -> None:
        """
        Unregistered a camera object from the CameraManager singleton
        """

        # Verify the camera is currently registered
        if not self.has_camera(camera):
            self.notify.warning('Tried to unregister an unknown camera (%s)' % camera.get_name())
            return

        self.remove_command('activate camera <%d>' % camera.get_id())
        self.remove_command(Command('activate camera <%s>' % camera.get_name()))

        if self.__active_camera == camera:
            camera.deactivate()

        self.__cameras.remove(camera)

    def _activate_camera(self, camera: Camera) -> bool:
        """
        Attempts to activate the requested camera and sets it as the current active camera.
        Returns true on success. False on no change or failure.
        """

        if not self.has_camera(camera):
            self.notify.warning('Tried to activate an unknown camera: %s' % camera.get_name())
            return False
        
        if self.__active_camera == camera:
            self.notify.warning('Tried to activate already active camera: %s' % camera.get_name())
            return False
        
        # Deactivate the existing active camera if any.
        if self.__active_camera:
            self.__active_camera.deactivate()

        runtime.base.disableMouse()
        self.__active_camera = camera
        self.__last_active_camera = None

        return True

    def _deactivate_camera(self, camera: Camera) -> bool:
        """
        Deactivates the requested camera. Removing it from the current active camera
        variable. Returns true on success. False on no change or failure.
        """

        if not self.has_camera(camera):
            self.notify.warning('Tried to deactivate an unknown camera: %s' % camera.get_name())
            return False
        
        if self.__active_camera != camera:
            self.notify.warning('Tried to deactivate a camera other then active: %s' % camera.get_name())
            return False

        self.__active_camera = None
        self.__last_active_camera = None
        runtime.base.enableMouse()

        return True

    def get_active_camera(self) -> object:
        """
        Returns the currently active camera
        """

        return self.__active_camera

    def get_cameras(self) -> list:
        """
        Returns all cameras owned by the camera manger singleton
        """

        return self.__cameras

    def reload(self) -> None:
        """
        Reloads the camera manger and its owning cameras
        """

        for camera in self:
            camera.reload()

    def toggle_active_camera(self) -> None:
        """
        Toggles the active camera
        """

        if self.last_active_camera:
            self.last_active_camera.activate()
        elif self.active_camera:
            last_active_camera = self.active_camera
            last_active_camera.deactivate()
            self.last_active_camera = last_active_camera

    def toggle_culling_camera(self) -> None:
        """
        Toggles the oobe culling camera
        """

        runtime.base.oobe_cull()

    def toggle_oobe_camera(self) -> None:
        """
        Toggles the oobe camera
        """

        runtime.base.oobe()

    def __iter__(self):
        """
        Customer iterator for iterating all cameras in the camera manager
        singleton
        """

        for camera in list(self.cameras):
            yield camera