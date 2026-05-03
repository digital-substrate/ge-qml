"""Actions model — exposes eval_actions to QML.

List of commit actions with enabled/disabled state, double-click to toggle.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel, QModelIndex, Qt, Slot,
)
from enum import IntEnum

class ActionsModel(QAbstractListModel):

    class Roles(IntEnum):
        Label = Qt.ItemDataRole.UserRole + 1
        Enabled = Qt.ItemDataRole.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = None
        self._actions: list = []  # list of CommitEvalAction

    def set_store(self, store, notifier):
        self._store = store
        notifier.state_did_change.connect(self.refresh)
        notifier.database_did_open.connect(self.refresh)
        notifier.database_did_close.connect(self.clear)

    # QAbstractListModel interface
    def rowCount(self, parent=QModelIndex()):
        return len(self._actions)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._actions):
            return None
        action = self._actions[index.row()]
        if role == self.Roles.Label:
            return action.header().label()
        if role == self.Roles.Enabled:
            return action.enabled()
        return None

    def roleNames(self):
        return {
            self.Roles.Label: b"label",
            self.Roles.Enabled: b"enabled",
        }

    def refresh(self):
        if not self._store.has_database():
            self._clear()
            return
        self.beginResetModel()
        # Exclude last action (implicit current)
        self._actions = list(self._store.state().eval_actions()[:-1])
        self.endResetModel()

    def clear(self):
        self._clear()

    def _clear(self):
        if self._actions:
            self.beginResetModel()
            self._actions.clear()
            self.endResetModel()

    @Slot(int)
    def toggleEnabled(self, row: int):
        """Double-click handler"""
        if row < 0 or row >= len(self._actions):
            return
        if not self._store.has_database():
            return
        action = self._actions[row]
        self._store.dispatch_enable_commit(
            action.header().commit_id(),
            not action.enabled()
        )
