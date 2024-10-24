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

from panda3d_gemstone.framework.controller import Controller, ControllerService
from panda3d_gemstone.framework.utilities import get_camel_case
from panda3d_gemstone.framework.exceptions import raise_not_implemented

class AnimationController(Controller):
    """
    Base class for all animation controllers inside Gemstone
    """

    def __init__(self, config_path: str, next_controller: object = None, section: str = 'Animation'):
        self.__game_object = None
        self.__current_animation = None
        self.__animation_states = {}
        self.__playing_emote = None
        self.__current_emote = None
        self.__next_animation = None
        self.__transition_duration = 0
        self.__transition_speed = 0.1
        super().__init__(config_path, next_controller, section)

    def destroy(self) -> None:
        """
        Destroys the animation controller instance
        """

        self.deactivate()
        self.__game_object = None
        super().destroy()

    def deactivate(self) -> None:
        """
        Deactivates the controller object
        """

        self.__current_animation = None
        self.__playing_emote = None

    def activate(self) -> None:
        """
        Activates the controller instance
        """

        # Play default idle animation if present
        if self.has_idle_animation():
            self.play_animation(self.get_idle_animation())

    def is_setup(self) -> bool:
        """
        Returns true if the controller has been setup
        """

        return self.__game_object != None

    def setup(self, game_object: object) -> None:
        """
        Performs setup operations for the controller instance. Takes
        an instnace of the game object to operate on
        """

        if self.is_setup():
            self.notify.warning('Attempting to setup already setup %s animation controller.' % (
                self.__class__.__name__))

            return

        self.__game_object = game_object

    def load_animation_states_data(self, data: dict) -> None:
        """
        Loads the animation states data into memory
        """

        self.__animation_states = data

    def has_animation_state(self, animation: str) -> bool:
        """
        Returns true if the controller has the requested animation state
        """

        return animation in self.__animation_states

    def get_animation_state(self, animation: str, default: str = None) -> str:
        """
        Retrieves the value of an animation state if available. Otherwise 
        returns default value
        """

        if not self.has_animation_state(animation):
            self.notify.warning('No animation state named: %s. Defaulting to "%s"' % (
                animation, default))

        return self.__animation_states.get(animation, default)

    def set_animation_state(self, animation: str, value: str) -> None:
        """
        Sets the animation state value
        """

        self.__animation_states[animation] = value

    def __set_animation_weight(self, animation: str, weight: int) -> None:
        """
        Sets an animations weight on the actor object
        """

        if weight > 1:
            weight = 0
        elif weight < 0:
            weight = 0

        self.notify.debug('(%s) %s = %s' % (self.__game_object.get_name(), animation, weight))
        self.__game_object.set_control_effect(animation, weight)

    def __getattr__(self, key: str) -> object:
        """
        Custom get attribute handler for allowing method access
        to the controller's animation states
        """

        result = None
        if len(key) > 4:
            type_name = key[:3]
            state_name = key[4:].replace('_animation', '')
            state_name = get_camel_case(state_name)

            if type_name == 'get':
                result = lambda x=None: self.get_animation_state(state_name, x)
            elif type_name == 'set':
                result = lambda x: self.set_animation_state(state_name, x)
            elif type_name == 'has':
                result = lambda: self.has_animation_state(state_name)
            elif len(key) > 5:
                type_name = key[:4]
                state_name = get_camel_case(key[5:])
                if type_name == 'play':
                    result = lambda x=False: self.__play_wrapper(state_name, x)

        if not result:
            raise AttributeError('%s does not have attribute %s' % (
                self.__class__.__name__, key))
        
        return result

    def __play_wrapper(self, state: str, *args, **kwargs) -> bool:
        """
        Wrapper to provide play_x() access to the play_animation function
        """

        state = getattr(self, 'get_%s_animation' % (state))()
        return self.play_animation(state, *args, **kwargs)

    def is_in_transition(self) -> bool:
        """
        Returns true if the controller is currently in an animation transition
        """

        return self.__next_animation != None

    def cancel_transition(self) -> None:
        """
        Cancels the current animation transition sequence
        """
        
        if not self.is_in_transition():
            return

        self.__game_object.stop(self.__next_animation)
        self.__set_animation_weight(self.__next_animation, 0)
        self.__next_animation = None

    def play_animation(self, animation: str, force: bool = False, instant: bool = False, transition_speed: int = 1) -> bool:
        """
        Plays the requested animation with optional force to play input, instant play, and transition speed parameters. 
        Returning true if the animation was played, otherwise false
        """

        if not self.is_setup():
            return False

        self.notify.debug('Playing animation %s on game object (%s)' % (
            animation, str(self.__game_object)))
        
        success = False
        if force or (self.__current_animation != animation and not self.is_in_transition()):
            self.__game_object.loop(animation)

            if instant or self.__current_animation == None:

                if self.__current_animation != None:
                    self.__game_object.stop(self.__current_animation)
                    self.__set_animation_weight(animation, 0)

                if self.__next_animation != None:
                    self.__game_object.stop(self.__next_animation)
                    self.__set_animation_weight(self.__next_animation, 0)
                    self.__next_animation = None
                
                self.__current_animation = animation
                self.__set_animation_weight(animation, 1)
            else:
                self.__set_animation_weight(animation, 0)
                self.__next_animation = animation
                self.__transition_duration = 1.0
                self.__transition_speed = transition_speed
        
            success = True

        return success

    def is_emoting(self) -> bool:
        """
        Returns true if the controller is currently emoting
        """

        return self.__playing_emote or self.__current_emote != None

    def can_play_emote(self, emote: str) -> bool:
        """
        Returns true if the controller is allowed to play the requested 
        emote. Intended to be overriden by children. 
        """

        return not self.is_emoting()

    def play_emote(self, emote: str) -> bool:
        """
        Attempts to play the requested emote. Returning true if the
        emote was played. Otherwise False
        """

        if not self.can_play_emote(emote):
            return False
        
        self.notify.debug('(%s) emote = %s' % (self.__game_object.get_name(), emote))
        self.__game_object.play(emote)
        self.__set_animation_weight(emote, 1)
        self.__playing_emote = self.__game_object.get_duration(emote)

        self.cancel_transition()
        self.__game_object.stop(self.__current_animation)
        self.__set_animation_weight(self.__current_animation, 0)

        return True

    async def update_node(self, nodepath: object, dt: float) -> object:
        """
        Performs animation update operations on the controller's
        node update loop.
        """

        await self.do_animation_logic(dt)
        await self.update_animation(dt)

        return nodepath

    async def do_animation_logic(self, dt: float) -> None:
        """
        Called once per frame to perform animation update logic. Intended
        to be overriden by children.
        """

    async def update_animation(self, dt: float) -> None:
        """
        Called once per frame to update the animation state. Intended
        to be overriden by children.
        """

        if self.__playing_emote != None:
            if self.__playing_emote - dt <= 0.0:
                self.play_idle(True)

                self.__game_object.stop(self.__current_emote)
                self.__set_animation_weight(self.__current_emote, 0)

                self.__current_emote = None
                self.__playing_emote = None
            else:
                self.__playing_emote -= dt
        elif self.__next_animation != None:
            remaining = self.__transition_duration
            self.__set_animation_weight(self.__current_animation, remaining)
            self.__set_animation_weight(self.__next_animation, 1.0 - remaining)
            self.__transition_duration -= self.__transition_speed * dt

            if self.__transition_duration <= 0:
                self.__set_animation_weight(self.__current_animation, 0)
                self.__set_animation_weight(self.__next_animation, 1)

                self.__game_object.stop(self.__current_animation)
                self.__current_animation = self.__next_animation
                self.__next_animation = None

