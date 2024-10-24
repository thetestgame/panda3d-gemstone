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

import re
import types
import os

from panda3d_gemstone.engine import runtime
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.registry import ClassRegistryMixIn
from panda3d_gemstone.framework.progress import ProgressController
from panda3d_gemstone.io.indented_file import parse

class Scene(InternalObject, ClassRegistryMixIn):
    """
    Represents a scene in the Gemstone framework
    """

    @staticmethod
    def insert_node(nodepath: object, parent: object) -> None:
        """
        Inserts a node into the parent if it meets requirements
        """

        if hasattr(nodepath, 'reparent_to'):
            nodepath.reparent_to(parent)

    @staticmethod
    def remove_node(nodepath: object) -> None:
        """
        Removes a node from the scene graph if it meets requirements
        """

        if hasattr(nodepath, 'deactivate'):
            nodepath.deactivate()
        if hasattr(nodepath, 'remove_node'):
            nodepath.remove_node()

    @staticmethod
    def show_node(nodepath: object) -> None:
        """
        Shows the node in the scene graph if it meets requirements
        """

        if hasattr(nodepath, 'show'):
            nodepath.show()

    @staticmethod
    def hide_node(nodepath: object) -> None:
        """
        Hides the node from the scene graph if it meets requirements
        """

        if hasattr(nodepath, 'hide'):
            nodepath.hide()

    @staticmethod
    def insert_empty(object: object, parent: object) -> None:
        """
        Empty insert function placeholder
        """

    def __init__(self, path: str = None, progress_controller: ProgressController = ProgressController()):
        InternalObject.__init__(self)
        self.__objects = []
        if path is not None:
            self.load(path, progress_controller)

    def destroy(self) -> None:
        """
        Destroys the scene freeing it from memory
        """

        InternalObject.destroy(self)
        self.clear()

    def load(self, path: str, progress_controller: ProgressController = ProgressController()) -> None:
        """
        Loads a scene file from the applications file system
        """

        assert path != None
        assert path != ''

        nodes = parse(path)
        progress_controller.set_max(len(nodes))
        progress_controller.set_current(0)

        for node in nodes:
            progress_controller.tick()
            arg = node.args.strip()
            cls = self._get_class(node.type)
            if not cls:
                self.notify.warning('Failed to load object. Unkonwn class %s' % node.type)
                continue

            insert = self._get_class_meta(node.type, 'Scene.insert')
            if not insert:
                insert = Scene.insert_node
            
            if node.free:
                insert = None

            if arg:
                inst = cls(arg)
            else:
                inst = cls()

            node.instance = inst
            if node.name:
                self.__dict__[node.name] = inst
                if hasattr(inst, 'set_name'):
                    inst.set_name(node.name)
                elif hasattr(inst, 'setName'):
                    inst.setName(node.name)

            self.__objects.append(inst)
            if insert:
                if node.parent:
                    insert(inst, node.parent.instance)
                else:
                    insert(inst, runtime.render)

        progress_controller.finish()

    def get_object(self, name: str) -> None:
        """
        Attempts to retrieve an object by its name
        otherwise returns NoneType if not found
        """

        return getattr(self, name, None)

    def has_object(self, name: str) -> bool:
        """
        Returns true if the scene contains the object 
        name
        """

        return self.get_object(name) != None

    def get_objects(self, cls: object = None) -> list:
        """
        Retrieves all objects by their class if provided. Otherwise
        returns all objects
        """

        if not cls:
            return self.__objects

        objects = []
        if isintance(cls, bytes):
            for obj in self.__objects:
                if obj.__class__.__name__ == cls:
                    objects.append(obj)

        elif isinstance(cls, type):
            for obj in self.__objects:
                if obj.__class__ == cls:
                    objects.append(obj)

        return objects

    def __get_object_meta(self, obj: object, key: str, default: object = None) -> object:
        """
        Retrieves the object's class metadata information
        """

        meta = self._get_class_meta(obj.__class__.__name__, key)
        if not meta:
            meta = default

        return meta

    def __call_object_meta_func(self, obj: object, key: str, default: object = None) -> None:
        """
        Attempts to call an object's meta class function if it exists. Otherwise default
        """

        func = self.__get_object_meta(obj, key, default=default)
        if func:
            func(obj)

    def __call_object_meta_func_all(self, key: str, default: object = None) -> None:
        """
        Attempts to call the meta class function if it exists on all objects in the scene
        """

        for obj in self.__objects:
            self.__call_object_meta_func(obj, key, default)

    def clear(self) -> None:
        """
        Clears all objects from the scene
        """
        
        self.__call_object_meta_func_all('Scene.remove', default=Scene.remove_node)
        self.__objects = []

    def show(self) -> None:
        """
        Shows the scenes objects
        """

        self.__call_object_meta_func_all('Scene.show', default=Scene.show_node)

    def hide(self) -> None:
        """
        Hides the scenes objects
        """

        self.__call_object_meta_func_all('Scene.hide', default=Scene.hide_node)