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

import weakref
import traceback

from panda3d.core import PNMImage, Filename, TextureAttrib
from panda3d.core import Texture

from panda3d_gemstone.logging.utilities import get_notify_category
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.utilities import get_camel_case
from panda3d_gemstone.engine import runtime

__texture_notify = get_notify_category('texture')

def load_texture(*args, **kwargs) -> object:
    """
    Loads a texture using the standard Panda3D Loader
    method
    """

    return runtime.loader.load_texture(*args, **kwargs)

async def load_texture_async(*args, **kwargs) -> object:
    """
    Loads a texture using the standard Panda3D Loader
    method in an async way
    """

    return await runtime.loader.load_texture(*args, **kwargs)

def load_texture_as_buffer(self, file_path: str) -> object:
    """
    Loads a texture into a Gemstone TextureBuffer object
    """

    return TextureBuffer.load_file(file_path)

def load_heightfield(file_path: str) -> object:
    """
    Loads a heightfield from the application's VFS
    """

    try:
        return HeightfieldBuffer.load_file(file_path)
    except Exception as e:
        __texture_notify.warning('Failed to load heightfield (%s) as a buffer. Loading default texture' % (
            file_path))
        __terrain_notify.warning(traceback.format_exc())
        
        return load_texture(file_path)

def assign_texture_to_geom_node(geom_node: object, texture: object) -> None:
    """
    Assigns a texture to a GeomNode instance
    """

    if not texture:
        __texture_notify.warning('Failed to assign texture. Texture is NoneType')
        return

    assert geom_node != None
    assert hasattr(geom_node, 'get_num_geoms')

    num_geoms = geom_node.get_num_geoms()
    for index in range(num_geoms):
        geom = geom_node.get_geom(index)
        geom_state = geom_node.get_geom_state(index)
        
        if geom_state.get_attrib(TextureAttrib.get_class_type()) != None:
            new_state = geom_state.remove_attrib(TextureAttrib.get_class_type())
        else:
            new_state = geom_state

        new_state = new_state.add_attrib(TextureAttrib.make(texture))
        geom_node.set_geom_state(index, new_state)

def get_texture_from_geom_node(geom_node: object) -> object:
    """
    Retrieves the texture from a GeomNode instance
    """

    assert geom_node != None
    assert hasattr(geom_node, 'get_num_geoms')

    if geom_node.get_num_geoms() == 0:
        return None

    geom_state = geom_node.get_geom_state(0)
    return geom_state.get_attrib(TextureAttrib.get_class_type()).get_texture()

