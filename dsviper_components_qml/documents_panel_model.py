"""Documents Panel Model — facade for the 3-panel document browser.

Encapsulates AbstractionModel, KeyModel, DocumentModel, NavigationController
and their internal wiring (DocumentsController). Applications create one object
and call registerContextProperties() — same as a Qt Widget that owns its sub-widgets.

Usage:
    documents_panel = DocumentsPanelModel(db_manager)
    documents_panel.registerContextProperties(engine)

    # For commit-based apps (cdbe, graph_editor):
    documents_panel = DocumentsPanelModel(mgr, commit_mode=True)
"""
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine

from dsviper_components_qml.abstraction_model import AbstractionModel
from dsviper_components_qml.key_model import KeyModel
from dsviper_components_qml.document_model import DocumentModel
from dsviper_components_qml.commit_document_model import CommitDocumentModel
from dsviper_components_qml.navigation_controller import NavigationController
from dsviper_components_qml.documents_controller import DocumentsController


class DocumentsPanelModel(QObject):
    """Facade that owns the document browser's internal models.

    models internally. This restores that encapsulation for QML.
    """

    def __init__(self, db_manager, commit_mode: bool = False, parent=None):
        super().__init__(parent)

        self._abstraction_model = AbstractionModel(db_manager)
        self._key_model = KeyModel(db_manager)
        if commit_mode:
            self._document_model = CommitDocumentModel(db_manager)
        else:
            self._document_model = DocumentModel(db_manager)
        self._nav_controller = NavigationController()

        # Internal wiring — private, like in Qt Widgets
        self._controller = DocumentsController(
            self._abstraction_model,
            self._key_model,
            self._document_model,
            self._nav_controller,
            db_manager,
        )

    def registerContextProperties(self, engine: QQmlApplicationEngine):
        """Expose internal models to QML — same context property names as before."""
        ctx = engine.rootContext()
        ctx.setContextProperty("abstractionModel", self._abstraction_model)
        ctx.setContextProperty("keyModel", self._key_model)
        ctx.setContextProperty("documentModel", self._document_model)
        ctx.setContextProperty("navController", self._nav_controller)

    def navigateToKey(self, key):
        """Public entry point for external signals (e.g. renderModel.inspectKey)."""
        self._controller.navigateToKey(key)
