<div align="center">
  <img src="logo.png" alt="archive-extractor" width="512"/>

  # archive-extractor

  [![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![PyPI](https://img.shields.io/pypi/v/archive-extractor)](https://pypi.org/project/archive-extractor/)

  **📦 Recursively extract ZIP and 7z archives from directory trees, with password-cracking support**

  [Installation](#installation) · [Usage](#usage) · [Security](#security)
</div>

## Overview

archive-extractor is a command-line tool for bulk extraction of archives nested within directory trees. It discovers and extracts `.zip` and `.7z` files, handles password-protected archives using a wordlist, and includes security measures against path traversal attacks.

Ideal for bulk extraction tasks or forensic analysis where archives may be deeply nested or encrypted.

## Features

- **🔍 Recursive discovery** - Finds all `.zip` and `.7z` files in a directory tree
- **🔓 Password cracking** - Tries passwords from a wordlist against encrypted archives
- **🛡️ Path traversal protection** - Sanitizes filenames and rejects unsafe paths
- **📊 Progress indicators** - Shows extraction progress with tqdm
- **📁 Preserves structure** - Extracts each archive into its own named folder

## Installation

```bash
uv tool install .
```

Or install in development mode:

```bash
uv pip install -e .
```

## Usage

Extract all archives under a directory:

```bash
archive-extractor /path/to/search
```

Extract with a password list (one password per line):

```bash
archive-extractor /path/to/search --passwords passwords.txt
```

### Output

- Archives extract to folders named after the archive file (without extension)
- Success: `✅ Extracted 'archive.7z' to 'archive'.`
- Failure: `❌ Could not extract 'archive.zip': no valid password found.`

## Security

archive-extractor includes several protections against malicious archives:

- **Filename sanitization** - Removes illegal characters and `..` sequences
- **Path normalization** - Uses `os.path.normpath()` to resolve paths
- **Absolute path rejection** - Skips members with absolute paths
- **Traversal detection** - Rejects paths that start with `..`

## License

This project is licensed under the [MIT License](LICENSE).
