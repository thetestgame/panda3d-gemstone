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
import copy
import traceback

import glob

from panda3d.core import NodePath, Point3

from panda3d_gemstone.io.file_system import get_file_size, get_matching_files, path_exists
from panda3d_gemstone.framework.cast import cast
from panda3d_gemstone.framework.progress import ProgressCounter
from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.utilities import disallow_production

from panda3d_gemstone.logging.utilities import get_notify_category

from panda3d_gemstone.engine.messenger import MessageListener, event_handler
from panda3d_gemstone.engine import runtime, prc
from panda3d_gemstone.world.entity import Entity, EntityProxy


__world_notify = get_notify_category('world')

class Layer(InternalObject):
    """
    Represents a layer for containing and managing entity objects in a Gemstone world
    """

    def __init__(self, id, world):
        super().__init__()
        self._id = id
        self._world = world
        self._entites = []
        self._hidden = False

    @property
    def id(self) -> str:
        """
        Returns this layer's id as a property
        """

        return self.get_id()

    @property
    def world(self) -> object:
        """
        Returns this layer's world as a property
        """
        
        return self.get_world()

    @property
    def hidden(self) -> bool:
        """
        Returns this layer's hidden state as a property
        """

        return self.is_hidden()

    def has_entity(self, entity: Entity) -> bool:
        """
        Returns true if the layer contains the requested
        entity instance
        """

        return entity in self._entites

    def add_entity(self, entity: Entity) -> None:
        """
        Adds a new entity to the layer
        """

        # Verify the layer does not already contain 
        # the requested entity
        if self.has_entity(entity):
            return

        self._entites.append(entity)

        # Hide the entity if we are currently hidden
        if self._hidden:
            entity.hide()

    def remove_entity(self, entity: Entity) -> None:
        """
        Removes the requested entity from the layer
        """
        
        # Verify the layer contains the requested entity
        if self.has_entity(entity):
            self.notify.warning('Attempted to remove nonexistant entity from layer %d' % (id(self)))
            return

        entity.remove_node()

    def _remove_entity(self, entity: Entity) -> None:
        """
        Removes the requested entity from the entity
        list
        """

        self._entites.remove(entity)

    def clear(self) -> None:
        """
        Clears the entity layer of all data
        """

        while self._entites:
            self._entites[-1].destroy()

        self._world = None
        self._entites = []

    def get_id(self) -> str:
        """
        Returns this layer's id
        """

        return self._id

    def get_world(self) -> object:
        """
        Returns this layer's world instance
        """

        return self._world

    def get_entity(self, name: str) -> object:
        """
        Attempts to retrieve entities from the layer
        that match the requested name
        """

        entities = []
        for entity in self._entites:
            if entity.get_name() == name:
                entities.append(entity)

        if len(entities) == 1:
            return entities[0]
        return entities

    def get_entities(self, filter: object = None) -> list:
        """
        Returns the layers entity list with an optional filter operation
        to perform on the retrieval
        """

        if filter is None:
            return copy.copy(self._entites)
        else:
            return [entity for entity in self._entites if list(filter(entity))]

    def is_hidden(self) -> bool:
        """
        Returns this layer's hidden state
        """

        return self._hidden

    def show(self) -> None:
        """
        Changes the layers hidden state to show the layer
        """

        # Verify we need to do any operations
        if not self.is_hidden():
            return

        self._hidden = False
        self.get_entities(lambda entity: entity.show())

    def hide(self) -> None:
        """
        Changes the layers hidden state to hide the layer
        """

        # Verify we need to do any operations
        if self.is_hidden():
            return

        self._hidden = True
        self.get_entities(lambda entity: entity.hide())

    @disallow_production
    def reload_source(self) -> None:
        """
        Called when the source of the application is reloaded
        """

        self.notify.debug('Reloading world: %s' % self.get_id())
        for entity in self.get_entities():
            has_reload = hasattr(entity, 'attempt_reload')
            if has_reload:
                entity.attempt_reload()

    def __str__(self) -> str:
        """
        Custom string handler for the layer object
        """

        return '%s <%s> %s' % (self.__class__.__name__, self._id, str(self._hidden))

