# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This application has its own version line, independent from the `dsviper`
runtime version (declared as a dependency in `requirements.txt`).

## [1.2.0] - 2026-06-17

First standalone release of the Graph Editor (QML port).

### Added
- QML Graph Editor GUI over a Database / CommitDatabase.
- Runs on Python 3.10–3.14; requires dsviper >= 1.2.16.
- Independent version line (`_version.py`), reported via the application
  version and the About panel, decoupled from the `dsviper` runtime.
