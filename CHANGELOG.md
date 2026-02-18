# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-18

### Added

- `python -m archex` now works via new `__main__.py` entry point
- `__version__` attribute for runtime version introspection
- `--version` / `-V` flag to display the installed version
- `--dry-run` / `-n` flag to list archives without extracting
- `--verbose` / `-v` flag to print each file path as it is extracted
- `list_archives()` public API function for programmatic archive discovery
- Rich-styled CLI output: colour-coded success/failure messages and extraction summary table
- Rich-styled help text via `rich-argparse`
- `py.typed` PEP 561 marker for type-checker support
- PyPI classifiers and `keywords` metadata

### Changed

- Replaced `tqdm` progress bars with `rich.progress` for consistent styling
- Fixed installation instructions: `pip install archex` is now the primary method
- Fixed project description: "password-cracking" → "password list support"
- Relaxed Python requirement from `>=3.12` to `>=3.10`

## [0.2.0] - 2024-12-01

### Added

- Library API: `extract_archives()` returns `dict[str, int]` mapping archive paths to file counts
- `--output-dir` CLI flag to specify a custom base extraction directory
- `--quiet` / `-q` flag to suppress all output

### Changed

- Refactored project structure and updated documentation

## [0.1.0] - 2024-11-01

### Added

- Initial release
- Recursive ZIP and 7z archive discovery and extraction
- Password list support for encrypted archives
- Path traversal protection
- Progress bars via tqdm
