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
import re

from panda3d_gemstone.logging.utilities import get_notify_category

from panda3d_gemstone.framework.internal_object import PandaBaseObject
from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.cast import cast
from panda3d_gemstone.framework.utilities import get_snake_case

from panda3d_gemstone.engine import runtime

__service_notify = get_notify_category('service')

class Command(object):
    """
    Represents a command that can be registered with a 
    Service object instance
    """

    def __init__(self, name: str, func: object, *args):
        self.name = name
        self.func = func
        self.args = list(args)

    def __call__(self, *args) -> None:
        """
        Custom call handler to execute our command
        handler function
        """

        self.func(*(list(self.args) + list(args)))

    def destroy(self) -> None:
        """
        Destroys the Command object instance
        freeing it from memory
        """

        self.name = None
        self.func = None
        self.args = []

class State(Command):
    """
    Represents a state based command for the Service
    objects to register
    """

    def __init__(self, name: str, *initial_value):
        super().__init__(self, name, self.set_state)
        self.args = []
        
        if len(initial_value) == 0:
            self.set_state(initial_value[0])
        else:
            self.set_state(initial_value)

    @property
    def value(self) -> object:
        """
        Returns this State objects current state
        """

        return self.get_state()

    def destroy(self) -> None:
        """
        Destroys the State object instance
        freeing it from memory
        """

        self.state = None
        Command.destroy(self)

    def set_state(self, state: object, *args) -> None:
        """
        Sets the state variable
        """

        self.state = state

    def get_state(self) -> object:
        """
        Returns the current state variable
        """

        return self.state

def register_command(*args):
    """
    Registers a service function as a command 
    """

    def decorate(f: object) -> None: 
        """
        Custom decorator for attaching the __events__ attribute
        to the class function for use by the Service's startup intializer
        """

        setattr(f, '__events__', args)

    return decorate

class Service(object):
    """
    Base class for all services. Allows the registering of commands inside a
    Gemstone application
    """

    def __init__(self, name: str = None, priority: int = 0, initialize_handle_attributes_as_commands: bool = True):
        self.__name = name if name else get_snake_case(self.__class__.__name__)
        self.__priority = priority
        self.__running = False
        self.__commands = {}

        if initialize_handle_attributes_as_commands:
            self.__initialize_commands()

        self.reset_commands_being_called()

    @property
    def service_name(self) -> str:
        """
        Returns the service's name as a property
        """

        return self.get_service_name()

    @service_name.setter
    def service_name(self, service_name: str) -> None:
        """
        Sets the service's name as a setter
        """

        self.set_service_name(service_name)

    @property
    def service_priority(self) -> int:
        """
        Returns the service's priority as a property
        """

        return self.get_service_priority()

    @service_priority.setter
    def service_priority(self, priority: int) -> None:
        """
        Sets the service's priority as a setter
        """

        self.set_service_priority(priority)

    def destroy(self) -> None:
        """
        Destroys the service object
        """

        self.deactivate()
        self.__deinitialize_commands()
    
        for command in list(self.__commands.keys()):
            self.remove_command(command)

        self.__commands = {}

    def get_commands_being_called(self) -> bool:
        """
        """

        return self.__commands_called

    def reset_commands_being_called(self) -> bool:
        """
        """

        self.__commands_called = False

    def set_commands_being_called(self) -> bool:
        """
        """

        self.__commands_called = True

    def __initialize_commands(self) -> None:
        """
        """

        service_manager = ServiceManager.get_singleton()
        command_methods = [(name, obj) for name, obj in inspect.getmembers(self) if inspect.ismethod(obj)]

        for name, method in command_methods:
            events = getattr(method, '__events__', None)
            if not events:
                continue

            self.add_command(Command(name, method))
            for event in events:
                if type(event) == type(()):
                    service_manager.register_event(event[0], self.get_service_name(), name, *event[1:])
                else:
                    service_manager.register_event(event, self.get_service_name(), name)

    def __deinitialize_commands(self) -> None:
        """
        """

        service_manager = ServiceManager.get_singleton()
        command_methods = [(name, obj) for name, obj in inspect.getmembers(self) if inspect.ismethod(obj)]

        for name, method in command_methods:
            events = getattr(method, '__events__', None)
            if not events:
                continue

            for event in events:
                if type(event) == type(()):
                    service_manager.unregister_event(event[0], name)
                else:
                    service_manager.unregister_event(event, name)        

    def get_service_name(self) -> str:
        """
        """

        return self.__name

    def set_service_name(self, name: str) -> None:
        """
        """

        self.__name = name

    get_name = get_service_name
    set_name = set_service_name

    def get_service_priority(self) -> int:
        """
        """

        return self.__priority

    def set_service_priority(self, priority: int) -> None:
        """
        """

        self.__priority = priority

    def add_command(self, command: Command, dev: bool = False) -> None:
        """
        Adds a new command handler to the service instance
        """

        # Check if we need to restrict this command based
        # on developer build status
        if dev and not runtime.is_developer_build():
            return

        if command.name in self.__commands:
            __service_notify.warning('command "%s" is already defined for "%s"!. Overriding handler' % (command.name, self.__class__.__name__))

        self.__commands[command.name] = command

    def remove_command(self, command_name: str) -> None:
        """
        Attempts to remove a command handler from the service
        instance
        """

        if command_name not in self.__commands:
            __service_notify.warning('Failed to remove command. Command "%s" is not defined' % (command_name))
            return

        self.__commands[command_name].destroy()
        del self.__commands[command_name]

    def get_command(self, command_name: str) -> Command:
        """
        """

        return self.__commands.get(command_name, None)

    def has_command(self, command_name: str) -> bool:
        """
        """

        return command_name in self.__commands

    def run_command(self, command_name: str, *args) -> bool:
        """
        Runs the requested command
        """

        if not self.__running:
            return False

        command = self.get_command(command_name)
        if not command:
            __service_notify.warning('run_command failed: %s is not a known command' % command_name)
            return False

        callable = not inspect.iscoroutinefunction(command)
        if not callable:
            __service_notify.warning('run_command failed: Command %s needs to be run async' % command_name)
            return False

        self.set_commands_being_called()
        command(*args)

    async def run_async_command(self, command_name: str, *args) -> bool:
        """
        Runs the requested command in async form
        """

        if not self.__running:
            return False

        command = self.get_command(command_name)
        if not command:
            __service_notify.warning('run_command failed: %s is not a known command' % command_name)
            return False

        awaitable = not inspect.iscoroutinefunction(command)
        self.set_commands_being_called()

        if awaitable:
            await command(*args)
        else:
            command(*args)

    def activate(self) -> bool:
        """
        Activates the service object
        """

        if self.__running:
            return False

        ServiceManager.get_singleton().activate(self)
        self.__running = True

        return True

    def deactivate(self) -> bool:
        """
        Deactivates the service object
        """

        if not self.__running:
            return False

        ServiceManager.get_singleton().deactivate(self)
        self.__running = False

        return True

    def is_activated(self) -> bool:
        """
        """

        return self.__running

    def get_state(self, command_name: str) -> object:
        """
        Retrieves the state from a command instance if present
        """

        if command_name not in self.__commands:
            __service_notify.warning('Failed to get state; Unknown state: %s' % command_name)
            return
        
        command = self.__commands[command_name]
        return command.get_state()

    def set_state(self, command_name: str, state: object) -> None:
        """
        """

        if command_name not in self.__commands:
            __service_notify.warning('Failed to set state; Unknown state: %s' % command_name)
            return

        command = self.__commands[command_name]
        command.set_state(state)        

    __getitem__ = get_state
    __setitem__ = set_state

    def __str__(self) -> str:
        """
        """

        mapping = ServiceManager.get_singleton().get_events(self)
        mapping.sort()

        s = ''
        for event, command_name in mapping:
            s += '%s: %s\n' % (command_name, event)

        return s

