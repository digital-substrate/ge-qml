"""Database manager — holds the Database connection and provides access.

Central coordinator between models. Owns the Database lifecycle
and exposes attachment_getting, blob_getting, definitions.

"""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, Property, Signal, Slot


class DatabaseManager(QObject):
    """Owns the Database connection and notifies models on open/close."""

    databaseOpened = Signal()
    databaseClosed = Signal()
    stateChanged = Signal()  # after mutation commit
    isOpenChanged = Signal()
    fileNameChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._database = None
        self._settings_mgr = None

    def setSettingsManager(self, settings_mgr):
        self._settings_mgr = settings_mgr

    @property
    def database(self):
        return self._database

    # QML-accessible properties
    def _get_is_open(self) -> bool:
        return self._database is not None

    isOpen = Property(bool, _get_is_open, notify=isOpenChanged)

    def _get_file_name(self) -> str:
        if self._database:
            return os.path.basename(self._database.path())
        return ""

    fileName = Property(str, _get_file_name, notify=fileNameChanged)

    @property
    def attachment_getting(self):
        return self._database.attachment_getting() if self._database else None

    @property
    def blob_getting(self):
        return self._database.blob_getting() if self._database else None

    @property
    def definitions(self):
        return self._database.definitions() if self._database else None

    @Slot(str)
    def openDatabase(self, path: str):
        """Open a database file. Closes previous if any.

        """
        from dsviper import Database
        self.closeDatabase()
        try:
            self._database = Database.open(path)
            if self._settings_mgr:
                self._settings_mgr._set_last_file_url(path)
            self.isOpenChanged.emit()
            self.fileNameChanged.emit()
            self.databaseOpened.emit()
        except Exception as e:
            print(f"Error opening database: {e}")
            self._database = None

    @Slot()
    def openDatabaseDialog(self):
        """Open a file dialog to select a database."""
        from PySide6.QtWidgets import QApplication, QFileDialog
        parent = QApplication.activeWindow()
        filename, _ = QFileDialog.getOpenFileName(
            parent, "Open Database",
            os.path.expanduser("~/Databases"),
            "Raptor files (*.rap);;All files (*.*)"
        )
        if filename:
            self.openDatabase(filename)

    @Slot()
    def closeDatabase(self):
        if self._database is not None:
            self._database.close()
            self._database = None
            self.isOpenChanged.emit()
            self.fileNameChanged.emit()
            self.databaseClosed.emit()

    def commit(self, attachment, key, path_const, value):
        """Mutate via path.set() on document, then persist.

        Transaction: begin → get doc → path.set(doc, value) → set → commit.
        Emits stateChanged on success.
        """
        if not self._database:
            return False
        try:
            ag = self._database.attachment_getting()
            opt = ag.get(attachment, key)
            if opt.is_nil():
                return False
            from dsviper import Value
            doc = Value.copy(opt.unwrap())
            path_const.set(doc, value)
            self._database.begin_transaction()
            self._database.set(attachment, key, doc)
            self._database.commit()
            self.stateChanged.emit()
            return True
        except Exception as e:
            if self._database.in_transaction():
                self._database.rollback()
            print(f"Commit error: {e}")
            return False

    def commitDocument(self, attachment, key, document):
        """Commit a pre-modified document directly.

        Used by container mutations (optional/vector/set/map/xarray/variant/any)
        that modify the document in-place before committing.
        """
        if not self._database:
            return False
        try:
            self._database.begin_transaction()
            self._database.set(attachment, key, document)
            self._database.commit()
            self.stateChanged.emit()
            return True
        except Exception as e:
            if self._database.in_transaction():
                self._database.rollback()
            print(f"Commit error: {e}")
            return False

    def createAttachments(self, attachments: list, instance_id) -> bool:
        """Create key+document for each attachment.

        """
        if not self._database or not attachments:
            return False
        try:
            self._database.begin_transaction()
            for att in attachments:
                key = att.create_key(instance_id)
                doc = att.create_document()
                self._database.set(att, key, doc)
            self._database.commit()
            self.stateChanged.emit()
            return True
        except Exception as e:
            if self._database.in_transaction():
                self._database.rollback()
            print(f"createAttachments error: {e}")
            return False

    @Slot(result=str)
    def path(self) -> str:
        return self._database.path() if self._database else ""

    @Slot(result=str)
    def uuid(self) -> str:
        return self._database.uuid().encoded() if self._database else ""

    @Slot(result=str)
    def codecName(self) -> str:
        return self._database.codec_name() if self._database else ""
