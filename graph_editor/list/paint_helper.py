from __future__ import annotations

import math

from PySide6.QtCore import Qt, QPoint, QSize, QRect
from PySide6.QtGui import QColor, QPainter, QFont, QFontMetrics, QPen, QPainterPath, QGuiApplication
from PySide6.QtWidgets import QApplication

import colors
from .element import ListVertex, ListEdge

MARGIN = 4


def edge_color() -> QColor:
    """Get the edge color based on the current color scheme."""
    dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    return colors.label() if dark else QColor.fromRgbF(0.6, 0.6, 0.6)


def margin_offset() -> QPoint:
    """Get the margin offset for drawing."""
    return QPoint(MARGIN * 2, MARGIN)


def add_margin(size: QSize) -> QSize:
    """Add margin to a size."""
    return size + QSize(MARGIN * 4, MARGIN * 2)


def adjust_margin(rect: QRect) -> QRect:
    """Adjust a rect by removing margins."""
    return rect.adjusted(MARGIN * 2, MARGIN, -MARGIN * 2, -MARGIN)


def vertex_font() -> QFont:
    """Get the font for vertex labels."""
    f = QApplication.font()
    f.setPointSize(f.pointSize() - 3)
    return f


def vertex_height(vertex: ListVertex) -> float:
    """Get the height of a vertex."""
    return vertex_size(vertex).height()


def vertex_size(vertex: ListVertex) -> QSize:
    """Get the size of a vertex based on its label."""
    fm = QFontMetrics(vertex_font())
    text_size = fm.size(0, vertex.label())

    s = max(text_size.width(), text_size.height()) + 10
    return QSize(s, s)


def draw_vertex_at_point(painter: QPainter, vertex: ListVertex, origin: QPoint) -> None:
    """Draw a vertex at a specific point."""
    size = vertex_size(vertex)
    draw_vertex(painter, vertex, QRect(origin.x(), origin.y(), size.width(), size.height()))


def draw_vertex(painter: QPainter, vertex: ListVertex, rect: QRect) -> None:
    """Draw a vertex in a rect."""
    line_width = 2.0
    r = rect.adjusted(1, 1, -1, -1)

    path = QPainterPath()
    path.addEllipse(r)
    if vertex.exists:
        painter.fillPath(path, vertex.color)

    pen = QPen()
    border_color = colors.label() if vertex.exists else colors.secondary_label()
    pen.setColor(border_color)
    pen.setWidthF(line_width)
    if not vertex.exists:
        pen.setDashPattern([4, 4])

    painter.setPen(pen)
    painter.drawPath(path)
    painter.drawText(r, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, vertex.label())


def edge_height(edge: ListEdge, row_height: float) -> float:
    """Get the height of an edge."""
    result = row_height
    result = max(result, vertex_height(edge.va))
    result = max(result, vertex_height(edge.vb))
    return result


def draw_edge_in_rect(painter: QPainter, edge: ListEdge, rect: QRect) -> None:
    """Draw an edge in a rect."""
    size0 = vertex_size(edge.va)
    rect0 = QRect(rect.x(), rect.y(), size0.width(), size0.height())

    size1 = vertex_size(edge.vb)
    origin1 = QPoint(rect.x() + rect.width() - size1.width(), rect.y())
    rect1 = QRect(origin1.x(), origin1.y(), size1.width(), size1.height())

    if rect0.height() < rect1.height():
        rect0.moveTop(rect0.y() + (rect1.height() - rect0.height()) // 2)
    elif rect1.height() < rect0.height():
        rect1.moveTop(rect1.y() + (rect0.height() - rect1.height()) // 2)

    draw_vertex_at_point(painter, edge.va, QPoint(rect0.x(), rect0.y()))
    draw_vertex_at_point(painter, edge.vb, QPoint(rect1.x(), rect1.y()))
    draw_edge_line(painter, rect0, rect1, edge.va.exists and edge.vb.exists)


def draw_edge_line(painter: QPainter, rect0: QRect, rect1: QRect, is_valid: bool) -> None:
    """Draw the line between two vertices."""
    edge_margin = 4.0
    line_width = 2.0

    location_0 = rect0.center()
    location_1 = rect1.center()
    delta = location_1 - location_0
    length = math.sqrt(QPoint.dotProduct(delta, delta))

    if length == 0:
        return

    scale_0 = (rect0.width() / 2 + edge_margin) / length
    scale_1 = (rect1.width() / 2 + edge_margin) / length
    p_0 = location_0 + QPoint(int(delta.x() * scale_0), int(delta.y() * scale_0))
    p_1 = location_1 - QPoint(int(delta.x() * scale_1), int(delta.y() * scale_1))

    pen = QPen(edge_color())
    pen.setWidthF(line_width)
    if not is_valid:
        pen.setDashPattern([4, 4])

    path = QPainterPath()
    path.moveTo(p_0)
    path.lineTo(p_1)
    painter.setPen(pen)
    painter.drawPath(path)
