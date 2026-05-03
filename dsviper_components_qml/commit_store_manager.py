"""Commit store manager — wraps a CommitStore for QML.

Replaces DatabaseManager from dbe — same interface, different backend.
Receives its store via constructor — no singleton.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, Property, Signal, Slot

from dsviper import Error


class CommitStoreManager(QObject):
    """Wraps a CommitStore and exposes state to QML."""

    databaseOpened = Signal()
    databaseClosed = Signal()
    stateChanged = Signal()
    definitionsChanged = Signal()
    isOpenChanged = Signal()
    fileNameChanged = Signal()
    canUndoChanged = Signal()
    canRedoChanged = Signal()
    dispatchError = Signal(str)
    showError = Signal(str)

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self._store = store
        self._settings_mgr = None

    @property
    def store(self):
        return self._store

    # QML-accessible properties
    def _get_is_open(self) -> bool:
        return self._store.has_database()

    isOpen = Property(bool, _get_is_open, notify=isOpenChanged)

    def _get_file_name(self) -> str:
        if self._store.has_database():
            return os.path.basename(self._store.database().path())
        return ""

    fileName = Property(str, _get_file_name, notify=fileNameChanged)

    def _get_can_undo(self) -> bool:
        return self._store.can_undo()

    canUndo = Property(bool, _get_can_undo, notify=canUndoChanged)

    def _get_can_redo(self) -> bool:
        return self._store.can_redo()

    canRedo = Property(bool, _get_can_redo, notify=canRedoChanged)

    @property
    def attachment_getting(self):
        return self._store.attachment_getting() if self._store.has_database() else None

    @property
    def blob_getting(self):
        return self._store.database().blob_getting() if self._store.has_database() else None

    @property
    def definitions(self):
        return self._store.database().definitions() if self._store.has_database() else None

    # Database lifecycle
    def setSettingsManager(self, settings_mgr):
        """Inject settings manager for last-file persistence."""
        self._settings_mgr = settings_mgr

    @Slot(str)
    def openDatabase(self, path: str):
        """Open a CommitDatabase."""
        from dsviper import CommitDatabase
        try:
            database = CommitDatabase.open(path)
            self._store.use(database)
            # Save last file URL
            if self._settings_mgr:
                self._settings_mgr._set_last_file_url(path)
        except Exception as e:
            self.showError.emit(str(e))

    @Slot()
    def openDatabaseDialog(self):
        """Open file dialog."""
        from PySide6.QtWidgets import QApplication, QFileDialog
        parent = QApplication.activeWindow()
        filename, _ = QFileDialog.getOpenFileName(
            parent, "Open Database",
            os.path.expanduser("~/Databases"),
            "All files (*.*)"
        )
        if filename:
            self.openDatabase(filename)

    @Slot()
    def closeDatabase(self):
        try:
            self._store.close()
        except Exception as e:
            self.showError.emit(str(e))

    @Slot(str, str)
    def connectToServer(self, host: str, service: str):
        from dsviper import CommitDatabase
        try:
            db = CommitDatabase.connect(host, service)
            self._store.use(db)
        except Exception as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot(str)
    def connectToServerLocal(self, socket_path: str):
        from dsviper import CommitDatabase
        try:
            db = CommitDatabase.connect_local(socket_path)
            self._store.use(db)
        except Exception as e:
            self.showError.emit(Error.parse(str(e)).explained())

    # Commit operations
    @Slot()
    def undo(self):
        self._store.undo()

    @Slot()
    def redo(self):
        self._store.redo()

    @Slot()
    def forward(self):
        try:
            self._store.forward()
        except Exception as e:
            self.showError.emit(str(e))

    @Slot()
    def reduceHeads(self):
        try:
            self._store.reduce_heads()
        except Exception as e:
            self.showError.emit(str(e))

    # Mutation helpers — used by CommitDocumentModel
    def commitMutations(self, label: str, mutable_state):
        """Commit a mutable state with label. Emits stateChanged."""
        self._store.commit_mutations(label, mutable_state)
        # stateChanged is emitted via notifier callback

    def mutableState(self):
        """Get a fresh mutable state for mutations."""
        return self._store.mutable_state()

    # Create attachments
    def createAttachments(self, attachments: list, instance_id) -> bool:
        """Create key+document for each attachment via commit store."""
        if not self._store.has_database() or not attachments:
            return False
        try:
            mutable_state = self._store.mutable_state()
            for att in attachments:
                key = att.create_key(instance_id)
                doc = att.create_document()
                mutable_state.attachment_mutating().set(att, key, doc)
            self._store.commit_mutations("New instance", mutable_state)
            return True
        except Exception as e:
            self.showError.emit(str(e))
            return False

    # Info slots — same interface as DatabaseManager
    @Slot(result=str)
    def path(self) -> str:
        return self._store.database().path() if self._store.has_database() else ""

    @Slot(result=str)
    def uuid(self) -> str:
        return self._store.database().uuid().encoded() if self._store.has_database() else ""

    @Slot(result=str)
    def codecName(self) -> str:
        return self._store.database().codec_name() if self._store.has_database() else ""

    # Notifier callbacks — called from main.py setup
    def onDatabaseDidOpen(self):
        self.isOpenChanged.emit()
        self.fileNameChanged.emit()
        self.databaseOpened.emit()

    def onDatabaseDidClose(self):
        self.isOpenChanged.emit()
        self.fileNameChanged.emit()
        self.databaseClosed.emit()

    def onStateDidChange(self):
        self.canUndoChanged.emit()
        self.canRedoChanged.emit()
        self.stateChanged.emit()

    def onDefinitionsDidChange(self):
        self.definitionsChanged.emit()

    def onDispatchError(self, error: str):
        self.dispatchError.emit(error)
