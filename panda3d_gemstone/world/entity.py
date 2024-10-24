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

from panda3d.core import NodePath, Point3

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.configurable import Configurable
from panda3d_gemstone.framework.registry import ClassRegistryMixIn
from panda3d_gemstone.framework.cast import cast
from panda3d_gemstone.io.file_system import fix_path

class EntityProxy(ClassRegistryMixIn, InternalObject):
    """
    """

    @staticmethod
    def from_string(s, lineNr = 0) -> object:
        """
        """

        entityProxy = EntityProxy('', '', '', '', '', '', Point3(0, 0, 0), 0, {})
        if entityProxy.deseralize(s):
            return entityProxy
        
        return None

    def __init__(self, layer_id, cls_name, config_path, name, model_cls_name, model_config_path, pos, heading, data):
        InternalObject.__init__(self)
        self.layer_id = layer_id
        self.cls_name = cls_name
        self.config_path = config_path
        self.name = name
        self.model_cls_name = model_cls_name
        self.model_config_path = model_config_path
        self.pos = pos
        self.heading = heading

        if not isinstance(data, dict):
            data = {}
            self.notify.error("Dictionary expected - data of entity '%s' is broken" % name)
        
        self.data = data

    def seralize(self) -> None:
        """
        """

        return "%s <%s> '%s' '%s' %s '%s' %f %f %f %f %s" % (
            self.cls_name,
            self.layer_id,
            self.name,
            fix_path(self.config_path),
            self.model_cls_name,
            fix_path(self.model_config_path),
            self.pos.getX(),
            self.pos.getY(),
            self.pos.getZ(),
            self.heading,
            {})

    def deseralize(self, s) -> bool:
        """
        """

        elements = s.split(' ')
        if len(elements) < 10:
            return False

        self.cls_name = elements[0]
        self.layer_id = elements[1].strip(' <>')
        self.name = elements[2].strip(" '")
        self.config_path = elements[3].strip(" '")
        self.model_cls_name = elements[4].strip(' ')
        self.model_config_path = elements[5].strip(" '")
        self.pos = Point3(float(elements[6]), float(elements[7]), float(elements[8]))
        self.heading = float(elements[9])
        self.data = cast(' '.join(elements[10:]))

        return True

    def instantiate(self, parent, lineNr = 0) -> object:
        """
        """

        cls = self._get_class(self.cls_name)

        if self.model_cls_name != 'None':
            model_cls = self._get_class(self.model_cls_name)
        else:
            model_cls = None
        
        if not cls:
            self.notify.error("Failed to instantiate entity. Unknown entity class '%s' at line #%d", self.cls_name, lineNr)
        elif not model_cls and self.model_cls_name != 'None':
            self.notify.error("Failed to instantiate entity. Unknown entity model class '%s' at line #%d", self.model_cls_name, lineNr)
        else:
            entity = cls(self.config_path)
            entity.set_name(self.name)
            entity.reparent_to(parent, layer_id=self.layer_id)
            entity.set_pos(self.pos)
            entity.set_h(self.heading)
            #entity.set_configuration(self.data)
            if model_cls:
                entity.set_model(model_cls(self.model_config_path))
        
        if not entity:
            entity = NodePath('')

        return entity


