from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor

from ge.data import Graph_VertexKey


@dataclass
class RenderVertex:
    """A vertex for rendering."""
    vertex_key: Graph_VertexKey
    value: int
    position: QPointF
    color: QColor
    is_valid: bool

    def label(self) -> str:
        return "?" if self.value == -1 else str(self.value)

    @staticmethod
    def make(vertex_key: Graph_VertexKey, value: int, position: QPointF,
             color: QColor, is_valid: bool) -> RenderVertex:
        return RenderVertex(vertex_key, value, position, color, is_valid)

    def __lt__(self, other: RenderVertex) -> bool:
        return str(self.vertex_key.instance_id()) < str(other.vertex_key.instance_id())
