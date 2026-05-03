"""Title Model — exposes graph title to QML.

Subscribes to DSCommitStoreNotifier, exposes title as Property.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from model.context import Context
from ge import attachments


class TitleModel(QObject):

    titleChanged = Signal()
    enabledChanged = Signal()

    def __init__(self, notifier, parent=None):
        super().__init__(parent)
        self._context = Context.instance()
        self._title = ""
        self._enabled = False

        notifier.database_did_open.connect(self._on_database_did_open)
        notifier.database_did_close.connect(self._on_database_did_close)
        notifier.state_did_change.connect(self._configure)

    # QML Properties
    def _get_title(self) -> str:
        return self._title

    title = Property(str, _get_title, notify=titleChanged)

    def _get_enabled(self) -> bool:
        return self._enabled

    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    # Slots
    @Slot(str)
    def setTitle(self, new_title: str):
        if new_title == self._title:
            return
        label = f"Set Title To '{new_title}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_graph_description_set_name(
                m, self._context.graph_key, new_title))

    def _on_database_did_open(self):
        self._enabled = True
        self.enabledChanged.emit()

    def _on_database_did_close(self):
        self._title = ""
        self.titleChanged.emit()
        self._enabled = False
        self.enabledChanged.emit()

    def _configure(self):
        try:
            opt = attachments.graph_graph_description_get(
                self._context.store.attachment_getting(), self._context.graph_key)
            if opt:
                description = opt.unwrap()
                if description.name != self._title:
                    self._title = description.name
                    self.titleChanged.emit()
        except Exception as e:
            print(f"TitleModel._configure error: {e}")
