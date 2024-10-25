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

try:
    from setuptools import setup as __setup
except ImportError:
    from distutils.core import setup as __setup

import os
import re
import sys
import codecs
import subprocess

# Verify the python version meets minimum requirements
if sys.version_info[0] == 3 and sys.version_info < (3, 4):
    sys.exit("Error: Python 3.4 or newer is required.")

__here = os.path.abspath(os.path.dirname(__file__))
__root_package = 'panda3d_gemstone'
__version_file = '__version__.py'
__description = 'top level framework built for the Panda3D game engine'
__license = 'MIT'
__repository = 'https://github.com/thetestgame/panda3d-gemstone'
__classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Natural Language :: English',
    'Programming Language :: Python :: 3'
]

def __has_thirdparty(import_string: str) -> bool:
    """
    Returns true if the import string is valid
    """

    found = False
    import importlib
    try:
        module = importlib.import_module(import_string)
        found = True
    except:
        pass

    return found

def __codec_read(*parts) -> object:
    """
    Reads a file with the codedcs module
    """

    with codecs.open(os.path.join(__here, *parts), 'r') as fp:
        return fp.read()

def __get_file_contents(file_path: str) -> str:
    """
    Returns the contents of a file as a string
    """

    return open(file_path).read()

def __get_readme() -> str:
    """
    Returns the contents of the package's README file
    """

    return __get_file_contents('README.md')

def __get_requirements(file_path: str = 'requirements.txt') -> list:
    """
    Returns the contents of the requested requirements.txt
    file
    """

    try: # for pip >= 10
        from pip._internal.req import parse_requirements
    except ImportError: # for pip <= 9.0.3
        from pip.req import parse_requirements

    install_reqs = parse_requirements(file_path, session='hack')
    reqs = [str(ir.requirement) for ir in install_reqs]
    
    return reqs

def __find_version(*file_paths) -> str:
    """
    Attempts to find the version from a specific module path
    """

    version_file = __codec_read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)

    if version_match:
        return version_match.group(1)

    raise RuntimeError('Install failed. Unable to find version string')

def __list_as_string(parts: list, splice: str = ', ') -> str:
    """
    Returns the list as a string
    """

    return splice.join(parts)

def __get_authors() -> str:
    """
    Returns all authors as a string
    """

    authors = ['Jordan Maxwell']
    #results = subprocess.check_output(['git', 'log', '--pretty="%an"']).decode()
    #results = results.split('\n')

    #for author in results:
    #    author = author.replace('"', '')
    #    if author not in authors and author != '':
    #        authors.append(author)

    return __list_as_string(authors)

def __get_modules(root_module: str) -> list:
    """
    Retrieves all modules inside a root module
    """

    modules = [root_module]
    for root, subdirs, _ in os.walk(root_module):
        root = root.replace(os.sep, '.')
        for subdir in subdirs:
            if subdir.startswith('__'):
                continue

            modules.append('%s.%s' % (root, subdir))

    return modules

def __main() -> int:
    """
    Main entry point for the setup script
    """

    __setup(
        name=__root_package,
        description=__description,
        long_description=__get_readme(),
        license=__license,
        version=__find_version(__root_package, __version_file),
        author=__get_authors(),
        url=__repository,
        #install_requires=__get_requirements(),
        packages=__get_modules(__root_package),
        zip_safe=False,
        classifiers=__classifiers)

    return 0

if __name__ == '__main__':
    sys.exit(__main())