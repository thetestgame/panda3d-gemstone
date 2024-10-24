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

import importlib.util
import builtins
import sys
import os

from direct.showbase.MessengerGlobal import messenger

dev = False

def __get_base_executable_name() -> str:
    """
    Returns the base executable name
    """

    basename = os.path.basename(sys.argv[0])
    if basename == '-m':
        basename = os.environ.get('APP_NAME', 'Gemstone-App')

    basename = os.path.splitext(basename)[0]
    return basename

executable_name = __get_base_executable_name()

def is_venv() -> bool:
    """
    Returns true if the application is being run inside
    a virtual environment
    """

    real_prefix = hasattr(sys, 'real_prefix')
    base_prefix = hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix

    return real_prefix or base_prefix

def is_frozen() -> bool:
    """
    Returns true if the application is being run from within
    a frozen Python environment
    """

    spec = importlib.util.find_spec(__name__)
    return spec is not None and spec.origin is not None

def is_interactive() -> bool:
    """
    Returns true if the application is being run from an
    interactive command prompt
    """

    import sys
    return hasattr(sys, 'ps1') and hasattr(sys, 'ps2')

def is_developer_build() -> bool:
    """
    Returns true if the application is currently
    running as a developer build
    """
    
    return (dev or is_interactive()) and not is_frozen()

def has_thirdparty(import_string) -> bool:
    """
    Returns true if the requested import is found in 
    the environment
    """

    import importlib
    found = False
    try:
        module = importlib.import_module(import_string)
        found = True
    except:
        pass

    return found

def has_render_pipeline_support() -> bool:
    """
    Returns true if the application has tobspr's 
    Render Pipeline module available in the environment
    """

    return has_thirdparty('rpcore')

def __get_module() -> object:
    """
    Returns the runtime module's object instance
    """

    return sys.modules[__name__]

def __has_variable(variable_name: str) -> bool:
    """
    Returns true if the runtime module has the requested variable name defined.
    Is served out via the custom __getattr__ function as has_x() method names
    """

    module = __get_module()
    defined = hasattr(module, variable_name)
    found = False

    if defined:
        attr = getattr(module, variable_name)
        found = attr != None

    return found

def __get_variable(variable_name: str) -> object:
    """
    Returns the requested variable from the runtime module if it exists.
    Otherwise returning NoneType
    """

    if not __has_variable(variable_name):
        return None

    module = __get_module()
    return getattr(module, variable_name)

def __getattr__(key: str) -> object:
    """
    Custom get attribute handler for allowing access to the has_x method names
    of the Gemstone runtime module. Also exposes the builtins module
    for the legacy Panda3d builtins provided by the ShowBase instance
    """

    result = None
    is_has_method = key.startswith('has_')
    is_get_method = key.startswith('get_')

    if len(key) > 4:
        variable_name = key[4:]
    else:
        variable_name = key

    if is_has_method:
        return lambda: __has_variable(variable_name)
    elif is_get_method:
        return lambda: __get_variable(variable_name)
    elif hasattr(builtins, key):
        return getattr(builtins, key)

    if not result:
        raise AttributeError('runtime module has no attribute: %s' % key)

    return result


