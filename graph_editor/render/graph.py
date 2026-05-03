from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QPainterPath, QColor, QFontMetrics, QImage, qRed, qGreen, qBlue
from PySide6.QtWidgets import QApplication

from ge.data import Graph_GraphKey, Graph_VertexKey, Graph_EdgeKey
from .vertex import RenderVertex
from .edge import RenderEdge


@dataclass
class MoveCopyData:
    """Data for move/copy operations."""
    vertices: dict[Graph_VertexKey, RenderVertex] = field(default_factory=dict)
    edges: dict[Graph_EdgeKey, RenderEdge] = field(default_factory=dict)


class RenderGraph:
    """Graph structure for rendering."""

    EDGE_MARGIN = 3.0

    def __init__(self, graph_key: Graph_GraphKey):
        self.graph_key = graph_key

        self.vertex_map: dict[Graph_VertexKey, RenderVertex] = {}
        self.edge_map: dict[Graph_EdgeKey, RenderEdge] = {}
        self.is_valid = True

        self.vertex_keys: set[Graph_VertexKey] = set()
        self.edge_keys: set[Graph_EdgeKey] = set()
        self.selected_vertex_keys: set[Graph_VertexKey] = set()
        self.selected_edge_keys: set[Graph_EdgeKey] = set()

        self.vertices: list[RenderVertex] = []
        self.edges: list[RenderEdge] = []
        self.selected_vertices: list[RenderVertex] = []
        self.selected_edges: list[RenderEdge] = []

        self.connector_vertex_key: Optional[Graph_VertexKey] = None
        self.move_copy_data: Optional[MoveCopyData] = None

        self.interactive_start_location = QPointF()
        self.interactive_drag_offset = QPointF()
        self.interactive_vertex_keys: set[Graph_VertexKey] = set()

        self._rect = QRectF()

    @staticmethod
    def make(graph_key: Graph_GraphKey) -> RenderGraph:
        return RenderGraph(graph_key)

    def has_selection(self) -> bool:
        return len(self.selected_vertex_keys) > 0 or len(self.selected_edge_keys) > 0

    def has_edge(self, va_key: Graph_VertexKey, vb_key: Graph_VertexKey) -> bool:
        for edge in self.edge_map.values():
            if ((edge.va.vertex_key == va_key and edge.vb.vertex_key == vb_key) or
                (edge.va.vertex_key == vb_key and edge.vb.vertex_key == va_key)):
                return True
        return False

    def prepare(self):
        self.vertex_keys = self.vertex_keys - self.selected_vertex_keys
        self.edge_keys = self.edge_keys - self.selected_edge_keys
        self.update_rendered_elements()

    # MARK: - Picking

    def pick_connector_vertex(self, location: QPointF):
        vertex = self.pick_vertex(location)
        if vertex:
            self.connector_vertex_key = vertex.vertex_key
        else:
            self.connector_vertex_key = None

    def pick_vertex(self, location: QPointF) -> Optional[RenderVertex]:
        for vertex in self.vertex_map.values():
            if self.rect_vertex(vertex).contains(location):
                return vertex
        return None

    def pick_edge(self, rect: QRectF, location: QPointF) -> Optional[RenderEdge]:
        width = int(rect.width())
        height = int(rect.height())

        image = QImage(width, height, QImage.Format.Format_RGB32)
        painter = QPainter()
        painter.begin(image)

        indices: dict[int, RenderEdge] = {}
        color_key = 1
        for edge in self.edge_map.values():
            r = (color_key >> 0) % 256
            g = (color_key >> 8) % 256
            b = (color_key >> 16) % 256

            # Draw with unique color for picking
            self._draw_edge_for_picking(painter, edge, r, g, b, 7.0)
            indices[color_key] = edge
            color_key += 1

        painter.end()

        q_rgb = image.pixel(int(location.x()), int(location.y()))
        lookup_key = qRed(q_rgb) | (qGreen(q_rgb) << 8) | (qBlue(q_rgb) << 16)
        if lookup_key == 0:
            return None

        return indices.get(lookup_key)

    def _draw_edge_for_picking(self, painter: QPainter, edge: RenderEdge, r: int, g: int, b: int, line_width: float):
        rect_0 = self.rect_vertex(edge.va)
        rect_1 = self.rect_vertex(edge.vb)
        location_0 = rect_0.center()
        location_1 = rect_1.center()
        delta = location_1 - location_0
        length = max(math.sqrt(QPointF.dotProduct(delta, delta)), 0.00001)

        scale_0 = (rect_0.width() / 2.0 + self.EDGE_MARGIN) / length
        scale_1 = (rect_1.width() / 2.0 + self.EDGE_MARGIN) / length
        p_0 = location_0 + QPointF(delta.x() * scale_0, delta.y() * scale_0)
        p_1 = location_1 - QPointF(delta.x() * scale_1, delta.y() * scale_1)

        pen = QPen(QColor(r, g, b))
        pen.setWidthF(line_width)

        path = QPainterPath()
        path.moveTo(p_0)
        path.lineTo(p_1)

        painter.setPen(pen)
        painter.drawPath(path)

    # MARK: - Move

    def has_vertex_to_move(self) -> bool:
        return len(self.interactive_vertex_keys) > 0

    def move_start(self, location: QPointF):
        self.move_collect_vertices()
        self.interactive_start_location = location
        self.interactive_drag_offset = QPointF()

    def move_copy_start(self, location: QPointF):
        self.move_copy_collect_vertices()
        self.interactive_start_location = location
        self.interactive_drag_offset = QPointF()
        self.update_rendered_elements()
        self.update_rendered_edges()

    def move_copy_collect_vertices(self):
        from model.context import Context
        from ge import attachments
        from model import tools

        context = Context.instance()
        if not context or not context.store.has_database():
            return

        attachment_getting = context.store.attachment_getting()

        self.interactive_vertex_keys.clear()

        value = tools.next_vertex_value(attachment_getting, self.graph_key)
        vertex_map: dict[Graph_VertexKey, Graph_VertexKey] = {}
        data = MoveCopyData()

        candidate_vertex_keys = set(self.selected_vertex_keys)
        for edge_key in self.selected_edge_keys:
            edge = self.edge_map.get(edge_key)
            if edge:
                if not self.is_selected_vertex(edge.va) and not self.is_selected_vertex(edge.vb):
                    candidate_vertex_keys.add(edge.va.vertex_key)
                    candidate_vertex_keys.add(edge.vb.vertex_key)

        for vertex_key in candidate_vertex_keys:
            vertex = self.vertex_map.get(vertex_key)
            if vertex:
                new_vertex_key = Graph_VertexKey.create()
                new_render_vertex = RenderVertex.make(new_vertex_key, value, vertex.position, vertex.color, True)
                vertex_map[vertex_key] = new_vertex_key
                self.vertex_map[new_vertex_key] = new_render_vertex
                self.vertex_keys.add(new_vertex_key)
                data.vertices[new_vertex_key] = new_render_vertex
                self.interactive_vertex_keys.add(new_vertex_key)
                value += 1

        candidate_edge_keys: set[Graph_EdgeKey] = set()
        for edge_key, render_edge in self.edge_map.items():
            if edge_key in self.selected_edge_keys:
                if (render_edge.va.vertex_key in candidate_vertex_keys or
                    render_edge.vb.vertex_key in candidate_vertex_keys):
                    candidate_edge_keys.add(edge_key)

        for edge_key in candidate_edge_keys:
            edge = self.edge_map.get(edge_key)
            if edge:
                va_key = vertex_map.get(edge.va.vertex_key, edge.va.vertex_key)
                vb_key = vertex_map.get(edge.vb.vertex_key, edge.vb.vertex_key)

                new_edge_key = Graph_EdgeKey.create()
                render_edge = RenderEdge.make(new_edge_key, self.vertex_map[va_key], self.vertex_map[vb_key])
                self.edge_map[new_edge_key] = render_edge
                self.edge_keys.add(new_edge_key)
                data.edges[new_edge_key] = render_edge

        self.move_copy_data = data

    def move_drag(self, location: QPointF):
        self.interactive_drag_offset = location - self.interactive_start_location

    def move_end(self):
        self.connector_vertex_key = None
        self.move_copy_data = None
        self.interactive_drag_offset = QPointF()
        self.interactive_vertex_keys.clear()

    def move_collect_vertices(self):
        self.interactive_vertex_keys = set(self.selected_vertex_keys)

        for edge_key in self.selected_edge_keys:
            edge = self.edge_map.get(edge_key)
            if edge:
                self.interactive_vertex_keys.add(edge.va.vertex_key)
                self.interactive_vertex_keys.add(edge.vb.vertex_key)

    # MARK: - Tools

    def rect_vertex(self, vertex: RenderVertex) -> QRectF:
        location = QPointF(vertex.position.x(), self._rect.height() - vertex.position.y())

        if vertex.vertex_key in self.interactive_vertex_keys:
            location = location + self.interactive_drag_offset

        label = vertex.label()
        fm = QFontMetrics(QApplication.font())
        size = fm.size(Qt.TextFlag.TextSingleLine, label)
        max_size = max(size.width(), size.height()) + 10
        return QRectF(location.x() - max_size / 2.0, location.y() - max_size / 2.0, max_size, max_size)

    def has_selected_vertices(self) -> bool:
        return len(self.selected_vertex_keys) > 0

    def is_selected_vertex(self, vertex: RenderVertex) -> bool:
        return vertex.vertex_key in self.selected_vertex_keys

    def has_selected_edges(self) -> bool:
        return len(self.selected_edge_keys) > 0

    def is_selected_edge(self, edge: RenderEdge) -> bool:
        return edge.edge_key in self.selected_edge_keys

    def update_rendered_elements(self):
        self.update_rendered_vertices()
        self.update_rendered_selected_vertices()
        self.update_rendered_edges()
        self.update_rendered_selected_edges()

    def update_rendered_vertices(self):
        self.vertices = []
        for vertex_key in self.vertex_keys:
            vertex = self.vertex_map.get(vertex_key)
            if vertex:
                self.vertices.append(vertex)
        self.vertices.sort()

    def update_rendered_selected_vertices(self):
        self.selected_vertices = []
        for vertex_key in self.selected_vertex_keys:
            vertex = self.vertex_map.get(vertex_key)
            if vertex:
                self.selected_vertices.append(vertex)
        self.selected_vertices.sort()

    def update_rendered_edges(self):
        self.edges = []
        for edge_key in self.edge_keys:
            edge = self.edge_map.get(edge_key)
            if edge:
                self.edges.append(edge)
        self.edges.sort()

    def update_rendered_selected_edges(self):
        self.selected_edges = []
        for edge_key in self.selected_edge_keys:
            edge = self.edge_map.get(edge_key)
            if edge:
                self.selected_edges.append(edge)
        self.selected_edges.sort()
