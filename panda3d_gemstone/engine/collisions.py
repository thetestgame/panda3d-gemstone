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

from panda3d.core import CollisionTraverser, CollisionHandlerFluidPusher, CollisionHandlerQueue
from panda3d.core import CollisionNode, BitMask32, NodePath

from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.runnable import Runnable

from panda3d_gemstone.engine import runtime

class CollisionSystem(Singleton, Runnable):
    """
    Manages all native Panda3D collision interactions inside
    the Gemstone framework
    """

    def __init__(self):
        Singleton.__init__(self)
        Runnable.__init__(self, priority=25)

        self.__traversers = {}
        self.__collision_handlers = {}
        self.__collision_objects = {}
        self.add_traverser('default')
        self.add_handler('queue', CollisionHandlerQueue())
        self.add_handler('pusher', CollisionHandlerFluidPusher())
        self.__debugging = False
    
    def destroy(self) -> None:
        """
        Destroys the collision system singleton instance
        """

        self.__traversers = {}
        self.__collision_handlers = {}
        self.__collision_objects = {}
        Runnable.deactive(self)

    def has_collision_object(self, name: str) -> bool:
        """
        Returns true if the collision object exists in the system
        """

        return name in self.__collision_objects

    def get_collision_object(self, name: str) -> object:
        """
        Returns the collision object if it exists. Otherwise
        returns NoneType
        """

        return self.__collision_objects.get(name, None)

    def show_collision_object(self, name: str) -> None:
        """
        Shows the collision object's NodePath
        """

        if not self.has_collision_object(name):
            return

        nodepath = self.get_collision_object(name)
        nodepath.show()

    def hide_collision_object(self, name: str) -> None:
        """
        Hides the collision object's NodePath
        """

        if not self.has_collision_object(name):
            return

        nodepath = self.get_collision_object(name)
        nodepath.hide()

    def hide_all_collision_objects(self) -> None:
        """
        Hides all collision objects in the system
        """

        for name in self.__collision_objects:
            self.hide_collision_object(name)

    def show_all_collision_objects(self) -> None:
        """
        Shows all collision objects in the system
        """

        for name in self.__collision_objects:
            self.show_collision_object(name)

    def add_traverser(self, name: str, priority: int = 0, traverser_class: object = CollisionTraverser) -> None:
        """
        Adds a new collision traverser to the collision system
        """

        if self.has_traverser(name):
            self.notify.warning('Failed to add traverser. Traverser (%s) already exists!' % name)
            return

        traverser = traverser_class()
        self.__traversers[name] = (priority, traverser)
        traverser.set_respect_prev_transform(True)

    def has_traverser(self, name: str) -> bool:
        """
        Returns true if the collision traverser exists
        """

        return name in self.__traversers

    def get_traverser(self, name: str) -> object:
        """
        Returns the collision traverser if it exists. Otherwise
        returns NoneType
        """

        return self.__traversers.get(name, None)

    def remove_traverser(self, name: str) -> None:
        """
        Removes a traverser from the collision system by its name
        """

        if not self.has_traverser(name):
            self.notify.warning('Failed to remove traverser. %s does not exist' % name)
            return

        if name == 'default':
            self.notify.warning('Failed to remove traverser. Cannot delete default')
            return

        del self.__traversers[name]

    def show_collisions(self) -> None:
        """
        Enables the debugging collision visualization and shows all collisions
        """

        self.__debugging = False
        for priority, traverser in lisT(self.__traversers.values()):
            if hasattr(traverser, 'show_collisions'):
                traverser.show_collisions(runtime.render)

    def hide_collision(self) -> None:
        """
        Disables the debugging collision visualization and hides all collisions
        """

        self.__debugging = False
        for priority, traverser in lisT(self.__traversers.values()):
            if hasattr(traverser, 'hide_collisions'):
                traverser.hide_collisions(runtime.render)

    def toggle_collisions(self) -> None:
        """
        Toggles the collision debugging visuals
        """

        if self.__debugging:
            self.hide_collision()
        else:
            self.show_collisions()

    def has_handler(self, name: str) -> bool:
        """
        Returns true if the collision handler exists
        """

        return name in self.__collision_handlers

    def add_handler(self, name: str, handler: object) -> object:
        """
        Adds a new collision handler if it does not already exist
        """

        if self.has_handler(name):
            self.notify.warning('Failed to add new handler. Handler (%s) already exists' % name)
            return None

        self.__collision_handlers[name] = handler
        return handler

    def remove_handler(self, name: str) -> None:
        """
        Attempts to remove a handler if it exists
        """

        if not self.get_handler(name):
            self.notify.warning('Failed to remove handler %s. Handler does not exist' % name)
            return

        del self.__collision_handlers[name]

    def get_handler(self, name: str) -> object:
        """
        Returns the handler object if it exists. Otherwise
        returns NoneType
        """

        return self.__collision_handlers.get(name, None)

    def add_collision_object(self, name: str, parent: object, obj: object) -> object:
        """
        Adds a collision object to the system
        """

        if self.has_collision_object(name):
            self.notify.warning('Attempted to add collision object that already exists (%s)!' % name)
            return self.get_collision_object(name)

        if type(obj) == type([]):
            objs = obj
        else:
            objs = [obj]

        collision_node = CollisionNode(name)
        for o in objs:
            collision_node.add_solid(o)

        collision_node.set_into_collide_mask(BitMask32.all_off())
        if parent:
            collision_path = parent.attach_new_node(collision_node)
        else:
            collision_path = NodePath(collision_node)

        self.__collision_objects[name] = collision_path
        return collision_path

    def enable_collision_object(self, object_name: str, handler_name: str, traverser_name: str = 'default') -> None:
        """
        Enables a collision object in the system
        """

        if not self.has_collision_object(object_name):
            self.notify.warning('Failed to remove collision object. Object "%s" does not exist' % object_name)
            return
        
        if not self.has_handler(handler_name):
            self.notify.warning('Failed to remove collision object. Handler "%s" does not exist' % handler_name)
            return      

        if not self.has_traverser(traverser_name):
            self.notify.warning('Failed to remove collision object. Traverser "%s" does not exist' % traverser_name)
            return

        nodepath = self.get_collision_object(object_name)
        handler = self.get_handler(handler_name)
        priority, traverser = self.get_traverser(traverser_name)
        traverser.add_collider(nodepath, handler)

        if isinstance(handler, CollisionHandlerFluidPusher) and runtime.base.drive:
            handler.add_collider(nodepath, nodepath.get_parent(), runtime.base.drive.node())

    def remove_collision_object(self, object_name: str, handler_name: str, traverser_name: str = 'default') -> None:
        """
        Removes a collision object from the system
        """

        if not self.has_collision_object(object_name):
            self.notify.warning('Failed to remove collision object. Object "%s" does not exist' % object_name)
            return
        
        if not self.has_handler(handler_name):
            self.notify.warning('Failed to remove collision object. Handler "%s" does not exist' % handler_name)
            return      

        if not self.has_traverser(traverser_name):
            self.notify.warning('Failed to remove collision object. Traverser "%s" does not exist' % traverser_name)
            return

        nodepath = self.get_collision_object(object_name)
        handler = self.get_handler(handler_name)
        priority, traverser = self.get_traverser(traverser_name)
        traverser.remove_collider(nodepath)

        if isinstance(handler, CollisionHandlerFluidPusher):
            handler.remove_collider(nodepath)

        del self.__collision_objects[object_name]

    async def tick(self, dt: float) -> None:
        """
        Called once per frame to perform collision traversal
        """

        traversers = list(self.__traversers.values())
        traversers.sort()

        for priority, traversers in traversers:
            traversers.traverse(runtime.render)