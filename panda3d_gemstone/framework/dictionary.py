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

from panda3d_gemstone.logging.utilities import get_notify_category

__notify = get_notify_category('dictionary')

class ObjectDictionary(dict):
    """
    """

    def __init__(self):
        super.__init__()

    def add_object(self, obj: object) -> None:
        """
        """

        if not hasattr(obj, 'get_object_id'):
            self.notify.warning('Attempted to add an invalid object to %s (%s)' % (
                self.__class__.__name__, obj.__class__.__name__))
            
            return

        object_id = obj.get_object_id()
        if object_id in self:
            self.notify.warning('Attempted to add duplicate object to %s.' % self.__class__.__name__)
        self[object_id] = obj

    def lookup_object(self, object_id: int) -> object:
        """
        """

        obj = self.get(object_id, None)
        if obj is None:
            __notify.warning('Object lookup failed. %s is not a known object idetifier' % object_id)
    
        return obj
