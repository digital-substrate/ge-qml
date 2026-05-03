"""Context Manager — wraps Context singleton for QML.

Bridges the Context singleton (store + graph_key) to QML properties/signals.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, QUrl, Property, Signal, Slot

from dsviper import CommitDatabase, ViperError, Error

from model.context import Context
from model import graph_topology, selection_vertices, selection_edges, selection_mixed
from model import graph_bug, graph_integrity, graph_killer
from model import random as model_random
from model import edge as model_edge
from model import tools as model_tools
from model import script_delete_selection
from ge.data import Graph_Rectangle


class ContextManager(QObject):
    """Wraps Context.instance() and exposes state to QML."""

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

    # Graph state signals
    hasVerticesChanged = Signal()
    hasEdgesChanged = Signal()
    hasSelectionChanged = Signal()
    hasSelectedVerticesChanged = Signal()
    hasSelectedEdgesChanged = Signal()
    hasRemainingEdgesChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._settings_mgr = None

    @property
    def store(self):
        return self._context.store

    @property
    def context(self):
        return self._context

    def setSettingsManager(self, settings_mgr):
        self._settings_mgr = settings_mgr

    @property
    def blob_getting(self):
        """Used by BlobModel"""
        return self._context.store.database().blob_getting() if self._context.store.has_database() else None

    @property
    def attachment_getting(self):
        """Used by AbstractionModel, KeyModel, CommitDocumentModel."""
        return self._context.store.attachment_getting() if self._context.store.has_database() else None

    @property
    def definitions(self):
        """Used by AbstractionModel, KeyModel."""
        return self._context.store.database().definitions() if self._context.store.has_database() else None

    def mutableState(self):
        """Get a fresh mutable state for mutations."""
        return self._context.store.mutable_state()

    def commitMutations(self, label: str, mutable_state):
        """Commit a mutable state with label."""
        self._context.store.commit_mutations(label, mutable_state)

    def createAttachments(self, attachments: list, instance_id) -> bool:
        """Create key+document for each attachment via commit store."""
        if not self._context.store.has_database() or not attachments:
            return False
        try:
            mutable_state = self._context.store.mutable_state()
            for att in attachments:
                key = att.create_key(instance_id)
                doc = att.create_document()
                mutable_state.attachment_mutating().set(att, key, doc)
            self._context.store.commit_mutations("New instance", mutable_state)
            return True
        except ViperError as e:
            self.showError.emit(Error.parse(str(e)).explained())
            return False

    # --- QML-accessible properties ---

    def _get_is_open(self) -> bool:
        return self._context.store.has_database()

    isOpen = Property(bool, _get_is_open, notify=isOpenChanged)

    def _get_file_name(self) -> str:
        if self._context.store.has_database():
            return os.path.basename(self._context.store.database().path())
        return ""

    fileName = Property(str, _get_file_name, notify=fileNameChanged)

    def _get_can_undo(self) -> bool:
        return self._context.store.can_undo()

    canUndo = Property(bool, _get_can_undo, notify=canUndoChanged)

    def _get_can_redo(self) -> bool:
        return self._context.store.can_redo()

    canRedo = Property(bool, _get_can_redo, notify=canRedoChanged)

    def _get_has_vertices(self) -> bool:
        if not self._context.store.has_database():
            return False
        return graph_topology.has_vertices(
            self._context.store.attachment_getting(), self._context.graph_key)

    hasVertices = Property(bool, _get_has_vertices, notify=hasVerticesChanged)

    def _get_has_edges(self) -> bool:
        if not self._context.store.has_database():
            return False
        return graph_topology.has_edges(
            self._context.store.attachment_getting(), self._context.graph_key)

    hasEdges = Property(bool, _get_has_edges, notify=hasEdgesChanged)

    def _get_has_selection(self) -> bool:
        if not self._context.store.has_database():
            return False
        return selection_mixed.has_selected(
            self._context.store.attachment_getting(), self._context.graph_key)

    hasSelection = Property(bool, _get_has_selection, notify=hasSelectionChanged)

    def _get_has_selected_vertices(self) -> bool:
        if not self._context.store.has_database():
            return False
        return selection_vertices.has_selected(
            self._context.store.attachment_getting(), self._context.graph_key)

    hasSelectedVertices = Property(bool, _get_has_selected_vertices, notify=hasSelectedVerticesChanged)

    def _get_has_selected_edges(self) -> bool:
        if not self._context.store.has_database():
            return False
        return selection_edges.has_selected(
            self._context.store.attachment_getting(), self._context.graph_key)

    hasSelectedEdges = Property(bool, _get_has_selected_edges, notify=hasSelectedEdgesChanged)

    def _get_has_remaining_edges(self) -> bool:
        if not self._context.store.has_database():
            return False
        return graph_topology.has_remaining_edges(
            self._context.store.attachment_getting(), self._context.graph_key)

    hasRemainingEdges = Property(bool, _get_has_remaining_edges, notify=hasRemainingEdgesChanged)

    # --- Notifier slots (called from main.py wiring) ---

    @Slot()
    def onDatabaseDidOpen(self):
        self.isOpenChanged.emit()
        self.fileNameChanged.emit()
        self._emitGraphState()
        self.databaseOpened.emit()

    @Slot()
    def onDatabaseDidClose(self):
        self.isOpenChanged.emit()
        self.fileNameChanged.emit()
        self.canUndoChanged.emit()
        self.canRedoChanged.emit()
        self._emitGraphState()
        self.databaseClosed.emit()

    @Slot()
    def onStateDidChange(self):
        self.canUndoChanged.emit()
        self.canRedoChanged.emit()
        self._emitGraphState()
        self.stateChanged.emit()

    @Slot()
    def onDefinitionsDidChange(self):
        self.definitionsChanged.emit()

    @Slot(str)
    def onDispatchError(self, error):
        self.dispatchError.emit(error)

    def _emitGraphState(self):
        self.hasVerticesChanged.emit()
        self.hasEdgesChanged.emit()
        self.hasSelectionChanged.emit()
        self.hasSelectedVerticesChanged.emit()
        self.hasSelectedEdgesChanged.emit()
        self.hasRemainingEdgesChanged.emit()

    # --- Database operations ---

    @Slot(str)
    @Slot(QUrl)
    def openDatabase(self, path):
        if isinstance(path, QUrl):
            path = path.toLocalFile()
        elif isinstance(path, str) and path.startswith('file://'):
            path = QUrl(path).toLocalFile()
        try:
            database = CommitDatabase.open(path)
            self._context.use(database)
            if self._settings_mgr:
                self._settings_mgr._set_last_file_url(path)
        except ViperError as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot(str)
    @Slot(QUrl)
    def newDatabase(self, path):
        if isinstance(path, QUrl):
            path = path.toLocalFile()
        elif isinstance(path, str) and path.startswith('file://'):
            path = QUrl(path).toLocalFile()
        try:
            if os.path.exists(path):
                os.remove(path)
            database = self._context.create_database(path)
            self._context.use(database)
            if self._settings_mgr:
                self._settings_mgr._set_last_file_url(path)
        except ViperError as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot()
    def closeDatabase(self):
        try:
            self._context.close()
        except ViperError as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot(str, str)
    def connectToServer(self, host: str, service: str):
        try:
            db = CommitDatabase.connect(host, service)
            self._context.use(db)
        except Exception as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot(str)
    def connectToServerLocal(self, socket_path: str):
        try:
            db = CommitDatabase.connect_local(socket_path)
            self._context.use(db)
        except Exception as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot()
    def forward(self):
        try:
            self._context.store.forward()
        except ViperError as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot()
    def reduceHeads(self):
        try:
            self._context.store.reduce_heads()
        except ViperError as e:
            self.showError.emit(Error.parse(str(e)).explained())

    @Slot()
    def undo(self):
        self._context.store.undo()

    @Slot()
    def redo(self):
        self._context.store.redo()

    # --- Graph operations ---

    @Slot()
    def newGraph(self):
        self._context.new_graph()

    @Slot()
    def clearGraph(self):
        self._context.store.dispatch(
            "Clear The Graph",
            lambda m: graph_topology.clear(m, self._context.graph_key))

    @Slot(int, int)
    def randomGraph(self, width, height):
        rect = Graph_Rectangle()
        rect.x, rect.y, rect.w, rect.h = 0, 0, width, height
        self._context.store.dispatch(
            "Random Graph",
            lambda m: model_random.graph(m, self._context.graph_key, 5, 6, rect))

    @Slot(int, int)
    def randomVertex(self, width, height):
        rect = Graph_Rectangle()
        rect.x, rect.y, rect.w, rect.h = 0, 0, width, height
        self._context.store.dispatch(
            "Random Vertex",
            lambda m: model_random.add_vertex(m, self._context.graph_key, rect))

    @Slot()
    def randomEdge(self):
        if not self._get_has_remaining_edges():
            return
        topology = model_random.find_edge_topology(
            self._context.store.attachment_getting(), self._context.graph_key)
        if not topology:
            return
        va_label = model_tools.vertex_label(self._context.store.attachment_getting(), topology.va_key)
        vb_label = model_tools.vertex_label(self._context.store.attachment_getting(), topology.vb_key)
        label = f"Random Edge '{va_label}' - '{vb_label}'"
        self._context.store.dispatch(
            label,
            lambda m: model_edge.add(m, self._context.graph_key, topology.va_key, topology.vb_key))

    @Slot()
    def randomTag(self):
        self._context.store.dispatch(
            "Random Tag",
            lambda m: model_random.tag(m, self._context.graph_key))

    @Slot()
    def randomComment(self):
        self._context.store.dispatch(
            "Random Comment",
            lambda m: model_random.comment(m, self._context.graph_key))

    @Slot()
    def incrementVertexValue(self):
        self._context.store.dispatch(
            "Increment Selection Value",
            lambda m: selection_vertices.increment_value(m, self._context.graph_key, 100))

    @Slot()
    def deleteSelection(self):
        self._context.store.dispatch(
            "Delete Selection",
            lambda m: script_delete_selection.delete_selection(m, self._context.graph_key))

    @Slot()
    def deleteBugged(self):
        self._context.store.dispatch(
            "Delete Bugged Selection",
            lambda m: script_delete_selection.delete_selection_bugged(m, self._context.graph_key))

    # Selection operations
    @Slot()
    def selectAllVertices(self):
        self._context.store.dispatch(
            "Select All Vertices",
            lambda m: selection_vertices.select_all(m, self._context.graph_key))

    @Slot()
    def selectAllEdges(self):
        self._context.store.dispatch(
            "Select All Edges",
            lambda m: selection_edges.select_all(m, self._context.graph_key))

    @Slot()
    def deselectAllVertices(self):
        self._context.store.dispatch(
            "Deselect All Vertices",
            lambda m: selection_vertices.deselect_all(m, self._context.graph_key))

    @Slot()
    def deselectAllEdges(self):
        self._context.store.dispatch(
            "Deselect All Edges",
            lambda m: selection_edges.deselect_all(m, self._context.graph_key))

    @Slot()
    def invertVerticesSelection(self):
        self._context.store.dispatch(
            "Invert Vertices Selection",
            lambda m: selection_vertices.invert(m, self._context.graph_key))

    @Slot()
    def invertEdgesSelection(self):
        self._context.store.dispatch(
            "Invert Edges Selection",
            lambda m: selection_edges.invert(m, self._context.graph_key))

    @Slot()
    def selectAll(self):
        self._context.store.dispatch(
            "Select All",
            lambda m: selection_mixed.select_all(m, self._context.graph_key))

    @Slot()
    def deselectAll(self):
        self._context.store.dispatch(
            "Deselect All",
            lambda m: selection_mixed.deselect_all(m, self._context.graph_key))

    @Slot()
    def invertSelection(self):
        self._context.store.dispatch(
            "Invert Selection",
            lambda m: selection_mixed.invert(m, self._context.graph_key))

    @Slot()
    def restoreVertexSelection(self):
        self._context.store.dispatch(
            "Restore Vertex Selection",
            lambda m: selection_vertices.restore(m, self._context.graph_key))

    # Bug / Integrity operations
    @Slot()
    def graphWithMissingVertex(self):
        self._context.store.dispatch(
            "Graph With Missing Vertex",
            lambda m: graph_bug.create_with_missing_vertex(m, self._context.graph_key))

    @Slot()
    def graphWithMissingVertexProperties(self):
        self._context.store.dispatch(
            "Graph With Missing Vertex Properties",
            lambda m: graph_bug.create_with_missing_vertex_properties(m, self._context.graph_key))

    @Slot()
    def graphWithError(self):
        self._context.store.dispatch(
            "Graph With Error",
            lambda m: graph_bug.create_with_error(m, self._context.graph_key))

    @Slot()
    def restoreIntegrityByDeleting(self):
        self._context.store.dispatch(
            "Restore Integrity by Deleting",
            lambda m: graph_integrity.restore_by_deleting(m, self._context.graph_key))

    @Slot()
    def restoreIntegrityByRestoring(self):
        self._context.store.dispatch(
            "Restore Integrity By Restoring",
            lambda m: graph_integrity.restore_by_respawning(m, self._context.graph_key))

    @Slot()
    def restoreIntegrityByCreating(self):
        value = model_tools.safe_next_vertex_value(
            self._context.store.attachment_getting(), self._context.graph_key)
        self._context.store.dispatch(
            "Restore Integrity By Creating",
            lambda m: graph_integrity.restore_by_creating(m, self._context.graph_key, value))

    @Slot()
    def killer(self):
        self._context.store.dispatch(
            "They Have Killed Commit",
            lambda m: graph_killer.shoot(m, self._context.graph_key, 1000))
