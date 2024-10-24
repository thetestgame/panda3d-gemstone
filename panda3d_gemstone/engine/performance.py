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

from panda3d_gemstone.engine import runtime as __runtime
from panda3d_gemstone.logging import utilities as __logging
from panda3d.core import PStatCollector as __PStatCollector
from panda3d.core import PStatClient as __PStatClient

__notify = __logging.get_notify_category('performance')
__client = None

def get_profile_client() -> __PStatClient:
    """
    Returns the application's profiler client instance
    """

    global __client
    if __client is None:
        __client = __PStatClient()
    
    return __client

def is_profiling() -> bool:
    """
    Returns true if the application is currently being
    profiled
    """

    client = get_profile_client()
    return client.is_connected()

def connect_profiler(*args, **kwargs) -> bool:
    """
    Connects the application to a profiler server
    """

    if is_profiling():
        __notify.warning('Failed to connect profiler. A profiler is already connected')
        return False

    client = get_profile_client()
    client.connect(*args, **kwargs)

def disconnect_profiler() -> None:
    """
    Disconnects the application from a profiler server if it
    is currently connected
    """

    if not is_profiling():
        return

    client = get_profile_client()
    client.disconnect()

def toggle_profiling() -> None:
    """
    Toggles the current application profiling setting. Connecting
    to a server available at localhost
    """

    if is_profiling():
        connect_profiler()
    else:
        disconnect_profiler()

def resume_profiling_after_pause() -> None:
    """
    Resumes the profiling client after the simuilation has been paused for a while.
    This allows stats to continue exactly where it left off, instead of leaving a big gap that would represent
    a chug in the application's performance
    """

    client = get_profile_client()
    client.resume_after_pause()

def get_collector(label: str) -> __PStatCollector:
    """
    Creates and returns a new pstats collector instance
    """

    return __PStatCollector(label)

def __has_custom_collectors() -> bool:
    """
    Returns true if the custom_collectors dictionary
    is defined on our showbase instance
    """

    return hasattr(__runtime.base, 'custom_collectors')

def __has_custom_collector(name: str) -> bool:
    """
    Returns true if the custom collector currently
    exists
    """

    return name in __get_custom_collectors()

def __get_custom_collector(name: str) -> __PStatCollector:
    """
    Returns the custom collector if it exists
    """

    return __get_custom_collectors().get(name, None)

def __get_custom_collectors() -> list:
    """
    Returns a complete list of custom collectors
    """

    if not __has_custom_collectors():
        return []

    return __runtime.base.custom_collectors

def __create_custom_collector(name: str) -> object:
    """
    Creates and returns a custom PStatCollector
    instance
    """

    base = __runtime.base
    if not __has_custom_collectors():
        base.custom_collectors = {}

    if __has_custom_collector(name):
        __notify.warning('Attempted to create a new collector when it already exists! Name: %s' % name)
        return base.custom_collectors[collector_name]

    base.custom_collectors[collector_name] = __PStatCollector(collector_name)
    return base.custom_collectors[collector_name]

def stat_collection(func: object) -> object:
    """
    Wraps a function with a Panda3D PStatCollector object
    for timing its performance
    """

    collector_name = 'Debug:%s' % func.__name__
    if __has_custom_collector(collector_name):
        pstat = __get_custom_collector(collector_name)
    else:
        pstat = __create_custom_collector(collector_name)

    def do_pstat(*args, **kwargs) -> object:
        """
        Performs the timing operations for the
        wrapped function
        """

        pstat.start()
        results = func(*args, **kwargs)
        pstat.stop()

        return results

    do_pstat.__name__ = func.__name__
    do_pstat.__dict__ = func.__dict__
    do_pstat.__doc__ = func.__doc__

    return do_pstat

# Simplified decorator alias
pstat = stat_collection