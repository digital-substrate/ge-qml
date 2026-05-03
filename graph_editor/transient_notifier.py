from __future__ import annotations

from PySide6.QtCore import QObject, Signal, QPointF
from PySide6.QtGui import QColor

from ge.data import Graph_VertexKey, Set_Graph_VertexKey


class TransientNotifier(QObject):
    """Notifier for transient (non-persisted) changes.

    Used for live updates during drag operations, color picker changes, etc.
    """

    # Signals
    vertices_moved = Signal(object, QPointF)  # Set_Graph_VertexKey, offset
    vertex_value_changed = Signal(object, int)  # Graph_VertexKey, value
    vertex_color_changed = Signal(object, QColor)  # Graph_VertexKey, color
    vertex_position_changed = Signal(object, QPointF)  # Graph_VertexKey, position

    _instance: TransientNotifier | None = None

    @classmethod
    def instance(cls) -> TransientNotifier:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()

    def notify_vertices_move(self, keys: Set_Graph_VertexKey, offset: QPointF):
        """Notify that vertices are being moved."""
        self.vertices_moved.emit(keys, offset)

    def notify_vertex_value(self, key: Graph_VertexKey, value: int):
        """Notify that a vertex value changed."""
        self.vertex_value_changed.emit(key, value)

    def notify_vertex_color(self, key: Graph_VertexKey, color: QColor):
        """Notify that a vertex color changed."""
        self.vertex_color_changed.emit(key, color)

    def notify_vertex_position(self, key: Graph_VertexKey, position: QPointF):
        """Notify that a vertex position changed."""
        self.vertex_position_changed.emit(key, position)
