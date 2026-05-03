"""List Model — exposes graph vertices+edges as a flat list to QML.

QAbstractListModel sorted by vertex value, with edges nested under vertices.
Selection dispatch via set_selection.
"""
from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal, Slot, Property
from PySide6.QtGui import QColor

from model.context import Context
from model import selection_mixed
from ge import attachments
from ge.data import (
    Graph_VertexKey,
    Graph_EdgeKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
)
from list.element import ListVertex, ListEdge
from graph_sorted_by_value import GraphSortedByValue
from dsviper_components_qml.collection_difference import OrderedCollectionDifference


class ListModel(QAbstractListModel):
    """Flat list: vertex rows + edge rows, sorted by value."""

    # Roles
    IsVertexRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = Qt.ItemDataRole.UserRole + 2
    ColorRole = Qt.ItemDataRole.UserRole + 3
    ExistsRole = Qt.ItemDataRole.UserRole + 4
    SelectedRole = Qt.ItemDataRole.UserRole + 5
    # Edge-specific
    VaLabelRole = Qt.ItemDataRole.UserRole + 6
    VaColorRole = Qt.ItemDataRole.UserRole + 7
    VbLabelRole = Qt.ItemDataRole.UserRole + 8
    VbColorRole = Qt.ItemDataRole.UserRole + 9
    VaExistsRole = Qt.ItemDataRole.UserRole + 10
    VbExistsRole = Qt.ItemDataRole.UserRole + 11

    enabledChanged = Signal()

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._elements: list[ListVertex | ListEdge] = []
        self._selected_rows: set[int] = set()
        self._enabled = False

        notifier.database_did_open.connect(self._on_database_did_open)
        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._configure)

    def roleNames(self):
        return {
            self.IsVertexRole: b"isVertex",
            self.LabelRole: b"label",
            self.ColorRole: b"elementColor",
            self.ExistsRole: b"exists",
            self.SelectedRole: b"selected",
            self.VaLabelRole: b"vaLabel",
            self.VaColorRole: b"vaColor",
            self.VbLabelRole: b"vbLabel",
            self.VbColorRole: b"vbColor",
            self.VaExistsRole: b"vaExists",
            self.VbExistsRole: b"vbExists",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._elements)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._elements):
            return None
        row = index.row()
        element = self._elements[row]

        if role == self.IsVertexRole:
            return isinstance(element, ListVertex)
        if role == self.SelectedRole:
            return row in self._selected_rows

        if isinstance(element, ListVertex):
            if role == self.LabelRole:
                return element.label()
            if role == self.ColorRole:
                return QColor(
                    int(element.color.red() if hasattr(element.color, 'red') else 0),
                    int(element.color.green() if hasattr(element.color, 'green') else 0),
                    int(element.color.blue() if hasattr(element.color, 'blue') else 0))
            if role == self.ExistsRole:
                return element.exists
        elif isinstance(element, ListEdge):
            if role == self.LabelRole:
                return element.label()
            if role == self.VaLabelRole:
                return element.va.label()
            if role == self.VaColorRole:
                return QColor(
                    int(element.va.color.red() if hasattr(element.va.color, 'red') else 0),
                    int(element.va.color.green() if hasattr(element.va.color, 'green') else 0),
                    int(element.va.color.blue() if hasattr(element.va.color, 'blue') else 0))
            if role == self.VbLabelRole:
                return element.vb.label()
            if role == self.VbColorRole:
                return QColor(
                    int(element.vb.color.red() if hasattr(element.vb.color, 'red') else 0),
                    int(element.vb.color.green() if hasattr(element.vb.color, 'green') else 0),
                    int(element.vb.color.blue() if hasattr(element.vb.color, 'blue') else 0))
            if role == self.VaExistsRole:
                return element.va.exists
            if role == self.VbExistsRole:
                return element.vb.exists
        return None

    def _get_enabled(self) -> bool:
        return self._enabled

    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    @Slot(list)
    def setSelection(self, selected_indices):
        selected_vertices = Set_Graph_VertexKey()
        selected_edges = Set_Graph_EdgeKey()

        for row in selected_indices:
            if 0 <= row < len(self._elements):
                element = self._elements[row]
                if isinstance(element, ListVertex):
                    selected_vertices.add(element.vertex_key)
                elif isinstance(element, ListEdge):
                    selected_edges.add(element.edge_key)

        self._context.store.dispatch(
            "Set Selection",
            lambda m: selection_mixed.set_selection(
                m, self._context.graph_key, selected_vertices, selected_edges))

    def _on_database_did_open(self):
        self._enabled = True
        self.enabledChanged.emit()

    def _on_database_did_close(self):
        self.beginResetModel()
        self._elements.clear()
        self._selected_rows.clear()
        self.endResetModel()
        self._enabled = False
        self.enabledChanged.emit()

    @staticmethod
    def _element_key(e):
        """Identity key for diff — vertex_key or edge_key + value for ordering."""
        if isinstance(e, ListVertex):
            return ("v", e.vertex_key.instance_id(), e.value)
        elif isinstance(e, ListEdge):
            return ("e", e.edge_key.instance_id())
        return id(e)

    def _configure(self):
        new_elements: list[ListVertex | ListEdge] = []
        new_selected_rows: set[int] = set()

        try:
            attachment_getting = self._context.store.attachment_getting()
            graph_key = self._context.graph_key

            # Build sorted list
            sorted_graph = GraphSortedByValue.build(attachment_getting, graph_key)

            vertex_keys = Set_Graph_VertexKey()
            opt_topology = attachments.graph_graph_topology_get(attachment_getting, graph_key)
            if opt_topology:
                vertex_keys = opt_topology.unwrap().vertex_keys

            for sorted_vertex in sorted_graph.sorted_vertices():
                list_vertex = self._create_list_vertex(
                    attachment_getting, sorted_vertex.vertex_key, vertex_keys)
                new_elements.append(list_vertex)

                for sorted_edge in sorted_vertex.edges:
                    list_edge = self._create_list_edge(
                        attachment_getting, sorted_edge.edge_key,
                        sorted_vertex.vertex_key, sorted_edge.vertex_key, vertex_keys)
                    new_elements.append(list_edge)

            # Build selection
            sel_vertex_keys = Set_Graph_VertexKey()
            sel_edge_keys = Set_Graph_EdgeKey()
            opt_selection = attachments.graph_graph_selection_get(attachment_getting, graph_key)
            if opt_selection:
                selection = opt_selection.unwrap()
                sel_vertex_keys = selection.vertex_keys
                sel_edge_keys = selection.edge_keys

            for i, element in enumerate(new_elements):
                if isinstance(element, ListVertex) and element.vertex_key in sel_vertex_keys:
                    new_selected_rows.add(i)
                elif isinstance(element, ListEdge) and element.edge_key in sel_edge_keys:
                    new_selected_rows.add(i)

        except Exception as e:
            print(f"ListModel._configure error: {e}")

        # Compute diff for animated transitions
        diff = OrderedCollectionDifference.from_collections(
            self._elements, new_elements, key=self._element_key)

        if not diff.has_changes:
            # Update elements (property changes: exists, color) and selection
            self._elements = list(new_elements)
            self._selected_rows = new_selected_rows
            if self._elements:
                self.dataChanged.emit(
                    self.index(0), self.index(len(self._elements) - 1))
            return

        # Step 1: Apply removals in reverse index order (contiguous ranges)
        for r in diff.removals:
            self.beginRemoveRows(QModelIndex(), r.first, r.last)
            del self._elements[r.first:r.last + 1]
            self.endRemoveRows()

        # Step 2: Apply insertions in ascending index order (contiguous ranges)
        for r in diff.insertions:
            self.beginInsertRows(QModelIndex(), r.first, r.last)
            self._elements[r.first:r.first] = r.elements
            self.endInsertRows()

        # Update selection
        self._selected_rows = new_selected_rows

        # Verify final state and update matched elements (property changes)
        final_keys = [self._element_key(e) for e in self._elements]
        expected_keys = [self._element_key(e) for e in new_elements]
        if final_keys != expected_keys:
            self.beginResetModel()
            self._elements = new_elements
            self._selected_rows = new_selected_rows
            self.endResetModel()
        else:
            # Replace matched elements with new data (exists, color may have changed)
            self._elements = list(new_elements)
            if new_elements:
                self.dataChanged.emit(
                    self.index(0), self.index(len(new_elements) - 1))

    def _create_list_vertex(self, getting, vertex_key, vertex_keys) -> ListVertex:
        opt_attrs = attachments.graph_vertex_visual_attributes_get(getting, vertex_key)
        if opt_attrs:
            attrs = opt_attrs.unwrap()
            value = attrs.value
            color = QColor(
                int(attrs.color.red * 255),
                int(attrs.color.green * 255),
                int(attrs.color.blue * 255))
        else:
            value = -1
            color = QColor(255, 0, 0)

        exists = vertex_key in vertex_keys
        return ListVertex.make(vertex_key, value, color, exists)

    def _create_list_edge(self, getting, edge_key, va_key, vb_key, vertex_keys) -> ListEdge:
        va = self._create_list_vertex(getting, va_key, vertex_keys)
        vb = self._create_list_vertex(getting, vb_key, vertex_keys)
        return ListEdge.make(edge_key, va, vb)
