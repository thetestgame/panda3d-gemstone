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

class SingleIntervalMixIn(object):
    """
    """

    def __init__(self):
        self.__interval = None
    
    @property
    def interval(self) -> object:
        """
        Currently active interval
        """
        
        return self.__interval

    def destroy(self) -> None:
        """
        Destroys the interval MixIn instance
        """

        self.finish_interval()

    def has_interval(self) -> bool:
        """
        Returns true if the object currently has an interval
        """

        return self.__interval != None

    def finish_interval(self) -> None:
        """
        Finishes and destroys the interval object
        """

        if not self.has_interval():
            return

        self.__interval.finish()
        self.__interval = None

    def set_interval(self, interval: object, start_interval: bool = False) -> None:
        """
        Sets the interval instance and attempts to start it if set
        """

        assert interval != None

        self.finish_interval()
        self.__interval = interval
        if start_interval:
            self.__interval.start()

    def get_interval(self) -> object:
        """
        Returns our interval instance
        """

        return self.__interval