"""Settings manager — wraps DSSettings for QML access.

Exposes sync source config and live session settings as QML properties.
"""
from __future__ import annotations

import os
import tempfile

from PySide6.QtCore import QObject, QSettings, Property, Signal, Slot

_DEFAULT_SOCKET_PATH = os.path.join(tempfile.gettempdir(), "commit.sock")


class SettingsManager(QObject):
    """Thin QML wrapper around QSettings — singleton, shared by all DS components."""

    changed = Signal()

    @classmethod
    def instance(cls) -> SettingsManager:
        if not hasattr(cls, "_instance"):
            setattr(cls, "_instance", cls())
        return getattr(cls, "_instance")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._s = QSettings()
        self._register_defaults()

    def _register_defaults(self):
        defaults = {
            "DSSettingsSyncSource": 0,
            "DSSettingsSyncFilePath": "",
            "DSSettingsSyncSocketPath": _DEFAULT_SOCKET_PATH,
            "DSSettingsSyncHostname": "localhost",
            "DSSettingsSyncService": "54321",
            "DSSettingsLiveUpdateInterval": 5,
            "DSSettingsLiveSyncWithSource": False,
            "DSSettingsReopenLastFile": False,
            "DSSettingsLastFileURL": "",
            "DSSettingsConnectHost": "localhost",
            "DSSettingsConnectService": "54321",
            "DSSettingsConnectSocketPath": _DEFAULT_SOCKET_PATH,
            "DSSettingsConnectUseSocketPath": False,
        }
        for k, v in defaults.items():
            if self._s.value(k) is None:
                self._s.setValue(k, v)
        self._s.sync()

    # --- Sync source ---
    def _get_sync_source(self) -> int:
        return int(str(self._s.value("DSSettingsSyncSource", type=int)))

    def _set_sync_source(self, v: int):
        self._s.setValue("DSSettingsSyncSource", v)
        self.changed.emit()

    syncSource = Property(int, _get_sync_source, _set_sync_source, notify=changed)

    def _get_sync_file_path(self) -> str:
        return str(self._s.value("DSSettingsSyncFilePath", type=str))

    def _set_sync_file_path(self, v: str):
        self._s.setValue("DSSettingsSyncFilePath", v)
        self.changed.emit()

    syncFilePath = Property(str, _get_sync_file_path, _set_sync_file_path, notify=changed)

    def _get_sync_socket_path(self) -> str:
        return str(self._s.value("DSSettingsSyncSocketPath", type=str))

    def _set_sync_socket_path(self, v: str):
        self._s.setValue("DSSettingsSyncSocketPath", v)
        self.changed.emit()

    syncSocketPath = Property(str, _get_sync_socket_path, _set_sync_socket_path, notify=changed)

    def _get_sync_hostname(self) -> str:
        return str(self._s.value("DSSettingsSyncHostname", type=str))

    def _set_sync_hostname(self, v: str):
        self._s.setValue("DSSettingsSyncHostname", v)
        self.changed.emit()

    syncHostname = Property(str, _get_sync_hostname, _set_sync_hostname, notify=changed)

    def _get_sync_service(self) -> str:
        return str(self._s.value("DSSettingsSyncService", type=str))

    def _set_sync_service(self, v: str):
        self._s.setValue("DSSettingsSyncService", v)
        self.changed.emit()

    syncService = Property(str, _get_sync_service, _set_sync_service, notify=changed)

    # --- Live session ---
    def _get_live_update_interval(self) -> float:
        return float(str(self._s.value("DSSettingsLiveUpdateInterval", type=int))) / 10.0

    def _set_live_update_interval(self, v: float):
        self._s.setValue("DSSettingsLiveUpdateInterval", int(v * 10))
        self.changed.emit()

    liveUpdateInterval = Property(float, _get_live_update_interval, _set_live_update_interval, notify=changed)

    def _get_live_sync_with_source(self) -> bool:
        return bool(self._s.value("DSSettingsLiveSyncWithSource", type=bool))

    def _set_live_sync_with_source(self, v: bool):
        self._s.setValue("DSSettingsLiveSyncWithSource", v)
        self.changed.emit()

    liveSyncWithSource = Property(bool, _get_live_sync_with_source, _set_live_sync_with_source, notify=changed)

    # --- Reopen last database
    def _get_reopen_last_file(self) -> bool:
        return bool(self._s.value("DSSettingsReopenLastFile", type=bool))

    def _set_reopen_last_file(self, v: bool):
        self._s.setValue("DSSettingsReopenLastFile", v)
        self._s.sync()
        self.changed.emit()

    reopenLastFile = Property(bool, _get_reopen_last_file, _set_reopen_last_file, notify=changed)

    def _get_last_file_url(self) -> str:
        return str(self._s.value("DSSettingsLastFileURL", type=str))

    def _set_last_file_url(self, v: str):
        self._s.setValue("DSSettingsLastFileURL", v)
        self._s.sync()

    lastFileUrl = Property(str, _get_last_file_url, _set_last_file_url, notify=changed)

    # --- Connect To Server
    def _get_connect_hostname(self) -> str:
        return str(self._s.value("DSSettingsConnectHost", type=str))

    def _set_connect_hostname(self, v: str):
        self._s.setValue("DSSettingsConnectHost", v)
        self.changed.emit()

    connectHostname = Property(str, _get_connect_hostname, _set_connect_hostname, notify=changed)

    def _get_connect_service(self) -> str:
        return str(self._s.value("DSSettingsConnectService", type=str))

    def _set_connect_service(self, v: str):
        self._s.setValue("DSSettingsConnectService", v)
        self.changed.emit()

    connectService = Property(str, _get_connect_service, _set_connect_service, notify=changed)

    def _get_connect_socket_path(self) -> str:
        return str(self._s.value("DSSettingsConnectSocketPath", type=str))

    def _set_connect_socket_path(self, v: str):
        self._s.setValue("DSSettingsConnectSocketPath", v)
        self.changed.emit()

    connectSocketPath = Property(str, _get_connect_socket_path, _set_connect_socket_path, notify=changed)

    def _get_connect_use_socket_path(self) -> bool:
        return bool(self._s.value("DSSettingsConnectUseSocketPath", type=bool))

    def _set_connect_use_socket_path(self, v: bool):
        self._s.setValue("DSSettingsConnectUseSocketPath", v)
        self.changed.emit()

    connectUseSocketPath = Property(bool, _get_connect_use_socket_path, _set_connect_use_socket_path, notify=changed)

    # --- Helpers
    def _get_has_source_of_sync(self) -> bool:
        return self._get_sync_source() != 0

    hasSourceOfSync = Property(bool, _get_has_source_of_sync, notify=changed)

    def has_source_of_synchronization(self) -> bool:
        return self._get_sync_source() != 0

    def create_synchronizer(self, mode: str, target_path: str):
        from dsviper import CommitDatabaseSQLite, CommitDatabaseRemote, CommitSynchronizer
        s_source = self._get_sync_source()
        source = None

        if s_source == 0:  # NONE
            return None
        elif s_source == 1:  # FILE
            source = CommitDatabaseSQLite.open(self._get_sync_file_path()).commit_databasing()
        elif s_source == 2:  # SOCKET
            source = CommitDatabaseRemote.connect(self._get_sync_socket_path()).commit_databasing()
        elif s_source == 3:  # HOST
            source = CommitDatabaseRemote.connect(
                self._get_sync_hostname(), self._get_sync_service()).commit_databasing()

        target = CommitDatabaseSQLite.open(target_path)
        return CommitSynchronizer(source, target.commit_databasing(), mode)

    @Slot()
    def save(self):
        self._s.sync()

    @Slot()
    def reload(self):
        """Re-read from disk (cancel edits)."""
        self._s.sync()
        self.changed.emit()

    @Slot(result=str)
    def browseFile(self) -> str:
        from PySide6.QtWidgets import QApplication, QFileDialog
        import os
        parent = QApplication.activeWindow()
        filename, _ = QFileDialog.getOpenFileName(
            parent, "Open Database",
            os.path.expanduser("~/Databases"),
            "All files (*.*)"
        )
        return filename or ""

    @Slot(result=str)
    def browseSocket(self) -> str:
        from PySide6.QtWidgets import QApplication, QFileDialog
        import os
        parent = QApplication.activeWindow()
        filename, _ = QFileDialog.getOpenFileName(
            parent, "Select Socket",
            os.path.expanduser("~/Databases"),
            "Socket files (*.sock);;All files (*.*)"
        )
        return filename or ""
