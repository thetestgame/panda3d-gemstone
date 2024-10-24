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

from panda3d_gemstone.io.file_system import path_exists
from panda3d_gemstone.engine import runtime

SUPPORTED_MODELS = [
    'bam.pz',
    'bam',
    'egg',
    'egg.pz',
    'fbx',
    'obj'
]

def attempt_load_model(model_name: str, **kwargs) -> bool:
    """
    Attempts to load the model path as all possble
    supported models
    """

    found = False
    for model_type in SUPPORTED_MODELS:
        possible_path = '%s.%s' % (model_name, model_type)
        if path_exists(possible_path):
            runtime.loader.load_model(possible_path, **kwargs)
            found = True
            break

    return found

def attempt_unload_model(model_name: str, **kwargs) -> bool:
    """
    Attempts to unload the model path as all possble
    supported models
    """

    found = False
    for model_type in SUPPORTED_MODELS:
        possible_path = '%s.%s' % (model_name, model_type)
        if path_exists(possible_path):
            runtime.loader.unload_model(possible_path, **kwargs)
            found = True
            break

    return found