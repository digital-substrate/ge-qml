#!/usr/bin/env python3
# Maintainer-only — sync dsviper_components_qml/ from the external
# dsviper-components-qml repository.
# Excluded from any release zip via the `dev/` convention.
#
# Run from the repo root after pulling updates in the sibling repo:
#
#     python3 dev/sync_dsviper_components_qml.py
#     git add dsviper_components_qml
#     git commit -m "sync: bump dsviper-components-qml to vX.Y.Z"
#
# Source resolution (in order):
#   1. $DSVIPER_COMPONENTS_QML — explicit path
#   2. ../dsviper-components-qml — sibling-checkout
#   3. installed wheel `dsviper_components_qml` (QML build) — future PyPI
#
# What gets copied:
#   - *.py (component logic — Python models, controllers, managers)
#   - qml/ (QML components + qmldir)
#   - images/ (PNG icons including @2x retina variants)
#
# What does NOT get copied:
#   - __pycache__/ and bytecode

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PKG = REPO / "dsviper_components_qml"


def resolve_source() -> Path:
    """Resolve the dsviper-components-qml source directory."""
    if env := os.environ.get("DSVIPER_COMPONENTS_QML"):
        candidate = Path(env)
        for c in (candidate / "dsviper_components_qml", candidate):
            if (c / "__init__.py").is_file():
                return c
        sys.exit(
            f"error: $DSVIPER_COMPONENTS_QML={env} does not contain a "
            f"dsviper_components_qml package"
        )

    sibling = REPO.parent / "dsviper-components-qml" / "dsviper_components_qml"
    if (sibling / "__init__.py").is_file():
        return sibling

    spec = importlib.util.find_spec("dsviper_components_qml")
    if spec is not None and spec.origin:
        return Path(spec.origin).resolve().parent

    sys.exit(
        "error: cannot resolve dsviper-components-qml source. "
        "Either checkout dsviper-components-qml alongside this repo "
        "(github.com/digital-substrate/dsviper-components-qml), set "
        "$DSVIPER_COMPONENTS_QML, or pip install dsviper-components-qml."
    )


def sync(src: Path) -> None:
    if PKG.exists():
        shutil.rmtree(PKG)

    def ignore(_dir: str, names: list[str]) -> list[str]:
        del _dir
        return [n for n in names if n == "__pycache__"]

    shutil.copytree(src, PKG, ignore=ignore)


def main() -> None:
    src = resolve_source()
    print(f"Source: {src}")
    print(f"Target: {PKG.relative_to(REPO)}/")
    sync(src)
    n_py = sum(1 for _ in PKG.glob("*.py"))
    n_qml = sum(1 for _ in (PKG / "qml").glob("*.qml")) if (PKG / "qml").is_dir() else 0
    n_img = sum(1 for _ in (PKG / "images").iterdir()) if (PKG / "images").is_dir() else 0
    print(f"Synced: {n_py} *.py, {n_qml} *.qml, {n_img} images.")


if __name__ == "__main__":
    main()