class World(NodePath, InternalObject):
    """
    Represents a game world in the gemstone framework. Containing all layers and entities
    used to perform visuals and actions within the level
    """

    def __init__(self):
        NodePath.__init__(self, '')
        InternalObject.__init__(self)
        self._layers = {}

    def get_entity(self, name: str, layer_id: str = None) -> object:
        """
        """

        if layer_id in self._layers:
            return self._layers[layer_id].get_entity(name)

        entities = []
        for layer in self.get_layers():
            entity = layer.get_entity(name)

            if type(entity) == type([]):
                entities += entity
            else:
                entities.append(entity)

        if len(entities) == 1:
            return entities[0]
        return entities

    def has_entity(self, entity: Entity) -> bool:
        """
        Returns true if the world contains the requested
        entity instance
        """

        for layer in self.get_layer():
            if layer.has_entity(entity):
                return True

        return False

    def get_entities(self, layer_id: str, filter: object = None) -> list:
        """
        Gets all entities in the requested layer using a filter lambda 
        operation
        """

        if layer_id in self._layers:
            return self._layers[layer_id].get_entities(filter)

        return []

    def get_all_entities(self, filter: object = None) -> list:
        """
        Retrieves all entities in the world using the requested filter
        lambda operation
        """

        return [ entity in layer in self.get_layers() for entity in layer.get_entities(filter)] 

    def get_all_layer_ids(self) -> list:
        """
        Returns all layer ids in the world
        """

        return list(self._layers.keys())

    def get_layers(self) -> list:
        """
        Returns all layers in the world
        """

        return list(self._layers.values())

    def has_layer_id(self, layer_id: str) -> bool:
        """
        Returns true if the layer id exists in the world
        """

        return layer_id in self._layers

    def get_layer(self, layer_id: str, create_if_needed: bool = False) -> Layer:
        """
        Attempts to retrieve a layer if it exists. Otherwise
        creates a new layer if create_if_needed is true and returns
        the new layer instance
        """

        if self.has_layer_id(layer_id):
            return self._layers[layer_id]
        else:
            if not create_if_needed:
                return None

            self._layers[layer_id] = Layer(layer_id, self)
            return self._layers[layer_id]

    def clear(self) -> None:
        """
        Clears the world of all data
        """

        for layer in self.get_layers():
            layer.clear()

        self._layers = {}

    def save(self, fh: object, progress_controller: object = ProgressCounter) -> None:
        """
        Saves the world to file using a file handle and progress controller
        instance
        """

        entities = self.get_all_entities()
        progress_controller.start(len(self._layers) + len(entities), 0)

        for layer_id, layer in list(self._layers.items()):
            if layer.get_entities():
                print(layer, file=fh)
            progress_controller.increase(1)
    
        for entity in entities:
            print(entity, file=fh)
            progress_controller.increase(1)

        progress_controller.finish()

    def _create_layer(self, layer_id: str, hidden: bool, line_nr: int) -> None:
        """
        """

        layer = self.get_layer(layer_id, create_if_needed=True)
        if layer:
            if hidden:
                layer.hide()
        else:
            logging.error('%s.load: Failed to create layer "%s" at line %d' % (
                self.__class__.__name__, layer_id, line_nr))

    def _create_entity(self, entity_proxy: EntityProxy, line_nr: int) -> Entity:
        """
        """

        try:
            return entity_proxy.instantiate(self, line_nr)
        except Exception as e:
            self.notify.warning('Failed to create entity on line %d (Error: %s)' % (line_nr, str(e)))
            if prc.get_prc_bool('gs-detailed-entity-errors', False):
                self.notify.warning(traceback.format_exc())
            
            return None

    def load(self, fh, progress_controller = ProgressCounter()) -> None:
        """
        """

        self.query(fh, self._create_layer, self._create_entity, progress_controller)

    def query(self, fh, for_each_layer = None, for_each_entity = None, progress_controller = ProgressCounter()) -> None:
        """
        """

        progress_controller.start(get_file_size(fh), 0)
        line_nr = 0

        try:
            for line in fh.readlines():
                line_nr += 1
                line = line[:-1]
                elements = line.split(' ')
                cls_name = elements[0]

                if cls_name == 'Layer':
                    layer_id = elements[1].strip(' <>')
                    hidden = elements[2]
                    if for_each_layer:
                        for_each_layer(layer_id, cast(hidden), line_nr)
                else:
                    entity_proxy = EntityProxy.from_string(line)
                    if entity_proxy:
                        if for_each_entity:
                            for_each_entity(entity_proxy, line_nr)
                    else:
                        self.notify.warning('Failed to parse entity at line #%d' % (self.__class__.__name__, line_nr))

                #progress_controller.set_current(fh.tell())
        except:
            self.notify.warning('Failed to parse world entities in file: %s' % fh.name)
            print(traceback.format_exc())

        progress_controller.finish()

    def is_hidden(self, layer_id: str) -> bool:
        """
        Returns true if the requested layer is hidden
        """

        layer = self.get_layer(layer_id)
        if layer:
            return layer.is_hidden()

        return False

    def show(self, layer_id: str = None) -> None:
        """
        Shows the specified layer id if provided. Otherwise
        shows all layers.
        """

        if layer_id is None:
            for layer in self.get_layers():
                layer.show()
        else:
            layer = self.get_layer(layer_id)
            if layer:
                layer.show()

    def hide(self, layer_id: str = None) -> None:
        """
        Hides the specified layer id if provided. Otherwise
        hides all layers
        """

        if layer_id is None:
            for layer in self.get_layers():
                layer.hide()
        else:
            layer = self.get_layer(layer_id)
            if layer:
                layer.hide()

    @disallow_production
    def reload_source(self) -> None:
        """
        Called on application source reload. Reloads owning layers
        """

        for layer in self.get_layers():
            layer.reload_source()

