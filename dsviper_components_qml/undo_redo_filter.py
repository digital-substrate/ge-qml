"""Undo/Redo event filter — intercepts Ctrl+Z/Shift+Ctrl+Z before QML TextInput.

macOS only. QML TextInput handles Ctrl+Z locally via ShortcutOverride.
This filter blocks it so the CommitStore undo/redo (via menu actions) takes priority.

On Windows, this filter is NOT installed — blocking ShortcutOverride
prevents menu QAction shortcuts from firing entirely.

Exception: when the Python Editor window is active, undo/redo passes through
so TextEdit undo works normally.

Install on QApplication in any app that uses CommitStore with QML TextInput.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QKeySequence, QGuiApplication


class UndoRedoFilter(QObject):
    """Application-level event filter that blocks TextInput local undo/redo.

    Passes undo/redo through when the Python Editor window has focus.
    """

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        try:
            if event.type() in (QEvent.Type.ShortcutOverride, QEvent.Type.KeyPress):
                from PySide6.QtGui import QKeyEvent
                key_event: QKeyEvent = event  # type: ignore[assignment]
                if key_event.matches(QKeySequence.StandardKey.Undo) or \
                   key_event.matches(QKeySequence.StandardKey.Redo):
                    # Let undo/redo pass through in Python Editor window
                    window = QGuiApplication.focusWindow()
                    if window and "Python Editor" in (window.title() or ""):
                        return False
                    event.ignore()
                    return True
            return super().eventFilter(obj, event)
        except (RuntimeError, KeyboardInterrupt):
            return False
