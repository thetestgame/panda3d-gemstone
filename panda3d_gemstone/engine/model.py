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

from panda3d.core import TextureAttrib, DepthWriteAttrib, TransparencyAttrib
from panda3d.core import ColorAttrib, ModelNode, NodePath, Texture, TextureStage

from direct.actor.Actor import Actor

from panda3d_gemstone.framework.resource import Resource, ExportProperty, ResourceManager
from panda3d_gemstone.io.file_system import path_exists
from panda3d_gemstone.framework.internal_object import InternalObject

from panda3d_gemstone.engine import runtime
from panda3d_gemstone.engine.model_utilities import get_all_geom_nodes, get_all_geom_states
from panda3d_gemstone.engine.loader import attempt_load_model, attempt_unload_model

class Model(Resource, InternalObject):
    """
    Represents a basic model in the Gemstone framework for game and editor use
    """

    def __init__(self, config_path: str, force_export: bool = False, load_immediate: bool = True):
        self._disable_setting_render_state = False
        InternalObject.__init__(self)
        Resource.__init__(self, config_path, force_export, load_immediate)

    @property
    def disable_setting_render_state(self) -> bool:
        """
        """

        return self.get_disable_setting_render()

    @disable_setting_render_state.setter
    def disable_setting_render_state(self, state) -> None:
        """
        """

        self.set_disable_setting_render_state(state)

    def set_disable_setting_render_state(self, state: bool) -> None:
        """
        """

        self._disable_setting_render_state = state

    def get_disable_setting_render(self):
        """
        """

        return self._disable_setting_render_state

    def prepare_as_rp_scene(self) -> None:
        """
        Prepares the model as a render pipeline scene
        """

        if not runtime.has_render_pipeline():
            self.notify.warning('Attempted to prepare as rp scene. RenderPipeline not found.')
            return

        runtime.render_pipeline.prepare_scene(self)

    def fixup_render_state(self) -> None:
        """
        """

        if self._disable_setting_render_state:
            return

        for geom_node in get_all_geom_nodes(self):
            for i in range(geom_node.get_num_geoms()):
                state = geom_node.get_geom_state(i)
                texture_attrib = state.get_attrib(TextureAttrib.get_class_type())

                if not texture_attrib:
                    continue

                texture = texture_attrib.get_texture()
                if not texture:
                    continue

                filename = texture.get_filename().get_basename_wo_extension()
                transparency_attrib = None
                color_attrib = None
                depth_write_attr = None

                if filename.find('_plant') >= 0:
                    transparency_attrib = TransparencyAttrib.make(TransparencyAttrib.MDual)
                
                if filename.find('_mask') >= 0:
                    transparency_attrib = TransparencyAttrib.make(TransparencyAttrib.MBinary)

                if filename.find('_shadow') >= 0:
                    depth_write_attr = DepthWriteAttrib.make(DepthWriteAttrib.MOff)
                    transparency_attrib = TransparencyAttrib.make(TransparencyAttrib.MAlpha)

                if filename.find('_bright') >= 0:
                    color_attrib = ColorAttrib.make_off()

                for attrib in [transparency_attrib, color_attrib, depth_write_attr]:
                    if attrib:
                        geom_node.set_geom_state(i, geom_node.get_geom_state(i).add_attrib(attrib))
 
