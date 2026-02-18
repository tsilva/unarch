"""Core utilities for archex."""

import os

from rich.console import Console

console = Console()


def validate_member_path(member_name: str, output_dir: str) -> str | None:
    """Return safe absolute path for extraction, or None to skip.

    Args:
        member_name: Archive member filename/path.
        output_dir: Destination directory for extraction.

    Returns:
        Safe absolute path string, or None if the path should be skipped.
    """
    normalized = os.path.normpath(member_name)
    if os.path.isabs(normalized):
        return None
    if ".." in normalized.split(os.sep):
        return None
    target = os.path.join(output_dir, normalized)
    target = os.path.realpath(target)
    if not target.startswith(os.path.realpath(output_dir) + os.sep):
        return None
    return target


def find_archive_files(root_path: str, extensions: set[str] | None = None):
    """Recursively yield paths to archive files under root_path.

    Args:
        root_path: Directory to search, or a single archive file path.
        extensions: Set of lowercase extensions to match (e.g. {'.zip', '.7z'}).
            If None, all supported extensions are used.

    Yields:
        Absolute paths to archive files found.
    """
    from archex import FORMAT_HANDLERS

    if extensions is None:
        extensions = set(FORMAT_HANDLERS.keys())

    if os.path.isfile(root_path):
        name_lower = root_path.lower()
        for ext in extensions:
            if name_lower.endswith(ext):
                yield root_path
                return
        return

    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            fname_lower = fname.lower()
            for ext in extensions:
                if fname_lower.endswith(ext):
                    yield os.path.join(dirpath, fname)
                    break


def load_passwords(password_file: str) -> list[str]:
    """Load passwords from a file, one per line, stripping whitespace.

    Args:
        password_file: Path to a file containing passwords.

    Returns:
        List of password strings.
    """
    with open(password_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]
