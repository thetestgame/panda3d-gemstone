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

from math import sqrt

from panda3d.core import NodePath, AmbientLight, DirectionalLight
from panda3d.core import PointLight, Spotlight, PerspectiveLens
from panda3d.core import Vec3, Vec4
from panda3d.core import PointLight as PandaPointLight
from panda3d.core import BoundingSphere

from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.utilities import delegate, perform_dependency_check
from panda3d_gemstone.framework.utilities import perform_child_class_check

from panda3d_gemstone.world.entity import Entity
from panda3d_gemstone.engine import runtime

PandaLights = {
    'point': PointLight,
    'ambient': AmbientLight,
    'directional': DirectionalLight,
    'spot': Spotlight
}

class Light(Configurable, NodePath):
    """
    Base class for all Gemstone lighting objects
    """

    @staticmethod
    def insert(light: object, parent: object) -> None:
        """
        Inserts the light object into the scene graph
        """

        light.reparent_to(parent)
        parent.set_light(light)

    @staticmethod
    def remove(light: object) -> None:
        """
        Removes the light from the scene graph
        """

        if not light.get_parent().is_empty():
            light.get_parent().clear_light(light)

        light.remove_node()
 
    def __init__(self, config_path: str, section: str = 'Configuration'):
        NodePath.__init__(self, '')
        Configurable.__init__(self, config_path, section)
        self.__light_type = self.pop('type')

    @property
    def light_type(self) -> str:
        """
        Returns the light's engine type as a property
        """

        return self.get_light_type()

    def get_light_type(self) -> str:
        """
        Returns this light's engine type
        """

        return self.__light_type

class PandaLight(Light):
    """
    Represents a light in the Gemstone framework. Acts
    as a wrapper object around the Panda3D lighting
    system
    """

    def __init__(self, config_path: str, section: str = 'Configuration'):
        super().__init__(config_path, section)
        self.__light = self.__create_light_instance()

        if self.__type == 'spot':
            self.__light.set_len(PerspectiveLens())
            self.assign(NodePath(self.__light.upcast_to_LensNode()))
        else:
            self.assign(NodePath(self.__light.upcast_to_PandaNode()))

        self.initialize()

    @property
    def light(self) -> object:
        """
        Returns the light's engine light object
        as a property
        """

        return self.get_light()

    def get_light(self) -> object:
        """
        Returns the native Panda3D engine light object
        for this gemstone light
        """

        return self.__light

    def __create_light_instance(self) -> object:
        """
        Creates a new light instance from the panda
        light's configured type
        """

        light_type = self.get_light_type()
        panda_type = PandaLights.get(light_type, None)
        assert panda_type != None

        return panda_type(light_type + 'Light')

    def set_pos(self, *pos) -> None:
        """
        Sets the lighting object's position
        """

        NodePath.set_pos(self, *pos)
        self.set_point(*pos)

    def __getattr__(self, name) -> object:
        """
        Custom getattr to pass through to the child light 
        object
        """

        def fail() -> None:
            """
            Throws an AttributeError exception
            """

            raise AttributeError('Unknown attribute: %s' % name)

        # Verify we have a light
        if self.__light is None:
            fail()

        if hasattr(self.__light, name):
            return getattr(self.__light, name)
        else:
            fail()

class RenderPipelineLight(Light):
    """
    Represents a light in the Gemstone framework. Acts
    as a wrapper object around the Panda3D Render Pipeline
    lighting system
    """

    def __init__(self, config_path: str, section: str = 'Configuration'):
        super().__init__(config_path, section)
        perform_dependency_check('rpcore')

        raise NotImplementedError('%s is not yet implemented!' % self.__class__.__name__)

class AmbientLightMixIn(object):
    """
    """

    def calc_light_color(self, point, normal) -> object:
        """
        """
        
        perform_child_class_check('AmbientLightMixIn', self.__class__, 'get_color')
        return self.get_color()

class DirectionalLightMixIn(object):
    """
    """

    def calc_light_color(self, point, normal) -> object:
        """
        """

        perform_child_class_check('DirectionalLightMixIn', self.__class__, 'get_direction')
        perform_child_class_check('DirectionalLightMixIn', self.__class__, 'get_color')

        direction = self.get_direction()
        intensity = -Vec3(direction[0], -direction[2], direction[1]).dot(normal)

        if intensity <= 0:
            intensity = 0

        return self.get_color * intensity

