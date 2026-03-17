<p align="center">
  <img src="https://raw.githubusercontent.com/tsilva/unarch/main/logo.png" alt="unarch" width="512" />
</p>

<h1 align="center">unarch</h1>

<p align="center">
  Recursively extract ZIP, 7z, tar, RAR, and single-file compressed archives from directory trees
</p>

<p align="center">
  <a href="https://pypi.org/project/unarch/"><img src="https://img.shields.io/pypi/v/unarch" alt="PyPI version"/></a>
  <a href="https://pypi.org/project/unarch/"><img src="https://img.shields.io/pypi/pyversions/unarch" alt="Python versions"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tsilva/unarch" alt="License"/></a>
</p>

## Features

[![CI](https://github.com/tsilva/unarch/actions/workflows/release.yml/badge.svg)](https://github.com/tsilva/unarch/actions/workflows/release.yml)

- **Recursive discovery** — finds all supported archives in a directory tree
- **Password list support** — tries passwords from a wordlist for encrypted ZIP, 7z, and RAR archives
- **Path traversal protection** — rejects absolute paths and `..` sequences uniformly across all formats
- **Folder structure preservation** — extracts each archive into its own named subfolder
- **Single-file compression support** — extracts `.gz`, `.bz2`, and `.xz` payloads without shelling out
- **Custom output directory** — extract to a location separate from the source tree
- **Configurable output naming** — append a suffix and skip archives whose destination is already populated
- **Rich progress output** — styled progress indicators and results tables via `rich`
- **Library API** — use programmatically in your own Python projects

## Quick Start

```bash
pip install unarch
unarch /path/to/search
```

## Installation

Install with `pip`:

```bash
pip install unarch
```

Install as an isolated CLI tool with [pipx](https://pipx.pypa.io/):

```bash
pipx install unarch
```

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install unarch
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
unarch [OPTIONS] PATH
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
unarch --dry-run /path/to/search

# Extract with a password wordlist
unarch /path/to/search --passwords passwords.txt

# Extract to a custom output directory
unarch /path/to/search --output-dir /path/to/output

# Verbose extraction showing each file
unarch -v /path/to/search

# Quiet mode (no output)
unarch -q /path/to/search

# Show version
unarch --version
```

## Library Usage

```python
from unarch import extract_archives, list_archives, __version__

# List archives without extracting
archives = list_archives("/path/to/search")
# [{"path": "/path/to/a.zip", "type": "zip", "member_count": 42}, ...]

# Extract all archives in a directory
results = extract_archives("/path/to/search")

# Extract with a password list
results = extract_archives("/path/to/search", passwords=["pass1", "pass2"])

# Extract to a custom output directory
results = extract_archives("/path/to/search", output_dir="/path/to/output")

# Match existing destination naming conventions
results = extract_archives(
    "/path/to/search",
    output_dir="/path/to/output",
    output_suffix="_archive",
    skip_existing=True,
)
```

`extract_archives()` returns a dictionary mapping archive paths to extracted file counts. A count of `-1` indicates failure.

## Supported Formats

| Extension | Format | Password Support | Backend |
|-----------|--------|:----------------:|---------|
| `.zip` | ZIP | Yes | stdlib |
| `.7z` | 7-Zip | Yes | py7zr |
| `.tar` | Tar | No | stdlib |
| `.tar.gz`, `.tgz` | Tar + Gzip | No | stdlib |
| `.tar.bz2`, `.tbz2`, `.tbz` | Tar + Bzip2 | No | stdlib |
| `.tar.xz`, `.txz` | Tar + XZ | No | stdlib |
| `.gz` | Gzip-compressed file | No | stdlib |
| `.bz2` | Bzip2-compressed file | No | stdlib |
| `.xz` | XZ-compressed file | No | stdlib |
| `.rar` | RAR | Yes | rarfile + unrar |

## Security

`unarch` enforces path safety uniformly across all formats via `validate_member_path()`:

- **Absolute path rejection** — skips members with absolute paths (e.g. `/etc/passwd`)
- **Traversal detection** — rejects any path containing `..` components
- **Real-path check** — resolves the final path and confirms it stays within the output directory
- **Symlink skipping** — tar archives skip symlink and hardlink members entirely
- **7z two-pass validation** — member paths are listed and validated before extraction begins; only safe members are extracted

## License

This project is licensed under the [MIT License](LICENSE).
