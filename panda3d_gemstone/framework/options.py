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

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.configurable import Configurable, RawOSConfigurableCache
from panda3d_gemstone.framework.singleton import SingletonWrapper

from panda3d_gemstone.io.file_system import path_exists

from panda3d_gemstone.engine import runtime
from panda3d_gemstone.engine.prc import get_prc_value, load_prc_file_data
from panda3d_gemstone.engine.audio import SoundManager

from panda3d.core import ConfigVariableList

class InvalidEnvironmentConfig(RuntimeError):
    """
    Represents an invalid environment configuration
    """

class ApplicationOptions(Configurable, InternalObject):
    """
    Base class for all Gemstone framework option
    file management
    """

    THREADING_MODELS = ['App/Cull/Draw', 'Cull/Draw', '/Draw', 'Cull']
    PRC_VARIABLES = ['load-display', 'fullscreen', 'win-size', 'sync-video', 'show-frame-rate-meter']
    SUPPORTED_GRAPHICS_LIBRARIES = ConfigVariableList('gs-display')
    SUPPORTED_LANGUAGES = ConfigVariableList('gs-option-lang')

    def __init__(self, config_path, local_settings):
        Configurable.__init__(self, config_path, override_cache=RawOSConfigurableCache())
        InternalObject.__init__(self)
        self.local_settings = local_settings
        self.config_prc_settings = None
        self.__validate_environment()

    def __validate_environment(self) -> None:
        """
        Validates the application environment to ensure its 
        is properly configured
        """

        if len(ApplicationOptions.SUPPORTED_GRAPHICS_LIBRARIES) <= 0:
            raise InvalidEnvironmentConfig('Invalid environment; No graphics library options are configured')

        if len(ApplicationOptions.SUPPORTED_LANGUAGES) <= 0:
            raise InvalidEnvironmentConfig('Invalid environment; No application languages are configured')

    def set_options_before_panda_start(self) -> None:
        """
        Performs application settings changes prior to Showbase
        initialization
        """

        self.config_prc_settings = self.get_settings_from_prc(self.PRC_VARIABLES)
        self.set_video_options()
        self.set_interface_options()
        self.__set_platform_specific_options()

        if runtime.is_developer_build():
            application_name = runtime.application.get_application_name()
            self.set_engine_setting('pstats-name', '%s Performance Stats' % application_name)

    def __set_platform_specific_options(self) -> None:
        """
        Sets the platform specific options for the application
        """

        platform_name = sys.platform
        setter_name = 'set_%s_options' % platform_name
        if hasattr(self, setter_name):
            self.notify.info('Setting platform options for: %s' % platform_name)
            getattr(self, setter_name)()
        else:
            self.notify.warning('No platform options setter found for: %s' % platform_name)

    def set_darwin_options(self) -> None:
        """
        Sets the darwin operation system specific options
        """

        load_prc_file_data("gl-version 3 2")

    def set_win32_options(self) -> None:
        """
        Sets the windows operation system specific options
        """

        self.__set_threading_model_is_enabled()

    def set_linux2_options(self) -> None:
        """
        Sets the linux operation system specific options
        """

        self.__set_threading_model_is_enabled()

    def __set_threading_model_is_enabled(self) -> None:
        """
        Sets the threading model for the application
        """

        multithreaded = self.get_setting('enableMultithreading', False, self._valdiate_true_or_false)
        threading_model = self.get_setting('multithreadingModel', 0, self._validate_threading_model)
        if multithreaded:
            threading_value = self.THREADING_MODELS[threading_model]
            self.notify.debug('Using threading model: %s' % threading_value)
            self.set_engine_setting('threading-model', threading_value)

    def set_options_after_panda_start(self) -> None:
        """
        Sets the application's options post Panda3D setup
        """

        self.set_audio_options()

    def set_interface_options(self) -> None:
        """
        Sets the application's interface options
        """

        self.get_setting('activeLanguage', True, self._validate_language)

    def set_engine_setting(self, key: str, value: object) -> None:
        """
        Sets the Panda3D engine prc configuration value
        """

        if runtime.has_base():
            self.notify.warning('Attempting to set engine setting "%s" after ShowBase startup. Setting may not take effect' % (
                key))
        
        final = ''
        if isinstance(value, bool):
            final = '#t' if value else '#f'
        elif isinstance(value, tuple) or isinstance(value, list):
            parts = []
            for v in value:
                parts.append(str(v))
            final = ' '.join(parts)
        else:
            final = value
        
        self.notify.debug('Setting engine setting "%s" to "%s"' % (key, final))
        load_prc_file_data('%s %s' % (key, final), 'application-setting')

    def set_video_options(self) -> None:
        """
        Sets the application's video and graphics options
        """

        display_default = None
        fullscreen_default = None
        size_default = None
        sync_video_default = None
        frame_rate_default = False

        if self.config_prc_settings:
            display_default = self.config_prc_settings.get('load-display', '')
            display_default = display_default[5:] if display_default.startswith('panda') else None
            
            sync_video_default = self.config_prc_settings.get('sync-video', 1)
            sync_video_default = sync_video_default == True or sync_video_default == '#t' or sync_video_default == 't'

            frame_rate_default = self.config_prc_settings.get('show-frame-rate-meter', False)
            frame_rate_default = frame_rate_default == True or frame_rate_default == '#t' or frame_rate_default == 't'
            
            #TODO: load the rest of the defaults

        display = self.get_setting('display', display_default, self._validate_display)
        fullscreen = self.get_setting('fullscreen', fullscreen_default, self._valdiate_true_or_false)
        size = self.get_setting('displaySize', size_default)
        sync_video = self.get_setting('syncVideo', sync_video_default, self._valdiate_true_or_false)
        frame_rate = self.get_setting('enableFrameRate', frame_rate_default, self._valdiate_true_or_false)

        self.set_engine_setting('fullscreen', fullscreen)
        self.set_engine_setting('load-display', 'panda%s' % display)
        self.set_engine_setting('win-size', size)
        self.set_engine_setting('sync-video', sync_video)
        self.set_engine_setting('show-frame-rate-meter', frame_rate)
 
    def _validate_value(self, val: object, options: list) -> bool:
        """
        Validates the value and returns true if the value is 
        contained in the options list
        """

        return val in options

    def _validate_type(self, val: str, val_type: object) -> bool:
        """
        Validates the value's type and returns true if it matches the
        type provided in val_type
        """

        return type(val) == val_type

    def _validate_threading_model(self, val: int) -> bool:
        """
        Validates the value to ensure its a valid threading model
        option
        """

        return val >= 0 and val < len(self.THREADING_MODELS)

    def _validate_display(self, val: str) -> bool:
        """
        Validates the value to ensure its a valid graphics library
        option
        """

        return self._validate_value(val, self.SUPPORTED_GRAPHICS_LIBRARIES)

    def _validate_language(self, val: str) -> bool:
        """
        Validates the value to ensure its a valid language option
        """

        return self._validate_value(val, self.SUPPORTED_LANGUAGES)

    def _validate_between_zero_and_one(self, val: int) -> bool:
        """
        Returns true if the valie is between 0 and 1
        """

        return val >= 0 and val <= 1

    def _valdiate_true_or_false(self, val: bool) -> bool:
        """
        Returns true if the value is a valid boolean
        """

        return type(val) is bool

    def _validate_string(self, val: str) -> bool:
        """
        Returns true if the value is a valid string type
        """

        return self._validate_type(val, str)

    def set_audio_options(self) -> None:
        """
        Sets the application's audio options
        """

        enable_music = self.get_setting('enableMusic', True, self._valdiate_true_or_false)
        volume_music = 0
        if enable_music:
            volume_music = self.get_setting('volumeMusic', 0.1, self._validate_between_zero_and_one)
        SoundManager.get_singleton().set_music_volume(volume_music)

        enable_sfx = self.get_setting('enableSFX', True, self._valdiate_true_or_false)
        volume_sfx = 0
        if enable_sfx:
            volume_sfx = self.get_setting('volumeSFX', 1.0, self._validate_between_zero_and_one)
        SoundManager.get_singleton().set_sound_effects_volume(volume_sfx)

    def get_setting(self, setting_name: str, default_fallback: object = None, valdiation_callback: object = None) -> object:
        """
        Retrieves an application setting value and runs it against a validation
        callback if present.
        """

        if setting_name in self.local_settings:
            val = self.local_settings.get(setting_name)
            is_ok = True

            if valdiation_callback is not None:
                is_ok = valdiation_callback(val)

            if is_ok:
                return val
            else:
                self.notify.warning('Invalid value %s for option %s found in application settings' % (
                    val, setting_name))

        if setting_name in self.configuration:
            ret = self.configuration.get(setting_name)
            self.local_settings[setting_name] = ret

            return ret

        if default_fallback is not None:
            self.notify.info('Setting default setting for "%s": %s' % (setting_name, default_fallback))
            self.local_settings[setting_name] = default_fallback

        self.notify.warning('No default setting for "%s" specified in %s. Defaulting to %s' % (
            setting_name, self.path, default_fallback))
        
        return default_fallback

    def get_settings_from_prc(self, setting_name_list) -> dict:
        """
        Retrieves the required settings from the Panda3D runtime config
        """

        values = {}
        for setting_name in setting_name_list:
            result = get_prc_value(setting_name, None)
            if result:
                values[setting_name] = result
            else:
                self.notify.warning('Failed to retrieve prc value for "%s"' % setting_name)

        return values

