"""dsviper_components_qml — shared QML components for Digital Substrate applications.

Call register_qml_types() once in main() before engine.load() to make
DS QML types available via `import DS 1.0` in QML files.
"""
from __future__ import annotations


def register_qml_types():
    """Register all dsviper_components_qml Python types as QML types under 'DS' module.

    Must be called once, after QApplication creation, before engine.load().
    Equivalent to qmlRegisterType() calls in a C++ QML plugin.
    """
    from PySide6.QtQml import qmlRegisterType

    from dsviper_components_qml.syntax_highlighter import SyntaxHighlighterHelper
    qmlRegisterType(SyntaxHighlighterHelper, "DS", 1, 0, "SyntaxHighlighter")