class StaticModel(Model, NodePath):
    """
    Represents a static model in the gemstone framework
    """

    def __init__(self, config_path: str, force_export: bool = False, load_immediate: bool = True):
        self._optimize_geometries = True
        self._generate_txo = False
        self._generate_mipmaps = False
        self._override_texture = None
        self._override_texture_name = None
        self._models = []
        self._model_data = {}
        self._pending_loads = 0

        NodePath.__init__(self, self.__class__.__name__)
        Model.__init__(self, config_path, force_export, load_immediate)

    @property
    def optimized_geometries(self) -> bool:
        """
        Returns the optimized geometries flag as a property
        """

        return self.get_optimize_geometries()

    @optimized_geometries.setter
    def optimized_geometries(self, value) -> None:
        """
        Sets the optimized geometries flag as a setter
        """

        self.set_optimize_geometries(value)

    def destroy(self) -> None:
        """
        Destroys the static model instance
        """
        
        Model.destroy(self)
        self.remove_node()

    def load_model_data(self, data: dict) -> None:
        """
        Loads a data dictionary into the static model
        """

        self._model_data = data

    def set_optimize_geometries(self, optimized_geometries: bool) -> None:
        """
        Sets the optimized geometries flag
        """

        self._optimize_geometries = optimized_geometries        

    def get_optimize_geometries(self) -> bool:
        """
        Returns the optimized geometries flag
        """

        return self._optimize_geometries

    def set_generate_txo(self, generate_txo: bool) -> None:
        """
        """

        self._generate_txo = generate_txo

    def get_generate_txo(self) -> bool:
        """
        """

        return self._generate_txo

    def set_generate_mipmaps(self, generate_mipmaps: bool) -> None:
        """
        """

        self._generate_mipmaps = generate_mipmaps

    def get_generate_mipmaps(self) -> None:
        """
        """

        return self._generate_mipmaps

    def set_override_texture(self, override_texture: object) -> None:
        """
        """

        self._override_texture = override_texture

    def get_override_texture(self) -> object:
        """
        """

        return self._override_texture

    def _generate_texture_options(self) -> dict:
        """
        Generates the texture export options
        """

        egg2bam_options = {}
        if self._generate_txo:
            egg2bam_options['-txo'] = ''
        if self._generate_mipmaps:
            egg2bam_options['-mipmaps'] = ''

        return egg2bam_options

    def export(self, force_export: bool) -> None:
        """
        Exports the static model to disk
        """

        self._models = []
        texture_options = self._generate_texture_options()
        for part, value in list(self._model_data.items()):
            export = ExportProperty(part, value, 'Export')
            export.options['-keep-uvs'] = ''
            self.add_export_step(export)
            #self.extend_export_steps(export.generate_post_egg2bampz(texture_options))
            self._models.append(self.get_export_step(-1).output_filename)

        Model.export(self, force_export)

    def _load(self, force_export: bool) -> bool:
        """
        """

        # Verify we are not already loaded
        if self.loaded:
            return False

        success = Model._load(self, force_export)
        if not success:
            return False

        if len(self._models) == 0:
            self.notify.warning('Failed to load %s. No models to load' % self.__class__.__name__)
            return False

        loader_options = ResourceManager.get_singleton().get_loader_options()
        for model_name in self._models:
            model = self.__load_model(model_name, loaderOptions=loader_options)

        return True

    def do_override_texture(self, texture_name: str) -> None:
        """
        """

        try:
            texture = runtime.loader.load_texture(texture_name)
            if texture:
                texture.set_magfilter(Texture.FTLinear)
                texture.set_minfilter(Texture.FTLinearMipmapLinear)

                for geom_node in get_all_geom_nodes(self):
                    for i in range(geom_node.get_num_geoms):
                        state = geom_node.get_geom_state(i)
                        geom_node.set_geom_state(i, state.add_attrib(TextureAttrib.make(texture)))
        except IOError:
            self.notify.warning('%s.do_override_texture: Failed to load texture "%s"' % (
                self.__class__.__name__, texture_name))

    def __process_model(self, model) -> None:
        """
        Processes a newly loaded model in async via a callback
        """

        if not model:
            self.notify.error('Failed to load model for object %s.' % self.__class__.__name__)
            return

        if self.is_empty():
            self.notify.warning('Failed to load model for object %s. StaticModel is empty' % (
                self.__class__.__name__))

            return

        if not self._optimize_geometries:
            model.reparent_to(self)
        else:
            model.get_children().reparent_to(self)
        self._pending_loads -= 1

        # Check if we are done loading
        if self._pending_loads <= 0:
            self.__finish_load()

    def __finish_load(self) -> None:
        """
        Called on model loading complete
        """

        if self._optimize_geometries:
            self.flatten_strong()

        if self._override_texture:
            self.do_override_texture(self._override_texture)

        self.fixup_render_state()

    def __load_model(self, model_name: str, **args) -> None:
        """
        Loads the requested model from the VFS
        """

        try:
            success = attempt_load_model(model_name, callback=self.__process_model, **args)
            if not success:
                self.notify.warning('Failed to load model (%s) for %s.' % (
                    model_name, self.__class__.__name__))
            else:
                self._pending_loads += 1
        except IOError:
            pass

    def _unload(self) -> bool:
        """
        Unloads the StaticModel object
        """

        if not self.loaded:
            return False
        
        for i in range(self.get_num_children() - 1, -1, -1):
            self.get_child(i).remove_node()

        for model_name in self._models:
            success = attempt_unload_model(model_name)
            if not success:
                self.notify.warning('%s.__unload: Failed to unload model (%s).' % (
                    self.__class__.__name__, model_name))

