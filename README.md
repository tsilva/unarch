<div align="center">
  <img src="logo.png" alt="archive-extractor" width="512"/>

  # archive-extractor

  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![PyPI](https://img.shields.io/pypi/v/archive-extractor)](https://pypi.org/project/archive-extractor/)

  **📦 Recursively extract ZIP and 7z archives from directory trees, with password support 🔓**

  [Installation](#installation) · [Usage](#usage) · [Security](#security)
</div>

## Overview

archive-extractor is a Python library and CLI tool for bulk extraction of archives nested within directory trees. It discovers and extracts `.zip` and `.7z` files, handles password-protected archives using a wordlist, and includes security measures against path traversal attacks.

Ideal for bulk extraction tasks or forensic analysis where archives may be deeply nested or encrypted.

## Features

- **🔍 Recursive discovery** - Finds all `.zip` and `.7z` files in a directory tree
- **🔓 Password list support** - Tries passwords from a user-provided wordlist
- **🛡️ Path traversal protection** - Sanitizes filenames and rejects unsafe paths
- **📊 Progress indicators** - Shows extraction progress with tqdm
- **📁 Preserves structure** - Extracts each archive into its own named folder
- **📚 Library API** - Use programmatically in your Python projects

## Installation

```bash
uv tool install .
```

Or install in development mode:

```bash
uv pip install -e .
```

## Usage

### 🖥️ CLI

Extract all archives under a directory:

```bash
archive-extractor /path/to/search
```

Extract with a password list (one password per line):

```bash
archive-extractor /path/to/search --passwords passwords.txt
```

Extract to a custom output directory:

```bash
archive-extractor /path/to/search --output-dir /path/to/output
```

Quiet mode (suppress progress output):

```bash
archive-extractor /path/to/search --quiet
```

### 📚 Library

Use archive-extractor programmatically in your Python projects:

```python
from archive_extractor import extract_archives

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

- Archives extract to folders named after the archive file (without extension)
- Success: `Extracted 'archive.7z' to 'archive'.`
- Failure: `Could not extract 'archive.zip': no valid password found or archive is corrupt.`

## Security

archive-extractor includes several protections against malicious archives:

- **Filename sanitization** - Removes illegal characters and `..` sequences
- **Path normalization** - Uses `os.path.normpath()` to resolve paths
- **Absolute path rejection** - Skips members with absolute paths
- **Traversal detection** - Rejects paths that start with `..`

## License

This project is licensed under the [MIT License](LICENSE).
