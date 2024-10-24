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

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.engine import shader, texture, runtime
from panda3d_gemstone.world.entity import Entity

from panda3d.core import ShaderTerrainMesh, GeoMipTerrain, Filename
from panda3d.core import Vec3

class TerrainBase(Entity):
    """
    Base class of all Panda3D terrain objects
    """

    def __init__(self, config_path: str, terrain: object = None):
        self.__texture = None
        self.__heightfield_texture = None
        self.__terrain_scale = Vec3(1, 1, 1)
        assert terrain != None
        self.__terrain = terrain
        self.__values = {}
        super().__init__(config_path)
        self.configure_terrain(self.__values)

    @property
    def terrain(self) -> object:
        """
        Panda3D native object instance
        """

        return self.__terrain

    def configure_terrain(self, values) -> None:
        """"
        Performs terrain configuration operations
        """

        # Configure terrain
        for value_key in self.__values:
            if hasattr(self.__terrain, value_key):
                value = self.__values[value_key]
                func = getattr(self.__terrain, value_key)
                if func and False:
                    if isinstance(value, tuple):
                        func(*value)
                    else:
                        func(value)
                else:
                    attr = getattr(self.__terrain, value_key.replace('set_', ''))
                    if attr:
                        attr = value
                    else:
                        self.notify.warning('%s does not have attribute %s!' % (
                            self.__terrain.__class__.__name__, value_key))   

    def set_heightfield(self, heightfield_path: str) -> None:
        """
        Sets the terrain's heightfield texture
        """

        self.__heightfield_texture = texture.load_heightfield(heightfield_path)
        assert self.__heightfield_texture != None

    def get_heightfield(self) -> object:
        """
        Returns the terrain's heightfield texture
        """

        return self.__heightfield_texture

    def set_terrain_texture(self, texture_path: str) -> None:
        """
        Sets the terrain's base texture 
        """

        self.__texture = texture.load_texture(texture_path, okMissing=True)

    def get_terrain_texture(self) -> object:
        """
        Retrieves the terrain's base texture
        """

        return self.__texture
 
    def set_terrain_scale(self, scale: object) -> None:
        """
        Sets the terrain's scale value
        """

        inputs = []
        if isinstance(scale, tuple):
            inputs = scale
        else:
            for num in scale.split(','):
                inputs.append(float(num))

        self.__terrain_scale = Vec3(*inputs)

    def get_terrain_scale(self) -> None:
        """
        Returns the terrain's scale value
        """

        return self.__terrain_scale

    def __get_value(self, key: str) -> object:
        """
        Attempts to retrieve the value from the values dictionary
        """

        return self.__values.get(key, None)

    def __set_value(self, key: str, obj: object) -> None:
        """
        Sets the value in the values dictionary
        """

        self.__values[key] = obj

    def __getattr__(self, key: str) -> object:
        """
        Custom attribute getter for passing along function
        calls to the native Panda3D terrain object
        """

        result = None

        def has_attribute(obj: object, key: str) -> bool:
            """
            Returns true if the object has a attribute from the getter/setter key
            """

            attrib_key = key.replace('get_', '').replace('set_', '')
            return hasattr(obj, key) or hasattr(obj, attrib_key)

        def valid_get(obj: object, key: str) -> bool:
            """
            Returns true if the requested attribute is a valid getter
            """

            ignored = ['get_class_type']
            return key.startswith('get_') and key not in ignored
        
        if isinstance(key, str):
            if has_attribute(self.__terrain, key):
                if valid_get(self.__terrain, key):
                    result = lambda: self.__get_value(key)
                elif key.startswith('set_'):
                    result = lambda x: self.__set_value(key, x)
                else:
                    return getattr(self.__terrain, key)

        if result is None:
            raise AttributeError('%s instance does not have attribute %s' % (
                self.__class__.__name__, key))

        return result

class CPUTerrain(TerrainBase):
    """
    Represents a gemstone cpu terrain object
    by wrapping the Panda3D native GeoMipTerrain
    node object
    """

    def __init__(self, config_path: str):
        self.__terrain_texture = None
        super().__init__(config_path, GeoMipTerrain(self.__class__.__name__))

        # Finalize terrain node
        self.terrain.set_heightfield(self.get_heightfield())
        self.__terrain_node = self.__terrain.get_root()
        self.__terrain_node.reparent_to(self)
        height_scale = self.get_scale().get_z()
        self.__terrain_node.set_scale(1, 1, height_scale)
        self.__terrain_node.set_z(self.__terrain_node.get_z() - (height_scale / 2))
        if self.get_terrain_texture():
            self.__terrain_node.set_texture(self.get_terrain_texture())
        self.__terrain.generate()

    @property
    def terrain_node(self) -> object:
        """
        Panda3D native Node instance representing
        the GeoMipTerrain instance
        """

        return self._terrain_node

class GPUTerrain(TerrainBase):
    """
    Represents a gemstone gpu terrain object
    by wrapping the Panda3d native ShaderTerrainMesh
    node object
    """

    def __init__(self, config_path: str):
        self.__terrain_texture = None
        self.__target_triangle_width = 10
        self.__vertex_shader = ''
        self.__fragment_shader = ''

        super().__init__(config_path, ShaderTerrainMesh())

        # Finalize terrain
        self.terrain.heightfield = self.get_heightfield()
        self.terrain.generate()

        self.__terrain_node = self.attach_new_node(self.terrain)
        terrain_scale = self.get_terrain_scale()
        self.__terrain_node.set_scale(terrain_scale)
        self.__terrain_node.set_pos(0, 0, -terrain_scale.get_z()/2)
        if self.get_terrain_texture():
            self.__terrain_node.set_texture(self.get_terrain_texture(), 1)

        self.__terrain_shader = shader.load_shader(self.__vertex_shader, self.__fragment_shader)
        self.__terrain_node.set_shader(self.__terrain_shader)
        self.__terrain_node.set_shader_input('camera', runtime.camera)
    
    @property
    def terrain_node(self) -> object:
        """
        Panda3D native NodePath representing the ShaderTerrainMesh
        instance
        """

        return self.__terrain_node

    def set_terrain_fragment_shader(self, shader_path: str) -> None:
        """
        Sets the terrain's fragment shader path
        """

        self.__fragment_shader = shader_path

    def get_terrain_fragment_shader(self) -> str:
        """
        Returns the terrain's fragment shader path
        """

        return self.__fragment_shader

    def set_terrain_vertex_shader(self, shader_path: str) -> None:
        """
        Sets the terrain's vertex shader path
        """

        self.__vertex_shader = shader_path

    def get_terrain_vertex_shader(self) -> str:
        """
        Returns the terrain's vertex shader path
        """

        return self.__vertex_shader

class PaintedChannel(InternalObject):
    """
    """

    def __init__(self):
        super().__init__()

class PaintedChannelTerrain(GPUTerrain):
    """
    """

    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.__channels = []