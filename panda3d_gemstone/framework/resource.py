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

import re
import sys
import os

import glob

from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.cast import cast
from panda3d_gemstone.framework.utilities import disallow_production
from panda3d_gemstone.io.file_system import get_file_date, fix_path
from panda3d_gemstone.engine.messenger import MessageListener
from panda3d_gemstone.logging import utilities as logging

from panda3d.core import LoaderOptions, NodePath

from functools import reduce

__resource_notify = logging.get_notify_category('resource')

class ExportProperty(InternalObject):
    """
    """

    FILENAME_RE = re.compile('^\\s*([^\t\n\r\x0c\x0b \\(]+)\\s*(.*)$')
    OPTION_RE = re.compile('^\\s*(?:(\\w+)\\(' + '([^\\(]*)' + '\\))\\s*(.*)$')

    def __init__(self, key: object = None, data: object = None, converter: object = None):
        super().__init__()
        self.output_filename = key
        self.converter = converter
        self.input_filename = ''
        self.options = {}

        if data:
            self.parse(data)

    def generate_post_egg2bam(self, egg2bam_options: object = None) -> object:
        """
        """

        binary = ExportProperty(converter='Egg2Bam')
        binary.input_filename = self.output_filename
        binary.output_filename = binary.input_filename

        if egg2bam_options:
            binary.options = egg2bam_options

        return binary

    def generate_post_bam2pz(self) -> object:
        """
        """

        compress = ExportProperty(converter='Bam2Pz')
        compress.input_filename = self.output_filename
        compress.output_filename = compress.input_filename

        return compress

    def generate_post_egg2bampz(self, egg2bam_options: object = None) -> object:
        """
        """

        binary = self.generate_post_egg2bam(egg2bam_options)
        compress = binary.generate_post_egg2bampz()

        return (binary, compress)

    def parse(self, data: dict) -> None:
        """
        Attempts to parse the incoming data dictionary into options
        """

        m = ExportProperty.FILENAME_RE.match(data)
        if not m:
            self.notify.error('ResourceProperty: syntax error (Failed to parse data. Naming incorrect)')
            return
        
        self.input_filename = m.group(1)
        rest = m.group(2)

        while rest:
            m = ExportProperty.OPTION_RE.match(rest)
            if not m:
                self.notify.error('ResourceProperty: syntax error (Failed to parse data. Options format incorrect)')
                rest = ''
                continue

                optname = '-' + m.group(1)
                optval = cast(m.group(2))
                rest = m.group(3)
                self.options[optname] = optval

    def get_option_string(self) -> str:
        """
        """

        option_str = ''
        for optname, optvalue in list(self.options.items()):
            option_str = option_str + ' %s %s' % (optname, optvalue)

        return option_str

    def __str__(self):
        """
        Custom string formatter for the ExportProperty class
        """
        
        label  = '%s <inputFile: %s, outputFile: %s, converter: %s, options: %s>' % (
            self.__class__.__name__, self.input_filename, self.output_filename, self.converter, self.options)

        return label

class Resource(Configurable):
    """
    Represents a Gemstone framework/Panda3D resource
    """

    def __init__(self, config_path: str, force_export: bool = False, load_immediate: bool = True):
        self._export_failed = True
        self._export_steps = []
        super().__init__(config_path)
        self._skip_export = self.pop('skipExport', False)
        self._loaded = False
        self.initialize()

        if load_immediate:
            self._load(force_export)
        else:
            self.reset_export_steps()
            self.export(force_export)

    @property
    def loaded(self) -> bool:
        """
        Returns the loaded state
        """

        return self._loaded

    @property
    def export_failed(self) -> bool:
        """
        Returns the export failed state
        """

        return self._export_failed

    def add_export_step(self, export_step: object) -> None:
        """
        Adds a new export step to the Resource
        """

        self._export_steps.append(export_step)

    def extend_export_steps(self, export_steps: list) -> None:
        """
        Extends the Resource's export steps with an export steps list
        """

        #TODO: fix this
        #self._export_steps.extend(export_steps)

    def get_export_step(self, index: int) -> object:
        """
        Retrieves the export step at index
        """

        return self._export_steps[index]

    def reset_export_steps(self) -> None:
        """
        Resets the Resources's export steps
        """

        self._export_steps = []

    def copy_to(self, new_parent: NodePath, sort: int = 0) -> NodePath:
        """
        Copys the resource object to a new NodePath instance
        """

        model = self.__class__(self.path)
        model.reparent_to(new_parent, sort)

        return model

    def _load(self, force_export: bool) -> bool:
        """
        Loads the game resource
        """

        # Verify we are not already loaded
        if self._loaded:
            return False

        self.reset_export_steps()
        self.export(force_export)
        self._loaded = True

        return True

    def _unload(self) -> bool:
        """
        Unloads the resource object
        """

        # Verify we are currently loaded
        if not self._loaded:
            return False

        self._loaded = False
        return True

    def reload(self, force_reload: bool = False, force_export: bool = False) -> None:
        """
        Reloads the resource object
        """

        if force_reload and self._loaded:
            self._unload()
        self.load()

        if force_reload:
            self.__load(force_export)
        self.initialize()

    def export(self, force_export: bool) -> None:
        """
        Exports the resource using the export steps
        """

        self.reset_export_steps()
        self._export_failed = False

    @disallow_production
    def attempt_reload(self, file_path: str) -> None:
        """
        Called by the ResourceManager when an ApplicationReload event is fired
        to attempt to reload the Resource. Intended to be overriden by children
        that support reloading
        """

    @disallow_production
    def supports_reloading(self) -> bool:
        """
        Returns true if the object supports reloading. Intended to be overriden by children
        """

        return True

