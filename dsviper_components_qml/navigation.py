"""Navigation — back/forward stack for key browsing.

Pure data structure, no UI dependency.
"""
from __future__ import annotations


class Navigation:
    """Back/forward stack for key + attachment + path locations."""

    class Location:

        def __init__(self, key, attachment=None, path=None):
            self.key = key
            self.attachment = attachment
            self.path = path

    def __init__(self, key, attachment=None, path=None):
        location = Navigation.Location(key, attachment, path)
        self._locations: list[Navigation.Location] = [location]
        self._current_index = 0

    @property
    def can_go_back(self) -> bool:
        return self._current_index != 0

    def go_back(self):
        self._current_index -= 1

    @property
    def can_go_forward(self) -> bool:
        return self._current_index < len(self._locations) - 1

    def go_forward(self):
        self._current_index += 1

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_location(self) -> Navigation.Location:
        return self._locations[self._current_index]

    def push(self, key, attachment=None, path=None):
        """Push a new location, truncating forward history.

        """
        if self._current_index != len(self._locations) - 1:
            self._locations[self._current_index + 1:] = []

        location = Navigation.Location(key, attachment, path)
        self._locations.append(location)
        self._current_index = len(self._locations) - 1
