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

import inspect
from panda3d_gemstone.engine import runtime

def event_handler(*args):
    """
    Registers a message listener event handler
    """

    def decorate(f: object) -> None:
        """
        Custom decorator for attaching the __messenger__ attribute
        to the class function for use by the MessengeListener's startup 
        initializer
        """

        setattr(f, '__messenger__', args)

    return decorate

class MessageListener(object):
    """
    Base class for all objects that listen for Messenger events. Accepts manual
    registering of events or automatically via the @event_handler decorator
    """

    def __init__(self, initialize_event_attributes: bool = True):
        if initialize_event_attributes:
            self.__initialize_events()

    def destroy(self) -> None:
        """
        Destroys the MessengerListener object
        """

        self.ignore_all()

    def __initialize_events(self) -> None:
        """
        Initializes the decorator set event handlers
        """

        event_methods = [(name, obj) for name, obj in inspect.getmembers(self) if inspect.ismethod(obj)]
        for name, method in event_methods:
            event = getattr(method, '__messenger__', None)
            if not event:
                continue

            self.accept(event[0], method, *events[1:])

    def accept(self, event: str, method: object, extra_args: list = []) -> object:
        """
        """

        return runtime.messenger.accept(event, self, method, extra_args, 1)

    def accept_once(self, event:str , method: object, extra_args: list = []) -> object:
        """
        """

        return runtime.messenger.accept(event, self, method, extra_args, 0)

    def ignore(self, event: str) -> object:
        """
        """

        return runtime.messenger.ignore(event, self)

    def ignore_all(self) -> object:
        """
        """

        return runtime.messenger.ignoreAll(self)

    def is_accepting(self, event: str) -> object:
        """
        """

        return runtime.messenger.isAccepting(event, self)

    def get_all_accepting(self) -> object:
        """
        """
        
        return runtime.messenger.getAllAccepting(self)

    def is_ignoring(self, event: str) -> object:
        """
        """

        return runtime.messenger.isIgnoring(event, self)