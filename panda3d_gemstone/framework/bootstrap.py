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

from panda3d_gemstone.logging import utilities as __logging
import importlib as __importlib

__bootstrap_notify = __logging.get_notify_category('bootstrap')

def create_class_entry(object_path: str, meta: dict = {}) -> tuple:
    """
    Creates a class entry for use with the bootstrap function
    """

    parts = object_path.split('.')
    class_name = parts[-1]

    return (class_name, object_path, meta)

def create_singleton_entry(object_path: str, meta: dict = {}) -> tuple:
    """
    Creates a singleton entry for use with the bootstrap function
    """

    parts = object_path.split('.')
    class_name = parts[-1]
    path = '.'.join(parts[:-1])

    return (path, class_name, meta)

def get_class_registry() -> object:
    """
    Retrieves the environments class registry
    singleton object
    """

    from panda3d_gemstone.framework.registry import ClassRegistry
    return ClassRegistry.instantiate_singleton()

def __import_module(module_name: str) -> object:
    """
    Imports the requested module by its module
    name import path
    """

    assert module_name != ''
    assert module_name != None

    components = module_name.split('.')
    module_path = '.'.join(components[:-1])
    module = __importlib.import_module(module_path)

    return module

def batch_instantiate_singletons(singleton_list: list) -> None:
    """
    Batch instantiates singletons from a list
    """

    for singleton in singleton_list:
        module_name, class_name, args = singleton
        module_path = '%s.%s' % (module_name, class_name)
        singleton_module = __import_module(module_path)
        if singleton_module is None:
            __bootstrap_notify.warning('Failed to setup singleton: %s. Invalid import' % class_name)
            continue

        singleton_cls = getattr(singleton_module, class_name)
        singleton_cls.instantiate_singleton(*args)

def __verify_thirdparty(modules: object) -> None:
    """
    Verifies the required modules are found in the environment
    prior to importing the rest of the gemstone module
    """

    from panda3d_gemstone.framework import exceptions
    exceptions.verify_thirdparty_modules(modules)

def bootstrap_module(class_list: list = [], meta_list: list = [], singleton_list: list = [], thirdparty: object = []) -> None:
    """
    Performs initial boostrap operations on a module
    """

    class_registry = get_class_registry()
    batch_instantiate_singletons(singleton_list)
    class_registry.batch_register_classes(class_list, meta_list)
    __verify_thirdparty(thirdparty)