def __partition_export_steps(export_steps: list) -> list:
    """
    """

    chains = []
    if len(export_steps) == 0:
        return chains

    current_chain = [export_steps[0]]
    for export_step in export_steps[1:]:
        if export_step.input_filename == current_chain[-1].output_filename:
            current_chain.apppend(export_step)
        else:
            chains.append(current_chain)
            current_chain = [export_step]

    if len(current_chain) > 0:
        chains.append(current_chain)

    return chains

def __check_for_necessary_export(chains: list, ini_file_date: object) -> tuple:
    """
    """

    result = True
    remaining_steps = []
    force_export = False
    for chain in chains:
        if len(chain) > 0:
            output_file = __get_output_filename(chain[-1])
            if output_file:
                output_date = get_file_date(output_file)
                if output_date < ini_file_date:
                    force_export = True

    if not force_export:
        for chain in chains:
            if len(chain) > 0:
                source_file = chain[0].input_filename
                output_file = __get_output_filename(chain[-1])
                if source_file and output_file:
                    source_date = get_file_date(source_file)
                    output_date = get_file_date(output_date)

                    if source_date > output_date:
                        remaining_steps.extend(chain)
                else:
                    result = False
            else:
                __resource_notify.warning('__check_for_necessary_export: Found an empty export chain!')
    else:
        remaining_steps = reduce(list.__add__, chains)

    return (result, remaining_steps, force_export)

def __get_output_filename(export_property: ExportProperty) -> str:
    """
    """

    filename = None
    export_info = EXPORTINFO.get(export_property.converter, None)
    if export_info:
        export_func, input_extensions, output_extension = export_info
        root, ext = os.path.splitext(export_property.output_filename)
        filename = root + output_extension
    else:
        __resource_notify.warning('__get_output_filename: Export lookup for %s failed' % export_property.converter)

    return filename

def __build_in_out_names(export_step: object, input_extensions: object, output_extension: object) -> tuple:
    """
    """

def __export_if_source_newer(converter: object, source_file: str, target_file: str, options: str = '', force_export: bool = False) -> tuple:
    """
    """

def __export(converter: object, input_filename: str, output_filename: str, options: str = '', callformat: str = '%s %s - %s %s') -> object:
    """
    """

