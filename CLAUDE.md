# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archive Extractor is a Python library and CLI tool that recursively searches for and extracts ZIP and 7z archives within a directory tree. It handles password-protected archives, preserves folder structures, and prevents path traversal attacks.

## Architecture

This is a Python package (`archive_extractor/`) with the following structure:

- **`archive_extractor/__init__.py`**: Public API and CLI entry point
  - `extract_archives()`: Main library function for programmatic use
  - `main()`: CLI entry point for command-line usage
- **`archive_extractor/core.py`**: Core extraction logic
  - `sanitize_filename()`: Path security
  - `find_archive_files()`: Archive discovery generator
  - `load_passwords()`: Password file parsing
  - `extract_zip_archive()`: ZIP extraction with password support
  - `extract_7z_archive()`: 7z extraction with password support

## Key Dependencies

- `zipfile` (stdlib): ZIP extraction
- `py7zr`: 7z archive extraction
- `tqdm`: Progress bars during extraction
- `lzma` (stdlib): Referenced in exception handling for 7z corruption detection

## Development Commands

**Install as a tool**:
```bash
uv tool install .
```

**Run directly**:
```bash
python -m archive_extractor /path/to/search
python -m archive_extractor /path/to/search --passwords passwords.txt
```

**Install in editable mode for development**:
```bash
uv pip install -e .
```

**Library usage**:
```python
from archive_extractor import extract_archives
results = extract_archives("/path/to/search", passwords=["pass1", "pass2"])
```

## Important Implementation Notes

- Extracted files are placed in directories named after each archive (without the archive extension)
- Path safety is enforced at extraction time: absolute paths and paths containing `..` are skipped
- For password-protected archives, the tool tries each password in sequence and stops at the first successful extraction
- Error handling is intentionally broad (catching generic `Exception`) to ensure the tool continues processing other archives even if one fails
- The `lzma.LZMAError` exception is caught to handle corrupt 7z archives
- The `extract_archives()` function returns a dictionary mapping archive paths to extraction counts (-1 for failures)

## README Requirements

README.md must be kept up to date with any significant project changes, including new archive format support, command-line options, or security-related improvements.
