"""License model — exposes app info and license text to QML.

Shared between dbe, cdbe, graph_editor.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal

VERSION = "1.2.0"
COPYRIGHT = "Copyright (c) 2026 Digital Substrate"
LICENSE_ID = "MIT"


def _get_license_path() -> Path:
    dsviper_components_qml_dir = Path(__file__).parent
    project_dir = dsviper_components_qml_dir.parent
    return project_dir / "LICENSE"


def _get_license_text() -> str:
    license_path = _get_license_path()
    if license_path.exists():
        return license_path.read_text(encoding="utf-8")
    return "License file not found."


class LicenseModel(QObject):
    """Exposes app info and license text to QML."""

    infoChanged = Signal()

    def __init__(self, app_name: str, app_description: str, version: str = VERSION, parent=None):
        super().__init__(parent)
        self._app_name = app_name
        self._app_description = app_description
        self._version = version

    # --- QML Properties ---
    def _get_app_name(self): return self._app_name
    appName = Property(str, _get_app_name, constant=True)

    def _get_app_description(self): return self._app_description
    appDescription = Property(str, _get_app_description, constant=True)

    def _get_version(self): return self._version
    version = Property(str, _get_version, constant=True)

    def _get_copyright(self): return COPYRIGHT
    copyright = Property(str, _get_copyright, constant=True)

    def _get_license_id(self): return LICENSE_ID
    licenseId = Property(str, _get_license_id, constant=True)

    def _get_license_text(self):
        return _get_license_text()
    licenseText = Property(str, _get_license_text, constant=True)
