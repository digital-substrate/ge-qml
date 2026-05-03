"""Tags Model — exposes graph tags to QML as a list model.

QAbstractListModel with key/value roles + CRUD slots.
Uses OrderedCollectionDifference for animated transitions.
"""
from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal, Slot, Property

from model.context import Context
from ge import attachments
from ge.data import Map_string_to_string, Set_string

from dsviper_components_qml.collection_difference import OrderedCollectionDifference


class TagsModel(QAbstractListModel):

    KeyRole = Qt.ItemDataRole.UserRole + 1
    ValueRole = Qt.ItemDataRole.UserRole + 2

    enabledChanged = Signal()

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._items: list[tuple[str, str]] = []
        self._enabled = False

        notifier.database_did_open.connect(self._on_database_did_open)
        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._configure)

    def roleNames(self):
        return {
            self.KeyRole: b"tagKey",
            self.ValueRole: b"tagValue",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        key, value = self._items[index.row()]
        if role == self.KeyRole:
            return key
        if role == self.ValueRole:
            return value
        return None

    def _get_enabled(self) -> bool:
        return self._enabled

    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    # CRUD Slots

    @Slot(str, str)
    def setTag(self, key: str, value: str):
        if not key or not value:
            return
        self._context.store.dispatch(
            f"Set Tag '{key}':'{value}'",
            lambda m: attachments.graph_graph_tags_union(
                m, self._context.graph_key, Map_string_to_string({key: value})))

    @Slot(str, str)
    def updateTag(self, key: str, value: str):
        if not key or not value:
            return
        self._context.store.dispatch(
            f"Update Tag '{key}':'{value}'",
            lambda m: attachments.graph_graph_tags_update(
                m, self._context.graph_key, Map_string_to_string({key: value})))

    @Slot(list)
    def unsetTags(self, keys):
        if not keys:
            return
        self._context.store.dispatch(
            "Unset Tag",
            lambda m: attachments.graph_graph_tags_subtract(
                m, self._context.graph_key, Set_string(set(keys))))

    def _on_database_did_open(self):
        self._enabled = True
        self.enabledChanged.emit()

    def _on_database_did_close(self):
        # Full reset on close — no animation needed
        self.beginResetModel()
        self._items.clear()
        self.endResetModel()
        self._enabled = False
        self.enabledChanged.emit()

    def _configure(self):
        new_items: list[tuple[str, str]] = []

        try:
            attachment_getting = self._context.store.attachment_getting()
            graph_key = self._context.graph_key
            opt_tags = attachments.graph_graph_tags_get(attachment_getting, graph_key)
            if opt_tags:
                tags = opt_tags.unwrap()
                for key, value in tags.items():
                    new_items.append((key, value))
        except Exception as e:
            print(f"TagsModel._configure error: {e}")

        # Compute diff for animated transitions
        diff = OrderedCollectionDifference.from_collections(
            self._items, new_items, key=lambda item: item)

        if not diff.has_changes:
            return

        # Step 1: Apply removals in reverse index order (contiguous ranges)
        for r in diff.removals:
            self.beginRemoveRows(QModelIndex(), r.first, r.last)
            del self._items[r.first:r.last + 1]
            self.endRemoveRows()

        # Step 2: Apply insertions in ascending index order (contiguous ranges)
        for r in diff.insertions:
            self.beginInsertRows(QModelIndex(), r.first, r.last)
            self._items[r.first:r.first] = r.elements
            self.endInsertRows()

        # Verify final state
        if self._items != new_items:
            self.beginResetModel()
            self._items = new_items
            self.endResetModel()
