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

import os

from panda3d_gemstone.logging.utilities import get_notify_category
from panda3d_gemstone.engine import prc

__default_revision = prc.get_prc_string('gs-sc-default', '???')
__source_control_notify = get_notify_category('source-control')

def contains_git_repo(path: str) -> bool:
    """
    Returns true if the specified path
    contains a git based source control
    repository
    """

    return os.path.exists(os.path.join(path, '.git'))

def contains_svn_repo(path: str) -> bool:
    """
    Returns true if the specified path
    contains a svn based source control
    repository
    """

    __source_control_notify.warning('contains_svn_repo is not currently implemented!')

    return False

def get_git_local_head_revision(path: str) -> str:
    """
    Returns the local git head revision at the specified
    path if its a valid git repository
    """

    assert path != None
    assert path != ''

    revision = __default_revision
    try:
        import git
        repo = git.Repo(path)
        revision = repo.head.commit
    except Exception as e:
        __source_control_notify.warning('Failed to retrieve git head revision: %s' % str(e))

    return str(revision)

def get_svn_local_head_revision(path: str) -> str:
    """
    Returns the local svn head revision at the specified
    path if its a valid svn repository
    """

    assert path != None
    assert path != ''

    revision = __default_revision
    try:
        import pysvn
        svn_client = pysvn.Client()
        svn_info = svn_client.info(path)
        revision = svn_info['revision'].number
    except:
        __source_control_notify.warning('Failed to retrieve svn head revision: %s' % str(e))

    return str(revision)

def get_local_head_revision(path: str) -> str:
    """
    Returns the local head revision of the repository at the
    specified path. Supports svn and git repositories. Returns
    the value of default revision if the repository is not known
    or it is invalid
    """

    revision = __default_revision
    if contains_git_repo(path):
        revision = get_git_local_head_revision(path)
    elif contains_svn_repo(path):
        revision = get_svn_local_head_revision(path)

    return revision

