#!/usr/bin/env python3
"""Graph Editor (ge-qml) — entry-point shim.

Thin wrapper that invokes graph_editor/main.py with the right
sys.path setup. Lets users run:

    python3 graph_editor.py [database.graph]

from the repo root, while the actual implementation lives inside
the graph_editor/ subpackage (alongside its Main.qml and assets).

Mirrors the cdbe.py / dbe.py shims in
dsviper-tools-qml.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "graph_editor" / "main.py"

# Make `dsviper_components_qml` importable, plus graph_editor's own
# sibling modules (model, ge, list, render, ...).
sys.path.insert(0, str(HERE / "graph_editor"))
sys.path.insert(0, str(HERE))

runpy.run_path(str(TARGET), run_name="__main__")
