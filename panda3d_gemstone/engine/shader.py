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

from panda3d.core import Shader, Filename

from panda3d_gemstone.logging.utilities import get_notify_category
from panda3d_gemstone.io.file_system import get_file_extension, path_exists

__shader_notify = get_notify_category('shaders')

class ShaderError(RuntimeError):
    """
    Base class for all shader errors
    """

class ShaderCompileError(ShaderError):
    """
    Fired when an error occures compiling a shader
    """

class MalformedShaderLoadRequest(ShaderError):
    """
    Fired when a malformed load_shader request is made
    """

def __kwargs_to_string(self, kwargs, sep=',') -> str:
    """
    Returns a list of keyword arguments as a string
    """

    output = ''
    for kwarg in kwargs:
        output += '%s: %s%s ' % (kwarg, kwargs[kwarg], sep)

    return output

__extension_map = {
    'glsl': Shader.SL_GLSL,
    'hlsl': Shader.SL_HLSL,
    'cg': Shader.SL_Cg,
    'spir': Shader.SL_SPIR_V
}

def is_supported_language(language: object) -> bool:
    """
    Returns true if the requested Panda3D idnetifier is supported
    """

    return language in __extension_map.values()

def shader_label_from_language(language: object) -> str:
    """
    Returns the shader language name based on the Panda3D identifier
    if found. Otherwise NoneType
    """

    found = None
    for shader_key in __extension_map:
        lang = __extension_map[shader_key]
        if lang == language:
            found = shader_key.upper()

    return found

def get_shader_language(shader_path: str) -> object:
    """
    Returns the Panda3D identifier for the shader file's language
    based on its file extension
    """

    ext = get_file_extension(shader_path)
    return __extension_map.get(ext, None)

def shader_file_supported(shader_path: str) -> bool:
    """
    Returns true if the shader file is supported by the Gemstone framework
    """

    return get_shader_language(shader_path) != None

def __matching_shader_languages(shader_paths: list) -> bool:
    """
    Returns true if all the shader paths provided match the same language
    """

    last_lang = None
    matching = True
    for shader_path in shader_paths:
        if shader_path is None:
            continue
            
        shader_lang = get_shader_language(shader_path)
        if last_lang != None and shader_lang != last_lang:
            matching = False
            break
        last_lang = shader_lang
    
    return matching

def __convert_path_list_filename_list(shader_paths: list) -> list:
    """
    Converts a list of string paths to a list of Panda3D Filename objects
    """

    converted = []
    for path in shader_paths:
        if path is None:
            continue
        
        converted.append(Filename(path))

    return converted

def make_shader(language: object, vertex: str, fragment: str, geometry: str = None, tess_control: str = None, tess_evaluation: str = None) -> object:
    """
    Creates a shader instance using string bodies instead of files
    """

    if not is_supported_language(language):
        raise ShaderCompileError('Failed to make shader. Language (%s) is not supported' % str(language))

    paths = [vertex, fragment, geometry, tess_control, tess_evaluation]
    paths = __convert_path_list_filename_list(paths)
    shader = Shader.make(language, *paths)

    # Verify no errors have occured
    if not shader or shader.get_error_flag():
        __shader_notify.warning('Failed to make shader. An error occured while compiling.')

    return shader

def make_compute_shader(language: object, vertex: str, fragment: str, geometry: str = None, tess_control: str = None, tess_evaluation: str = None) -> object:
    """
    Creates a compute shader instance using string bodies instead of files
    """

    if not is_supported_language(language):
        raise ShaderCompileError('Failed to make shader. Language (%s) is not supported' % str(language))

    paths = [vertex, fragment, geometry, tess_control, tess_evaluation]
    paths = __convert_path_list_filename_list(paths)
    shader = Shader.make_compute(language, *paths)

    # Verify no errors have occured
    if not shader or shader.get_error_flag():
        __shader_notify.warning('Failed to make compute shader. An error occured while compiling.')

    return shader

def load_shader(vertex: str, fragment: str, geometry: str = None, tess_control: str = None, tess_evaluation: str = None) -> object:
    """
    Loads a shader from the application's file system using the various shader program files.
    """

    # Verify the shader language is supported
    if not shader_file_supported(vertex):
        raise MalformedShaderLoadRequest('Invalid load request. Shader extension %s is not supported' % (get_file_extension(vertex)))

    # Verify all the requested shader files are the same language
    paths = [vertex, fragment, geometry, tess_control, tess_evaluation]
    if not __matching_shader_languages(paths):
        raise MalformedShaderLoadRequest('Invalid load request. Not all shader files are the same language. Shaders: [%s]' % (', '.join(paths)))

    shader_language = get_shader_language(vertex)
    paths = __convert_path_list_filename_list(paths)
    shader = Shader.load(shader_language, *paths)

    # Verify no errors have occured
    if not shader or shader.get_error_flag():
        __shader_notify.warning('Failed to load shader. An error occured while compiling.')

    return shader

def load_compute_shader(vertex: str, fragment: str, geometry: str = None, tess_control: str = None, tess_evaluation: str = None) -> object:
    """
    Loads a compute shader from the application's file system using the various shader program files.
    """

    # Verify the shader language is supported
    if not shader_file_supported(vertex):
        raise MalformedShaderLoadRequest('Invalid load compute request. Shader extension %s is not supported' % (get_file_extension(vertex)))

    # Verify all the requested shader files are the same language
    paths = [vertex, fragment, geometry, tess_control, tess_evaluation]
    if not __matching_shader_languages(paths):
        raise MalformedShaderLoadRequest('Invalid load compute request. Not all shader files are the same language. Shaders: [%s]' % (', '.join(paths)))

    shader_language = get_shader_language(vertex)
    paths = __convert_path_list_filename_list(paths)
    shader = Shader.load_compute(shader_language, *paths, **kwargs)

    # Verify no errors have occured
    if not shader or shader.get_error_flag():
        raise ShaderCompileError('Failed to load compute shader. An error occured while compiling.')

    return shader

def enable_shader_generator(nodepath: object) -> None:
    """
    Enables the default Panda3D shader generator on the requested node
    """

    assert hasattr(nodepath, 'set_shader_auto')
    nodepath.set_shader_auto()

def enable_global_shader_generator() -> None:
    """
    Globally enables the default Panda3D shader generator for the entire
    application 3d scene graph
    """

    from panda3d_gemstone.engine import runtime
    
    assert runtime.has_render()
    runtime.render.set_shader_auto()
