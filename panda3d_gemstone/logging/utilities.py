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

import os
import sys

from panda3d.core import MultiplexStream, Filename, load_prc_file_data
from panda3d.core import Notify, ConfigVariableString

from panda3d_gemstone.engine import runtime

def get_notify_categories() -> object:
    """
    Retrieves all Panda3D notifier categories
    """

    from direct.directnotify.DirectNotifyGlobal import directNotify
    return directNotify.getCategories()

def get_notify_category(name: str, create: bool = True) -> object:
    """
    Returns the requested Panda3D notifier category. Creating a new
    one if create is set to True
    """

    assert name != None
    assert name != ''

    from direct.directnotify.DirectNotifyGlobal import directNotify

    category = None
    if create:
        category = directNotify.newCategory(name)
    else:
        category = directNotify.getCategory(name)
    return category

def log(message: str, name: str = 'global', type: str = 'info') -> None:
    """
    Writes a message to the requested logger name
    """

    category = get_notify_category(name)
    assert hasattr(category, type)
    getattr(category, type)(message)

def log_error(message: str, name: str = 'global') -> None:
    """
    Writes an error message to the requested logger name
    """

    log(name, message, 'error')

def log_warn(message: str, name: str = 'global') -> None:
    """
    Writes an warn message to the requested logger name
    """

    log(name, message, 'warn')

def log_info(message: str, name: str = 'global') -> None:
    """
    Writes an info message to the requested logger name
    """

    log(name, message, 'info')

def log_debug(message: str, name: str = 'global') -> None:
    """
    Writes an debug message to the requested logger name
    """

    log(name, message, 'debug')

def condition_error(logger: object, condition: bool, message: str) -> None:
    """
    Writes a error message to the logging object if the provided
    condition is true
    """

    condition_log(logger, condition, message, 'error')

def condition_warn(logger: object, condition: bool, message: str) -> None:
    """
    Writes a warning message to the logging object if the provided
    condition is true
    """

    condition_log(logger, condition, message, 'warning')

def condition_info(logger: object, condition: bool, message: str) -> None:
    """
    Writes a info message to the logging object if the provided
    condition is true
    """

    condition_log(logger, condition, message, 'info')

def condition_debug(logger: object, condition: bool, message: str) -> None:
    """
    Writes a debug message to the logging object if the provided
    condition is true
    """

    condition_log(logger, condition, message, 'debug')

def condition_log(logger: object, condition: bool, message: str, type: str = 'info') -> None:
    """
    Writes a message to the logging object if the provided
    condition is true using the supplied type attribute function name
    """

    assert hasattr(logger, type)
    if condition:
        getattr(logger, type)(message)

def get_log_directory() -> str:
    """
    Returns this applications log directory
    based on the PRC configuration
    """

    default = '.%slogs' % os.sep
    return ConfigVariableString('gs-log-directory', default).value

def get_log_filename() -> str:
    """
    Returns the filename used for this applications
    log file
    """

    basename = runtime.executable_name.lower()
    log_ext = ConfigVariableString('gs-log-ext', 'txt').value
    return '%s.%s' % (basename, log_ext)
