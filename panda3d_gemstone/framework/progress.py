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

import inspect

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.engine import runtime

class ProgressCounter(InternalObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.start(*args, **kwargs)

    @property
    def max(self) -> float:
        """
        Returns this counters max as a property
        """

        return self.get_max()

    @max.setter
    def max(self, max: float) -> None:
        """
        Sets this counters max a setter
        """

        self.set_max(max)

    @property
    def current(self) -> float:
        """
        Returns this counters current as a property
        """

        return self.get_current()

    @current.setter
    def current(self, current: float) -> None:
        """
        Sets this counters current as a setter
        """

        self.set_current(current)

    def start(self, max: float = 0, current: float = 0) -> None:
        """
        """

        self._max = max
        self._current = current

    def get_max(self) -> float:
        """
        """

        return self._max

    def set_max(self, max: float) -> None:
        """
        """

        self._max = max

    def get_current(self) -> float:
        """
        """

        return self._current

    def set_current(self, current: float) -> None:
        """
        """

        self._current = current

    def reset_current(self) -> None:
        """
        Reset's this counters current value to zero
        """

        self.set_current(0)

    def finish(self):
        """
        Completes the counter by setting its current to the
        configured max value
        """

        self.set_current(self._max)

    def increase(self, value: float) -> None:
        """
        """

        current = self._current + value
        self.set_current(min(current, self._max))

    def decrease(self, value: float) -> None:
        """
        """

        current = self._current + value
        self.set_current(max(current, 0))

    def tick(self) -> None:
        """
        Increaes the counter by one
        """

        self.increase(1)

class ProgressController(ProgressCounter):
    """
    """

    @property
    def update_frequency(self) -> float:
        """
        Returns this controllers update frequency as a property
        """

        return self.get_update_frequency()

    @update_frequency.setter
    def update_frequency(self, frequency: float) -> None:
        """
        Sets this controllers update frequency as a setter
        """

        self.set_update_frequency(frequency)

    def start(self, max: float = 0, current: float = 0, update_frequency: float = 0.0) -> None:
        """
        """

        ProgressCounter.start(self, max, current)
        self._update_frequency = update_frequency
        self._last_update = 0.0

    def get_update_frequency(self) -> float:
        """
        Returns this controller's update frequency
        """

        return self._update_frequency

    def set_update_frequency(self, update_frequency: float) -> None:
        """
        Sets this controller's update frequency
        """

        self._update_frequency = update_frequency
        self._last_update = 0.0

    def set_current(self, current: float) -> None:
        """
        """

        ProgressCounter.set_current(self, current)
        dt = globalClock.get_dt()

        self._last_update += dt
        if self._last_update > self._update_frequency:
            self._last_update = 0
            
            sig = inspect.getfullargspec(self.update)
            args = len(sig[0])
            if args == 1:
                self.update()
            elif args == 2:
                self.update(current)
            elif args > 2:
                self.update(current. self.get_max())

    def update(self) -> None:
        """
        Called on progress counter change
        """

        raise NotImplementedError('%s does not implement update!' % self.__class__.__name__)

class RenderController(ProgressController):
    """
    Custom Progress Controller instance that forces
    a frame render each progress update
    """

    def update(self, current: object) -> None:
        """
        Called on progress counter change. Instructs
        the graphics engine to render a frame
        """

        if not runtime.has_base():
            self.notify.warning('Attempted to render frame via %s without a ShowBase!' % self.__class__.__name__)
            return

        try:
            runtime.base.graphicsEngine.render_frame()
        except:
            self.notify.warning('Failed to render frame for %s update: %s' % (self.__class__.__name__, current))