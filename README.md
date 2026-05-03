# Graph Editor (ge-qml)

QML port of the Digital Substrate graph editor, with an integrated
Python scripting editor.

## Prerequisites

- Python 3.14+

## Installation

```bash
pip install -r requirements.txt
```

This installs `dsviper` (the Viper Python binding, from [PyPI](https://pypi.org/project/dsviper/)) along with `PySide6`.

## Usage

```bash
python3 graph_editor.py [database.graph]
```

## Architecture

```
graph_editor.py             # entry point shim — runs graph_editor/main.py
graph_editor/               # Graph Editor app package
    main.py, Main.qml         (entry point + root QML)
    *.py, *.qml               (models, panels, dialogs)
    ge/, list/, model/,       (graph editor internals)
        render/, scripts/, images/
dsviper_components_qml/     # Shared Python models + QML components
                            # — synced from dsviper-components-qml
                            # via dev/sync_dsviper_components_qml.py
doc/                        # Technical documentation
```

## Updating shared components

The `dsviper_components_qml/` directory is sourced from
`dsviper-components-qml`. To pull updates:

```bash
python3 dev/sync_dsviper_components_qml.py
git diff dsviper_components_qml
git commit -am "sync: bump dsviper-components-qml to vX.Y.Z"
```

End-user workflow: `git clone && python3 graph_editor.py` —
`dsviper_components_qml/` is committed, so no build step is required.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
