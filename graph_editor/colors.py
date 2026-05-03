from __future__ import annotations

from PySide6.QtGui import QColor


def background() -> QColor:
    return QColor.fromRgbF(0.160, 0.165, 0.186)


def label() -> QColor:
    return QColor.fromRgbF(0.9, 0.9, 0.9)


def secondary_label() -> QColor:
    return QColor.fromRgbF(0.7, 0.7, 0.7)


def yellow() -> QColor:
    return QColor(248, 216, 74)
