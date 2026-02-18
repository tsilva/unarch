<p align="center">
  <img src="logo.png" alt="archex" width="200"/>
</p>

<h1 align="center">archex</h1>

<p align="center">
  Recursively extract ZIP, 7z, tar, and RAR archives from directory trees, with password support
</p>

<p align="center">
  <a href="https://pypi.org/project/archex/"><img src="https://img.shields.io/pypi/v/archex" alt="PyPI version"/></a>
  <a href="https://pypi.org/project/archex/"><img src="https://img.shields.io/pypi/pyversions/archex" alt="Python versions"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tsilva/archex" alt="License"/></a>
</p>

## Features

- **Recursive discovery** — finds all supported archives in a directory tree
- **Password list support** — tries passwords from a wordlist for encrypted ZIP, 7z, and RAR archives
- **Path traversal protection** — rejects absolute paths and `..` sequences uniformly across all formats
- **Folder structure preservation** — extracts each archive into its own named subfolder
- **Custom output directory** — extract to a location separate from the source tree
- **Rich progress output** — styled progress indicators and results tables via `rich`
- **Library API** — use programmatically in your own Python projects

## Quick Start

```bash
pip install archex
archex /path/to/search
```

## Installation

Install with `pip`:

```bash
pip install archex
```

Install as an isolated CLI tool with [pipx](https://pipx.pypa.io/):

```bash
pipx install archex
```

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install archex
```

### RAR Support

RAR extraction requires the `unrar` system binary in addition to the `rarfile` Python package:

```bash
# macOS
brew install unrar

# Debian / Ubuntu
apt install unrar
```

## CLI Reference

```
archex [OPTIONS] PATH
```

| Flag | Short | Description |
|------|-------|-------------|
| `--dry-run` | | List archives found without extracting |
| `--passwords FILE` | | Password wordlist (one per line) for encrypted archives |
| `--output-dir DIR` | | Base directory for extraction output |
| `--verbose` | `-v` | Print each file path during extraction |
| `--quiet` | `-q` | Suppress all output |
| `--version` | | Show installed version and exit |

### Examples

```bash
# Preview archives before extracting
archex --dry-run /path/to/search

# Extract with a password wordlist
archex /path/to/search --passwords passwords.txt

# Extract to a custom output directory
archex /path/to/search --output-dir /path/to/output

# Verbose extraction showing each file
archex -v /path/to/search

# Quiet mode (no output)
archex -q /path/to/search

# Show version
archex --version
```

## Library Usage

```python
from archex import extract_archives, list_archives, __version__

# List archives without extracting
archives = list_archives("/path/to/search")
# [{"path": "/path/to/a.zip", "type": "zip", "member_count": 42}, ...]

# Extract all archives in a directory
results = extract_archives("/path/to/search")

# Extract with a password list
results = extract_archives("/path/to/search", passwords=["pass1", "pass2"])

# Extract to a custom output directory
results = extract_archives("/path/to/search", output_dir="/path/to/output")
```

`extract_archives()` returns a dictionary mapping archive paths to extracted file counts. A count of `-1` indicates failure.

## Supported Formats

| Extension | Format | Password Support | Backend |
|-----------|--------|:----------------:|---------|
| `.zip` | ZIP | Yes | stdlib |
| `.7z` | 7-Zip | Yes | py7zr |
| `.tar` | Tar | No | stdlib |
| `.tar.gz`, `.tgz` | Tar + Gzip | No | stdlib |
| `.tar.bz2`, `.tbz2` | Tar + Bzip2 | No | stdlib |
| `.tar.xz`, `.txz` | Tar + XZ | No | stdlib |
| `.rar` | RAR | Yes | rarfile + unrar |

## Security

`archex` enforces path safety uniformly across all formats via `validate_member_path()`:

- **Absolute path rejection** — skips members with absolute paths (e.g. `/etc/passwd`)
- **Traversal detection** — rejects any path containing `..` components
- **Real-path check** — resolves the final path and confirms it stays within the output directory
- **Symlink skipping** — tar archives skip symlink and hardlink members entirely
- **7z two-pass validation** — member paths are listed and validated before extraction begins; only safe members are extracted

## License

This project is licensed under the [MIT License](LICENSE).