class MovementController(ControllerService):
    """
    Base class for all character movement controllers inside Gemstone
    """

    def __init__(self, config_path: str, next_controller: object = None, section: str = None):
        self.__collision_engine = None
        self.__fall_callback = None
        self.__stand_callback = None
        super().__init__(config_path, next_controller, section)

    async def do_movement_logic(self, nodepath: object) -> None:
        """
        """

    async def update_move(self, nodepath: object, dt: float) -> None:
        """
        """

    async def update_node(self, nodepath: object, dt: float) -> object:
        """
        """

class AvatarController(MovementController, AnimationController):
    """
    Base class for all avatar controllers inside Gemstone
    """

    def __init__(self, config_path: str, next_controller: object = None, section: str = None):
        MovementController.__init__(self, config_path, next_controller, section)
        AnimationController.__init__(self, config_path, next_controller, section)

    def destroy(self) -> None:
        """
        Destroys the avatar controller instance
        """

        self.deactivate()

        MovementController.destroy(self)
        AnimationController.destroy(self)

    async def update_node(self, node_path: object, dt: float) -> object:
        """
        Called once per frame to update the avatar node instance
        """

        if self.get_commands_being_called():

            await self.do_movement_logic(node_path)
            await self.do_animation_logic()

            self.reset_commands_being_called()

        await self.update_move(node_path, dt)
        await self.update_animation(dt)

        return node_path

    def deactivate(self) -> None:
        """
        Deactivates the avatar controller
        """

        MovementController.deactivate(self)
        AnimationController.deactivate(self)

    def activate(self) -> None:
        """
        Activates the avatar controller
        """

        MovementController.activate(self)
        AnimationController.activate(self)



    