class TextureCache(InternalObject):
    """
    """

    def __init__(self, load_async: bool = False):
        super().__init__()

        self.texture_dict = {}
        self.image_dict = {}
        self.weakrefs = set()
        self.requested_for_cpu = set()
        self.requested_for_gpu = set()
        self.requested_for_cpu_and_gpu = set()
        self.set_load_async(load_async)

    def set_load_async(self, load_async: bool) -> None:
        """
        """

        if load_async:
            self.__load_texture_for_cpu_func = self.__load_texture_for_cpu
            self.__load_texture_for_gpu_func = self.__load_texture_for_gpu
            self.__load_texture_for_cpu_and_gpu_func = self.__load_texture_for_cpu_and_gpu
        else:
            self.__load_texture_for_cpu_func = self.__load_sync_Texture_for_cpu
            self.__load_texture_for_gpu_func = self.__load_sync_texture_for_gpu
            self.__load_texture_for_cpu_and_gpu_func = self.__load_sync_texture_for_cpu_and_gpu

    def destroy(self) -> None:
        """
        Destroys the texture cache instance
        """

        InternalObject.destroy(self)

        self.texture_dict = {}
        self.image_dict = {}
        self.weakrefs = set()
        self.requested_for_cpu = set()
        self.requested_for_gpu = set()
        self.requested_for_cpu_and_gpu = set()

    def has_texture(self, texture_name: str) -> bool:
        """
        Returns true if the texture is in the cache
        """

        return texture_name in self.texture_dict

    def has_image(self, image_name: str) -> bool:
        """
        Returns true if the image is in the cache
        """

        return image_name in self.image_dict

    def __load_image(self, path: str, *args, **kwargs) -> object:
        """
        Loads an image using the Panda3D loader object
        and returns the result
        """

        return runtime.loader.load_texture(path, *args, **kwargs)

    def __async_load_image(self, path: str, *args, **kwargs) -> object:
        """
        Loads an image using the Panda3D loader object asynchronously
        """

        return runtime.loader.asyncLoadTexture(path, *args, **kwargs)

    def request_texture_cpu(self, texture_name: str, querying_obj: object) -> None:
        """
        """

        exists = self.has_image(image_name)
        self.__request_texture_generate(texture_name, querying_obj, exists, self.requested_for_cpu, self.__load_texture_for_cpu_func)

    def request_texture_gpu(self, texture_name: str, querying_obj: object) -> None:
        """
        """

        exists = self.has_image(image_name)
        self.__request_texture_generate(texture_name, querying_obj, exists, self.requested_for_gpu, self.__load_texture_for_gpu_func)

    def request_texture_cpu_and_gpu(self, texture_name: str, querying_obj: object) -> None:
        """
        """

        exists = self.has_image(image_name)
        self.__request_texture_generate(texture_name, querying_obj, exists, self.requested_for_cpu_and_gpu, self.__load_texture_for_cpu_and_gpu_func)

    def __request_texture_generic(self, texture_name: str, querying_obj: object, existing: bool, requested_set: object, load_function: object) -> None:
        """
        """

        if existing:
            querying_obj.notify_of_new_texture()
        else:
            self.__store_object(querying_obj)
            if texture_name not in requested_set:
                requested_set.update([texture_name])
                load_function(texture_name)

    def __load_texture_for_cpu(self, texture_name: str) -> None:
        """
        """

        self.notify.debug('Requesting CPU only texture: %s' % texture_name)
        image = PNMImage()
        runtime.loader.asyncPnmImageRead(image, Filename(texture_name), callback=self.__texture_loaded_for_cpu_only_async_callback, extraArgs=[texture_name, image])

    def __load_texture_for_gpu(self, texture_name: str) -> None:
        """
        """

        self.notify.debug('Requesting GPU only texture: %s' % texture_name)
        self.__async_load_image(texture_name, callback=self.__texture_loaded_for_gpu_only_async_callback, extraArgs=[texture_name])

    def __load_texture_for_cpu_and_gpu(self, texture_name: str) -> None:
        """
        """

        self.notify.debug('Requesting CPU and GPU texture: %s' % texture_name)
        self.__async_load_image(texture_name, callback=self.__texture_loaded_for_cpu_and_gpu_async_callback, extraArgs=[texture_name])

    def __load_sync_texture_for_cpu(self, texture_name: str) -> None:
        """
        """

        self.notify.debug('Requesting CPU only texture: %s' % texture_name)
        image = PNMImage()
        success = PNMImage.read(image, Filename(texture_name))
        self.__texture_loaded_for_cpu_only_async_callback(success, texture_name, image)

    def __load_sync_texture_for_gpu(self, texture_name: str) -> None:
        """
        """

        self.notify.debug('Requesting GPU only texture: %s' % texture_name)
        texture = self.__load_image(texture_name)
        self.__texture_loaded_for_gpu_only_async_callback(texture, texture_name)

    def __load_sync_texture_for_cpu_and_gpu(self, texture_name: str) -> None:
        """
        """

        self.notify.debug('Requesting CPU and GPU texture: %s' % texture_name)
        texture = self.__load_image(texture_name)
        self.__texture_loaded_for_cpu_and_gpu_async_callback(texture, texture_name)

    def __store_object(self, obj: object) -> None:
        """
        Stores the weakref reference to the object for later use
        """

        self.weakrefs.update([weakref.ref(obj)])

    def __notify_all_objects(self) -> None:
        """
        """

        list_of_refs_to_remove = []
        for obj in self.weakrefs:
            reference = obj()
            if reference is None:
                list_of_refs_to_remove.remove(obj)
            else:
                if reference.notify_of_new_texture():
                    list_of_refs_to_remove.append(obj)
        
        for obj in list_of_refs_to_remove:
            self.weakrefs.remove(obj)

    def __texture_loaded_for_cpu_only_async_callback(self, success: bool, texture_name: str, texture: object) -> None:
        """
        """

        self.notify.debug('Received CPU texture: %s' % texture_name)
        self.request_texture_cpu.remove(texture_name)
        self.image_dict[texture_name] = texture

        if not success:
            self.notify.warning('Async texture load for CPU failed (%s)' % texture_name)
        
        self.__notify_all_objects()

    def __texture_loaded_for_gpu_only_async_callback(self, texture: object, texture_name: object) -> None:
        """
        """

        self.notify.debug('Received GPU texture: %s' % texture_name)
        self.requested_for_gpu.remove(texture_name)
        self.texture_dict[texture_name] = texture

        if not texture:
            self.notify.warning('Async texture load for GPU failed (%s)' % texture_name)

        self.__notify_all_objects()

    def __texture_loaded_for_cpu_and_gpu_async_callback(self, texture: object, texture_name: object) -> None:
        """
        """

        self.notify.debug('Received CPU and GPU texture: %s' % texture_name)
        self.requested_for_cpu_and_gpu.remove(texture_name)
        self.texture_dict[texture_name] = texture_name

        if not texture:
            self.notify.warning('Async texture load for CPU and GPU failed (%s)' % texture_name)

        self.__notify_all_objects()

