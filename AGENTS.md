# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archive Extractor is a Python library and CLI tool that recursively searches for and extracts ZIP, 7z, tar family, and RAR archives within a directory tree. It handles password-protected archives, preserves folder structures, and prevents path traversal attacks via unified security validation.

## Architecture

This is a Python package (`unarch/`) with the following structure:

- **`unarch/__init__.py`**: Public API, CLI entry point, and `FORMAT_HANDLERS` registry
  - `FORMAT_HANDLERS`: Dict mapping file extensions to extractor callables
  - `extract_archives()`: Main library function for programmatic use
  - `list_archives()`: Dry-run archive discovery (no extraction)
  - `__version__`: Package version string from importlib.metadata
  - `main()`: CLI entry point for command-line usage
- **`unarch/__main__.py`**: Enables `python -m unarch`
- **`unarch/core.py`**: Shared utilities
  - `validate_member_path()`: Unified path traversal prevention (used by all extractors)
  - `find_archive_files()`: Archive discovery generator (uses FORMAT_HANDLERS keys)
  - `load_passwords()`: Password file parsing
- **`unarch/zip.py`**: ZIP extractor — password support, per-member validation
- **`unarch/sevenz.py`**: 7z extractor — two-pass (list+validate, then extract), password support
- **`unarch/tar.py`**: Tar extractor — .tar/.tar.gz/.tgz/.tar.bz2/.tbz2/.tar.xz/.txz, symlink skipping
- **`unarch/rar.py`**: RAR extractor — requires `rarfile` package + `unrar` binary, password support
- **`unarch/py.typed`**: PEP 561 marker for type-checker support

## Key Dependencies

- `zipfile` (stdlib): ZIP extraction
- `tarfile` (stdlib): Tar family extraction
- `py7zr`: 7z archive extraction (v1.0+; uses `list()` + `extract()` API, no `read()`)
- `rarfile`: RAR extraction (requires `unrar` system binary)
- `rich`: Progress bars, styled output, and results tables
- `rich-argparse`: Rich-formatted argparse help text
- `lzma` (stdlib): Referenced in exception handling for 7z corruption detection

## Security Model

All extractors use `validate_member_path()` from `core.py` to prevent path traversal:
1. Normalizes the member name with `os.path.normpath()`
2. Rejects absolute paths
3. Rejects paths containing `..` components
4. Resolves the real path and confirms it's still within `output_dir`

7z uses a two-pass approach: list members first (validate), then extract only safe members.

## Supported Formats

| Extension | Format | Password | Notes |
|-----------|--------|----------|-------|
| `.zip` | ZIP | Yes | stdlib |
| `.7z` | 7-Zip | Yes | py7zr |
| `.tar` | Tar | No | stdlib |
| `.tar.gz`, `.tgz` | Tar+Gzip | No | stdlib |
| `.tar.bz2`, `.tbz2` | Tar+Bzip2 | No | stdlib |
| `.tar.xz`, `.txz` | Tar+XZ | No | stdlib |
| `.rar` | RAR | Yes | rarfile + unrar |

## Development Commands

**Run tests**:
```bash
uv run --group dev pytest tests/ -v
```

**Install as a tool**:
```bash
uv tool install .
```

**Run directly**:
```bash
python -m unarch /path/to/search
python -m unarch /path/to/search --passwords passwords.txt
python -m unarch --dry-run /path/to/search
python -m unarch -v /path/to/search
```

**Install in editable mode for development**:
```bash
uv pip install -e .
```

**Library usage**:
```python
from unarch import extract_archives, list_archives, __version__
print(__version__)
archives = list_archives("/path/to/search")
results = extract_archives("/path/to/search", passwords=["pass1", "pass2"])
```

## Important Implementation Notes

- Extracted files are placed in directories named after each archive (without the archive extension)
- Compound extensions (`.tar.gz`, `.tar.bz2`, `.tar.xz`) are matched longest-first in `_get_archive_ext()`
- For password-protected archives, the tool tries each password in sequence and stops at the first successful extraction
- Tar archives don't support passwords — the `passwords` argument is not passed to `extract_tar_archive()`
- RAR extraction requires both the `rarfile` Python package and the `unrar` system binary
- The `extract_archives()` function returns a dictionary mapping archive paths to extraction counts (-1 for failures)

## Test Suite

Tests live in `tests/`. Run with `uv run --group dev pytest tests/ -v`.

- `tests/conftest.py`: Fixtures creating test archives programmatically
- `tests/test_core.py`: `validate_member_path()`, `find_archive_files()`, `load_passwords()`
- `tests/test_zip.py`: ZIP extraction edge cases
- `tests/test_sevenz.py`: 7z extraction
- `tests/test_tar.py`: Tar family extraction, symlink skipping
- `tests/test_rar.py`: RAR import handling
- `tests/test_security.py`: Path traversal rejection for ZIP and tar
- `tests/test_cli.py`: CLI flags (--version, --dry-run, --quiet, --verbose, --passwords)

## README Requirements

README.md must be kept up to date with any significant project changes, including new archive format support, command-line options, or security-related improvements.
