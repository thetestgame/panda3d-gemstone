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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.registry import ClassRegistry

class QObjectTreeView(QTreeView):
    """
    """

    def __init__(self, *args, **kwargs):
        super(QTreeView, self).__init__(*args, **kwargs) 

    def build_tree(self, asset_tree: dict) -> None:
        """
        """

        root_model = QStandardItemModel()
        self.setModel(root_model)
        self._populate_tree(asset_tree, root_model.invisibleRootItem())
        root_model.setHeaderData(0, Qt.Horizontal, 'Available Objects')

        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)

    def _populate_tree(self, children: object, parent: object) -> None:
        """
        """

        for child in sorted(children):
            child_item = QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self._populate_tree(children[child], child_item)

class QObjectLibraryWidget(QDockWidget, InternalObject):
    """
    Object library tree for the current Gemstone application. Auto populates
    from the application's class registry
    """

    def __init__(self, *args, **kwargs):
        super(QDockWidget, self).__init__('Object Library', *args, **kwargs)
        super(InternalObject, self).__init__()
        self._registry = ClassRegistry.get_singleton()
        self.build_widget()

    def build_widget(self):
        """
        Builds the layer properties widget
        """

        # Build widget object tree
        object_tree = {}
        for class_name, class_data in self._registry:
            _, import_path, _, meta = class_data
            path_parts = import_path.split('.')
            sub_name = path_parts[1].capitalize()
            root_name = path_parts[0].capitalize()

            editor_object = meta.get('editor_object', False)    
            #if not editor_object:
            #    self.notify.warning(meta)
            #    continue

            if root_name not in object_tree:
                object_tree[root_name] = {}

            if sub_name not in object_tree[root_name]:
                object_tree[root_name][sub_name] = []

            object_tree[root_name][sub_name].append(class_name)

        self.tree = QObjectTreeView(self)
        self.tree.build_tree(object_tree)
        self.setWidget(self.tree)