class Entity(NodePath, InternalObject, Configurable):
    """
    Base class for all entities in the gemstone framework
    """

    def __init__(self, config_path):
        self._layer = None
        self._model = None
        self._user_data = {}
        InternalObject.__init__(self)
        Configurable.__init__(self, config_path)
        NodePath.__init__(self, '')
        self.initialize()

    @property
    def layer(self) -> object:
        """
        Returns this entity's layer as a property
        """

        return self.get_layer()

    @property
    def world(self) -> object:
        """
        Returns this entity's world as a property
        """

        return self.get_world()

    @property
    def model(self) -> object:
        """
        Returns this entity's model as a property
        """

        return self.get_model()

    @property
    def user_data(self) -> dict:
        """
        Returns this entity's user data as a property
        """

        return self.get_user_data()

    @property
    def rendered(self) -> bool:
        """
        Value is true when the Entity is currently being rendered
        """

        return self.is_rendered()

    def destroy(self) -> None:
        """
        Performs destruction operations on the entity
        """

        PandaBaseObject.destroy(self)
        self.clear_model()
        self.remove_node()

    def is_rendered(self) -> bool:
        """
        Retrusn true if the Entity is currently
        being rendered
        """

        return not self.get_parent().is_empty()

    def set_name(self, name: str) -> None:
        """
        Sets the entity's scene graph name
        """

        # Sanitize the incoming name if it contains
        # whitespaces
        if ' ' in name:
            self.notify.warning('Spaces removed from entity name: "%s' % name)
            name = name.replace(' ', '')

        NodePath.set_name(self, name)

    def get_layer(self) -> object:
        """
        Return's this entity's layer
        """

        return self._layer

    def get_world(self) -> object:
        """
        Returns this entity's world instance
        """

        return self._layer.get_world()

    def reparent_to(self, root: object, sort: int = 0, layer_id: str = '') -> None:
        """
        Reparents this entity to a new node parent
        """

        self.detach_node()

        if layer_id is not None and hasattr(root, 'get_layer'):
            self._layer = root.get_layer(layer_id, create_if_needed=True)
        
        if self._layer:
            self._layer.add_entity(self)

        NodePath.reparent_to(self, root, sort)

    def clear_model(self) -> None:
        """
        Clears this entity's model instance
        """

        if self._model is not None:
            self._model.destroy()
            self._model = None

    def get_model(self) -> object:
        """
        Returns this entity's model instance
        """

        return self._model

    def set_model(self, model_template: object) -> None:
        """
        Sets this entity's model from a model template
        """

        self.clear_model()
        if hasattr(model_template, 'copyTo'):
            self._model = model_template.copy_to(self)

    def attach_model(self, model: object) -> None:
        """
        Ataches a model to the entity
        """

        self.clear_model()
        self._model = model
        model.reparent_to(self)

    def copy_model_to(self, root: object) -> None:
        """
        Copys the entity model to the new root
        """

        assert root != None
        return self._model.copy_to(root)

    def copy_to(self, parent: object) -> object:
        """
        """

        copy = self.__class__(self.path)
        copy.reparent_to(parent, layer_id=self._layer)
        copy.set_pos(self.get_pos())
        copy.set_h(self.get_h())

        if self.get_model() and not copy.get_model():
            copy.set_model(self.get_model())

        if self.get_name() and not copy.get_name():
            copy.set_name(self.get_name())

        return copy

    def __remove_from_layer(self) -> None:
        """
        Removes the entity instance from its current layer
        """

        if self._layer:
            self._layer.remove_entity(self)
            self._layer = None

    def remove_node(self) -> None:
        """
        Removes the entity node from the scene graph
        """

        self.__remove_from_layer()
        NodePath.remove_node(self)

    def detach_node(self) -> None:
        """
        Detaches the entity node from the scene graph
        """

        self.__remove_from_layer()
        NodePath.detach_node(self)

    def set_user_data(self, user_data: dict) -> None:
        """
        Sets the entity's user data
        """

        if isinstance(user_data, dict):
            self._user_data = user_data
        else:
            self.notify.error('Setting user data failed. Data is not a valid dictionary')

    def get_user_data(self) -> dict:
        """
        Returns this entity's user data
        """

        return self._user_data

    def update_user_data(self, user_data: dict) -> None:
        """
        Updates the entity's user data with another 
        dictionary
        """

        self._user_data.update(user_data)

    def set_user_data(self, key: str, value: object) -> None:
        """
        Sets the entity's user data key with the
        requested value
        """

        self._user_data[key] = value

    def get_user_data(self, key: str, default: object = None) -> object:
        """
        Returns this entity's user data key
        if present. otherwise returns the value
        of default
        """

        return self._user_data.get(key, default)

    def set_configuration(self, data: dict) -> None:
        """
        """

        if data:
            self.configuration = data
            Configurable.initialize(self)

    def seralize_configuration(self) -> dict:
        """
        """

        if self._user_data:
            return {'userData': self._user_data}
        else:
            return {}

    def attempt_reload(self) -> None:
        """
        Attempts to reload the entity object
        """

    def __str__(self) -> str:
        """
        """

        layer_id = ''
        if hasattr(self, '__layer'):
            layer_id = self.__layer.get_id()
        
        path = ''
        if hasattr(self, 'path'):
            path = self.path
        
        model_cls_name = 'None'
        model_config_path = ''
        if hasattr(self, '__model'):
            model_cls_name = self.__model.__class__.__name__
            model_config_path = self.__model.path
        
        return EntityProxy(
            layer_id, 
            self.__class__.__name__, 
            path, 
            self.get_name(), 
            model_cls_name, 
            model_config_path, 
            self.get_pos(), 
            self.get_h(), 
            self.seralize_configuration()).seralize()