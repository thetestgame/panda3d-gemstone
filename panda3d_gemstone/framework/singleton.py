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

from panda3d_gemstone.logging.utilities import get_notify_category

_notify = get_notify_category('singleton')

class Singleton(object):
    """
    Represents a singleton object in the gemstone framework
    """

    _singleton_instance = None

    def __init__(self):
        if not self.__class__.is_instantiated():
            self.__class__.reset_singleton(self)
        else:
            raise RuntimeError('%s singleton already exists' % self.__class__.__name__)
        self.setup()

    @classmethod
    def instantiate_singleton(cls, *args, **kwargs):
        """
        Instantiates a new singleton instance
        """

        if not cls.is_instantiated():
            cls.reset_singleton(cls(*args, **kwargs))

        return cls.get_singleton()

    @classmethod
    def reset_singleton(cls, inst: object = None) -> None:
        """
        Resets the singleton instance
        """

        # Destroy existing singleton if one exists
        if cls._singleton_instance is not None and id(inst) != id(cls._singleton_instance):
            cls.destroy(cls._singleton_instance)

        # Setup new singleton
        cls._singleton_instance = inst

    @classmethod
    def get_singleton(cls, silent: bool = False) -> object:
        """
        Returns the current singleton instance
        """

        instance = cls._singleton_instance
        if not instance and not silent:
            _notify.warning('Failed to get singleton. %s is not instantiated' % (
                cls.__name__))

        return instance

    @classmethod
    def is_instantiated(cls) -> bool:
        """
        Returns true if the current singleton has an instance
        """

        return cls._singleton_instance != None

    def setup(self) -> None:
        """
        Performs setup operations on the singleton
        """

    def destroy(self) -> None:
        """
        Performs shutdown operations on the singleton
        """

class SingletonWrapper(Singleton):
    """
    Custom Singleton instance for wrapping Python objects as Gemstone
    singleton objects.
    """

    WRAPPED_OBJECT = None

    def __init__(self, *args, **kwargs):
        assert self.WRAPPED_OBJECT != None
        self.__object = self.WRAPPED_OBJECT(*args, **kwargs)
        assert self.__object != None

    @property
    def wrapped(self) -> object:
        """
        Singleton's wrapped object instance
        """

        return self.get_wrapped()

    def get_wrapped(self) -> object:
        """
        Returns the wrapped object instance
        """

        return self.__object

    def __getattr__(self, key: str) -> object:
        """
        Custom attributes retrieval handler to pass through unknown
        attributes to our wrapped object instance
        """

        result = None
        if self.__object != None:
            if hasattr(self.__object, key):
                result = getattr(self.__object, key)

        if not result:
            raise AttributeError('%s instance does not have attribute %s' % (
                self.__class__.__name__, key))    

        return result