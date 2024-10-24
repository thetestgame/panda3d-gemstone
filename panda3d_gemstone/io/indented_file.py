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

import re
import copy
import weakref
import codecs

from panda3d_gemstone.framework.pcast import cast
from panda3d_gemstone.logging.utilities import get_notify_category
from panda3d_gemstone.engine import prc

WORD = '([A-Za-z_][a-zA-Z_0-9]*)'
OPTIONAL_WORD = WORD + '?'
LINE_RE = re.compile('(\\s*)(\\*?)\\s*' + WORD + '\\s*' + OPTIONAL_WORD + '\\s*\\:\\s*(.*)')
__notify = get_notify_category('indented-file')
__detailed_syntax_error = prc.get_prc_bool('gs-if-detailed-syntax', False)

class ParserNode(object):
    """
    Represents a node in the indented file parser
    """

    def __init__(self, pn: object = None):
        if pn:
            self.type = pn.type
            self.free = pn.free
            self.name = pn.name
            self.args = copy.copy(pn.args)
            self.parent = pn.parent
        else:
            self.type = ''
            self.free = ''
            self.name = ''
            self.args = ''
            self.parent = None

    def __str__(self):
        """
        Custom string handler for printing out information regarding
        the ParserNode object
        """

        if self.parent:
            parent_name = self.parent.name
            if not parent_name:
                parent_name = 'ID: ' + str(id(self.parent))
        else:
            parent_name = 'None'

        return 'self: %s\ntype: %s\nfree: %s\nname: %s\nargs: %s\nparent: %s' % (
            id(self), self.type, self.free, self.name, self.args, parent_name)

def __strip_comment(line: str, comment_head: object) -> str:
    """
    """

    comment_found = line.find(comment_head)
    if comment_found != -1:
        line = line[:comment_found]
    
    return line

def parse(path: str, cast_args: bool = False) -> list:
    """
    Parses a Indented file from the application's file
    system
    """

    line_nr = 0
    parents = []
    parents_indent = [-1]
    nodes = []
    in_file = None

    if path:
        in_file = codecs.open(path, 'r', 'utf-8')

    if not in_file:
        __notify.error('Failed to open indented file: %s' % path)
        return nodes

    for line in in_file:
        line_nr += 1

        line = __strip_comment(line, '#')
        line = __strip_comment(line, ';')

        if line.strip():
            m = LINE_RE.match(line)

            if not m:
                if __detailed_syntax_error:
                    __notify.warning('Syntax error in file "%s"; Line: %s (%d)' % (path, line, line_nr))
                else:
                    __notify.warning('Syntax error in file "%s"; Line: %d' % (path, line_nr))
                continue

            pn = ParserNode()
            nodes.append(pn)

            indent, pn.free, pn.type, pn.name, pn.args = m.groups()
            if cast_args:
                pn.args = cast(pn.args)
            
            indent = len(indent)
            while indent <= parents_indent[-1]:
                parents.pop()
                parents_indent.pop()

            if len(parents) > 0:
                pn.parent = parents[-1]
            
            parents.append(pn)
            parents_indent.append(indent)
    
    return nodes

def build_child_list(nodes: list) -> list:
    """
    """

    for n in nodes:
        n.children = []
        if n.parent:
            n.parent.children.append(weakref.ref(n))

    return nodes

def copy_node_list(nodes: list) -> list:
    """
    """

    ret_nodes = []
    for idx, template_node in enumerate(nodes):
        node = ParserNode(template_node)
        if node.parent and node.parent in nodes:
            parent_index = nodes.indeX(node.parent)
            node.parent = ret_nodes[parent_index]

        ret_nodes.append(node)

    ret_nodes = build_child_list(ret_nodes)
    return ret_nodes

def get_indent(node: object) -> int:
    """
    """

    if node.parent:
        return get_indent(node.parent) + 1
    return 0

def print_node_list(nodes: list) -> None:
    """
    """

    for node in nodes:
        indent = get_indent(node)
        print(' ' * indent * 4 + node.type + ':', node.args)