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

from panda3d.core import NodePath
from panda3d.core import Fog as _Fog

from panda3d_gemstone.framework.configurable import Configurable

class Fog(Configurable):
    """
    Represents a gemstone fog by wrapping
    the Panda3D native fog node object
    """

    @staticmethod
    def insert(fog: object, parent: NodePath) -> None:
        """
        Adds the fog's fog node to the requested
        parent NodePath instance
        """

        parent.set_fog(fog.fog_node)

    @staticmethod
    def remove(fog: object) -> None:
        """
        Removes the fog from the scene by iterating over
        all its parents and clearing the fog attribute
        """

        for i in range(fog.fog_node.get_num_parents()):
            fog.fog_node.get_parent(i).clear_fog()

    def __init__(self, config_path: str, section: str = 'Configuration'):
        super().__init__(config_path, section)
        self._fog_node = _Fog(self.pop('name', 'Fog'))
        self.initialize()

    @property
    def fog_node(self) -> _Fog:
        """
        Panda3D native fog node instance
        """

        return self._fog_node