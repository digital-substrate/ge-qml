from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtGui import QColor

from ge.data import Graph_VertexKey, Graph_EdgeKey


@dataclass
class ListVertex:
    """Represents a vertex in the list."""
    vertex_key: Graph_VertexKey
    value: int
    color: QColor
    exists: bool

    def label(self) -> str:
        return "?" if self.value == -1 else str(self.value)

    @staticmethod
    def make(vertex_key: Graph_VertexKey, value: int, color: QColor, exists: bool) -> ListVertex:
        return ListVertex(vertex_key, value, color, exists)


@dataclass
class ListEdge:
    """Represents an edge in the list."""
    edge_key: Graph_EdgeKey
    va: ListVertex
    vb: ListVertex

    def label(self) -> str:
        return f"{self.va.value} - {self.vb.value}"

    @staticmethod
    def make(edge_key: Graph_EdgeKey, va: ListVertex, vb: ListVertex) -> ListEdge:
        return ListEdge(edge_key, va, vb)
