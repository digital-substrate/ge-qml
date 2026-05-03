"""Vertex Model — exposes selected vertex properties to QML.

Exposes value, color, position for the single selected vertex.
Handles transient notifications for live preview.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QPointF, Property, Signal, Slot
from PySide6.QtGui import QColor

from transient_notifier import TransientNotifier
from model.context import Context
from ge import attachments
from ge.data import Graph_VertexKey, Graph_Color, Graph_Position


class VertexModel(QObject):
    """Exposes vertex value/color/position to QML when exactly 1 vertex is selected."""

    valueChanged = Signal()
    colorChanged = Signal()
    positionChanged = Signal()
    hasVertexChanged = Signal()
    enabledChanged = Signal()

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._vertex_key: Graph_VertexKey | None = None
        self._value: int = 0
        self._color: QColor = QColor(255, 255, 255)
        self._location: QPointF = QPointF()
        self._drag_origin: QPointF | None = None  # position at drag start
        self._has_vertex = False
        self._enabled = False

        notifier.database_did_open.connect(self._on_database_did_open)
        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._configure)

        transient_notifier = TransientNotifier.instance()
        transient_notifier.vertices_moved.connect(self._vertices_moved)

    # --- QML Properties ---

    def _get_value(self) -> int:
        return self._value

    value = Property(int, _get_value, notify=valueChanged)

    def _get_color(self) -> QColor:
        return self._color

    color = Property(QColor, _get_color, notify=colorChanged)

    def _get_position_x(self) -> int:
        return int(self._location.x())

    positionX = Property(int, _get_position_x, notify=positionChanged)

    def _get_position_y(self) -> int:
        return int(self._location.y())

    positionY = Property(int, _get_position_y, notify=positionChanged)

    def _get_has_vertex(self) -> bool:
        return self._has_vertex

    hasVertex = Property(bool, _get_has_vertex, notify=hasVertexChanged)

    def _get_enabled(self) -> bool:
        return self._enabled

    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    # --- Value Slots ---

    @Slot(int)
    def setValue(self, new_value: int):
        if not self._vertex_key:
            return
        label = f"Set Value '{new_value}' For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_visual_attributes_set_value(
                m, self._vertex_key, new_value))

    @Slot(int)
    def previewValue(self, new_value: int):
        """Transient value preview — illusion pattern for stepper hold."""
        if not self._vertex_key:
            return
        TransientNotifier.instance().notify_vertex_value(self._vertex_key, new_value)

    # --- Color Slots ---

    @Slot(QColor)
    def setColor(self, new_color: QColor):
        if not self._vertex_key:
            return
        color = Graph_Color()
        color.red = new_color.redF()
        color.green = new_color.greenF()
        color.blue = new_color.blueF()
        label = f"Set Color For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_visual_attributes_set_color(
                m, self._vertex_key, color))

    @Slot(QColor)
    def previewColor(self, color: QColor):
        """Transient color preview"""
        if not self._vertex_key:
            return
        TransientNotifier.instance().notify_vertex_color(self._vertex_key, color)

    @Slot()
    def cancelColor(self):
        """Restore original color"""
        if not self._vertex_key:
            return
        TransientNotifier.instance().notify_vertex_color(self._vertex_key, self._color)

    # --- Position Slots ---

    @Slot(int)
    def setPositionX(self, x: int):
        if not self._vertex_key:
            return
        self._location = QPointF(x, self._location.y())
        position = Graph_Position()
        position.x = int(self._location.x())
        position.y = int(self._location.y())
        label = f"Set Position.X To {x} For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_render_2d_attributes_set_position(
                m, self._vertex_key, position))

    @Slot(int)
    def setPositionY(self, y: int):
        if not self._vertex_key:
            return
        self._location = QPointF(self._location.x(), y)
        position = Graph_Position()
        position.x = int(self._location.x())
        position.y = int(self._location.y())
        label = f"Set Position.Y To {y} For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_render_2d_attributes_set_position(
                m, self._vertex_key, position))

    @Slot(int)
    def previewPositionX(self, x: int):
        """Transient X preview"""
        if not self._vertex_key:
            return
        TransientNotifier.instance().notify_vertex_position(
            self._vertex_key, QPointF(x, self._location.y()))

    @Slot(int)
    def previewPositionY(self, y: int):
        """Transient Y preview"""
        if not self._vertex_key:
            return
        TransientNotifier.instance().notify_vertex_position(
            self._vertex_key, QPointF(self._location.x(), y))

    # --- Transient Notifier ---

    def _vertices_moved(self, keys, offset: QPointF):
        """offset is cumulative from drag start (not incremental), so we compute
        position from the saved drag origin rather than accumulating on _location.
        """
        if not self._vertex_key or self._vertex_key not in keys:
            return
        if self._drag_origin is None:
            self._drag_origin = QPointF(self._location)
        p = QPointF(self._drag_origin.x() + offset.x(), self._drag_origin.y() - offset.y())
        self._location = p
        self.positionChanged.emit()

    # --- Notifier Slots ---

    def _on_database_did_open(self):
        self._enabled = True
        self.enabledChanged.emit()

    def _on_database_did_close(self):
        self._vertex_key = None
        self._value = 0
        self._color = QColor(255, 255, 255)
        self._location = QPointF()
        self._has_vertex = False
        self.valueChanged.emit()
        self.colorChanged.emit()
        self.positionChanged.emit()
        self.hasVertexChanged.emit()
        self._enabled = False
        self.enabledChanged.emit()

    def _configure(self):
        self._drag_origin = None  # reset drag state after commit
        try:
            attachment_getting = self._context.store.attachment_getting()
            graph_key = self._context.graph_key

            vertex_keys = set()
            opt_selection = attachments.graph_graph_selection_get(attachment_getting, graph_key)
            if opt_selection:
                selection = opt_selection.unwrap()
                vertex_keys = set(selection.vertex_keys)

            if len(vertex_keys) == 1:
                self._vertex_key = next(iter(vertex_keys))
                self._configure_vertex(attachment_getting)
                if not self._has_vertex:
                    self._has_vertex = True
                    self.hasVertexChanged.emit()
            else:
                self._vertex_key = None
                if self._has_vertex:
                    self._has_vertex = False
                    self._value = 0
                    self._color = QColor(255, 255, 255)
                    self._location = QPointF()
                    self.valueChanged.emit()
                    self.colorChanged.emit()
                    self.positionChanged.emit()
                    self.hasVertexChanged.emit()

        except Exception as e:
            print(f"VertexModel._configure error: {e}")

    def _configure_vertex(self, attachment_getting):
        old_value = self._value
        old_color = QColor(self._color)
        old_location = QPointF(self._location)

        self._value = 0
        self._color = QColor(255, 255, 255)
        opt_visual = attachments.graph_vertex_visual_attributes_get(
            attachment_getting, self._vertex_key)
        if opt_visual:
            visual = opt_visual.unwrap()
            self._value = visual.value
            self._color = QColor(
                int(visual.color.red * 255),
                int(visual.color.green * 255),
                int(visual.color.blue * 255))

        self._location = QPointF()
        opt_render = attachments.graph_vertex_render_2d_attributes_get(
            attachment_getting, self._vertex_key)
        if opt_render:
            render = opt_render.unwrap()
            self._location = QPointF(render.position.x, render.position.y)

        if self._value != old_value:
            self.valueChanged.emit()
        if self._color != old_color:
            self.colorChanged.emit()
        if self._location != old_location:
            self.positionChanged.emit()
