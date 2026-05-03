"""Comments Model — exposes graph comments to QML as a list model.

QAbstractListModel with text role + CRUD slots.
Uses OrderedCollectionDifference for animated transitions.
"""
from __future__ import annotations

import dsviper
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal, Slot, Property

from model.context import Context
from ge import attachments

from dsviper_components_qml.collection_difference import OrderedCollectionDifference


class CommentsModel(QAbstractListModel):

    TextRole = Qt.ItemDataRole.UserRole + 1

    enabledChanged = Signal()

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._items: list[tuple[dsviper.ValueUUId, str]] = []  # (position, text)
        self._enabled = False

        notifier.database_did_open.connect(self._on_database_did_open)
        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._configure)

    def roleNames(self):
        return {
            self.TextRole: b"commentText",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        position, text = self._items[index.row()]
        if role == self.TextRole:
            return text
        return None

    def _get_enabled(self) -> bool:
        return self._enabled

    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    # CRUD Slots

    @Slot(int, str)
    def addComment(self, selected_row: int, text: str):
        if not text:
            return
        position = dsviper.ValueUUId.INVALID
        if 0 <= selected_row < len(self._items):
            position = self._items[selected_row][0]

        self._context.store.dispatch(
            f"Insert Comment '{text}'",
            lambda m: attachments.graph_graph_comments_insert(
                m, self._context.graph_key, position,
                dsviper.ValueUUId.create(), text))

    @Slot(int, str)
    def assignComment(self, selected_row: int, text: str):
        if not text or selected_row < 0 or selected_row >= len(self._items):
            return
        position = self._items[selected_row][0]
        old_text = self._items[selected_row][1]
        self._context.store.dispatch(
            f"Update Comment '{old_text}' to '{text}'",
            lambda m: attachments.graph_graph_comments_update(
                m, self._context.graph_key, position, text))

    @Slot(int)
    def removeComment(self, selected_row: int):
        if selected_row < 0 or selected_row >= len(self._items):
            return
        position = self._items[selected_row][0]
        text = self._items[selected_row][1]
        self._context.store.dispatch(
            f"Remove Comment '{text}'",
            lambda m: attachments.graph_graph_comments_remove(
                m, self._context.graph_key, position))

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
        new_items: list[tuple[dsviper.ValueUUId, str]] = []

        try:
            attachment_getting = self._context.store.attachment_getting()
            graph_key = self._context.graph_key
            opt_comments = attachments.graph_graph_comments_get(attachment_getting, graph_key)
            if opt_comments:
                comments = opt_comments.unwrap()
                for position, element in comments.items():
                    new_items.append((position, element))
        except Exception as e:
            print(f"CommentsModel._configure error: {e}")

        # Compute diff for animated transitions — key on text (position is opaque)
        diff = OrderedCollectionDifference.from_collections(
            self._items, new_items, key=lambda item: item[1])

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
        expected_texts = [t for _, t in new_items]
        actual_texts = [t for _, t in self._items]
        if actual_texts != expected_texts:
            self.beginResetModel()
            self._items = new_items
            self.endResetModel()
