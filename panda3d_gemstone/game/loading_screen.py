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

from panda3d_gemstone.framework.progress import ProgressController
from panda3d_gemstone.framework.service import Service
from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.singleton import Singleton

class LoadingScreenBase(Service, Configurable, Singleton, InternalObject):
    """
    Base class for all loading screens in the Gemstone framework
    """

    def __init__(self, config_path: str, service_name: str = 'LoadingScreen'):
        Service.__init__(self, service_name or self.__class__.__name__)
        Singleton.__init__(self)
        Configurable.__init__(self, config_path)
        InternalObject.__init__(self)

    def destroy(self) -> None:
        """
        Destroys the loading screen object instance
        """

        Service.destroy(self)
        InternalObject.destroy(self)

    def update_loading_progress(self, section: object, current: int, max: int = None) -> None:
        """
        Updates the loading screen's progress. Intended to be overridden by children
        """

        raise NotImplementedError('%s does not implement update_loading_progress!' % self.__class__.__name__)

class LoadingScreenProgressController(ProgressController):
    """
    Custom progress controller for progressing the Gemstone 
    framework loading screen objects
    """

    def __init__(self, section: object, logic_cls: object):
        assert logic_cls != None
        assert hasattr(logic_cls, 'get_singleton')

        self.__section = section
        self.__logic_cls = logic_cls

    @property
    def section(self) -> object:
        """
        Section of loading logic to update
        """

        return self.__section

    def update(self, current: int, max: int) -> None:
        """
        Called on progression to update the loading screen
        """

        loading_screen = self.__logic_cls.get_singleton()
        if not loading_screen:
            return
        
        loading_screen.update_loading_progress(self.__section, current, max)