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

class SceneNode(NodePath):
    """
    Wrapper for the Panda3D NodePath to auto fill
    the NodePath as an empty string
    """

    def __init__(self, name=''):
        super().__init__(name)

class NodeObject(object):
    """
    Base class for node based Gemstone framework
    objects. Includes a blank NodePath object
    wrapped as a SceneNode.
    """

    def __init__(self, *args, **kwargs):
        self._node = SceneNode(*args, **kwargs)

    @property
    def node(self) -> NodePath:
        """
        Returns the object's node path
        """

        return self._node

    def __getattr__(self, key) -> object:
        """
        Passes attribute retrievals to the Panda3D NodePath
        object for legacy support
        """

        if hasattr(self._node, key):
            return getattr(self._node, key)

        raise AttributeError('%s does not have an attribute: %s' % (
            self.__class__.__name__, key))