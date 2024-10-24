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
import copy
import configparser
import pickle

from panda3d_gemstone.logging.utilities import get_notify_category
from panda3d_gemstone.engine import runtime, prc

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.io.file_system import get_file_date
from panda3d_gemstone.framework.cast import cast
from panda3d_gemstone.framework.utilities import get_snake_case

from panda3d.core import ConfigVariableBool, VirtualFileSystem
from panda3d.core import Filename

_config_notify = get_notify_category('configurable')

class BaseConfigurableCache(InternalObject):
    """
    Base class for all configurable cache handlers
    """

class VFSConfigurableCache(BaseConfigurableCache):
    """
    Caching object for the configuration files
    loaded from the Panda3D virtual file
    system
    """

    vfs = VirtualFileSystem.get_global_ptr()

    def __init__(self):
        super().__init__()
        self.__files = {}

    def read(self, filepath: str, cls: object) -> object:
        """
        Reads the requested file from the cache
        """

        filepath_dat = OSConfigurableCache.get_cache_filename(filepath)
        if filepath not in self.__files:
            filepath_dat_name = Filename(filepath_dat)
            fh = self.vfs.get_file(filepath_dat_name)
            if fh:
                reader = pickle.loads(fh.read_file(True))
                self.__files[filepath] = reader
            fh = None

        if filepath not in self.__files:
            self.notify.warning('Failed to read file: %s. Not found' % filepath)
            return

        return self.__files[filepath]

    def get_notify_name(self) -> str:
        """
        Returns this object's custom notifier name
        """

        return 'vfs-configurable-cache'

class RawOSConfigurableCache(BaseConfigurableCache):
    """
    Caching object for configuration files loaded from
    the operation system's IO without using binary dat
    files
    """

    def __init__(self):
        super().__init__()
        self._files = {}

    def __read_file(self, filepath: str, clsName: str) -> configparser.ConfigParser:
        """
        """

        reader = configparser.ConfigParser()
        reader.optionxform = str
        self.notify.info('Reading config: %s' % filepath)

        try:
            if not reader.read(filepath):
                self.notify.warning('Failed to load ini file "%s". Path does not exist' % (filepath))
                return None
        except Exception as e:
            self.notify.error('Failed to read ini file "%s": %s' % (filepath, str(e)))
            return None

        return reader

    def read(self, filepath: str, cls) -> object:
        """
        Reads the requested file from the cache
        """

        # Add the file to the cache if not already added
        if filepath not in self._files:
            reader = self.__read_file(filepath, cls.__name__)
            self._files[filepath] = (reader, get_file_date(filepath))

        return self._files[filepath][0]

    def get_notify_name(self) -> str:
        """
        Returns this object's custom notifier name
        """

        return 'raw-os-configurable-cache'

class OSConfigurableCache(BaseConfigurableCache):
    """
    Caching object for configuration files loaded from the
    operation system's IO 
    """

    def __init__(self):
        super().__init__()
        self._files = {}
        self._use_dat = ConfigVariableBool('gs-use-dat', False).value

    @staticmethod
    def get_cache_filename(filepath: str) -> str:
        """
        Returns the cache filename for the requested file path
        """

        output, ext = os.path.splitext(filepath)
        output += '.dat'

        return output

    def __read_file(self, filepath: str, clsName: str) -> configparser.ConfigParser:
        """
        """

        reader = configparser.ConfigParser()
        reader.optionxform = str
        self.notify.info('Reading config: %s' % filepath)

        try:
            if not reader.read(filepath):
                self.notify.warning('Failed to load ini file "%s". Path does not exist' % (filepath))
                return None
        except Exception as e:
            self.notify.error('Failed to read ini file "%s": %s' % (filepath, str(e)))
            return None

        return reader

    def read(self, filepath: str, cls) -> object:
        """
        Reads the requested file from the cache
        """

        dat_file = OSConfigurableCache.get_cache_filename(filepath)
        if get_file_date(filepath) > get_file_date(dat_file):

            # Create a new dat file if it does not exist
            try:
                reader = self.__read_file(filepath, cls.__name__)
                if reader:
                    fh = open(dat_file, 'wb')
                    fh.write(pickle.dumps(
                        reader,
                        protocol=pickle.HIGHEST_PROTOCOL))
                    fh.close()
            except IOError:
                pass

        # Add the file to the cache if not already added
        if filepath not in self._files:
            if get_file_date(dat_file) and self._use_dat:
                fh = open(dat_file, 'rb')
                reader = pickle.load(fh.read())
                fh.close()

                self._files[filepath] = (reader, get_file_date(dat_file))
            else:
                reader = self.__read_file(filepath, cls.__name__)
                self._files[filepath] = (reader, get_file_date(dat_file))
        elif get_file_date(dat_file) > self._files[filepath][1]:
            reader = pickle.load(open(dat_file, 'rb'))
            self._files[filepath] = (reader, get_file_date(dat_file))

        if filepath not in self._files:
            self.notify.warning('Failed to read file: %s. Not found' % filepath)
            return

        return self._files[filepath][0]

    def get_notify_name(self) -> str:
        """
        Returns this object's custom notifier name
        """

        return 'os-configurable-cache'

