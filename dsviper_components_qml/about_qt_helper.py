"""Helper to expose QApplication.aboutQt() to QML."""
from __future__ import annotations

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication


class AboutQtHelper(QObject):
    """Exposes QApplication.aboutQt() as a QML-callable slot."""

    @Slot()
    def showAboutQt(self):
        app = QApplication.instance()
        if app is not None:
            app.aboutQt()  # type: ignore[attr-defined]
