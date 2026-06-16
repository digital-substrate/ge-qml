#!/usr/bin/env python3
"""graph_editor.py — Graph Editor (QML port).

QML equivalent of the graph_editor.py app in ge-py.
Uses Context singleton (CommitStore + graph_key).
Adds undo/redo, commit navigation, live mode, graph operations.

Run:
    python3 main.py [database.graph]
"""
import os
import sys
from pathlib import Path

# Add project root so dsviper_components_qml is importable, and script dir for local models
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

from PySide6.QtCore import QObject, QUrl, QTimer, Signal, Property, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine


class _ModifierHelper(QObject):
    """Poll keyboard modifiers and expose to QML"""

    modifierChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = -1
        self._timer = QTimer(self)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._poll)
        self._timer.start()

    def _poll(self):
        modifiers = QGuiApplication.queryKeyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            key = Qt.Key.Key_Control
        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            key = Qt.Key.Key_Shift
        elif modifiers & Qt.KeyboardModifier.AltModifier:
            key = Qt.Key.Key_Alt
        else:
            key = -1
        if key != self._current:
            self._current = key
            self.modifierChanged.emit()

    def _get_current_modifier(self) -> int:
        return self._current

    currentModifier = Property(int, _get_current_modifier, notify=modifierChanged)


from model.context import Context

from dsviper_components_qml.commit_admin_model import CommitAdminModel
from dsviper_components_qml.documents_panel_model import DocumentsPanelModel
from dsviper_components_qml.license_model import LicenseModel
from _version import __version__
from dsviper_components_qml.about_qt_helper import AboutQtHelper
from dsviper_components_qml.bootstrap import bootstrap_database
from dsviper_components_qml import register_qml_types

# graph_editor-specific models
from context_manager import ContextManager
from title_model import TitleModel
from statistics_model import StatisticsModel
from tags_model import TagsModel
from comments_model import CommentsModel
from list_model import ListModel
from vertex_model import VertexModel
from render_model import RenderModel
from select_graph_model import SelectGraphModel


def main():
    context = Context.instance()

    app = QApplication(sys.argv)
    app.setOrganizationName("DigitalSubstrate")
    app.setApplicationName("GraphEditor")
    app.setApplicationVersion(__version__)
    from PySide6.QtGui import QIcon
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "images" / "app_icon.png")))
    engine = QQmlApplicationEngine()

    # Core: context manager wraps Context.instance()
    mgr = ContextManager()

    # Commit admin — black box, owns notifier setup + settings + undo/actions/program/commits/live/blobs/inspect
    commit_admin = CommitAdminModel(mgr, app, context.store,
                                    on_reset_database=context.reset)
    commit_admin.registerContextProperties(engine)

    # Documents panel — black box, owns abstraction/key/document/nav
    documents_panel = DocumentsPanelModel(mgr, commit_mode=True)
    documents_panel.registerContextProperties(engine)

    # Models: graph_editor-specific components — receive notifier from facade
    notifier = commit_admin.notifier
    title_model = TitleModel(notifier)
    statistics_model = StatisticsModel(notifier)
    tags_model = TagsModel(notifier)
    comments_model = CommentsModel(notifier)
    list_model = ListModel(notifier)
    vertex_model = VertexModel(notifier)
    render_model = RenderModel(notifier)
    render_model.inspectKey.connect(documents_panel.navigateToKey)

    # Expose to QML
    ctx = engine.rootContext()
    ctx.setContextProperty("contextManager", mgr)
    ctx.setContextProperty("storeMgr", mgr)  # alias for shared dsviper_components_qml (CommitToolBar, ErrorDialog)
    ctx.setContextProperty("titleModel", title_model)
    ctx.setContextProperty("statisticsModel", statistics_model)
    ctx.setContextProperty("tagsModel", tags_model)
    ctx.setContextProperty("graphCommentsModel", comments_model)
    ctx.setContextProperty("listModel", list_model)
    ctx.setContextProperty("vertexModel", vertex_model)
    ctx.setContextProperty("renderModel", render_model)
    select_graph_model = SelectGraphModel()
    ctx.setContextProperty("selectGraphModel", select_graph_model)
    license_model = LicenseModel("Graph Editor", "Graph Editor for Digital Substrate databases", version=__version__)
    ctx.setContextProperty("licenseModel", license_model)
    about_qt_helper = AboutQtHelper()
    ctx.setContextProperty("aboutQtHelper", about_qt_helper)
    modifier_helper = _ModifierHelper()
    ctx.setContextProperty("modifierHelper", modifier_helper)

    ctx.setContextProperty("appPid", os.getpid())

    # Python Editor model — inject Context into namespace
    from dsviper_components_qml.python_editor_model import PythonEditorModel
    scripts_folder = str(Path(__file__).parent / "scripts")
    python_editor_model = PythonEditorModel(scripts_folder, namespace_vars={
        "ctx": context,
        "render_model": render_model,
        "_documents_panel": documents_panel,
    })
    ctx.setContextProperty("pythonEditorModel", python_editor_model)

    register_qml_types()
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "Main.qml")))
    if not engine.rootObjects():
        return 1

    from dsviper_components_qml.settings_manager import SettingsManager
    bootstrap_database(mgr, SettingsManager.instance())

    # Run main_init.py
    python_editor_model.runInitScript()

    result = app.exec()
    # Destroy QML engine before Python objects — prevents teardown TypeError
    del engine
    return result


if __name__ == "__main__":
    sys.exit(main())
