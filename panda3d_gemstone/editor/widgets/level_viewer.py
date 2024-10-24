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
from panda3d_gemstone.editor.level import EditorWorldManager, EditorScene

class QLevelTreeView(QTreeView):
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
        root_model.setHeaderData(0, Qt.Horizontal, 'Level Browser')

        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)

    def _populate_tree(self, children: object, parent: object) -> None:
        """
        """

        if isinstance(children, str):
            parent.appendRow(QStandardItem(children))
            return

        for child in sorted(children):
            child_item = QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self._populate_tree(children[child], child_item)

class QLevelViewerWidget(QDockWidget, InternalObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super(QDockWidget, self).__init__('Level Tree', *args, **kwargs)
        super(InternalObject, self).__init__()
        self._editor_scene = EditorScene.get_singleton()
        self._editor_world = EditorWorldManager.get_singleton()
        self.build_widget()

    def build_widget(self):
        """
        Builds the layer properties widget
        """

        # Build widget level tree
        level_tree = {
            'Scene': {},
            'Levels': {}
        }

        scene_objects = self._editor_scene.get_objects()
        for scene_object in scene_objects:
            name_parts = str(scene_object).split('/')
            object_name = name_parts[-1]

            tree_name = '%s (%s)' % (object_name, scene_object.__class__.__name__)
            level_tree['Scene'] = tree_name

        worlds = self._editor_world.worlds
        for world_key in worlds:
            world = worlds[world_key]
            if world_key not in level_tree['Levels']:
                level_tree['Levels'][world_key] = []
            
            for layer in world.get_layers():
                for entity in layer.get_entities():
                    tree_name = '%s (%s) (%s)' % (
                        entity.name, 
                        entity.__class__.__name__,
                        entity.get_layer().get_id())
                    
                    level_tree['Levels'][world_key].append(tree_name)
        
        self.tree = QLevelTreeView(self)
        self.tree.build_tree(level_tree)
        self.setWidget(self.tree)