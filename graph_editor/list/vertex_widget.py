from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QSizePolicy

from .element import ListVertex
from . import paint_helper


class ListVertexWidget(QWidget):
    """Widget for displaying a vertex in a list."""

    def __init__(self, vertex: ListVertex, parent=None):
        super().__init__(parent)
        self.vertex = vertex
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(paint_helper.add_margin(paint_helper.vertex_size(vertex)))

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(paint_helper.vertex_font())
        paint_helper.draw_vertex_at_point(painter, self.vertex, paint_helper.margin_offset())
