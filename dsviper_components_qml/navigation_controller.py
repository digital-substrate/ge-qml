"""Navigation controller — QObject wrapper for back/forward navigation.

Exposed to QML as context property for button enabled bindings.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from .navigation import Navigation


class NavigationController(QObject):
    """Manages back/forward navigation stack, exposed to QML."""

    navigationChanged = Signal()
    # Emitted when navigation triggers a key change — (key, attachment, path)
    navigateTo = Signal(object, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._navigation: Navigation | None = None

    def _get_can_go_back(self) -> bool:
        return self._navigation is not None and self._navigation.can_go_back

    canGoBack = Property(bool, _get_can_go_back, notify=navigationChanged)

    def _get_can_go_forward(self) -> bool:
        return self._navigation is not None and self._navigation.can_go_forward

    canGoForward = Property(bool, _get_can_go_forward, notify=navigationChanged)

    @Slot()
    def goBack(self):
        if not self._get_can_go_back():
            return
        self._navigation.go_back()
        location = self._navigation.current_location
        self.navigateTo.emit(location.key, location.attachment, location.path)
        self.navigationChanged.emit()

    @Slot()
    def goForward(self):
        if not self._get_can_go_forward():
            return
        self._navigation.go_forward()
        location = self._navigation.current_location
        self.navigateTo.emit(location.key, location.attachment, location.path)
        self.navigationChanged.emit()

    def updateLocation(self, key, attachment, path):
        """Update current location's attachment and path (called when user browses tree)."""
        if self._navigation is not None:
            location = self._navigation.current_location
            if location and location.key == key:
                location.attachment = attachment
                location.path = path

    def pushJump(self, from_key, from_attachment, from_path, to_key):
        """Push a jump-to-key navigation entry.

        """
        if self._navigation is None:
            self._navigation = Navigation(from_key, from_attachment, from_path)
        elif self._navigation.current_index == 0:
            self._navigation = Navigation(from_key, from_attachment, from_path)

        # Update current location
        location = self._navigation.current_location
        if location.key == from_key:
            location.attachment = from_attachment
            location.path = from_path

        self._navigation.push(to_key, None, None)
        self.navigationChanged.emit()

    def reset(self):
        """Clear navigation on abstraction change or database close."""
        self._navigation = None
        self.navigationChanged.emit()
