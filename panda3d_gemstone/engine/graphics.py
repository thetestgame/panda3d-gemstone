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

from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.utilities import get_snake_case

from panda3d_gemstone.engine.shader import load_shader
from panda3d_gemstone.engine import runtime

from panda3d.core import NodePath

class GraphicsManager(Singleton, Configurable, InternalObject):
    """
    """

    def __init__(self, config_path: str):
        Singleton.__init__(self)
        InternalObject.__init__(self)
        self.__shader_data = {}
        self.__shader_defines = {}
        Configurable.__init__(self, config_path)
        self.__activated = False
        self.initialize()

    def load_shader_data(self, data: dict) -> None:
        """
        Loads the shader data into memory
        """

        self.__shader_data = data

    def load_defines_data(self, data: dict) -> None:
        """
        Loads the graphics define data into memory
        """

        for key, value in data.items():
            define_name = get_snake_case(key).upper()
            self.__shader_defines[define_name] = value

    def is_active(self) -> bool:
        """
        Returns true if the graphics manager is active
        """

        return self.__activated

    def activate(self, root_node: NodePath) -> None:
        """
        Activates the graphics manager on the requested root node 
        instance
        """

        if self.__activated:
            self.notify.warning('Failed to activate %s. Already active' % (
                self.__class__.__name__))
        
            return

        assert root_node != None
        assert runtime.has_base()
        assert isinstance(root_node, NodePath)

        # Setup shaders
        core_shader = load_shader(
            vertex=self.__shader_data.get('coreVertexPath', None),
            fragment=self.__shader_data('coreFragmentPath', None))
        assert core_shader != None
        root_node.set_shader(core_shader)

        # Set general inputs
        root_node.set_shader_input('camera', runtime.base.cam)