class Configurable(object):
    """
    Represents a configurable object in the Gemstone framework
    """

    __include_str = '__include__'
    __cache = OSConfigurableCache()

    def __init__(self, path: str, section: str = 'Configuration', auto_configure: bool = False, fixup_include_path_func: object = None, override_cache: object = None):
        self.__config = None
        self._included_config = None
        self._fixup_include_path_func = fixup_include_path_func
        self.__want_config_warnings = prc.get_prc_bool('gs-config-warnings', False)
        
        if not hasattr(self, 'path'):
            self.path = path
            self.section = section

        self.auto_configure = auto_configure
        self.configuration = {}
        self._override_cache = override_cache

        if path:
            self.load(path, section)

    @property
    def config(self) -> object:
        """
        Returns this configurables working config value
        """

        self.__config

    def __prepare_data(self, data: dict) -> dict:
        """
        Prepares the incoming data
        by casting it to its respective type
        """

        new_data = {}
        for key, value in data:
            new_data[key] = cast(value)

        return new_data

    def __fixup_include_config_path(self, config_path: str) -> str:
        """
        Runs the fixup include path function on the config path 
        if provided on construction
        """

        if not self._fixup_include_path_func:
            return config_path
        
        return self._fixup_include_path_func(config_path)

    def load(self, opath = None, osection = None) -> None:
        """
        Loads the configuration from the applications
        file system into memory
        """

        # Load the appropriate cache for the configuration
        # load operation
        if self._override_cache is not None:
            cache = self._override_cache
        else:
            cache = Configurable.__cache

        # Read the data from the cache and begin processing
        self.__config = cache.read(opath or self.path, self.__class__)
        if not self.__config:
            return

        processed_section = []
        main_section = osection or self.section

        if self.__config.has_section(main_section):
            data = self.__config.items(main_section)

            # Process include path if present
            include_path = dict(data).get(Configurable.__include_str)
            if include_path:
                included_configurable = Configurable(
                    path=self.__fixup_include_config_path(include_path),
                    fixup_include_path_func=self._fixup_include_path_func)
                self._included_config = included_configurable.config
                self.configuration = copy.copy(included_configurable.configuration)
                processed_section.append(main_section)

            # Populate section data in configuration dict
            for key, value in data:
                if key != Configurable.__include_str:
                    self.configuration[key] = cast(value) 

        # Load all sections in our configuration object
        for section in self.__config.sections():
            if section != main_section:
                data = self.__config.items(section)
                if self._included_config and self._included_config.has_section(section):
                    included_data = self._included_config.items(section)
                    included_data.extend(data)
                    data = included_data

                    self.__config.remove_section(section)
                    self.__copy_section(section, data)
                    processed_section.append(section)
                
                self.__load_section(section, data)
        
        # Process any included configurations
        if self._included_config:
            for section in self._included_config.sections():
                if section not in processed_section:
                    data = self._included_config.items(section)
                    self.__load_section(section, data)
                    self.__copy_section(section, data)

        self._included_config = None
        self._fixup_include_path_func = None

    def __copy_section(self, section: str, data: object) -> None:
        """
        Copys a section of data to the current configuration
        object instance
        """

        temp = dict(data)
        self.__config.add_section(section)

        # Population section with data
        for key, value in temp.items():
            self.__config.set(section, key, value)

    def __get_loader_name(self, section: str) -> str:
        """
        Returns the loader name for the
        requested config section
        """
        
        snake_case = get_snake_case(section)
        return 'load_%s_data' % snake_case

    def __load_section(self, section: str, data: object) -> None:
        """
        Loads the requested section into the
        configurable object
        """

        # Retrieve the loader function if present
        loader_name = self.__get_loader_name(section)

        # Process the section's data
        if hasattr(self, loader_name):
            loader = getattr(self, loader_name)
            loader(self.__prepare_data(data))
        else:
            if self.__want_config_warnings:
                _config_notify.warning('Failed to load section for %s. Section loader "%s" does not exist' % (
                    self.__class__.__name__, section))
            self.load_data(section, self.__prepare_data)

    def __get_snake_case(self, label: str) -> str:
        """
        Returns the label as a snake case variant
        """

        return get_snake_case(label)

    def __get_setter_name(self, key: str) -> str:
        """
        Returns the attributes setter name
        from its configuration key
        """

        setter_name = 'set_%s' % (self.__get_snake_case(key))
        return setter_name

    def initialize(self) -> None:
        """
        Performs inintialization operations
        on the configurable object
        """

        if not isinstance(self.configuration, dict):
            _config_notify.warning('Failed to initialize %s. Configuration is not a valid type (%s) expected dict' % (
                self.__class__.__name__, self.configuration.__class__.__name__))
            
            return

        for key, value in list(self.configuration.items()):
            setter_name = self.__get_setter_name(key)
            setter = getattr(self, setter_name, None)

            if setter:
                self.notify.debug('(Setter) %s: %s' % (setter_name, str(value)))
                if isinstance(value, tuple):
                    setter(*value)
                else:
                    setter(value)
            elif self.auto_configure:
                setattr(self, key, value)
            else:
                _config_notify.warning('%s does not implement setter: %s' % (
                    self.__class__.__name__, setter_name))

        self.configuration = {}
        self.__config = None
        self._included_config = None

    def load_data(self, section: str, data: object) -> None:
        """
        Processes the incoming data from a config section. 
        Intended to be overridden by child objects
        """

        if self.__want_config_warnings:
            _config_notify.warning('%s does not implement general section loader "load_data"' % (
                self.__class__.__name__))

    def pop(self, attr: str, default: object = None) -> object:
        """
        Pops the requested attribute from the 
        configuration dictionary
        """

        return self.configuration.pop(attr, default)

    def pop_as(self, attr: str, cls: object, default: object = None) -> object:
        """
        Pops the requested attribute from the 
        configuration dictionary and passes it as the first argument
        into the provided cls object
        """

        assert cls != None

        variable = self.pop(attr, default)
        assert variable != None

        return cls(variable)

    def pop_call(self, attr: str, func: object, default: object = None, **kwargs) -> object:
        """
        Pops the requested attribute from the configuration dictionary
        and passes it into the function callback returning the result
        """

        assert func != None
        assert callable(func)

        variable = self.pop(attr, default)
        assert variable != None

        return func(variable, **kwargs)

    def get(self, attr: str, default: object = None) -> object:
        """
        Retrieves the requested attribute from
        the configuration dictionary
        """

        return self.configuration.get(attr, default)

    def get_as(self, attr: str, cls: object, default: object = None) -> None:
        """
        Retrieves the requested attribute from the configuration
        dictionary and passes it as the first argument in the cls 
        object
        """

        assert cls != None

        variable = self.get(attr, default)
        assert variable != None

        return cls(variable)

    def get_call(self, attr: str, func: object, default: object = None, **kwargs) -> None:
        """
        Retrieves the requested attribute from the configuration
        dictionary and passes it as the first argument into the function 
        returning the results
        """

        assert func != None
        assert callable(func)

        variable = self.get(attr, default)
        assert variable != None

        return func(variable)        

    def reload(self) -> None:
        """
        Reloads the configuration object
        """

        self.load()
        self.initialize()
