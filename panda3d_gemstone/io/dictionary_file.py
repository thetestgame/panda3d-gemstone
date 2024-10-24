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

import json

from panda3d_gemstone.io.file_system import get_file_extension, path_exists

from panda3d_gemstone.framework.exceptions import raise_not_implemented
from panda3d_gemstone.framework.internal_object import InternalObject

def load_file(file_path: str) -> object:
    """
    Attempts to load a dictionary file from the application's
    file system
    """

    dict_file = DictionaryFile()
    success = dict_file.load(file_path)
    if not success:
        return None

    return dict_file

class DictionaryFile(InternalObject):
    """
    Represents a dictionary file in the Gemstone framework
    """

    def __init__(self):
        InternalObject.__init__(self)
        DataContainer.__init__(self)

        self.__data = {}

    @property
    def data(self) -> dict:
        """
        Data contained inside the dictionary file
        """

        return self.get_data()

    def get_data(self) -> dict:
        """
        Returns the data loaded from the dictionary file
        """

        return self.__data

    def load(self, file_path: str) -> bool:
        """
        Loads a dictionary file from the application's file system
        """

        if not path_exists(file_path):
            self.notify.wanring('Attempted to load nonexistance file: %s' % file_path)
            return False

        ext = get_file_extension(file_path).lower()
        ext_handler = getattr(self, '__parse_%s' % ext)
        if not ext_handler:
            self.notify.warning('Attempted to load unsupported file type: %s' % ext)
            return False

        data = open(file_path, 'r')
        try:
            ext_handler(data)
        except Exception as e:
            self.notify.warning('Failed to parse dictionary file: %s' % file_path)
            return False

        return True

    def write(self, file_path: str) -> None:
        """
        Writes a dictionary file to the application's file system
        """

        raise_not_implemented(self, 'write')

    def __parse_json(self, data: str) -> None:
        """
        Parses incoming json data
        """

        incoming = json.loads(data)
        for key, value in incoming.items():
            self.__data[key] = value
        

