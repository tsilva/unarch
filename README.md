<div align="center">
  <img src="logo.png" alt="archive-extractor" width="512"/>

  # archive-extractor

  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![PyPI](https://img.shields.io/pypi/v/archive-extractor)](https://pypi.org/project/archive-extractor/)
  [![CI](https://github.com/tsilva/archive-extractor/actions/workflows/release.yml/badge.svg)](https://github.com/tsilva/archive-extractor/actions/workflows/release.yml)

  **📦 Recursively extract ZIP and 7z archives from directory trees, with password support 🔓**

  [Installation](#installation) · [Usage](#usage) · [Security](#security) · [Changelog](CHANGELOG.md)
</div>

## Overview

archive-extractor is a Python library and CLI tool for bulk extraction of archives nested within directory trees. It discovers and extracts `.zip` and `.7z` files, handles password-protected archives using a wordlist, and includes security measures against path traversal attacks.

Ideal for bulk extraction tasks or forensic analysis where archives may be deeply nested or encrypted.

## Features

- **🔍 Recursive discovery** - Finds all `.zip` and `.7z` files in a directory tree
- **🔓 Password list support** - Tries passwords from a user-provided wordlist
- **🛡️ Path traversal protection** - Sanitizes filenames and rejects unsafe paths
- **📊 Rich progress indicators** - Shows styled extraction progress and results tables
- **📁 Preserves structure** - Extracts each archive into its own named folder
- **📚 Library API** - Use programmatically in your Python projects

## Installation

```bash
pip install archive-extractor
```

Or with [pipx](https://pipx.pypa.io/) (recommended for CLI tools):

```bash
pipx install archive-extractor
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install archive-extractor
```

## Usage

### 🖥️ CLI

```bash
archive-extractor /path/to/search
```

You can also run it as a Python module:

```bash
python -m archive_extractor /path/to/search
```

#### CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--passwords FILE` | | Password wordlist (one per line) for encrypted archives |
| `--output-dir DIR` | | Base directory for extraction output |
| `--dry-run` | `-n` | List archives found without extracting |
| `--verbose` | `-v` | Print each file path during extraction |
| `--quiet` | `-q` | Suppress all output |
| `--version` | `-V` | Show installed version and exit |

#### Examples

```bash
# Preview archives before extracting
archive-extractor --dry-run /path/to/search

# Extract with a password wordlist
archive-extractor /path/to/search --passwords passwords.txt

# Extract to a custom output directory
archive-extractor /path/to/search --output-dir /path/to/output

# Verbose extraction showing each file
archive-extractor -v /path/to/search

# Quiet mode (no output)
archive-extractor -q /path/to/search
```

### 📚 Library

Use archive-extractor programmatically in your Python projects:

```python
from archive_extractor import extract_archives, list_archives, __version__

# Print installed version
print(__version__)  # e.g. "0.3.0"

# List archives without extracting
archives = list_archives("/path/to/search")
# [{"path": "/path/to/a.zip", "type": "zip", "member_count": 42}, ...]

# Extract all archives in a directory
results = extract_archives("/path/to/search")

# Extract a single archive
results = extract_archives("/path/to/archive.zip")

# With passwords
results = extract_archives("/path/to/search", passwords=["pass1", "pass2"])

# Custom output directory
results = extract_archives("/path/to/search", output_dir="/path/to/output")

# Silent mode (no progress bars)
results = extract_archives("/path/to/search", show_progress=False)
```

The `extract_archives()` function returns a dictionary mapping archive paths to extraction counts (-1 indicates failure).

### Output

Archives extract to folders named after the archive file (without extension). The CLI prints colour-coded results:

- Success: `Extracted 'archive.7z' to 'archive' (18 files)`
- Failure: `Failed 'encrypted.zip' — no valid password or corrupt archive`

A summary table is shown after all archives are processed.

## Security

archive-extractor includes several protections against malicious archives:

- **Filename sanitization** - Removes illegal characters and `..` sequences
- **Path normalization** - Uses `os.path.normpath()` to resolve paths
- **Absolute path rejection** - Skips members with absolute paths
- **Traversal detection** - Rejects paths that start with `..`

## License

This project is licensed under the [MIT License](LICENSE).