class TextureModel(StaticModel):
    """
    Represents a texture model in the Gemstone framework
    """

    def __init__(self, config_path: str, force_export: bool = False):
        self.__generate_ico = False
        self.__width = 0
        self.__height = 0
        self.__depth = 0
        super().__init__(config_path, force_export)
        self.__cache_width_and_height()

    @property
    def generate_ico(self) -> bool:
        """
        Returns the model's generate ico attribute
        as a property
        """

        return self.get_generate_ico()

    @generate_ico.setter
    def generate_ico(self, generate_ico: bool) -> None:
        """
        Sets the model's generate ico attribute
        as a setter
        """

        self.set_generate_ico(generate_ico)

    @property
    def width(self) -> int:
        """
        Returns this model's cached width
        as a property
        """

        return self.get_width()

    @property
    def height(self) -> int:
        """
        Returns this model's cached height
        as a property
        """

        return self.get_height()

    @property
    def depth(self) -> int:
        """
        Returns this model's cached depth
        as a property
        """

        return self.get_depth()

    def set_generate_ico(self, generate_ico: bool) -> None:
        """
        Sets the texture model's generate ico attribute
        used in exporting
        """

        self.__generate_ico = generate_ico

    def get_generate_ico(self) -> bool:
        """
        Returns the texture model's generate ico attribute
        """

        return self.__generate_ico

    def export(self, force_export: bool) -> None:
        """
        Exports the TextureModel to disk
        """

        texture_options = self._generate_texture_options()
        for part, value in list(self._model_data.items()):
            export = ExportProperty(part, value, 'TextureCards')
            self.add_export_step(export)
            self.extend_export_steps(export.generate_post_bam2pz(texture_options))
            
            if self.__generate_ico:
                export = ExportProperty(part, value, 'Png2Ico')
                self.add_export_step(export)

            self._models.append(self.get_export_step(-1).output_filename)

        Resource.export(self, force_export)

    def __cache_width_and_height(self) -> None:
        """
        Caches the TextureModels width and height
        of its geom textures
        """

        self.__width = 0
        self.__height = 0
        self.__depth = 0

        for geom_state in get_all_geom_states(self):
            texture_attrib = geom_state.get_attrib(TextureAttrib.get_class_type())

            if not texture_attrib:
                continue

            texture = texture_attrib.get_texture()
            if not texture:
                continue

            self.__width = max(self.__width, texture.get_x_size())
            self.__height = max(self.__height, texture.get_y_size())
            self.__depth = max(self.__depth, texture.get_z_size())

    def get_width(self) -> int:
        """
        Returns the TextureModel's cached width
        """

        return self.__width
    
    def get_height(self) -> int:
        """
        Returns the TextureModel's cached height
        """

        return self.__height

    def get_depth(self) -> int:
        """
        Returns the TextureModel's cached depth
        """

        return self.__depth
    