class LocalSettings(dict, Configurable):
    """
    Represents a local application configuration file
    """

    def __init__(self, config_path: str):
        dict.__init__(self)
        self.__child_dicts = {}
        self.__first_time = True
        self.__dirty = False

        if os.path.exists(config_path):
            self.__first_time = False

        Configurable.__init__(self, config_path, override_cache=RawOSConfigurableCache())
        self.update(self.configuration)
        del self.configuration
    
    def is_first_time(self) -> bool:
        """
        Returns true if the local settings is a newly created
        file
        """

        return self.__first_time

    def is_dirty(self) -> bool:
        """
        Returns true if the application settings are currently dirty
        """

        return self.__dirty

    def write(self) -> None:
        """
        Writes the application settings to file
        """

        f = open(self.path, 'w')
        f.write('[Configuration]\n')

        for key, value in list(self.items()):
            f.write('%s: %s\n' % (str(key), str(value)))

        for key, value in self.__child_dicts.items():
            f.write('\n[%s]\n' % str(key))
            if type(value) == dict:
                for subKey, sub_value in value.items():
                    if type(sub_value) == type(''):
                        f.write("%s: '%s'\n" % (str(sub_key), str(sub_value.encode('utf8'))))
                    elif type(subValue) == str:
                        f.write("%s: '%s'\n" % (str(sub_key), str(sub_value)))
                    else:
                        f.write('%s: %s\n' % (str(sub_key), str(sub_value)))

        f.close()     
        self.__dirty = False     

    def load_data(self, section: str, data: dict) -> None:
        """
        Loads the data from the local application settings file
        """

        if data is None:
            data = {}

        self.__child_dicts[section] = data

    def reset(self) -> None:
        """
        Resets the local settings
        """

        if os.path.exists(self.path):
            os.remove(self.path)

        if os.path.exists(self.path):
            os.remove(self.path)

        self.__first_time = True
        self.clear()

    def set_value_in_child_dict(self, child_dict_name: object, key: str, value: object) -> None:
        """
        """

        temp_dict = self.__child_dicts.get(child_dict_name, {})
        temp_dict[key] = value
        self.__child_dicts[child_dict_name] = temp_dict

    def get_value_in_child_dict(self, child_dict_name: object, key: str, value: object) -> None:
        """
        """

        return self.__child_dicts.get(child_dict_name, {}).get(key, default)

    def get_child_dicts_copy(self) -> object:
        """
        """

        return copy.deepcopy(self.__child_dicts)

    def replace_child_dict(self, new_dict: dict) -> None:
        """
        """

        self.__child_dicts = dict(new_dict)

    def on_setting_changed(self, key: str, new_value: object, old_value: object) -> None:
        """
        Called on setting changed
        """

        self.__dirty = True

    def __setitem__(self, key: str, item: object) -> None:
        """
        Custom item setter for calling on_setting_changed
        """

        old_value = dict.get(self, key, None)
        dict.__setitem__(self, key, item)
        self.on_setting_changed(key, item, old_value)

class SingletonLocalSettings(SingletonWrapper):
    """
    Singleton wrapper for the application local settings
    """

    WRAPPED_OBJECT = LocalSettings