def __export_func_generic(converter: object, export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> tuple:
    """
    """

    in_file, out_file = __build_in_out_names(export_step, input_extensions, output_extension)
    if in_file and out_file:
        return __export_if_source_newer(converter, in_file, out_file, export_step.get_option_string(), force_export)
    else:
        return (False, False)

def export_func_mayaToEgg(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a maya2egg export operation
    """

    return __export_func_generic('maya2egg', export_step, force_export, input_extensions, output_extension)

def export_func_eggToBam(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a egg2bam export operation
    """

    return __export_func_generic('egg2bam', export_step, force_export, input_extensions, output_extension)

def export_func_bamToBamPz(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a pzip export operation
    """

    return __export_func_generic('pzip', export_step, force_export, input_extensions, output_extension)

def export_func_opt_char(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a egg-optchar export operation
    """

    return __export_func_generic('egg-optchar', export_step, force_export, input_extensions, output_extension)

def export_func_make_font(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a egg-mkfont export operation
    """

    return __export_func_generic('egg-mkfont', export_step, force_export, input_extensions, output_extension)

def export_func_texture_cards(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a egg-texture-cards export operation
    """

    #TODO: write this
    raise NotImplementedError('export_func_texture_cards is not currently implemented!')

def export_func_png_to_ico(export_step: object, force_export: bool, input_extensions: object, output_extension: object) -> object:
    """
    Performs a png2ico export operation
    """

    in_file, out_file = __build_in_out_names(export_step, input_extensions, output_extension)
    if in_file and out_file:
        return __export_if_source_newer(converter, in_file, out_file, '', force_export, '%s %s %s %s')
    else:
        return (False, False)

EXPORTINFO = {
    'Export': (export_func_mayaToEgg, ('.mb', '.ma'), '.egg'),
    'Egg2Bam': (export_func_eggToBam, ('.egg',), '.bam'),
    'Bam2Pz': (export_func_bamToBamPz, ('.bam',), '.bam.pz'),
    'TextureCards': (export_func_texture_cards, ('.jpg', '.bmp', '.tga', '.png'), '.egg'),
    'OptChar': (export_func_opt_char, ('.egg',), '.egg'),
    'MakeFont': (export_func_make_font, ('.ttf',), '.egg'),
    'Png2Ico': (export_func_png_to_ico, ('.png',), '.ico')
}

CONVERTER = {
    'win32': {
        'maya2egg': 'maya2egg2008.exe',
        'egg2bam': 'egg2bam.exe',
        'pzip': 'pzip.exe',
        'egg-texture-cards': 'egg-texture-cards.exe',
        'egg-optchar': 'egg-optchar.exe',
        'egg-mkfont': 'egg-mkfont.exe',
        'png2ico': 'png2ico.exe'
    },
    'darwin': {
        'maya2egg': 'maya2egg2008',
        'egg2bam': 'egg2bam',
        'pzip': 'pzip',
        'egg-texture-cards': 'egg-texture-cards',
        'egg-optchar': 'egg-optchar',
        'egg-mkfont': 'egg-mkfont',
        'png2ico': 'png2ico'
    },
    'linux2': {
        'maya2egg': 'maya2egg2008',
        'egg2bam': 'egg2bam',
        'pzip': 'pzip',
        'egg-texture-cards': 'egg-texture-cards',
        'egg-optchar': 'egg-optchar',
        'egg-mkfont': 'egg-mkfont',
        'png2ico': 'png2ico'
    }
}

class ResourceManager(Singleton, MessageListener, Configurable):
    """
    Singleton instance for managing resources inside Gemstone
    """

    def __init__(self, config_path: str = None):
        Singleton.__init__(self)
        MessageListener.__init__(self)
        self.accept('gs-file-changed', self.__on_file_changed)
        self._skip_export = False
        self._resources = []
        self._loader_options = LoaderOptions()
        Configurable.__init__(self, config_path)

    def destroy(self) -> None:
        """
        Destroys the resource manager instance
        """

        Singleton.destroy(self)
        MessageListener.destroy(self)

    @property
    def skip_export(self) -> bool:
        """
        Property access to the get_skip_exports
        method
        """

        return self.get_skip_export()

    @skip_export.setter
    def skip_export(self, enable: bool) -> None:
        """
        Setter access to the set_skip_exports
        method
        """

        self.set_skip_export(enable)

    @property
    def loader_options(self) -> LoaderOptions:
        """
        Property access to get_loader_options
        method
        """

        return self.get_loader_options()

    @loader_options.setter
    def loader_options(self, flags: object) -> None:
        """
        Setter access to the set_loader_options
        method
        """

        self.set_loader_options(flags)

    def register(self, resource: Resource) -> None:
        """
        Registers the requested resource with the resource manager.
        """

    def unregister(self, resource: Resource) -> None:
        """
        Unregisters the requested resource from the resource manager.
        """

    def reload(self, force_reload: bool = False, force_export: bool = False) -> None:
        """
        Reloads the resources currently attached to the resource manager
        """

        for resource in self._resources:
            resource.reload(force_reload, force_export)

    @disallow_production
    def __on_file_changed(self, file_path: str, ext: str) -> None:
        """
        Called on ApplicationReloader file change event.
        """

        for resource in self._resources:
            if resource.supports_reloading():
                resource.attempt_reload(file_path)

    def set_skip_export(self, enable: bool) -> None:
        """
        Sets the resource manager's skip export flag
        """

        self._skip_export = enable

    def get_skip_export(self) -> None:
        """
        Retrieves the resource manager's skip export flag
        """

        return self._skip_export

    def get_loader_options(self) -> LoaderOptions:
        """
        Retrieves the resource manager's loader flags
        """

        return self._loader_options
    
    def set_loader_options(self, flags: object) -> None:
        """
        Sets the resource manager's loader flags
        """

        self._loader_options.set_flags(flags)