# Contributing to Digital Substrate QML Tools (ge-qml)

Thanks for your interest in contributing.

## Reporting issues

Use [GitHub Issues](https://github.com/digital-substrate/ge-qml/issues) and pick the appropriate template (bug report or feature request).

## Submitting pull requests

1. Fork the repository and create a feature branch from `main`
2. Make your changes (see "Running locally" below)
3. Verify the app you touched still launches and the flows you changed still work
4. Open a pull request with a clear description of what changed and why

## Running locally

Requires Python 3.10-3.14 and PySide6 with QML support.

```bash
pip install -r requirements.txt          # PySide6 and deps
pip install dsviper                      # Viper Python binding
```

Launch one of the three apps:

```bash
python3 dbe/main.py             # Database Editor
python3 cdbe/main.py            # Commit Database Editor
python3 graph_editor/main.py    # Graph Editor
```

## Architecture

Three QML apps built on a shared `dsviper_components_qml/` library (Python models + QML components). `dsviper` provides persistence and commit operations — don't attempt to port Viper.

- `dbe/` — Database Editor (direct database editing)
- `cdbe/` — Commit Database Editor (adds undo/redo, live mode, sync)
- `graph_editor/` — Graph Editor (adds render canvas, vertex/edge operations, Python editor)

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)). By submitting a pull request, you agree that your contribution is provided under the same license (inbound = outbound). No CLA is required.
