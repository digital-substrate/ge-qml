"""CommitStore notifier — bridges C++ CommitStoreNotifying to Qt signals.

"""
from __future__ import annotations

from PySide6.QtCore import Signal, QObject


class DSCommitStoreNotifier(QObject):
    # Database
    database_did_open = Signal()
    database_did_close = Signal()
    state_did_change = Signal()
    definitions_did_change = Signal()

    # Dispatch
    dispatch_error = Signal(str)

    # Live Mode
    stop_live = Signal()

    # Evil
    reset_database = Signal()
    database_will_reset = Signal()
    database_did_reset = Signal()

    def __init__(self):
        super().__init__()

    def notify_database_did_open(self):
        self.database_did_open.emit()

    def notify_database_did_close(self):
        self.database_did_close.emit()

    def notify_state_did_change(self):
        self.state_did_change.emit()

    def notify_definitions_did_change(self):
        self.definitions_did_change.emit()

    def notify_dispatch_error(self, error):
        message = error.explained() if hasattr(error, 'explained') else str(error)
        self.dispatch_error.emit(message)

    def notify_stop_live(self):
        self.stop_live.emit()

    def notify_reset_database(self):
        self.reset_database.emit()

    def notify_database_will_reset(self):
        self.database_will_reset.emit()

    def notify_database_did_reset(self):
        self.database_did_reset.emit()
