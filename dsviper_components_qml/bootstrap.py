"""Bootstrap — open database from command line or last file settings.

Common startup logic shared by all DS applications.
Accepts any manager with openDatabase(path) via duck typing.
"""
from __future__ import annotations

import os
import sys


def bootstrap_database(manager, settings_mgr=None):
    """Open database from argv[1] or, if settings allow, the last opened file.

    """
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        if os.path.exists(db_path):
            manager.openDatabase(db_path)
    elif settings_mgr is not None:
        if settings_mgr.reopenLastFile:
            last = settings_mgr.lastFileUrl
            if last and os.path.exists(last):
                manager.openDatabase(last)
