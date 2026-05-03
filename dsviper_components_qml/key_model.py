"""Key model — lists ValueKey instances for the selected abstraction.

Equivalent of w_key_tree_widget in DSDocuments.
Populated from attachment_getting.keys() filtered by the selected type.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    Signal,
    Slot,
)

from .database_manager import DatabaseManager


class KeyModel(QAbstractTableModel):

    keySelected = Signal(int)  # row index

    _HEADERS = ["Instance ID", "Name"]

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._items: list[tuple] = []  # (ValueKey, instance_id_str, smart_name)
        self._attachments: list = []   # attachments matching current abstraction
        self._current_abstraction = None
        self._selected_key_id = None

        self._db.databaseClosed.connect(self._clear)
        self._db.stateChanged.connect(self._reload)

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        _, instance_id, smart_name = self._items[index.row()]
        col = index.column()
        if col == 0:
            return instance_id
        if col == 1:
            return smart_name
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self._HEADERS):
                return self._HEADERS[section]
        return None

    def key_at(self, row: int):
        """Return the ValueKey at given row."""
        if 0 <= row < len(self._items):
            return self._items[row][0]
        return None

    def attachments_for_key(self, key) -> list:
        """Return all attachments for all forms of key in the hierarchy.

        Transposition of ge-py DSDocumentsBuilder: ValueKey.keys(key) iterates
        all key forms (e.g. LightSky + Light), then for each form finds
        attachments with matching type_key that have a document for that key.
        """
        from dsviper import ValueKey
        ag = self._db.attachment_getting
        defs = self._db.definitions
        if ag is None or defs is None:
            return []
        result = []
        seen = set()
        for key_form in ValueKey.keys(key):
            for att in defs.attachments():
                att_id = att.runtime_id().encoded()
                if att_id in seen:
                    continue
                if att.type_key() == key_form.type_key():
                    if ag.has(att, key_form):
                        result.append(att)
                        seen.add(att_id)
        result.sort(key=lambda a: a.type_name().name())
        return result

    keyIndexChanged = Signal(int)  # notify QML to update ListView.currentIndex

    @Slot(int)
    def select(self, row: int):
        if 0 <= row < len(self._items):
            self.keySelected.emit(row)

    def selectKey(self, key):
        """Select the row matching key. Used by jump-to-key."""
        self._selected_key_id = key.instance_id().encoded()
        for i, (k, instance_id, _) in enumerate(self._items):
            if instance_id == self._selected_key_id:
                self.keyIndexChanged.emit(i)
                return

    @Slot(int, result=list)
    def getContextMenu(self, row: int) -> list:
        """Return context menu actions for key at row.

        """
        if row < 0 or row >= len(self._items):
            return []
        return [
            {"id": "add_attachments", "label": "Add Attachments"},
            {"id": "copy_key_id", "label": "Copy Key Instance ID"},
            {"id": "find_key_id", "label": "Find Key Instance ID"},
        ]

    @Slot(int, str, result=bool)
    def executeContextAction(self, row: int, action_id: str) -> bool:
        """Execute key context menu action.

        """
        if action_id == "copy_key_id":
            if 0 <= row < len(self._items):
                from PySide6.QtGui import QGuiApplication
                key = self._items[row][0]
                QGuiApplication.clipboard().setText(key.instance_id().encoded())
                return True

        if action_id == "find_key_id":
            self._find_key_by_id()
            return True

        return False

    # Add Attachments
    attachmentsAdded = Signal(object)  # emits ValueKey of last created attachment

    @Slot(int, result=list)
    def getAddAttachmentsData(self, row: int) -> list:
        """Return missing attachments for key at row.

        """
        if row < 0 or row >= len(self._items):
            return []
        key = self._items[row][0]
        ag = self._db.attachment_getting
        if ag is None:
            return []
        from dsviper import KeyHelper
        self._add_att_key = key
        self._add_att_missing = KeyHelper.missing_attachments(key, ag)
        return [
            {"name": att.type_name().name(), "description": att.representation()}
            for att in self._add_att_missing
        ]

    @Slot(int, list)
    def addAttachments(self, row: int, selected_indices: list):
        """Add selected missing attachments to key.

        """
        if not hasattr(self, '_add_att_missing') or not hasattr(self, '_add_att_key'):
            return
        key = self._add_att_key
        instance_id = key.instance_id()
        selected = [
            self._add_att_missing[i]
            for i in selected_indices
            if 0 <= i < len(self._add_att_missing)
        ]
        if not selected:
            return
        if self._db.createAttachments(selected, instance_id):
            last_key = selected[-1].create_key(instance_id)
            self.attachmentsAdded.emit(last_key)

    def _find_key_by_id(self):
        """Find a key by UUID input."""
        from PySide6.QtWidgets import QApplication, QInputDialog, QDialog
        parent = QApplication.activeWindow()
        text, ok = QInputDialog.getText(
            parent, "Find Key By Instance ID", "Key Instance ID:"
        )
        if not ok or not text:
            return

        from dsviper import ValueUUId
        instance_id = ValueUUId.try_parse(text.strip())
        if instance_id is None:
            return

        for i, (key, _, _) in enumerate(self._items):
            if key.instance_id() == instance_id:
                self.keyIndexChanged.emit(i)
                self.keySelected.emit(i)
                return

    def setAbstraction(self, abstraction_type):
        """Set the current abstraction and reload keys."""
        self._current_abstraction = abstraction_type
        self._reload()

    def _reload(self):
        ag = self._db.attachment_getting
        defs = self._db.definitions
        if ag is None or defs is None or self._current_abstraction is None:
            return

        from dsviper import TypeKey, TypeSet, ValueKey, ValueSet, KeyHelper

        try:
            # Collect keys — exact match on type_key, like ge-py
            type_key = TypeKey(self._current_abstraction)
            keys = ValueSet(TypeSet(type_key))
            self._attachments = []
            for att in defs.attachments():
                if att.type_key() == type_key:
                    keys.update(ag.keys(att))
                    self._attachments.append(att)

            # Build display items with smart names
            from dsviper import KeyNamer
            key_namer = KeyNamer(defs)
            items = []
            for k in keys:
                vk = ValueKey.cast(k)
                instance_id = vk.instance_id().encoded()
                smart_name = key_namer.smart_name(vk, ag) or "-"
                items.append((vk, instance_id, smart_name))

            # Sort by smart name, then instance_id
            items.sort(key=lambda x: (x[2], x[1]))

            self.beginResetModel()
            self._items = items
            self.endResetModel()

            # Restore visual selection (like ge-py _update_key_selection)
            if self._selected_key_id:
                for i, (k, instance_id, _) in enumerate(items):
                    if instance_id == self._selected_key_id:
                        self.keyIndexChanged.emit(i)
                        break
        except Exception as e:
            print(f"KeyModel._reload error: {e}")

    def _smart_name(self, key) -> str:
        """Use native KeyNamer for smart name resolution."""
        ag = self._db.attachment_getting
        defs = self._db.definitions
        if ag is None or defs is None:
            return "-"

        from dsviper import KeyNamer
        return KeyNamer(defs).smart_name(key, ag) or "-"

    def _clear(self):
        self._current_abstraction = None
        self._attachments = []
        self.beginResetModel()
        self._items = []
        self.endResetModel()
