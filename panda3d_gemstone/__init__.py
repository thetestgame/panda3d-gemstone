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

from panda3d_gemstone.engine.lighting import Light as __Light
from panda3d_gemstone.engine.fog import Fog as __Fog
from panda3d_gemstone.world.scene import Scene as __Scene
from panda3d_gemstone.framework import bootstrap as __bootstrap
from panda3d_gemstone.controllers.avatar import AvatarController as __AvatarController
from panda3d_gemstone import __version__ as package_version

__version__ = package_version.__version__

__singleton_list = [
    __bootstrap.create_singleton_entry('panda3d_gemstone.application.events.EventsManager'),
    __bootstrap.create_singleton_entry('panda3d_gemstone.logging.handler.ApplicationLogger'),
    __bootstrap.create_singleton_entry('panda3d_gemstone.framework.service.ServiceManager'),
    __bootstrap.create_singleton_entry('panda3d_gemstone.framework.resource.ResourceManager'),
    __bootstrap.create_singleton_entry('panda3d_gemstone.engine.collisions.CollisionSystem'),
    __bootstrap.create_singleton_entry('panda3d_gemstone.engine.camera.CameraManager'),
    __bootstrap.create_singleton_entry('panda3d_gemstone.engine.audio.SoundManager'),
]

__class_list = [
    __bootstrap.create_class_entry('panda3d_gemstone.engine.lighting.Light'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.fog.Fog'),
    __bootstrap.create_class_entry('panda3d_gemstone.world.world.World'),
    __bootstrap.create_class_entry('panda3d_gemstone.world.streaming.StreamableWorld'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.skybox.Skybox'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.terrain.CPUTerrain'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.terrain.GPUTerrain'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.terrain.PaintedChannelTerrain'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.model.StaticModel'),
    __bootstrap.create_class_entry('panda3d_gemstone.world.streaming.StreamableStaticModel'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.model.AnimatedModel'), 
    __bootstrap.create_class_entry('panda3d_gemstone.engine.model.TextureModel'),
    __bootstrap.create_class_entry('panda3d_gemstone.world.entity.Entity'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.lighting.LightSet'),
    __bootstrap.create_class_entry('panda3d_gemstone.engine.text.Font'),
    __bootstrap.create_class_entry('panda3d_gemstone.game.avatar.Avatar'),
    __bootstrap.create_class_entry('panda3d_gemstone.controllers.movement.MovementController'), 
    __bootstrap.create_class_entry('panda3d_gemstone.controllers.movement.JumpController'), 
    __bootstrap.create_class_entry('panda3d_gemstone.controllers.basic.FixedController'), 
    __bootstrap.create_class_entry('panda3d_gemstone.controllers.camera.CameraCollisionController'), 
    __bootstrap.create_class_entry('panda3d_gemstone.controllers.physics.PhysicsMovementController'),
    __bootstrap.create_class_entry('panda3d_gemstone.controllers.avatar.AvatarController')
]

__meta_list = [
    ('Light', 'Scene.insert', __Light.insert),
    ('Light', 'Scene.remove', __Light.remove),
    ('Light', 'editor_object', True),
    ('Fog', 'Scene.insert', __Fog.insert),
    ('Fog', 'Scene.remove', __Fog.remove),
    ('Fog', 'editor_object', True),
    ('Skybox', 'editor_object', True),
    ('CPUTerrain', 'editor_object', True),
    ('GPUTerrain', 'editor_object', True),
    ('StaticModel', 'editor_object', True),
    ('StreamableStaticModel', 'editor_object', True),
    ('AnimatedModel', 'editor_object', True),
    ('Font', 'Scene.insert', __Scene.insert_empty),
    #('JumpController', 'Controller.setup', __JumpController.set_ground_collision),
    #('CameraCollisionController', 'Controller.setup', __CameraCollisionController.set_target),
    ('AvatarController', 'Controller.setup', __AvatarController.setup)
]

# Perform setup operations on the gemstone module
__bootstrap.bootstrap_module(
    class_list = __class_list,
    meta_list=__meta_list,
    singleton_list=__singleton_list)