class PointLightMixIn(object):
    """
    """

    def calc_bounding_sphere(self) -> object:
        """
        """
        
        perform_child_class_check('PointLightMixIn', self.__class__, 'get_point')

        point = self.get_point()
        radius = self.calc_relevant_radius()

        if radius > 0:
            return BoundingSphere(center=point, radius=radius)
        
        return None

    def calc_relevant_radius(self) -> float:
        """
        """

        perform_child_class_check('PointLightMixIn', self.__class__, 'get_attenuation')

        max_att = 32.0
        attenuation_vec = self.get_attenuation()
        if attenuation_vec[2] != 0:

            sqr = attenuation_vec[1] * attenuation_vec[1] - 4 * (attenuation_vec[2] * attenuation_vec[0] - max_att)
            if sqr < 0:
                return 0

            sqr_val = sqrt(sqr)
            r1 = (-attenuation_vec[1] + sqr_val) / (2 * attenuation_vec[2])
            r2 = (-attenuation_vec[1] - sqr_val) / (2 * attenuation_vec[2])

            if r1 > r2:
                return r1
            else:
                return r2
        elif attenuation_vec[1] != 0:
            return (max_att - attenuation_vec[0]) / attenuation_vec[1]
        else:
            return 0

    def calc_light_intensity(self, point: object) -> float:
        """
        """

        perform_child_class_check('PointLightMixIn', self.__class__, 'get_point')
        perform_child_class_check('PointLightMixIn', self.__class__, 'get_attenuation')

        point_to_light_vec = self.get_point() - point
        distance_vec = Vec3(1, point_to_light_vec.length(), point_to_light_vec.length_squared())
        intensity = self.get_attenuation().dot(distance_vec)

        if intensity > 0:
            intensity = 1.0 / intensity
        else:
            intensity = 0

        return intensity

    def calc_light_color(self, point, normal) -> object:
        """
        """

        perform_child_class_check('PointLightMixIn', self.__class__, 'get_point')
        perform_child_class_check('PointLightMixIn', self.__class__, 'get_color')

        point_to_light_vec = self.get_point() - point
        point_to_light_vec.normalize()

        intensity = point_to_light_vec.dot(normal)
        if intensity <= 0:
            intensity = 0
        else:
            intensity *= self.calc_light_intensity(point)

        return self.get_color() * intensity

class LightSet(Entity):
    """
    """

    class GemDirectionalLight(DirectionalLight, DirectionalLightMixIn):
        """
        """

        def __init__(self, name: str):
            DirectionalLight.__init__(self, name)
            self.set_color(Vec4(0, 0, 0, 1))

    class GemAmbientLight(AmbientLight, AmbientLightMixIn):
        """
        """

        def __init__(self, name: str):
            AmbientLight.__init__(self, name)
            self.set_color(Vec4(0, 0, 0, 1))

    def __init__(self, config_path: str):
        self.__ambient = LightSet.GemAmbientLight('ambient')
        self.__directional_lights = [LightSet.GemDirectionalLight('directional%d' % (i + 1)) for i in range(2)]
        self.__light_nps = []
        super().__init__(config_path)

    def destroy(self) -> None:
        """
        Destroys the light set entity
        """

        self.deactivate()
        Entity.destory(self)

    def get_relevant_lights(self) -> list:
        """
        """

        return [light for light in [self.__ambient] + self.__directional_lights if light.get_color()[0] == 0 and light.get_color()[1] == 0 and light.get_color()[2] == 0]

    def activate(self, root: object = None) -> None:
        """
        Activates the light set on the root NodePath instance
        """

        if not root:
            root = runtime.render

        self.deactivate()
        for light in self.get_relevant_lights():
            self.set_transform(TransformStat.make_pos_hpr_scale(Vec3(0, 0, 0), Vec3(0, 90, 0), Vec3(1, 1, 1)))
            light_np = self.attach_new_node(light)
            root.set_light(light_np)
            self.__light_nps.append(light_np)

    def deactivate(self, root: object = None) -> None:
        """
        Deactivates the light set
        """

        if not root:
            root = runtime.render

        for light in self.__light_nps:
            if light:
                light.remove_node()

        root.clear_light()
        self.__light_nps = []

    def serialize_configuration(self) -> dict:
        """
        """

        data = Entity.serialize_configuration(self)
        data['ambientColor'] = Vec4(self.__ambient.get_color())

        for i in range(3):
            data['_directional_color%d' % (i + 1)] = Vec4(self.__directional_lights[i].get_color())
            data['_directional_hpr%d' % (i + 1)] = self.__directional_lights[i].get_direction()

        return data 

    def set_ambient_color(self, value: object) -> None:
        """
        """

        self.__ambient.set_color(value)

    def get_ambient_color(self) -> object:
        """
        """

        return self.__ambient.get_color()

    def get_directional(self, index: int) -> object:
        """
        Retrieves the directional at the requested index if it exists.
        Otherwise returns NoneType
        """

        if index > len(self.__directional_lights):
            return None

        return self.__directional_lights[index]

    def set_directional_hpr(self, index: int, value: object) -> None:
        """
        Sets the hpr of the directional at the requested index
        """

        directional = self.get_directional(index)
        if directional:
            directional.set_direction(value)

    def get_directional_hpr(self, index: int) -> object:
        """
        Retrieves the hpr of the directional at the requested index
        if it exists. Otherwise returns NoneType
        """

        directional = self.get_directional(index)
        if directional:
            return directional.get_direction()

        return None
                
    def set_directional_color(self, index: int, color: object) -> None:
        """
        Sets the color of the directional at the requested index
        """

        directional = self.get_directional(index)
        if directional:  
            directional.set_color(color)    

    def get_directional_color(self, index: int) -> object:
        """
        Retrieves the color of the directional at the requestsed index
        if it exists. Otherwise returns NoneType
        """

        directional = self.get_directional(index)
        if directional:
            return directional.get_color()

        return None