class ServiceManager(Singleton, PandaBaseObject):
    """
    Service manager for handling commands and events in the gemstone framework
    """

    ACTION_SERVICE_RE = '[^\t\n\r\x0c\x0b\\:]+'
    ACTION_NAME_RE = '[^\t\n\r\x0c\x0b\\(]+'
    ACTION_ARGS_RE = '[^\t\n\r\x0c\x0b\\)]+'
    ACTION_RE = re.compile('\\s*(' + ACTION_SERVICE_RE + ':)*(' + ACTION_NAME_RE + ')\\s*(?:\\((' + ACTION_ARGS_RE + ')\\))?\\s*:\\s*(\\S+)')

    def __init__(self):
        Singleton.__init__(self)
        PandaBaseObject.__init__(self)

        self.services = []
        self.events = {}
        self.__activated = True

    async def __select_highest_priority_services(self, command_name: str) -> list:
        """
        """

        services = {}
        for service in self.services:
            if service.has_command(command_name):
                priority = service.get_service_priority()
                if priority in services:
                    services[priority].append(service)
                else:
                    services[priority] = [service]

        if not services:
            self.notify.warning('Failed to select highest priority services. No services found')
            return []
        
        priorities = list(services.keys())
        priorities.sort(reverse=True)
        return services[priorities[0]]

    async def __dispatch(self, event: object, *event_args) -> None:
        """
        Receives an incoming event from the Panda3D messenger and redirects
        it into a Gemstone service command to dispatch
        """

        if not self.__activated:
            self.notify.warning('Attempting to dispatch event while not active (%s)' % event)
            return

        commands = self.events[event]
        for service_name, command_name, args in commands:
            await self.dispatch(command_name, service_name, *(event_args + args))

    async def dispatch(self, command_name: str, service_name: str = None, *args) -> None:
        """
        Dispatches a command to the requested service if available. Otherwise 
        dispatches to all services in the application if they consume the fired
        command
        """

        services = await self.__select_highest_priority_services(command_name)
        if not len(services):
            self.notify.warning('Failed to dispatch command "%s". No services found' % (
                command_name))
            
            return

        for service in services:

            if service_name and service_name != service.get_service_name():
                continue

            command = service.get_command(command_name)
            if command:
                service.set_commands_being_called()

                awaitable = inspect.iscoroutinefunction(command)
                if awaitable:
                    await command(*args)
                else:
                    command(*args)

    def register_event(self, event: str, service_name: str, command_name: str, *args) -> None:
        """
        Registers an event with the service manager
        """

        if event not in self.events:
            self.events[event] = []
            self.notify.debug('Registering event "%s" to command "%s" from service "%s"' % (
                event, command_name, service_name))
            self.accept(event, self.__dispatch, [event])

        self.events[event].append((service_name, command_name, args))

    def unregister_event(self, event: str, service_name: str, command_name: str) -> None:
        """
        Unregisters an event from the service manager
        """

        if command_name is None:
            del self.events[event]
        else:
            rem = []

            for i, info in enumerate(self.events[event]):
                if info[1] == command_name:
                    rem.append(i)

            for i in rem.__reversed__():
                del self.events[event][i]

    def get_events(self, service: Service = None) -> list:
        """
        Returns all registered events within the service manager
        """

        if service:
            return [(event, command_name) for event, data in list(self.events.items()) for service_name, command_name, args in data if service_name == service.get_service_name()]
        else:
            return list(self.events.keys())

    def activate(self, service: Service = None) -> None:
        """
        Activates a service with the ServiceManager singleton
        """

        if not service:
            self.__activated = True
            return

        if service not in self.services:
            self.services.append(service)

    def deactivate(self, service: Service = None) -> None:
        """
        Deactivates a service from the ServiceManager singleton
        """

        if not service:
            self.__activated = False
            return

        if service not in self.services:
            self.services.remove(service)

    def parse(self, lst: object, path: str = None) -> None:
        """
        """

        def syntax_error(line: str, line_nr: int) -> None:
            """
            Logs a syntax error
            """

            if path != None:
                self.notify.warning('Syntax error "%s" (#%d) in file: %s' % (line, line_nr, path))
            else:
                self.notify.warning('Syntax error "%s" (#%d)' % (line, line_nr))

        line_nr = 0
        for line in lst:
            line_nr += 1
            stripped_line = line.strip()
            if stripped_line and stripped_line[0] != '#':
                m = ServiceManager.ACTION_RE.match(line)
                if not m:
                    syntax_error(line, line_nr)
                    continue
            
                args = []
                service_name, command_name, command_args, event = m.groups()
                if service_name:
                    service_name = service_name[:-1]
                
                if command_args:
                    args = list(map(cast, command_args.split(',')))
                
                self.register_event(event, service_name, command_name, *args)

    def load(self, path: str) -> None:
        """
        Opens an event map ini config file from the application's VFS and loads it
        into the service manager instance
        """

        self.parse(open(path, 'r'), path=path)

    @classmethod
    def analyze_services(cls) -> None:
        """
        Analyzes the application services. Printing debug
        information to the console
        """

        singleton = cls.get_singleton()

        print('--------------------------------------------------------')
        print(str(singleton))
        print('--------------------------------------------------------')

    def __str__(self) -> str:
        """
        Custom string handler for returning a debug string about the ServerManager singleton
        for debugging purposes
        """

        s = ''
        s += 'Active Services\n'
        s += 'Class Instance\n--------------------------------------------------------\n'
        for service in self.services:
            cls_name = service.__class__.__name__
            name = ''
            if hasattr(service, 'get_service_name'):
                name = service.get_service_name()
            s += '%s%s%s\n' % (service.__class__.__name__, ' ' * (30 - len(cls_name)), name)

        s += '\nActive Event Mapping\n'
        s += 'Event Service Command -> Call\n--------------------------------------------------------\n'
        events = list(self.events.keys())
        events.sort()

        for event in events:
            s += '%s' % event
            first_line = True
            for service_name, command_name, args in self.events[event]:
                for service in self.services:
                    if service_name and service_name != service.get_service_name():
                        continue

                    command = service.get_command(command_name)
                    if not command:
                        continue
                    
                    service_name = service.__class__.__name__
                    if hasattr(service, 'get_service_name') and service.get_service_name():
                        service_name = service.get_service_name()

                    if first_line:
                        first_line = False
                        s += ' ' * (30 - len(event))
                    else:
                        s += ' ' * 30

                    func = command.func
                    if hasattr(func, 'im_class'):
                        cls = command.func.__self__.__class__.__name__ + '.'
                    else:
                        cls = ''
                    
                    s += '%s %s -> %s%s%s\n' % (
                        service_name, command.name, cls, command.func.__name__, str(tuple(command.args) + tuple(args)))

                if first_line:
                    s += ' (unassigned)%s%s%s\n' % (' ' * (30 - len(event) - len(' (unassigned)')), command_name, str(tuple(args)))

        return s