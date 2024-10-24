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

from panda3d.core import *
from panda3d_gemstone.editor.gizmos import gizmo

class GizmoGrid(gizmo.EditorGizmo):
    """
    """

    def __init__(self, name: str, grid_size: int = 500, grid_step: int = 100, subdiv: int = 5):
        super(gizmo.EditorGizmo, self).__init__(name)
        self.axis_lines = LineSegs()
        self.grid_lines = LineSegs()
        self.subdiv_lines = LineSegs()
        self.grid_size=grid_size
        self.grid_step = grid_step
        self.subdiv = subdiv
        self.x_axis_color = VBase4(1, 0, 0, 1)
        self.y_axis_color = VBase4(0, 1, 0, 1)
        self.z_xxis_color = VBase4(0, 0, 1, 1)
        self.grid_color = VBase4(1, 1, 1, 1)
        self.subdiv_color = VBase4(.35, .35, .35, 1)
        self.axis_thickness = 3
        self.grid_thickness = 1
        self.subdiv_thickness = 1

    def draw_gizmo(self) -> None:
        """
        Draws the Gizmo object and creates the required nodes
        """

        gizmo.EditorGizmo.draw_gizmo(self)
        if self.grid_step != 0:
            self.grid_lines.set_color(self.grid_color)

            for x in self.__myfrange(0, self.grid_size, self.grid_step):
                self.grid_lines.move_to(x, -(self.grid_size), 0)
                self.grid_lines.draw_to(x, self.grid_size, 0)
                self.grid_lines.move_to(-x, -(self.grid_size), 0)
                self.grid_lines.draw_to(-x, self.grid_size, 0)

                # Draw endcap lines
                self.grid_lines.move_to(self.grid_size, -(self.grid_size), 0)
                self.grid_lines.draw_to(self.grid_size, self.grid_size, 0)
                self.grid_lines.move_to(-(self.grid_size), -(self.grid_size), 0)
                self.grid_lines.draw_to(-(self.grid_size), self.grid_size, 0)

            for y in self.__myfrange(0, self.grid_size, self.grid_step):
                self.grid_lines.move_to(-(self.grid_size), y, 0)
                self.grid_lines.draw_to(self.grid_size, y, 0)
                self.grid_lines.move_to(-(self.grid_size), -y, 0)
                self.grid_lines.draw_to(self.grid_size, -y, 0)

                # Draw endcap lines
                self.grid_lines.move_to(-(self.grid_size), self.grid_size, 0)
                self.grid_lines.draw_to(self.grid_size, self.grid_size, 0)
                self.grid_lines.move_to(-(self.grid_size), -(self.grid_size), 0)
                self.grid_lines.draw_to(self.grid_size, -(self.grid_size), 0)

        if self.subdiv != 0:
            self.subdiv_lines.set_color(self.subdiv_color)
            adjustedstep = self.grid_step / self.subdiv

            for x in self.__myfrange(0, self.grid_size, adjustedstep):
                self.subdiv_lines.move_to(x, -(self.grid_size), 0)
                self.subdiv_lines.draw_to(x, self.grid_size, 0)
                self.subdiv_lines.move_to(-x, -(self.grid_size), 0)
                self.subdiv_lines.draw_to(-x, self.grid_size, 0)

            for y in self.__myfrange(0, self.grid_size, adjustedstep):
                self.subdiv_lines.move_to(-(self.grid_size), y, 0)
                self.subdiv_lines.draw_to(self.grid_size, y, 0)
                self.subdiv_lines.move_to(-(self.grid_size), -y, 0)
                self.subdiv_lines.draw_to(self.grid_size, -y, 0)

        # Create axis lines node and path, then reparent
        self.axis_lines_node = self.axis_lines.create()
        self.axis_lines_node_path = NodePath(self.axis_lines_node)
        self.axis_lines_node_path.reparentTo(self)

        # Create grid lines node and path, then reparent
        self.grid_lines_node = self.grid_lines.create()
        self.grid_lines_node_path = NodePath(self.grid_lines_node)
        self.grid_lines_node_path.reparentTo(self)

        # Create subdivision lines node and path then reparent
        self.subdiv_lines_node = self.subdiv_lines.create()
        self.subdiv_lines_node_path = NodePath(self.subdiv_lines_node)
        self.subdiv_lines_node_path.reparentTo(self)

    def __myfrange(self, start: float, stop: float = None, step: float = None) -> object:
        """
        """

        if stop is None:
            stop = float(start)
            start = 0.0

        if step is None:
            step = 1.0

        cur = float(start)
        while cur < stop:
            yield cur
            cur += step
