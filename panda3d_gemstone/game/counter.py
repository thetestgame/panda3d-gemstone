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

from direct.interval.IntervalGlobal import Sequence, Wait, Func

from panda3d_gemstone.framework.internal_object import InternalObject

class CooldownCounter(InternalObject):
    """
    """

    def __init__(self, initial_value: object = 0.0, callback: object = None, *callback_args):
        self.initial_value = initial_value
        self.callback = callback
        self.callback_args = callback_args
        self.interval = None
        self.is_stopping = False

    @property
    def time(self) -> float:
        """
        Returns this counter's time as a property
        """

        return self.get_time()

    def get_time(self) -> float:
        """
        Returns this counters interval time
        """

        if self.interval:
            return self.interval.getT()

        return 0.0

    def set_speed(self, speed: float) -> None:
        """
        Sets this counter's current speed
        """

        self.speed = speed
    
    def get_speed(self) -> float:
        """
        Returns this counter's current speed
        """

        return self.speed

    def is_running(self) -> bool:
        """
        Returns true if the counter is currently running
        """

        if self.interval:
            return self.interval.isPlaying()

        return False

    def is_finished(self) -> bool:
        """
        Returns true if the counter is currently finished
        """

        if self.interval:
            return self.interval.isStopped() and not self.interval.isPlaying()
        return True

    def is_paused(self) -> bool:
        """
        Returns true if the counter is currently paused
        """

        if self.interval:
            return not self.interval.isPlaying() and not self.interval.isStopped()
        return False

    def __begin_interval(self, interval_func_name: str, initial_value: object, callback: object, *callback_args) -> None:
        """
        """

        # Stop any existing intervals
        self.stop(True)

        if initial_value is not None:
            self.initial_value = initial_value
        
        if callback is not None:
            self.callback = callback
            self.callback_args = callback_args
    
        if self.callback:
            self.interval = Sequence(Wait(self.initial_value), Func(self.callback, *callback_args))
        else:
            self.interval = Sequence(Wait(self.initial_value))

        interval_func = getattr(self.interval, interval_func_name, None)
        if callable(interval_func):
            interval_func()
        else:
            self.notify.error('Failed to start interval. Invalid interval function: %s' % interval_func_name)

    def start(self, initial_value: object, callback: object = None, *callback_args) -> None:
        """
        Starts the counter object interval
        """

        self.__begin_interval('start', initial_value, callback, *callback_args)

    def loop(self, initial_value: object, callback: object = None, *callback_args) -> None:
        """
        Loops the counter object interval
        """

        self.__begin_interval('loop', initial_value, callback, *callback_args)

    def stop(self, ignore_callback: bool = False) -> None:
        """
        Stops the counter object interval
        """

        if self.interval and not self.is_stopping():

            if ignore_callback:
                self.interval.clearIntervals()

            self.is_stopping = True
            self.interval.finish()
            self.interval = None
            self.is_stopping = False

    def pause(self) -> None:
        """
        Pauses the counter object interval
        """

        if self.interval:
            self.interval.pause()

    def resume(self) -> None:
        """
        Resumes the counter object interval
        """

        if self.interval:
            self.interval.resume()