class TextureBuffer(Texture, InternalObject):
    """
    Represents an editable texture buffer inside Gemstone
    """

    def __init__(self, *args, **kwargs):
        Texture.__init__(self)
        InternalObject.__init__(self)
        self._pnm = PNMImage(*args, **kwargs)
        self.refresh()

    @classmethod
    def load_file(cls: object, file_path: str) -> object:
        """
        Loads an image file into the TextureBuffer instance
        """

        instance = cls(Filename(file_path))
        return instance

    def __wrapper(self, method, *args, **kwargs) -> object:
        """
        Wrapper for a PNMImage function to auto update our 
        texture instance
        """

        results = None
        try:
            result = method(*args, **kwargs)
        except Exception as e:
            raise e

        self.refresh()
        return results

    def refresh(self) -> None:
        """
        Refreshes the texture instance from the internal PNMImage
        object
        """

        self.notify.debug('Refreshing %s %d' % (
            self.__class__.__name__, id(self)))
        self.load(self._pnm)

    def __getattr__(self, key: str) -> object:
        """
        Custom attribute getter for wrapping the Panda3D PNMImage object
        """

        results = None
        is_getter = key.startswith('get')
        if hasattr(self._pnm, key):
            results = getattr(self._pnm, key)
            if is_getter:
                results = lambda *args, **kwargs: self.__wrapper(results, *args, **kwargs)
        elif hasattr(self._pnm, get_camel_case(key)):
            results = getattr(self._pnm, get_camel_case(key))
            if is_getter:
                results = lambda *args, **kwargs: self.__wrapper(results, *args, **kwargs)

        if not results:
            raise AttributeError('%s does not have attribute %s' % (
                self.__class__.__name__, key))

        return results

class HeightfieldBuffer(TextureBuffer):
    """
    A Heightfield specific variant of the TextureBuffer. Automatically converts
    the incoming texture into a valid heightfield for use with GPUTerrain objects
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_max_value()

    def __set_max_value(self) -> None:
        """
        Sets the required max value of a gpu heightfield
        """
        
        self.set_maxval(65535)
        