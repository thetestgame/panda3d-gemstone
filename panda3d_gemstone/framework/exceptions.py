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

def verify_thirdparty_modules(modules: object) -> None:
    """
    Verifies the required thirdparty modules are available
    in the environment. If the modules are not found
    a MissingThirdpartySupportError is thrown
    """

    if isinstance(modules, list):
        module_list = modules
    else:
        module_list = [modules]

    from panda3d_gemstone.engine import runtime
    for module in module_list:
        found = runtime.has_thirdparty(module)
        if not found:
            raise MissingThirdpartySupportError(module)

def verify_attribute(obj: object, attrib_name: str) -> None:
    """
    Raises an AttributeError if the object does not have the 
    required attribute name present
    """

    object_name = obj.__class__.__name__
    found = hasattr(obj, attrib_name)
    if not found:
        raise AttributeError('%s does not have the required attribute: %s' % (
            object_name, attrib_name))

def raise_not_implemented(obj: object, method_name: str) -> None:
    """
    Raises a NotImplementedError relating to inform the user
    of the missing method in a child class
    """

    if isinstance(obj, str):
        obj_name = obj
    else:
        obj_name = obj.__class__.__name__

    message = '%s does not implement %s.' % (obj_name, method_name)
    raise NotImplementedError(message)

class ImproperClassUsageError(RuntimeError):
    """
    Thrown when a parent class is improperly used
    with an unsupported child class
    """

    def __init__(self, base_class: str, use_class: str):
        super().__init__('Improper use of %s! %s is not a valid child class.' % (base_class, use_class))

class MissingThirdpartySupportError(RuntimeError):
    """
    Thrown when a thirdparty dependency is missing
    from the environment
    """

    def __init__(self, library_name):
        super().__init__('Missing required thirdparty dependency: %s' % library_name)

class NotSupportedError(RuntimeError):
    """
    Thrown when a method is used that is not supported by
    a variant of the base class
    """

    def __init__(self, cls: object, method_name: str):
        super().__init__('%s does not support %s.' % (cls.__name__, method_name))

class InvalidEnvironmentError(RuntimeError):
    """
    Thrown when an invalid environment is detected
    """