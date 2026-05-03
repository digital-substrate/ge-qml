"""Render Model — exposes graph rendering data + mouse interactions to QML.

Replaces QPainter paintEvent with data exposed to QML Canvas.
Replaces QWidget mouse events with @Slot methods called from QML MouseArea.
"""
from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import QObject, QPointF, QRectF, Property, Signal, Slot
from PySide6.QtGui import QColor, QFontMetrics, QGuiApplication

from model.context import Context
from transient_notifier import TransientNotifier
from ge.data import Graph_GraphKey, Graph_VertexKey, Graph_Position
from render.graph import RenderGraph
from render.vertex import RenderVertex
from render import graph_builder
import colors

from model import selection_vertices
from model import selection_edges
from model import selection_mixed
from model import vertex as model_vertex
from model import edge as model_edge
from model import random as model_random
from model import tools


class RenderModel(QObject):

    graphChanged = Signal()
    enabledChanged = Signal()
    inspectKey = Signal("QVariant")  # emits ValueKey for navigate_to_key

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._graph_key: Optional[Graph_GraphKey] = None
        self._render_graph: Optional[RenderGraph] = None
        self._is_drag_canceled = False
        self._canvas_width = 0.0
        self._canvas_height = 0.0

        self._setup_connections(notifier)

    def _setup_connections(self, notifier):
        transient_notifier = TransientNotifier.instance()
        transient_notifier.vertex_value_changed.connect(self._vertex_value_changed)
        transient_notifier.vertex_position_changed.connect(self._vertex_position_changed)
        transient_notifier.vertex_color_changed.connect(self._vertex_color_changed)

        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._on_state_did_change)

    # --- QML Properties ---

    def _get_enabled(self) -> bool:
        return self._render_graph is not None

    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    # --- Canvas size (set from QML) ---

    @Slot(float, float)
    def setCanvasSize(self, width: float, height: float):
        """Called from QML when Canvas size changes."""
        self._canvas_width = width
        self._canvas_height = height
        if self._render_graph:
            self._render_graph._rect = QRectF(0, 0, width, height)
        self.graphChanged.emit()


    def _on_database_did_close(self):
        self._render_graph = None
        self._graph_key = None
        self.enabledChanged.emit()
        self.graphChanged.emit()

    def _on_state_did_change(self):
        if self._context.store.has_database():
            try:
                attachment_getting = self._context.store.attachment_getting()
                graph = graph_builder.build(attachment_getting, self._context.graph_key)
                graph._rect = QRectF(0, 0, self._canvas_width, self._canvas_height)
                self._graph_key = self._context.graph_key
                self._render_graph = graph
            except Exception as e:
                print(f"RenderModel: graph build failed: {e}")
                self._render_graph = None
        else:
            self._render_graph = None

        self.enabledChanged.emit()
        self.graphChanged.emit()

    # --- Drawing data for QML Canvas ---

    @Slot(result=list)
    def getVertices(self) -> list:
        """Return vertex data for QML Canvas drawing."""
        if not self._render_graph:
            return []
        result = []
        # Unselected first, then selected (draw order)
        for vertex in self._render_graph.vertices:
            result.append(self._vertex_data(vertex, False))
        for vertex in self._render_graph.selected_vertices:
            result.append(self._vertex_data(vertex, True))
        return result

    @Slot(result=list)
    def getEdges(self) -> list:
        """Return edge data for QML Canvas drawing."""
        if not self._render_graph:
            return []
        result = []
        # Unselected first, then selected (draw order)
        for edge in self._render_graph.edges:
            result.append(self._edge_data(edge, False))
        for edge in self._render_graph.selected_edges:
            result.append(self._edge_data(edge, True))
        return result

    @Slot(result="QVariant")
    def getConnector(self):
        """Return connector data for QML Canvas drawing."""
        if not self._render_graph or not self._render_graph.connector_vertex_key:
            return None
        vertex = self._render_graph.vertex_map.get(self._render_graph.connector_vertex_key)
        if not vertex:
            return None

        r = self._rect_vertex(vertex)
        size = r.width()
        delta = self._render_graph.interactive_start_location - r.center()
        length = max(math.sqrt(QPointF.dotProduct(delta, delta)), 0.00001)
        scale = (size / 2.0 + RenderGraph.EDGE_MARGIN) / length
        p0 = r.center() + QPointF(delta.x() * scale, delta.y() * scale)
        end = self._render_graph.interactive_start_location

        selected = self._render_graph.connector_vertex_key in self._render_graph.selected_vertex_keys
        return {
            "x0": p0.x(), "y0": p0.y(),
            "x1": end.x(), "y1": end.y(),
            "vertex": self._vertex_data(vertex, selected),
        }

    @Slot(result=str)
    def backgroundColor(self) -> str:
        """Background color as hex string."""
        return colors.background().name()

    def _vertex_data(self, vertex: RenderVertex, selected: bool) -> dict:
        """Build vertex dict for QML Canvas."""
        r = self._rect_vertex(vertex)
        if selected:
            border_color = colors.yellow()
        elif vertex.is_valid:
            border_color = colors.label()
        else:
            border_color = colors.secondary_label()

        return {
            "x": r.x(), "y": r.y(), "size": r.width(),
            "label": vertex.label(),
            "fillColor": vertex.color.name() if vertex.is_valid else "",
            "borderColor": border_color.name(),
            "isValid": vertex.is_valid,
            "selected": selected,
        }

    def _edge_data(self, edge, selected: bool) -> dict:
        """Build edge dict for QML Canvas."""
        is_valid = edge.is_valid()
        if selected:
            color = colors.yellow()
        elif is_valid:
            color = colors.label()
        else:
            color = colors.secondary_label()

        rect_0 = self._rect_vertex(edge.va)
        rect_1 = self._rect_vertex(edge.vb)
        location_0 = rect_0.center()
        location_1 = rect_1.center()
        delta = location_1 - location_0
        length = max(math.sqrt(QPointF.dotProduct(delta, delta)), 0.00001)

        scale_0 = (rect_0.width() / 2.0 + RenderGraph.EDGE_MARGIN) / length
        scale_1 = (rect_1.width() / 2.0 + RenderGraph.EDGE_MARGIN) / length
        p_0 = location_0 + QPointF(delta.x() * scale_0, delta.y() * scale_0)
        p_1 = location_1 - QPointF(delta.x() * scale_1, delta.y() * scale_1)

        return {
            "x0": p_0.x(), "y0": p_0.y(),
            "x1": p_1.x(), "y1": p_1.y(),
            "color": color.name(),
            "isValid": is_valid,
            "lineWidth": 1.5,
        }

    def _rect_vertex(self, vertex: RenderVertex) -> QRectF:
        location = QPointF(vertex.position.x(), self._canvas_height - vertex.position.y())

        if (self._render_graph and
                vertex.vertex_key in self._render_graph.interactive_vertex_keys):
            location = location + self._render_graph.interactive_drag_offset

        label = vertex.label()
        fm = QFontMetrics(QGuiApplication.font())
        size = fm.size(0, label)
        max_size = max(size.width(), size.height()) + 10
        return QRectF(location.x() - max_size / 2.0, location.y() - max_size / 2.0,
                       max_size, max_size)

    # --- Mouse interactions

    @Slot(float, float, int)
    def mousePress(self, x: float, y: float, modifiers: int):
        if not self._context.store.has_database():
            return
        if not self._render_graph:
            return

        attachment_getting = self._context.store.attachment_getting()
        is_shift = bool(modifiers & 0x02000000)    # Qt.ShiftModifier
        is_control = bool(modifiers & 0x04000000)   # Qt.ControlModifier
        is_alt = bool(modifiers & 0x08000000)        # Qt.AltModifier

        self._is_drag_canceled = False
        location = QPointF(x, y)

        # Pick vertex
        vertex = self._render_graph.pick_vertex(location)
        if vertex:
            if is_control:
                return
            elif is_shift:
                if not self._render_graph.is_selected_vertex(vertex):
                    graph_key = self._graph_key
                    vk = vertex.vertex_key
                    self._context.store.dispatch(
                        f"Add Vertex '{vertex.label()}' To Selection",
                        lambda m: selection_vertices.combine(m, graph_key, vk, True))
                return
            elif is_alt:
                if self._render_graph.is_selected_vertex(vertex):
                    graph_key = self._graph_key
                    vk = vertex.vertex_key
                    self._context.store.dispatch(
                        f"Remove Vertex '{vertex.label()}' From Selection",
                        lambda m: selection_vertices.combine(m, graph_key, vk, False))
                return
            else:
                if not (len(self._render_graph.selected_vertex_keys) == 1 and
                        self._render_graph.is_selected_vertex(vertex) and
                        not self._render_graph.has_selected_edges()):
                    graph_key = self._graph_key
                    vk = vertex.vertex_key
                    self._context.store.dispatch(
                        f"Set Vertex Selection To '{vertex.label()}'",
                        lambda m: selection_vertices.select(m, graph_key, vk))
                return

        # Pick edge
        edge = self._render_graph.pick_edge(
            QRectF(0, 0, self._canvas_width, self._canvas_height), location)
        if edge:
            edge_label = tools.safe_edge_label(attachment_getting, edge.edge_key)
            if is_control:
                return
            elif is_shift:
                if not self._render_graph.is_selected_edge(edge):
                    graph_key = self._graph_key
                    ek = edge.edge_key
                    self._context.store.dispatch(
                        f"Add Edge '{edge_label}' To Selection",
                        lambda m: selection_edges.combine(m, graph_key, ek, True))
                return
            elif is_alt:
                if self._render_graph.is_selected_edge(edge):
                    graph_key = self._graph_key
                    ek = edge.edge_key
                    self._context.store.dispatch(
                        f"Remove Edge '{edge_label}' From Selection",
                        lambda m: selection_edges.combine(m, graph_key, ek, False))
                return
            else:
                if not (len(self._render_graph.selected_edge_keys) == 1 and
                        self._render_graph.is_selected_edge(edge) and
                        not self._render_graph.has_selected_vertices()):
                    graph_key = self._graph_key
                    ek = edge.edge_key
                    self._context.store.dispatch(
                        f"Set Selection To Edge '{edge_label}'",
                        lambda m: selection_edges.select(m, graph_key, ek))
                return

        # Ctrl+click on empty → new vertex
        if is_control:
            value = tools.next_vertex_value(attachment_getting, self._render_graph.graph_key)
            label = f"New Vertex '{value}'"
            position = Graph_Position()
            position.x = x
            position.y = self._canvas_height - y
            color = model_random.make_color()
            graph_key = self._graph_key
            self._context.store.dispatch(
                label,
                lambda m: model_vertex.add(m, graph_key, value, position, color))
            return

        if is_shift:
            return

        # Click on empty → deselect all
        if self._render_graph.has_selected_edges() or self._render_graph.has_selected_vertices():
            graph_key = self._graph_key
            self._context.store.dispatch(
                "Deselect All",
                lambda m: selection_mixed.deselect_all(m, graph_key))

    @Slot(float, float, int)
    def mouseMove(self, x: float, y: float, modifiers: int):
        if not self._render_graph:
            return
        if self._is_drag_canceled:
            return

        location = QPointF(x, y)
        is_control = bool(modifiers & 0x04000000)
        is_alt = bool(modifiers & 0x08000000)

        if is_control or self._render_graph.connector_vertex_key:
            # Connector drag
            if not self._render_graph.connector_vertex_key:
                self._render_graph.pick_connector_vertex(location)
            if self._render_graph.connector_vertex_key:
                self._render_graph.interactive_start_location = location
                self.graphChanged.emit()
        elif self._render_graph.has_selection():
            if not self._render_graph.has_vertex_to_move():
                if is_alt:
                    self._render_graph.move_copy_start(location)
                else:
                    self._render_graph.move_start(location)

            self._render_graph.move_drag(location)
            TransientNotifier.instance().notify_vertices_move(
                self._render_graph.interactive_vertex_keys,
                self._render_graph.interactive_drag_offset)
            self.graphChanged.emit()

    @Slot(float, float)
    def mouseRelease(self, x: float, y: float):
        if not self._render_graph:
            return
        if self._is_drag_canceled:
            return

        attachment_getting = self._context.store.attachment_getting()

        connector_vertex_key = self._render_graph.connector_vertex_key
        picked_vertex = self._render_graph.pick_vertex(QPointF(x, y))

        # Connect edge
        if connector_vertex_key and picked_vertex and picked_vertex.vertex_key != connector_vertex_key:
            if not self._render_graph.has_edge(picked_vertex.vertex_key, connector_vertex_key):
                edge_label = tools.safe_edge_label_from_vertices(
                    attachment_getting, picked_vertex.vertex_key, connector_vertex_key)
                graph_key = self._graph_key
                pvk = picked_vertex.vertex_key
                cvk = connector_vertex_key
                self._context.store.dispatch(
                    f"New Edge '{edge_label}'",
                    lambda m: model_edge.add(m, graph_key, pvk, cvk))

        # Move / move-copy
        if self._render_graph.interactive_vertex_keys:
            dx = int(self._render_graph.interactive_drag_offset.x())
            dy = int(self._render_graph.interactive_drag_offset.y())
            length = math.sqrt(dx * dx + dy * dy)
            offset = Graph_Position()
            offset.x = dx
            offset.y = -dy
            s_offset = f" By ({dx},{dy})"

            if self._render_graph.move_copy_data:
                if length > 30:
                    from model import script_move_copy
                    move_copy_data = self._render_graph.move_copy_data
                    graph_key = self._graph_key
                    self._context.store.dispatch(
                        f"Move/Copy Selection{s_offset}",
                        lambda m: script_move_copy.run(m, graph_key, move_copy_data, offset))
            else:
                from model import graph_vertices
                vertex_keys = self._render_graph.interactive_vertex_keys
                self._context.store.dispatch(
                    f"Move Selection{s_offset}",
                    lambda m: graph_vertices.move(m, vertex_keys, offset))

        self._render_graph.move_end()
        self.graphChanged.emit()

    # --- Picking for menu actions (inspect element) ---

    @Slot(float, float, result="QVariant")
    def pickVertexKey(self, x: float, y: float):
        """Pick vertex at location — for inspect element."""
        if self._render_graph:
            vertex = self._render_graph.pick_vertex(QPointF(x, y))
            if vertex:
                return vertex.vertex_key
        return None

    @Slot(float, float, result="QVariant")
    def pickEdgeKey(self, x: float, y: float):
        """Pick edge at location — for inspect element."""
        if self._render_graph:
            edge = self._render_graph.pick_edge(
                QRectF(0, 0, self._canvas_width, self._canvas_height), QPointF(x, y))
            if edge:
                return edge.edge_key
        return None

    @Slot(float, float, result=bool)
    def inspectElement(self, x: float, y: float) -> bool:
        """Pick vertex/edge/graph at location and emit inspectKey.

        Returns True if an element was found.
        """
        if not self._render_graph:
            return False

        location = QPointF(x, y)

        # Try vertex first
        vertex = self._render_graph.pick_vertex(location)
        if vertex:
            self.inspectKey.emit(vertex.vertex_key.vpr_value)
            return True

        # Then edge
        edge = self._render_graph.pick_edge(
            QRectF(0, 0, self._canvas_width, self._canvas_height), location)
        if edge:
            self.inspectKey.emit(edge.edge_key.vpr_value)
            return True

        # Then graph
        if self._graph_key:
            self.inspectKey.emit(self._graph_key.vpr_value)
            return True

        return False

    # --- Transient notifications

    def _vertex_value_changed(self, key: Graph_VertexKey, value: int):
        if self._render_graph:
            vertex = self._render_graph.vertex_map.get(key)
            if vertex:
                vertex.value = value
                self.graphChanged.emit()

    def _vertex_color_changed(self, key: Graph_VertexKey, color: QColor):
        if self._render_graph:
            vertex = self._render_graph.vertex_map.get(key)
            if vertex:
                vertex.color = color
                self.graphChanged.emit()

    def _vertex_position_changed(self, key: Graph_VertexKey, position: QPointF):
        if self._render_graph:
            vertex = self._render_graph.vertex_map.get(key)
            if vertex:
                vertex.position = position
                self.graphChanged.emit()
