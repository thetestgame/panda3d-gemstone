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

from direct.task import Task

from panda3d_gemstone.framework.utilities import create_task, remove_task
from panda3d_gemstone.engine.performance import get_collector

from panda3d.core import ConfigVariableBool

class Runnable(object):
    """
    Represents a repeating runnable object/task
    """

    def __init__(self, priority = 0, task_chain_name=None):
        self.__task = None
        self.__priority = priority
        self.__task_chain_name = task_chain_name
        self.__collector = get_collector('Gemstone:%s' % self.__class__.__name__)
        self.__collect = ConfigVariableBool('gs-time-runnables', True)

    @property
    def activated(self) -> bool:
        """
        Returns true if the runnable object is active
        """

        return self.is_activated()

    def activate(self) -> None:
        """
        Activates the runnable object's updates
        """

        if self.__task == None:
            self.__task = create_task(
                self._do_tick, 
                priority=self.__priority,
                task_chain_name=self.__task_chain_name)

            return True

        return False

    def deactivate(self) -> None:
        """
        Deactivates the runnable object's updates
        """

        if self.__task != None:
            self.__task = remove_task(self.__task)

            return True

        return False

    def is_activated(self) -> bool:
        """
        Returns true if the runnable object is active
        """

        return self.__task != None

    async def tick(self, dt: float) -> None:
        """
        Performs the tick operation for the runnable object
        """

        raise NotImplementedError('%s.tick does not implement tick!' % self.__class__.__name__)

    async def _do_tick(self, task: object) -> int:
        """
        Performs the task tick operation
        """

        if self.__collect.value:
            self.__collector.start()

        await self.tick(globalClock.get_dt())

        if self.__collect.value:
            self.__collector.stop()

        return Task.cont