"""Documents Controller — owns the selection cascade between the 3 document panel models.

Encapsulates the internal wiring that was previously exposed in each app's main.py.
Applications just create it — no manual signal/connect needed.

"""
from __future__ import annotations

from PySide6.QtCore import QObject

from dsviper_components_qml.abstraction_model import AbstractionModel
from dsviper_components_qml.key_model import KeyModel
from dsviper_components_qml.base_document_model import BaseDocumentModel
from dsviper_components_qml.navigation_controller import NavigationController


class DocumentsController(QObject):
    """Internal wiring for AbstractionModel ↔ KeyModel ↔ DocumentModel."""

    def __init__(self, abstraction_model: AbstractionModel,
                 key_model: KeyModel,
                 document_model: BaseDocumentModel,
                 nav_controller: NavigationController,
                 db_manager,
                 parent=None):
        super().__init__(parent)
        self._abstraction_model = abstraction_model
        self._key_model = key_model
        self._document_model = document_model
        self._nav_controller = nav_controller

        # Selection cascade
        abstraction_model.abstractionSelected.connect(self._on_abstraction_selected)
        key_model.keySelected.connect(self._on_key_selected)
        document_model.jumpToKey.connect(self._on_jump_to_key)
        document_model.selectionChanged.connect(nav_controller.updateLocation)
        nav_controller.navigateTo.connect(self._navigate_to_location)
        db_manager.databaseClosed.connect(nav_controller.reset)
        db_manager.databaseOpened.connect(self._on_database_opened)

        # New instance / add attachments — navigate to created key
        abstraction_model.newInstanceCreated.connect(self._navigate_to_key)
        key_model.attachmentsAdded.connect(self._navigate_to_key)

    def _on_abstraction_selected(self, row: int):
        atype = self._abstraction_model.type_at(row)
        if atype:
            self._nav_controller.reset()
            self._document_model.clear()
            self._key_model.setAbstraction(atype)
            # Auto-select first key (like ge-py _abstraction_selection_changed)
            first_key = self._key_model.key_at(0)
            if first_key:
                self._key_model.selectKey(first_key)
                self._document_model.setKey(first_key, self._key_model.attachments_for_key(first_key))

    def _on_database_opened(self):
        """Auto-select first abstraction + first key on open (like ge-py)."""
        from PySide6.QtCore import QTimer
        def _auto_select():
            if self._abstraction_model.rowCount() > 0:
                self._abstraction_model.select(0)
        QTimer.singleShot(0, _auto_select)

    def _on_key_selected(self, row: int):
        key = self._key_model.key_at(row)
        if key:
            self._document_model.setKey(key, self._key_model.attachments_for_key(key))

    def _navigate_to_key(self, key):
        # Preserve attachment+path if navigating to same type_key (like ge-py _set_key)
        current_key = self._document_model._current_key
        if (current_key and self._document_model._current_attachment
                and self._document_model._current_path
                and current_key.type_key() == key.type_key()):
            self._navigate_to_location(key, self._document_model._current_attachment,
                                        self._document_model._current_path)
        else:
            self._navigate_to_location(key, None, None)

    def _navigate_to_location(self, key, attachment, path):
        atype = key.type_key().element_type()
        self._abstraction_model.selectType(atype)
        self._key_model.setAbstraction(atype)
        self._key_model.selectKey(key)
        self._document_model.setKey(key, self._key_model.attachments_for_key(key),
                                     attachment, path)

    def _on_jump_to_key(self, key):
        self._nav_controller.pushJump(
            self._document_model._current_key,
            self._document_model._current_attachment,
            self._document_model._current_path,
            key
        )
        self._navigate_to_key(key)

    def navigateToKey(self, key):
        """Public entry point for external signals (e.g. renderModel.inspectKey)."""
        self._navigate_to_key(key)
