# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archive Extractor is a command-line utility that recursively searches for and extracts ZIP and 7z archives within a directory tree. It handles password-protected archives, preserves folder structures, and prevents path traversal attacks.

## Architecture

This is a single-module Python CLI tool (`main.py`) with a straightforward architecture:

- **Entry point**: `main()` function parses arguments and orchestrates archive discovery and extraction
- **Archive discovery**: `find_archive_files()` walks the directory tree to locate .zip and .7z files
- **Extraction logic**: Separate functions for ZIP (`extract_zip()`) and 7z (`extract_7z()`) formats
- **Password handling**: `load_passwords()` reads password lists; extraction functions attempt each password sequentially until success
- **Security**: `sanitize_filename()` prevents directory traversal; extraction functions validate paths with `os.path.normpath()` and reject absolute paths or `..` sequences

## Key Dependencies

- `zipfile` (stdlib): ZIP extraction
- `py7zr`: 7z archive extraction
- `tqdm`: Progress bars during extraction
- `lzma`: Referenced in exception handling for 7z corruption detection (note: currently imported but not directly used due to py7zr wrapping it)

## Development Commands

**Install as a tool**:
```bash
uv tool install .
```

**Run directly**:
```bash
python main.py /path/to/search
python main.py /path/to/search --passwords passwords.txt
```

**Install in editable mode for development**:
```bash
uv pip install -e .
```

## Important Implementation Notes

- Extracted files are placed in directories named after each archive (without the archive extension)
- Path safety is enforced at extraction time: absolute paths and paths containing `..` are skipped
- For password-protected archives, the tool tries each password in sequence and stops at the first successful extraction
- Error handling is intentionally broad (catching generic `Exception`) to ensure the tool continues processing other archives even if one fails
- The `lzma.LZMAError` exception is caught to handle corrupt 7z archives, though `lzma` is no longer a direct dependency (handled internally by py7zr)

## README Requirements

README.md must be kept up to date with any significant project changes, including new archive format support, command-line options, or security-related improvements.
