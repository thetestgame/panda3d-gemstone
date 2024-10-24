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

import logging
from functools import reduce

from panda3d.core import BitMask32, Point2, Point3
from panda3d.core import Point4, Vec2, Vec3, Vec4

from panda3d_gemstone.framework.registry import ClassRegistry

class Caster(object):
    """
    Base class for all Gemstone framework casters
    """

    def accepted(self, value: object):
        """
        Returns true if the attempted cast is valid. Required to be implemented
        by child classes.
        """

        raise NotImplementedError('%s.accepted is not implemented!' % self.__class__.__name__)

    def __call__(self, value):
        """
        Returns the value of the attempted cast. Required to be implemented
        by the child classes.
        """

        raise NotImplementedError('%s called! Custom call function not implemented!' % self.__class__.__name__)

def get_class_registry() -> ClassRegistry:
    """
    Returns the class registry singleton object
    """

    return ClassRegistry.instantiate_singleton()

def register_caster(*args, **kwargs) -> None:
    """
    Registrs a class with the class registry
    """

    registry = get_class_registry()
    registry.register_class(is_caster=True, *args, **kwargs)

def __register_internal_caster(class_name) -> None:
    """
    Registers an internal caster class with the class registry
    based inside this module
    """

    package_path = 'panda3d_gemstone.framework.cast.%s' % class_name
    register_caster(class_name, package_path)

class CastBridge(object):
    """
    Bridge object to allow for object casting against
    known casters within the gemstone framework
    """

    __casters__ = []
    __primitives__ = [int, float]

    @classmethod
    def __attempt_primitive_cast(cls, type: object, value: object) -> bool:
        """
        Attempts to cast the value to a primitive type. Returns true and 
        the newly casted value on success. Otherwise False and NoneType
        """

        success = True
        output = None
        try:
            output = type(value)
        except (ValueError, TypeError):
            success = False

        return (success, output)

    def __new__(cls, value) -> object:
        """
        Attempts to create a new casted object
        from the supplied value on CastBridge 
        instantion
        """

        output = value

        # Attempt to cast against primtives
        for primitive in cls.__primitives__:
            success, output = cls.__attempt_primitive_cast(primitive, value)
            if success:
                return output

        # Attempt to cast against casters
        output = str(value).strip()
        for cast in cls.__casters__:
            if cast.accepted(output):
                output = cast(output)
                break

        return output

cast = CastBridge

class SequenceCaster(Caster):
    """
    """

    def __init__(self, cls: object, left: str, right: str, seperator: str):
        self._cls = cls
        self._left = left
        self._right = right
        self._seperator = seperator
    
    def accepted(self, value: str) -> bool:
        """
        """

        return value and value[0] == self._left and value[-1] == self._right

    def __split(self, value: str) -> list:
        """
        """

        words = []
        word = ''
        stack = []

        for i, v in enumerate(value):
            if v == self._left:
                stack.append(i)
                word += v
            elif v == self._right:
                stack.pop()
                word += v
            elif v == self._seperator and not stack:
                words.append(word.strip())
                word = ''
            else:
                word += v

        if word.strip():
            words.append(word.strip())
        
        return words

    def __call__(self, value):
        """
        """

        value = value[1:-1]
        values = self.__split(value)

        if values:
            values = [ cast(v) for v in values ]
            return self._cls(values)
        else:
            return self._cls()

class StringCaster(Caster):
    """
    Base caster for comparing the value of a cast to a string keyword
    and returning a basic type in the resulting cast
    """

    def __init__(self, key: str, obj: object):
        self._key = key
        self._obj = obj

    def accepted(self, value: str) -> bool:
        """
        Returns true if the attempted cast string value
        matches the string key of the caster
        """

        return value.lower() == self._key

    def __call__(self, value) -> object:
        """
        Returns the requested cast value provided
        by the child object
        """

        return self._obj

class ScalarCaster(Caster):
    """
    """

    def __init__(self, type_name: str, classes: []):
        self._type_name = type_name
        self._type_name_len = len(type_name)
        self._classes = classes

    def accepted(self, value: str) -> bool:
        """
        Returns true if the string value matches the scalar cast inputs
        """

        return value[:self._type_name_len] == self._type_name and value[self._type_name_len] == '(' and value[-1] == ')'

    def __call__(self, value: str) -> object:
        """
        """

        value = value[self._type_name_len + 1:-1]
        value = value.split(',')
        cls = self._classes[len(value) - 2]
        value = [float(n) for n in value]
        return cls(*value)

class FalseCast(StringCaster):
    """
    """

    def __init__(self):
        super().__init__('false', False)

__register_internal_caster('FalseCast')

class TrueCast(StringCaster):
    """
    """

    def __init__(self):
        super().__init__('true', True)

__register_internal_caster('TrueCast')

class ListCast(SequenceCaster):
    """
    """

    def __init__(self):
        super().__init__(list, '[', ']', ',')

__register_internal_caster('ListCast')

class NoneCast(StringCaster):
    """
    """

    def __init__(self):
        super().__init__('none', None)

__register_internal_caster('NoneCast')

class PandaBitCast(Caster):
    """
    """

    def __init__(self):
        self._type_name = 'Bit'
        self._type_name_len = len(self._type_name)

    def accepted(self, value: str) -> bool:
        """
        """

        return value[:self._type_name_len] == self._type_name and value[self._type_name_len] == '(' and value[-1] == ')'

    def __call__(self, value) -> object:
        """
        """

        value = value[self._type_name_len + 1:-1]
        value = value.split(',')
        bits = []

        for n in value:
            if n:
                n = int(n)
                bits.append(BitMask32.bit(n))

        if bits:
            return reduce(BitMask32.__or__, bits)
        else:
            return BitMask32()

__register_internal_caster('PandaBitCast')

class PandaPointCast(ScalarCaster):
    """
    """

    def __init__(self):
        super().__init__('Point', (Point2, Point3, Point4))

__register_internal_caster('PandaPointCast')

class PandaVectorCast(ScalarCaster):
    """
    """

    def __init__(self):
        super().__init__('Vec', (Vec2, Vec3, Vec4))

__register_internal_caster('PandaVectorCast')

class QuotedStringCast(Caster):
    """
    """

    def accepted(self, value: str) -> bool:
        """
        """

        return value and value[0] == value[-1] and value[0] in ('"', "'")

    def __call__(self, value: str) -> object:
        """
        """

        return value[1:-1]

__register_internal_caster('QuotedStringCast')

class TupleCast(SequenceCaster):
    """
    """

    def __init__(self):
        super().__init__(tuple, '(', ')', ',')

__register_internal_caster('TupleCast')

def __setup_casting() -> None:
    """
    Performs casting setup operations
    """

    # Setup bridge casters from registry
    CastBridge.__casters__ = [cls() for cls in get_class_registry().query_meta(is_caster=True)]

# Perform setup on import
__setup_casting()