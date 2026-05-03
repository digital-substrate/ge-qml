"""Live mode model — manages Go Live / Manager toggle + sync timer.

"""
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Property, Signal, Slot

from dsviper import CommitSynchronizer, Logging


class DSLogger(QObject):
    """Minimal logger"""
    messageReceived = Signal(int, str)

    def __init__(self, level, parent=None):
        super().__init__(parent)
        self._level = level

    def log(self, level: int, message: str):
        self.messageReceived.emit(level, message)


class LiveModel(QObject):
    """Encapsulates live mode state and sync timer."""

    liveChanged = Signal()
    syncLogMessage = Signal(str)
    connectionError = Signal(str)

    def __init__(self, settings_mgr, parent=None):
        super().__init__(parent)
        self._store = None
        self._settings = settings_mgr
        self._live_enabled = False
        self._live_is_manager = False
        self._synchronizer = None
        self._sync_logger = DSLogger(Logging.LEVEL_ALL)
        self._sync_logger.messageReceived.connect(lambda level, msg: self.syncLogMessage.emit(msg))
        self._sync_logging = Logging.create(self._sync_logger)

    def set_store(self, store):
        self._store = store

    # --- QML properties ---
    def _get_live_enabled(self) -> bool:
        return self._live_enabled

    liveEnabled = Property(bool, _get_live_enabled, notify=liveChanged)

    def _get_live_is_manager(self) -> bool:
        return self._live_is_manager

    liveIsManager = Property(bool, _get_live_is_manager, notify=liveChanged)

    # --- Slots ---
    @Slot()
    def toggleLive(self):
        if not self._live_enabled:
            self._enable_live()
        else:
            self._disable_live()

    @Slot()
    def toggleManager(self):
        self._live_is_manager = not self._live_is_manager
        self.liveChanged.emit()

    @Slot()
    def stopLive(self):
        """Called from notifier.stop_live signal."""
        self._disable_live()

    @Slot(str)
    def synchronize(self, mode: str):
        try:
            path = self._store.database().path()
            synchronizer = self._settings.create_synchronizer(mode, path)
            if synchronizer is None:
                return
            info = synchronizer.sync(self._sync_logging)
            if info.updated_definitions():
                self._store.notify_definitions_did_change()
        except Exception as e:
            self.connectionError.emit(str(e))

    # --- Internal
    def _enable_live(self):
        try:
            live_sync = self._settings._get_live_sync_with_source()
            if live_sync:
                path = self._store.database().path()
                self._synchronizer = self._settings.create_synchronizer(
                    CommitSynchronizer.MODE_SYNC, path)

            self._live_enabled = True
            self.liveChanged.emit()
            self._schedule_live_timer()
        except Exception as e:
            self.connectionError.emit(str(e))

    def _disable_live(self):
        self._synchronizer = None
        self._live_enabled = False
        self._live_is_manager = False
        self.liveChanged.emit()

    def _schedule_live_timer(self):
        interval = self._settings._get_live_update_interval()
        interval_ms = interval * 1000.0
        QTimer.singleShot(int(interval_ms), self._live_timer_timeout)

    def _live_timer_timeout(self):
        if not self._live_enabled:
            return

        if self._synchronizer:
            # Synchronous for now (thread version deferred)
            try:
                info = self._synchronizer.sync(self._sync_logging)
                if info and info.updated_definitions():
                    self._store.notify_definitions_did_change()
                self._live_schedule_if_safe_reduce_forward()
            except Exception:
                self._disable_live()
        else:
            self._live_schedule_if_safe_reduce_forward()

    def _live_schedule_if_safe_reduce_forward(self):
        if not self._live_safe_reduce_forward():
            self._disable_live()
        else:
            self._schedule_live_timer()

    def _live_safe_reduce_forward(self) -> bool:
        try:
            if self._live_is_manager:
                self._store.reduce_heads()
            self._store.forward()
            return True
        except Exception:
            return False
