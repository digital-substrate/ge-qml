"""Commit Admin Model — facade for commit store admin panels.

Encapsulates UndoModel, ActionsModel, ProgramModel, CommitsModel,
LiveModel, BlobModel, InspectModel, UndoRedoFilter, and the manager-notifier
wiring. Applications create one object and call registerContextProperties().

Same principle as DocumentsPanelModel — internal models are private,
the app sees only the facade.

Usage:
    commit_admin = CommitAdminModel(mgr, app, store)
    commit_admin.registerContextProperties(engine)
"""
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from dsviper import CommitStoreNotifying

from dsviper_components_qml.ds_commit_store_notifier import DSCommitStoreNotifier
from dsviper_components_qml.settings_manager import SettingsManager
from dsviper_components_qml.undo_redo_filter import UndoRedoFilter
from dsviper_components_qml.undo_model import UndoModel
from dsviper_components_qml.actions_model import ActionsModel
from dsviper_components_qml.program_model import ProgramModel
from dsviper_components_qml.commits_model import CommitsModel
from dsviper_components_qml.live_model import LiveModel
from dsviper_components_qml.blob_model import BlobModel
from dsviper_components_qml.inspect_model import InspectModel


class CommitAdminModel(QObject):
    """Facade that owns the commit store admin models.

    Receives the store explicitly — no singleton.
    Creates the notifier and wires everything.
    """

    def __init__(self, mgr, app: QApplication, store,
                 on_reset_database=None, parent=None):
        super().__init__(parent)
        settings_mgr = SettingsManager.instance()

        # Create notifier and install on store
        notifier = DSCommitStoreNotifier()
        self._notifier = notifier  # prevent GC
        store.set_notifier(CommitStoreNotifying.create(notifier))

        # Evil — reset_database: app can override (e.g. graph_editor resets Context)
        if on_reset_database is not None:
            notifier.reset_database.connect(on_reset_database)
        else:
            notifier.reset_database.connect(store.reset)

        # UndoRedo filter — intercept Ctrl+Z before QML TextInput (macOS only)
        import sys
        if sys.platform == 'darwin':
            self._undo_redo_filter = UndoRedoFilter(app)
            app.installEventFilter(self._undo_redo_filter)

        # Wire notifier to manager
        notifier.database_did_open.connect(mgr.onDatabaseDidOpen)
        notifier.database_did_close.connect(mgr.onDatabaseDidClose)
        notifier.state_did_change.connect(mgr.onStateDidChange)
        notifier.definitions_did_change.connect(mgr.onDefinitionsDidChange)
        notifier.dispatch_error.connect(mgr.onDispatchError)

        # Wire settings to manager
        mgr.setSettingsManager(settings_mgr)

        # Live model
        self._live_model = LiveModel(settings_mgr)
        self._live_model.set_store(store)
        notifier.stop_live.connect(self._live_model.stopLive)
        notifier.database_did_close.connect(self._live_model.stopLive)
        notifier.database_will_reset.connect(self._live_model.stopLive)

        # Commit admin models — receive store + notifier
        self._undo_model = UndoModel()
        self._undo_model.set_store(store, notifier)
        self._actions_model = ActionsModel()
        self._actions_model.set_store(store, notifier)
        self._program_model = ProgramModel()
        self._program_model.set_store(store, notifier)
        self._commits_model = CommitsModel()
        self._commits_model.set_store(store, notifier)

        # BlobModel — needs mgr as db_manager
        self._blob_model = BlobModel(mgr)

        # InspectModel — pure view, push data via notifier
        self._inspect_model = InspectModel()
        self._inspect_store = store
        notifier.database_did_open.connect(self._push_inspect_open)
        notifier.database_did_close.connect(self._inspect_model.clear)
        notifier.definitions_did_change.connect(self._push_inspect_definitions)

    @property
    def notifier(self):
        return self._notifier

    def _push_inspect_open(self):
        store = self._inspect_store
        if store.has_database():
            db = store.database()
            m = self._inspect_model
            m.set_path(db.path())
            m.set_documentation(db.documentation())
            m.set_uuid(db.uuid().encoded())
            m.set_codec_name(db.codec_name())
            m.set_definitions_hexdigest(db.definitions_hexdigest())
            m.set_definitions(db.definitions())

    def _push_inspect_definitions(self):
        store = self._inspect_store
        if store.has_database():
            self._inspect_model.set_definitions(store.database().definitions())

    def registerContextProperties(self, engine: QQmlApplicationEngine):
        """Expose internal models to QML — same context property names as before."""
        ctx = engine.rootContext()
        ctx.setContextProperty("settingsMgr", SettingsManager.instance())
        ctx.setContextProperty("liveModel", self._live_model)
        ctx.setContextProperty("undoModel", self._undo_model)
        ctx.setContextProperty("actionsModel", self._actions_model)
        ctx.setContextProperty("programModel", self._program_model)
        ctx.setContextProperty("commitsModel", self._commits_model)
        ctx.setContextProperty("blobModel", self._blob_model)
        ctx.setContextProperty("inspectModel", self._inspect_model)