class WorldManager(InternalObject, MessageListener):
    """
    """

    def __init__(self):
        InternalObject.__init__(self)
        MessageListener.__init__(self)
        self.accept('gs-file-changed', self.__on_file_change)
        self._worlds = {}
        self._collision = None

    @property
    def worlds(self) -> dict:
        """
        Property for accessing the worlds dictionary
        """

        return self._worlds

    @property
    def collision(self) -> object:
        """
        Property for accessing the WorldManager collision node
        """

        return self._collision

    @staticmethod
    def encode_world_coords(pos: tuple) -> str:
        """
        Encodes a 3d coordinate for the world transform
        """

        try:
            max = pow(2, 15)
            x = int(pos[0])
            y = int(pos[1])

            if x > max - 1 or x < -max or y > max - 1 or y < -max:
                __world_notify.warning('WorldManager.encode_world_coords: World position (%s) is invalid for encoding!' % str(pos))
                return '-' * 8
            return '%04x%04x' % (x + max, y + max) 
        except:
            return pos

    @staticmethod
    def decode_world_coords(code: str)-> tuple:
        """
        Decodes a 3d world transform coordinate
        """

        try:
            max = pow(2, 15)
            x = '0x%s' % code[:4]
            y = '0x%s' % code[4:]

            return (int(x, 16) - max, int(y, 16) - max, 0)
        except:
            return code

    def create_world(self, idx: object) -> World:
        """
        Creates a new world instance
        """

        return World()

    def __get_index(self, pos: object):
        """
        """

        if isinstance(pos, str):
            return pos
        else:
            return (int(pos[0]), int(pos[1]), 0)

    def has_world(self, idx: object) -> bool:
        """
        Returns true if the world manager contains a world
        with the requested idx
        """

        return idx in self._worlds

    def get_world(self, pos) -> World:
        """
        """

        idx = self.__get_index(pos)
        if not self.has_world(idx):
            world = self.create_world(idx)

            # Reparent the world if the render has been defined
            if runtime.has_render():
                world.reparent_to(runtime.render)

            self._worlds[idx] = world

        return self._worlds[idx]

    def __getitem__(self, pos) -> World:
        """
        Custom get item handler for retrieving a world
        by its idx from the WorldManager
        """

        idx = self.__get_index(pos)
        if idx in self._worlds:
            return self._worlds[idx]

        return None

    def __len__(self) -> int:
        """
        Custom length handler for counting all the
        worlds within the WorldManager
        """

        all_empty = True

        for world in self._worlds:
            if len(world):
                all_empty = False
                break
        
        if all_empty:
            return 0
        else:
            return len(self._worlds)

    def __iter__(self) -> iter:
        """
        Custom iteration handler for iterating the worlds
        within the WorldManager
        """

        return iter(self._worlds)

    def keys(self) -> list:
        """
        Returns the world dictionary keys
        """

        return list(self._worlds.keys())

    def values(self) -> list:
        """
        Returns the world dictionary values
        """

        return list(self._worlds.values())

    def items(self) -> list:
        """
        Returns the world dictionary items
        """

        return list(self._worlds.items())

    @disallow_production
    def __on_file_change(self, file_path: str, ext: str) -> None:
        """
        Called on application file change. Informs all its owning worlds
        """
        
        for world in self.values():
            world.reload_source()

    def get_all_entities(self, filter: object = None) -> list:
        """
        Retrieves all entities in the world manager by 
        iterating through all the worlds
        """

        entities = []
        for world in self.values():
            enitities += world.get_all_entities(filter)

        return entities

    def has_entity(self, entity) -> bool:
        """
        Iterates through all the worlds in the WorldManager
        and returns true if the entity has been identified in a child
        world instance
        """

        for world in self.values():
            if world.has_entity(entity):
                return True

        return False

    def clear(self) -> None:
        """
        Clears the WorldManager instance of all worlds and data
        """

        for world in self.values():
            world.clear()
            world.remove_node()

        if self._collision:
            self._collision.remove_node()
            self._collision = None

        self._worlds = {}

    def stash(self) -> None:
        """
        Stashes all the worlds belonging to the WorldManager instance
        """

        for world in self.values():
            world.stash()

    def unstash(self) -> None:
        """
        Unstashes all the worlds belonging to the WorldManager instance
        """

        for world in self.values():
            world.unstash()

    def _iterate_worlds(self, path: str, progress_controller: object, process_func: object, func: object, *args) -> None:
        """
        Iterates over all level files in a directory and performs the process callback on each level
        file path
        """

        self.notify.debug('Iterating worlds at path: %s' % path)

        # Verify the process function is callable
        if not callable(process_func):
            raise Exception('Failed to iterate worlds at: %s. Process function is not callable' % path)

        # Verify the callback is callable
        if not callable(func):
            raise Exception('Failed to iterate worlds at: %s. Callback is not callable' % path)

        # Retrieve all worlds worlds and verify results were returned
        worlds = get_matching_files(path, '*.lvl')
        if not worlds:
            self.notify.warning('Failed to iterate worlds at: %s. No worlds found' % (path))
            return

        # Process all found worlds
        progress_controller.start(len(worlds), 0)
        for world_name in worlds:
            process_func(world_name, func, *args)
            progress_controller.increase(1)

        progress_controller.finish()

    def _process_world(self, world_name: str, func: object, *args) -> None:
        """
        """

        self.notify.debug('Processing world (%s) with function: %s' % (world_name, str(func)))

        # Verify our function is callable
        if not callable(func):
            self.notify.warning('Failed to process world %s. %s is not callable' % (
                world_name, str(func)))
            
            return

        world_coord = WorldManager.decode_world_coords(os.path.basename(world_name))[1:-4]
        world = self.get_world(world_coord)
        fh = open(world_name, 'r')
        func(world, fh, *args)
        fh.close()

    def load(self, path: str, process_world = World.load, progress_controller: object = ProgressCounter()) -> None:
        """
        Loads all levels at the requested path if any exist
        """

        self._iterate_worlds(path, progress_controller, self._process_world, process_world)

    def query(self, path: str, for_each_layer: object = None, for_each_entity: object = None, progress_counter: object = ProgressCounter()) -> None:
        """
        """

        self._iterate_worlds(path, progress_counter, self._process_world, World.query, for_each_layer, for_each_entity)

    def save(self, path: str, progress_counter: object = ProgressCounter()) -> None:
        """
        """

        self.notify.info('Saving WorldManager worlds to folder: %s' % path)
        progress_counter.start(len(self._worlds), 0)
        
        # Verify save directory exists
        if not os.path.exists(path):
            os.mkdir(path)

        for i, world_coord in enumerate(self._worlds):
            world = self.get_world(world_coord)
            
            if world.get_all_entities():
                output_path = os.path.join(path, 'b%s.lvl' % WorldManager.encode_world_coords(world_coord))
                fh = open(output_path, 'w')
                world.save(fh)
                fh.close()
            
            progress_counter.increase(1)
        
        progress_counter.finish()

    def clear_path(self, path: str) -> None:
        """
        """

        files = glob.glob(os.path.join(path, '*.lvl'))
        for file in files:
            os.unlink(file)

    def flatten(self, type: str = 'medium') -> None:
        """
        """

        for world in self.values():
            self.notify.debug('Flattening: %s' % world)

            if type == 'light':
                world.flatten_light()
            elif type == 'medium':
                world.flatten_medium()
            elif type == 'strong':
                world.flatten_strong()
            else:
                self.notify.warning('WorldManager.flatten Failed to flatten world. Unknown type: %s' % type)

    def load_collisions(self, collision_name) -> None:
        """
        """

        # Verify path eixsts
        if not path_exists(collision_name):
            return

        try:
            self._collision = runtime.loader.load_model(collision_name)
            if self._collision and runtime.has_render():
                self._collision.reparent_to(runtime.render)
        except:
            pass