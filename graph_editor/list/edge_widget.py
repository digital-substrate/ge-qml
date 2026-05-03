from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QSizePolicy

from .element import ListEdge
from . import paint_helper


class ListEdgeWidget(QWidget):
    """Widget for displaying an edge in a list."""

    def __init__(self, edge: ListEdge, parent=None):
        super().__init__(parent)
        self.edge = edge
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(paint_helper.add_margin(
            QSize(20, int(paint_helper.edge_height(edge, 8)))
        ))

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(paint_helper.vertex_font())
        paint_helper.draw_edge_in_rect(painter, self.edge, paint_helper.adjust_margin(self.rect()))
