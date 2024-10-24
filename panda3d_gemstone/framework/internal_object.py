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

from direct.showbase.DirectObject import DirectObject

from panda3d_gemstone.logging import utilities as logging
from panda3d_gemstone.framework.utilities import get_snake_case

class InternalObject(object):
    """
    Base class for all Gemstone framework internal objects
    """

    def __init__(self, *args, **kwargs):
        self.notify = logging.get_notify_category(self.get_notify_name())

    def get_notify_name(self) -> str:
        """
        Returns this object's notifier name
        """

        return get_snake_case(self.__class__.__name__, splitter='-')

    def destroy(self) -> None:
        """
        Called on object destruction
        """

    def __str__(self) -> str:
        """
        Custom base string handler for debugging 
        internal gemstone objects
        """

        return self.__class__.__name__

class PandaBaseObject(DirectObject):
    """
    Legacy base class of all Gemstone framework internal objects that
    utilize Panda3d internal code
    """

    def __init__(self, *args, **kwargs):
        DirectObject.__init__(self, *args, **kwargs)
        self.__notify = logging.get_notify_category(self.get_notify_name())
        self.notify.warning('%s is inheriting from legacy object: PandaBaseObject' % (
            self.__class__.__name__))

    @property
    def notify(self) -> object:
        """
        Returns this object's notifier logger
        """

        return self.__notify

    def get_notify_name(self) -> str:
        """
        Returns this object's notifier name
        """

        return get_snake_case(self.__class__.__name__, splitter='-')

    def destroy(self) -> None:
        """
        Called on object destruction
        """

        self.ignore_all()

    def __str__(self) -> str:
        """
        Custom base string handler for debugging 
        internal gemstone objects
        """

        return self.__class__.__name__