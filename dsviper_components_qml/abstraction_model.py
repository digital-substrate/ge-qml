"""Abstraction model — lists type concepts and clubs from definitions.

Equivalent of w_abstraction_tree_widget in DSDocuments.
Populated dynamically from database.definitions().concepts() and .clubs().
"""
from __future__ import annotations

from enum import IntEnum

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
    Signal,
    Slot,
)

from .database_manager import DatabaseManager


class AbstractionModel(QAbstractListModel):

    abstractionSelected = Signal(int)  # row index

    class Roles(IntEnum):
        Name = Qt.ItemDataRole.UserRole + 1
        Category = Qt.ItemDataRole.UserRole + 2

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._items: list[tuple] = []  # (type_obj, name, category)

        self._db.databaseOpened.connect(self._reload)
        self._db.databaseClosed.connect(self._clear)
        if hasattr(self._db, 'definitionsChanged'):
            self._db.definitionsChanged.connect(self._reload)

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        _, name, category = self._items[index.row()]
        if role == self.Roles.Name:
            return name
        if role == self.Roles.Category:
            return category
        return None

    def roleNames(self):
        return {
            self.Roles.Name: b"name",
            self.Roles.Category: b"category",
        }

    def type_at(self, row: int):
        """Return the dsviper type object at given row."""
        if 0 <= row < len(self._items):
            return self._items[row][0]
        return None

    abstractionIndexChanged = Signal(int)  # notify QML to update ListView.currentIndex

    @Slot(int)
    def select(self, row: int):
        """Called from QML when user clicks an abstraction."""
        if 0 <= row < len(self._items):
            self.abstractionSelected.emit(row)

    def selectType(self, atype):
        """Select the row matching atype. Used by jump-to-key."""
        for i, (t, _, _) in enumerate(self._items):
            if t == atype:
                self.abstractionIndexChanged.emit(i)
                return

    # New Instance
    newInstanceCreated = Signal(object)  # emits ValueKey of last created attachment

    @Slot(int, result=list)
    def getNewInstanceAttachments(self, row: int) -> list:
        """Return available attachments for new instance creation.

        Returns list of {"name": str, "description": str} for the dialog.
        """
        if row < 0 or row >= len(self._items):
            return []
        vpr_type = self._items[row][0]
        defs = self._db.definitions
        if defs is None:
            return []
        from dsviper import KeyHelper
        self._new_instance_attachments = KeyHelper.attachments(vpr_type, defs)
        self._new_instance_type = vpr_type
        return [
            {"name": att.type_name().name(), "description": att.representation()}
            for att in self._new_instance_attachments
        ]

    @Slot(str, list)
    def createNewInstance(self, instance_id_str: str, selected_indices: list):
        """Create new instance with selected attachments.

        """
        if not hasattr(self, '_new_instance_attachments'):
            return
        from dsviper import ValueUUId
        if instance_id_str:
            instance_id = ValueUUId.try_parse(instance_id_str)
            if instance_id is None:
                return
        else:
            instance_id = ValueUUId.create()

        selected = [
            self._new_instance_attachments[i]
            for i in selected_indices
            if 0 <= i < len(self._new_instance_attachments)
        ]
        if not selected:
            return
        if self._db.createAttachments(selected, instance_id):
            key = selected[-1].create_key(instance_id)
            self.newInstanceCreated.emit(key)

    def _reload(self):
        defs = self._db.definitions
        if defs is None:
            return

        from dsviper import Type
        items = []
        for c in defs.concepts():
            items.append((c, c.representation(), "concept"))
        for c in defs.clubs():
            items.append((c, c.representation(), "club"))
        for att in defs.attachments():
            if att.key_type == Type.ANY_CONCEPT:
                items.append((Type.ANY_CONCEPT, "Any Concept", "any_concept"))
                break

        # Sort alphabetically by name
        items.sort(key=lambda x: x[1])

        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def _clear(self):
        self.beginResetModel()
        self._items = []
        self.endResetModel()