class AnimatedModel(Model, Actor):
    """
    Represents an animated model in the Gemstone framework
    """

    def __init__(self, config_path: str, force_export: bool = False, have_anim_in_node: bool = True):
        self.__have_anim_in_node = have_anim_in_node
        self.__optimize_geometries = True
        self.__optimize_animations = False
        self.__generate_txo = False
        self.__generate_mipmaps = False
        self.__include_animation = False
        self.__models = []
        self.__load_on_demand = False
        self.__animations = []
        self.__animation_blend = False
        self.__frame_blend = False

        Actor.__init__(self)
        Model.__init__(self, config_path, force_export)

        resource_mgr = ResourceManager.get_singleton()
        if resource_mgr and hasattr(self, 'model_loader_options'):
            self.model_loader_options.set_flags(self.model_loader_options.get_flags() | resource_manager.get_loader_options().get_flags())
        
    def destroy(self) -> None:
        """
        Destroys the animated model
        """

        self.cleanup()
        self.remove_node()

    def np_copy_to(self, destination: object, sort: int = 0) -> object:
        """
        Copys the nodepath to a new destination with an optional sort
        """

        return NodePath.copy_to(self, destination, sort)

    def make_copy_to(self, destination: object, callback: object = None, extra_args: list = [], task_chain_name: str = None) -> None:
        """
        """

        destination.copyActor(other=self, overrwrite=False, callback=callback, extraArgs=extra_args, taskChainName=task_chain_name)
        destination.__optimize_geometries = self.__optimize_geometries
        destination.__optimize_animations = self.__optimize_animations
        destination.__generate_txo = self.__generate_txo
        destination.__generate_mipmaps = self.__generate_mipmaps
        destination.__include_animation = self.__include_animation
        destination.__models = copy.copy(self.__models)
        destination.__model_data = copy.copy(self.__model_data)
        destination.__load_on_demand = self.__load_on_demand
        destination.__animations = copy.copy(self.__animations)
        destination.__actions = copy.copy(self.__actions)
        destination.__emotes = copy.copy(self.__emotes)
        destination.__animation_data =copy.copy(self.__animation_data)
        destination.path = self.path
        destination.sectoin = self.section

    def load_model_data(self, data: dict) -> None:
        """
        Loads the model data into memory
        """

        self.__model_data = data

    def load_animation_data(self, data: dict) -> None:
        """
        Loads the animation data into memory
        """

        self.__animation_data = data

    def load_action_data(self, data: dict) -> None:
        """
        Loads the action data into memory
        """

        self.__actions = data

    def load_emote_data(self, data: dict) -> None:
        """
        Loads the emote data into memory
        """

        self.__emotes = data

    def get_actions(self) -> list:
        """
        Returns the available actions
        """

        return list(self.__actions.keys())

    def get_emotes(self) -> list:
        """
        Returns the available emotes
        """

        return list(self.__emotes.keys())

    def set_animation_blend(self, state: bool) -> None:
        """
        Sets the animated model's animation blend value
        """

        self.__animation_blend = state

    def set_frame_blend(self, state: bool) -> None:
        """
        Sets the animated model's frame blend value
        """

        self.__frame_blend = state
 
    def set_load_on_demand(self, load_on_demand: bool) -> None:
        """
        Sets the animated model's load on demand value
        """

        self.__load_on_demand = load_on_demand

    def set_optimize_geometries(self, optimized_geometries: bool) -> None:
        """
        Sets the aniamted model's optimize geometry flag for auto flattening
        """

        self.__optimize_geometries = optimized_geometries

    def get_optimize_geometries(self) -> bool:
        """
        """

        return self.__optimize_geometries

    def set_optimize_animations(self, optimize_animations: bool) -> None:
        """
        """

        self.__optimize_animations = optimize_animations

    def get_optimize_animations(self) -> bool:
        """
        """

        return self.__optimize_animations

    def set_generate_tx_(self, generate_txo: bool) -> None:
        """
        """

        self.__generate_txo = generate_txo

    def get_generate_txo(self) -> bool:
        """
        """

        return self.__generate_txo

    def set_generate_mipmaps(self, generate_mipmaps: bool) -> None:
        """
        """

        self.__generate_mipmaps = generate_mipmaps

    def get_generate_mipmaps(self) -> bool:
        """
        """

        return self.__generate_mipmaps

    def set_include_animation(self, include_animation: bool) -> None:
        """
        """

        self.__include_animation = include_animation

    def get_include_animation(self) -> bool:
        """
        """

        return self.__include_animation

    def _generate_texture_options(self) -> dict:
        """
        Returns the model's texture export options
        """

        egg2bam_options = {}
        if self.__generate_txo:
            egg2bam_options['-txo'] = ''

        if self.__generate_mipmaps:
            egg2bam_pptions['-mipmap'] = ''
        
        return egg2bam_options

    def export(self, force_export: bool) -> None:
        """
        Performs export operations on the AnimatedModel instance
        """

        texture_options = self._generate_texture_options()
        for part, value in list(self.__model_data.items()):
            export = ExportProperty(part, value, 'Export')
            if self.__include_animation:
                export.options['-a'] = 'both'
                export.options['-cn'] = 'idle'
            else:
                export.options['-a'] = 'model'
            export.options['-keep-uvs'] = ''
            self.add_export_step(export)
            
            previous_step = export
            if not self.__optimize_geometries:
                optimize = ExportProperty()
                optimize.input_filename = previous_step.output_filename
                optimize.output_filename = optimize.input_filename
                optimize.options['-flag'] = '"*"'
                optimize.options['-keepall']  = ''
                optimize.converter = 'OptChar'

                self.add_export_step(optimize)
                previous_step = optimize

            if self.__optimize_animations:
                self.notify.warning('Optimizing animations on export is not currently supported')

            self.extend_export_steps(export.generate_post_bam2pz())
            self.__models.append(self.get_export_step(-1).output_filename)

        for part, value in list(self.__animation_data.items()):
            export = ExportProperty(part, value, 'Export')
            export.options['-a'] = 'chan'
            self.add_export_step(export)
            self.extend_export_steps(export.generate_post_bam2pz())
            self.__animations.append(self.get_export_step(-1).output_filename)

        Model.export(self, force_export)

    def _load_model(self, model_name: str) -> None:
        """
        Loads the AnimatedModel instance from disk
        """

        self.notify.debug('Loading %s "%s"...' % (self.__class__.__name__, model_name))
        try:
            if path_exists(model_name + '.bam.pz'):
                self.load_model(model_name + '.bam.pz', autoBindAnims=self.__have_anim_in_node)
            elif path_exists(model_name + '.bam'):
                self.load_model(model_name + '.bam', autoBindAnims=self.__have_anim_in_node)
            elif path_exists(model_name + '.egg'):
                self.load_model(model_name + '.egg', autoBindAnims=self.__have_anim_in_node)    
            else:
                self.notify.warning('Failed to load model. Missing model part file "%s"' % model_name)
        except Exception:
            self.notify.warning('Failed to load model. Missing model part file "%s"' % model_name)

    def __get_all_animation_items(self) -> list:
        """
        Returns all configured animations in the AnimatedModel instance
        """

        return list(self.__actions.items()) + list(self.__emotes.items())

    def _load(self, force_export: bool) -> bool:
        """
        Loads the animated model into memory
        """

        if not Model._load(self, force_export):
            self.notify.error('Failed to load %s. Base load failed' % (
                self.__class__.__name__))
            return False

        if not len(self.__models):
            self.notify.error('Failed to load %s. No models to load' % (
                self.__class__.__name__))
            
            return False

        for part in self.__models:
            self._load_model(part)

        animation_dict = {}
        animation_items = self.__get_all_animation_items()
        if not len(animation_items):
            self.notify.warning('No animation items loaded into AnimatedModel')

        for action_name, action_file in animation_items:
            found = False

            for animation_name in self.__animations:
                if action_file == animation_name:
                    suffix = None
                    if path_exists(action_file + '.bam.pz'):
                        suffix = '.bam.pz'
                    elif path_exists(action_file + '.bam'):
                        suffix = '.bam'
                    elif path_exists(action_file + '.egg'):
                        suffix = '.egg'

                    if suffix:
                        animation_dict[action_name] = action_file + suffix
                        found = True

            if not found:
                self.notify.error('Missing animation file "%s" for action "%s"' % (action_file, action_name))

        self.set_blend(
            animBlend=True, #self.__animation_blend, #TODO: fix order of operations for the config
            frameBlend=self.__frame_blend)

        self.load_anims(animation_dict)
        if not self.__load_on_demand:
            try:
                for animation in animation_dict:
                    self.bind_anim(animation) 
            except KeyError as e:
                self.notify.warning('Failed to bind animations, Required part missing: %s' % str(e))

        self.fixup_render_state()
        return True

    def _unload(self) -> bool:
        """
        Unloads the AnimatedModel from memory
        """

        if Model._unload(self):
            children = self.get_geom_node().get_children()
            children.detach()
            for part in self.__models:
                self.remove_part(part)
                runtime.loader.unload_model(part + '.bam.pz')

            self.unload_anims(self.__actions)
            self.unload_anims(self.__emotes)

            return True

        return False