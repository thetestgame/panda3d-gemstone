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

from panda3d_gemstone.world.entity import Entity
from panda3d_gemstone.engine.audio import SoundSource

class ObjectIDMixIn(object):
    """
    Mixable class for managing object identifiers
    """

    def __init__(self):
        self.__object_id = None

    @property
    def object_id(self) -> int:
        """
        Object's unique identifier
        """

        return self.__object_id

    def get_object_id(self) -> int:
        """
        Returns the object's identifier
        """

        return self.__object_id

    def set_object_id(self, object_id: int) -> None:
        """
        Sets the object's identifier
        """

        self.__object_id = object_id

class GameObject(Entity, SoundSource, ObjectIDMixIn):
    """
    Base class for all game objects in the Gemstone framework
    """

    def __init__(self, config_path: str):
        Entity.__init__(self, config_path)
        SoundSource.__init__(self)
        ObjectIDMixIn.__init__(self)
    
    def destroy(self) -> None:
        """
        Called on gameobject destruction
        """

        Entity.destroy(self)
        self.remove_all_sounds()