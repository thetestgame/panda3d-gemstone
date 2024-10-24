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

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.engine import prc

def get_gemstone_modules() -> list:
    """
    Returns all modules used by all gemstone applications
    """

    return [
        'panda3d_gemstone.application',
        'panda3d_gemstone.controllers',
        'panda3d_gemstone.engine',
        'panda3d_gemstone.framework',
        'panda3d_gemstone.game',
        'panda3d_gemstone.gui',
        'panda3d_gemstone.io',
        'panda3d_gemstone.network',
        'panda3d_gemstone']

def __file_exists(path: str) -> bool:
    """
    Returns true if the file exists
    """

    return os.path.exists(path)

class CompilerError(RuntimeError):
    """
    Base error for all compiler errors
    """

class InvalidCompileError(CompilerError):
    """
    Thrown when an invalid compile operation occures
    """

class BuildTarget(object):
    """
    Represents a build target for the Panda3D compiler
    """

    def __init__(self, key: str, executable: str, includes: list = [], modules: list = [], icons: list = [], plugins: list = []):
        self.__key = key
        self.__executable = executable
        self.__includes = includes
        self.__modules = modules
        self.__icons = icons
        self.__plugins = plugins

    @property
    def key(self) -> str:
        """
        Returns this build target's key
        """

        return self.__key

    @property
    def executable(self) -> str:
        """
        Returns this build target's executable file
        """

        return self.__executable

    @property
    def includes(self) -> list:
        """
        Returns this build target's include list
        """

        return self.__includes

    @property
    def modules(self) -> list:
        """
        Returns this build target's module list
        """

        return self.__modules

    @property
    def icons(self) -> list:
        """
        Returns this build target's icon list
        """

        return self.__icons

    @property
    def plugins(self) -> list:
        """
        Returns this build target's required plugins
        """

        return self.__plugins

    def is_valid(self) -> bool:
        """
        Returns true if this build target is valid
        """

        valid = True

        # Verify the executable file exists
        if not __file_exists(self.__executable):
            valid = False

        return valid

class GemstoneCompiler(InternalObject):
    """
    Base tool for compiling Gemstone applications using
    the Panda3D game engine build system
    """

    def __init__(self, application: str, prc: list = [], debug: bool = False):
        InternalObject.__init__(self)
        self.__application = application
        self.__prc = prc
        self.__debug = debug
        self.__targets = []

    @property
    def targets(self) -> list:
        """
        Returns this compiler objects build targets
        """

        return self.__targets

    def __load_prc_files(self) -> None:
        """
        Loads the compilers prc files
        """

        for prc_file in self.__prc:
            prc.load_prc_file(prc_file)

    def setup(self) -> None:
        """
        Performs setup operations on the compiler
        object instance
        """

        self.__load_prc_files()

    def destroy(self) -> None:
        """
        Performs the compiler objects destruction 
        operations
        """

        InternalObject.destroy(self)

    def add_build_targets(self, targets: list) -> None:
        """
        Adds a list of build targets to the compiler
        """

        for target in targets:
            self.add_build_target(target)

    def get_build_target_by_key(self, key: str) -> BuildTarget:
        """
        Registers a list of build targets with the compiler
        """

        target = None
        for target in self.__targets:
            if target.key == key:
                found = target
                break
        
        return target

    def add_build_target(self, target: BuildTarget) -> None:
        """
        Registers a new build target with the compiler
        """

        # Verify a target does not already exist
        if self.get_build_target_by_key(target.key) != None:
            raise InvalidCompileError('Failed to add target: %s. Target already exists with that key' % target.key)

        self.__targets.append(target)

    def __get_include_patterns(self) -> dict:
        """
        Gets the include patterns required by this compiler's
        build targets
        """

        includes = {}
        include_count = 0
        for target in self.__targets:
            includes[target.key] = target.includes
            include_count += len(target.includes)

        if include_count == 0:
            self.notify.warning('No includes identified. You may experience unexpected behaviour')

        return includes

    def __get_include_modules(self) -> dict:
        """
        Gets the include modules required by this compiler's
        build targets
        """

        modules = {}
        module_count = 0
        for target in self.__targets:
            modules[target.key] = target.modules
            module_count += len(target.modules)

        if module_count == 0:
            self.notify.warning('No modules identified. You may experience unexpected behaviour')

        return modules

    def __get_gui_apps(self) -> dict:
        """
        Gets the gui apps required by this compiler's 
        build targets
        """

        apps = {}
        for target in self.__targets:
            apps[target.key] = target.executable

        if len(apps) == 0:
            raise InvalidCompileError('Failed to compile %s. No GUI apps defined' % self.__class__.__name__)

        return apps

    def __get_icons(self) -> dict:
        """
        Gets the icons required by this compiler's 
        build targets
        """

        icons = {}
        icon_count = 0
        for target in self.__targets:
            icons[target.key] = target.icons
            icon_count += len(target.icons)

        if icon_count == 0:
            self.notify.warning('No icons identified. You may experience unexpected behaviour')

        return icons 

    def __get_plugins(self) -> list:
        """
        Gets the plugins required by the compiler's 
        build targets
        """

        identified = []
        for target in self.__targets:
            for plugin in target.plugins:
                if plugin not in identified:
                    identified.append(plugin)

        if len(identified) == 0:
            self.notify.warning('No plugins identified. You may experience unexpected behaviour.')

        return identified

    def __get_log_filename(self) -> str:
        """
        Returns the log filename used by the compiler
        """

        return prc.get_prc_string('gs-compiler-log', './%s-output.txt' % self.__class__.__name__)

    def __get_build_options(self) -> dict:
        """
        Returns the setup options used by the application
        to compile the Gemstone application
        """

        options = {
            'include_patterns': self.__get_include_patterns(),
            'include_modules': self.__get_include_modules(),
            'gui_apps': self.__get_gui_apps(),
            'icons': self.__get_icons(),
            'log_filename': self.__get_log_filename(),
            'log_append': prc.get_prc_bool('gs-compiler-log-append', False),
            'plugins': self.__get_plugins()
        }

        if self.__debug:
            print('\n==== Compiler Options ====\n')
            self.__dump_dict_to_console(options)
            print('\n')

        return options

    def __dump_dict_to_console(self, data: dict) -> None:
        """
        Dumps a dictionary to console for debugging
        """

        import json
        print(json.dumps(data, indent=4))

    def __get_compiler_setup(self) -> object:
        """
        Returns the setup tools setup object
        for use in the Gemstone application
        compiling process
        """

        from setuptools import setup
        return setup

    def __get_application_version(self) -> str:
        """
        Returns this application's version
        """

        from panda3d_gemstone.application.version import ApplicationVersion
        version_inst = ApplicationVersion.instantiate_singleton()

        return '%s.%s.%s' % version_inst.get()

    def compile(self) -> object:
        """
        Performs the application compiling process.
        Intended to be called from the setup file
        in the Gemstone applications root directory
        """

        if len(self.__targets) == 0:
            raise InvalidCompileError('Failed to compiler %s. No build targets found' % (
                self.__application))

        setup_cls = self.__get_compiler_setup()
        compiler_setup = setup_cls(
            name=self.__application,
            version=self.__get_application_version(),
            options={'build_apps': self.__get_build_options()})

        return compiler_setup

