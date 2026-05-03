"""Undo stack model — exposes undo/redo history to QML.

Simple read-only list: commit labels in reverse order, with current position.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel, QModelIndex, Qt, Property, Signal,
)
from enum import IntEnum


class UndoModel(QAbstractListModel):

    class Roles(IntEnum):
        Label = Qt.ItemDataRole.UserRole + 1

    currentRowChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = None
        self._labels: list[str] = []
        self._commit_ids: list = []
        self._current_row: int = -1

    def set_store(self, store, notifier):
        self._store = store
        notifier.state_did_change.connect(self.refresh)
        notifier.database_did_open.connect(self.refresh)
        notifier.database_did_close.connect(self.clear)

    # QML property: current position in list
    def _get_current_row(self) -> int:
        return self._current_row

    currentRow = Property(int, _get_current_row, notify=currentRowChanged)

    # QAbstractListModel interface
    def rowCount(self, parent=QModelIndex()):
        return len(self._labels)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._labels):
            return None
        if role == self.Roles.Label:
            return self._labels[index.row()]
        return None

    def roleNames(self):
        return {self.Roles.Label: b"label"}

    # Refresh — called from Python signal connections in main.py
    def refresh(self):
        if not self._store.has_database():
            self._clear()
            return

        commit_ids, current = self._store.undo_stack_ids()
        commit_ids.reverse()

        if commit_ids != self._commit_ids:
            self._commit_ids = commit_ids
            self.beginResetModel()
            db = self._store.database()
            self._labels = [db.commit_header(cid).label() for cid in commit_ids]
            self.endResetModel()

        new_row = (len(commit_ids) - 1 - current) if current is not None else -1
        if new_row != self._current_row:
            self._current_row = new_row
            self.currentRowChanged.emit()

    def clear(self):
        self._clear()

    def _clear(self):
        if self._labels:
            self.beginResetModel()
            self._labels.clear()
            self._commit_ids.clear()
            self.endResetModel()
        if self._current_row != -1:
            self._current_row = -1
            self.currentRowChanged.emit()
