"""Archive Extractor - Recursively extract ZIP and 7z archives.

CLI Usage:
    archive-extractor /path/to/search
    archive-extractor /path/to/search --passwords passwords.txt

Library Usage:
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
"""

import argparse
import os

from .core import (
    find_archive_files,
    load_passwords,
    extract_zip_archive,
    extract_7z_archive,
)

__all__ = ["extract_archives"]


def extract_archives(
    path: str,
    output_dir: str | None = None,
    passwords: list[str] | None = None,
    show_progress: bool = True
) -> dict[str, int]:
    """Extract all archives found at the given path.

    Args:
        path: Single archive file or directory to search for archives.
        output_dir: Optional base directory for extraction output.
            If None, each archive extracts to a sibling directory named after the archive.
        passwords: Optional list of password strings to try for encrypted archives.
        show_progress: Whether to show progress bars during extraction.

    Returns:
        Dictionary mapping archive paths to extraction counts.
        A count of -1 indicates extraction failure.
    """
    results = {}

    for archive_path in find_archive_files(path):
        if output_dir:
            archive_name = os.path.splitext(os.path.basename(archive_path))[0]
            dest_dir = os.path.join(output_dir, archive_name)
        else:
            dest_dir = os.path.splitext(archive_path)[0]

        ext = os.path.splitext(archive_path)[1].lower()

        if ext == ".zip":
            count = extract_zip_archive(archive_path, dest_dir, passwords, show_progress)
        elif ext == ".7z":
            count = extract_7z_archive(archive_path, dest_dir, passwords, show_progress)
        else:
            continue

        results[archive_path] = count

        if show_progress:
            if count >= 0:
                print(f"Extracted '{archive_path}' to '{dest_dir}'.")
            else:
                print(f"Could not extract '{archive_path}': no valid password found or archive is corrupt.")

    return results


def main():
    """CLI entry point for archive-extractor."""
    parser = argparse.ArgumentParser(
        description="Recursively extract all files from .zip and .7z archives under a given path."
    )
    parser.add_argument(
        "path",
        help="Root directory or file to search for .zip/.7z files"
    )
    parser.add_argument(
        "--passwords",
        help="Path to a file containing passwords (one per line) to try for encrypted archives"
    )
    parser.add_argument(
        "--output-dir",
        help="Base directory for extraction output (default: sibling directory of each archive)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    args = parser.parse_args()

    passwords = load_passwords(args.passwords) if args.passwords else None

    extract_archives(
        args.path,
        output_dir=args.output_dir,
        passwords=passwords,
        show_progress=not args.quiet
    )
