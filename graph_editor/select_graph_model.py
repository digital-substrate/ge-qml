"""Select Graph Model — lists available graphs for QML dialog.

Exposes graph list + selection logic to QML.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QAbstractListModel, Qt, Property, Signal, Slot

from model.context import Context
from ge import attachments


class SelectGraphModel(QAbstractListModel):
    """Lists available graphs from the store's attachments."""

    NameRole = Qt.ItemDataRole.UserRole + 1

    countChanged = Signal()
    currentIndexChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []        # list of (label, graph_key)
        self._saved_graph_key = None
        self._current_index = -1

    # --- QAbstractListModel ---

    def rowCount(self, parent=None):
        return len(self._items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        if role == self.NameRole or role == Qt.ItemDataRole.DisplayRole:
            return self._items[index.row()][0]
        return None

    def roleNames(self):
        return {
            self.NameRole: b"name",
        }

    # --- Properties ---

    def _get_count(self):
        return len(self._items)

    count = Property(int, _get_count, notify=countChanged)

    def _get_current_index(self):
        return self._current_index

    currentIndex = Property(int, _get_current_index, notify=currentIndexChanged)

    # --- Slots ---

    @Slot()
    def configure(self):
        """Load available graphs"""
        context = Context.instance()
        if not context.store.has_database():
            return

        self._saved_graph_key = context.graph_key

        self.beginResetModel()
        self._items.clear()

        try:
            attachment_getting = context.store.attachment_getting()
            graph_keys = attachments.graph_graph_description_keys(attachment_getting)
            for graph_key in graph_keys:
                opt = attachments.graph_graph_description_get(attachment_getting, graph_key)
                if not opt:
                    continue
                description = opt.unwrap()
                self._items.append((description.name, graph_key))

            self._items.sort(key=lambda item: item[0])
        except Exception as e:
            print(f"SelectGraphModel.configure error: {e}")

        self.endResetModel()
        self.countChanged.emit()

        # Select current graph
        self._current_index = -1
        for i, (_, graph_key) in enumerate(self._items):
            if graph_key == self._saved_graph_key:
                self._current_index = i
                break
        self.currentIndexChanged.emit()

    @Slot(int)
    def select(self, row):
        """Live selection"""
        if row < 0 or row >= len(self._items):
            return
        context = Context.instance()
        context.graph_key = self._items[row][1]
        context.store.notify_state_did_change()
        self._current_index = row
        self.currentIndexChanged.emit()

    @Slot()
    def accept(self):
        """Confirm selection"""
        context = Context.instance()
        if self._saved_graph_key != context.graph_key:
            context.store.reset_undo_redo()
            context.store.notify_state_did_change()

    @Slot()
    def cancel(self):
        """Cancel — revert to saved graph key."""
        context = Context.instance()
        context.graph_key = self._saved_graph_key
        context.store.notify_state_did_change()
