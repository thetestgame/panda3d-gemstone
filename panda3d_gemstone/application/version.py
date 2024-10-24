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

from panda3d_gemstone.engine import runtime

from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.engine.prc import get_prc_bool, get_prc_string
from panda3d_gemstone.engine.prc import get_prc_int
from panda3d_gemstone.engine import runtime
from panda3d_gemstone import __version__ as gemstone_version

class ApplicationVersion(Singleton):
    """
    Wrapper to identify the version of the Gemstone Application
    """

    def __init__(self):
        version_parts = gemstone_version.split('.')
        self._major = get_prc_int('gs-v-major', int(version_parts[0]))
        self._minor = get_prc_int('gs-v-minor', int(version_parts[1]))
        self._release = get_prc_int('gs-v-release', int(version_parts[2]))
        super().__init__()

        use_sc_revision = get_prc_bool('gs-sc-revision', False)
        if use_sc_revision and runtime.is_developer_build():
            self._release = self.__get_version_from_revision()

    def major(self) -> int:
        """
        Application's major version integer
        """

        return self.major

    @property
    def minor(self) -> int:
        """
        Applications's minor version integer
        """

        return self._minor

    @property
    def release(self) -> int:
        """
        Application's release version integer
        """
        
        return self._release

    def __str__(self) -> str:
        """
        Returns the version as a string
        """

        base_str = '%s.%s.%s' % self.get()

        is_dev = runtime.is_developer_build()
        if is_dev:
            base_str = '%s - DEV' % base_str
    
        return base_str

    def get(self) -> tuple:
        """
        Returns the version as a tuple
        """

        return (self._major, self._minor, self._release)

    def __get_version_from_revision(self) -> str:
        """
        Returns the applications version from its current source
        control revision
        """

        from panda3d_gemstone.tools import source_control
        return source_control.get_local_head_revision('.')