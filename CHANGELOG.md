# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This application has its own version line, independent from the `dsviper`
runtime version (declared as a dependency in `requirements.txt`).

## [1.2.1] - 2026-06-16

### Fixed
- Corrected the declared supported Python range from "3.14+" to "3.10-3.14";
  the application already ran on 3.10.

### Changed
- The application version is now tracked independently of the `dsviper`
  runtime version.

## [1.2.0] - 2026-05-03

### Added
- First standalone release of the Graph Editor (QML).
