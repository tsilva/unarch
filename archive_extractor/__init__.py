"""Archive Extractor - Recursively extract ZIP and 7z archives.

CLI Usage:
    archive-extractor /path/to/search
    archive-extractor /path/to/search --passwords passwords.txt
    archive-extractor --dry-run /path/to/search
    archive-extractor -v /path/to/search

Library Usage:
    from archive_extractor import extract_archives, list_archives

    # Extract all archives in a directory
    results = extract_archives("/path/to/search")

    # Dry-run: list archives without extracting
    archives = list_archives("/path/to/search")

    # With passwords
    results = extract_archives("/path/to/search", passwords=["pass1", "pass2"])

    # Custom output directory
    results = extract_archives("/path/to/search", output_dir="/path/to/output")

    # Silent mode (no progress bars)
    results = extract_archives("/path/to/search", show_progress=False)
"""

import argparse
import os
import zipfile
from importlib.metadata import version, PackageNotFoundError

import py7zr
from rich.console import Console
from rich.table import Table
from rich_argparse import RichHelpFormatter

from .core import (
    find_archive_files,
    load_passwords,
    extract_zip_archive,
    extract_7z_archive,
)

try:
    __version__ = version("archive-extractor")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = ["extract_archives", "list_archives", "__version__"]

console = Console()


def _count_members(archive_path: str) -> int | None:
    """Count members in an archive without extracting. Returns None on failure."""
    ext = os.path.splitext(archive_path)[1].lower()
    try:
        if ext == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zf:
                return len([m for m in zf.infolist() if not m.is_dir()])
        elif ext == ".7z":
            with py7zr.SevenZipFile(archive_path, mode="r") as zf:
                return len(zf.getnames())
    except Exception:
        return None
    return None


def list_archives(path: str) -> list[dict]:
    """List all archives found at the given path without extracting.

    Args:
        path: Single archive file or directory to search for archives.

    Returns:
        List of dicts with keys: path, type, member_count (or None on error).
    """
    results = []
    for archive_path in find_archive_files(path):
        ext = os.path.splitext(archive_path)[1].lower().lstrip(".")
        member_count = _count_members(archive_path)
        results.append({"path": archive_path, "type": ext, "member_count": member_count})
    return results


def extract_archives(
    path: str,
    output_dir: str | None = None,
    passwords: list[str] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
) -> dict[str, int]:
    """Extract all archives found at the given path.

    Args:
        path: Single archive file or directory to search for archives.
        output_dir: Optional base directory for extraction output.
            If None, each archive extracts to a sibling directory named after the archive.
        passwords: Optional list of password strings to try for encrypted archives.
        show_progress: Whether to show progress bars during extraction.
        verbose: Whether to print each extracted file path.

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
            count = extract_zip_archive(archive_path, dest_dir, passwords, show_progress, verbose)
        elif ext == ".7z":
            count = extract_7z_archive(archive_path, dest_dir, passwords, show_progress, verbose)
        else:
            continue

        results[archive_path] = count

        if show_progress:
            if count >= 0:
                console.print(
                    f"[green]Extracted[/green] '{archive_path}' [dim]to[/dim] '{dest_dir}' [dim]({count} files)[/dim]"
                )
            else:
                console.print(
                    f"[red]Failed[/red] '{archive_path}' [dim]— no valid password or corrupt archive[/dim]"
                )

    if show_progress and results:
        table = Table(title="Extraction Results")
        table.add_column("Archive", style="cyan")
        table.add_column("Files", justify="right")
        table.add_column("Status")
        for archive_path, count in results.items():
            name = os.path.basename(archive_path)
            if count >= 0:
                table.add_row(name, str(count), "[green]Success[/green]")
            else:
                table.add_row(name, "-1", "[red]Failed[/red]")
        console.print(table)

    return results


def main():
    """CLI entry point for archive-extractor."""
    parser = argparse.ArgumentParser(
        prog="archive-extractor",
        description="Recursively extract all files from .zip and .7z archives under a given path.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "path",
        help="Root directory or file to search for .zip/.7z files",
    )
    parser.add_argument(
        "--passwords",
        help="Path to a file containing passwords (one per line) to try for encrypted archives",
    )
    parser.add_argument(
        "--output-dir",
        help="Base directory for extraction output (default: sibling directory of each archive)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print each extracted file path",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="List archives that would be extracted without extracting them",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    verbose = args.verbose and not args.quiet
    show_progress = not args.quiet

    passwords = load_passwords(args.passwords) if args.passwords else None

    if args.dry_run:
        archives = list_archives(args.path)
        if not archives:
            console.print("[yellow]No archives found.[/yellow]")
            return

        table = Table(title="Archives Found")
        table.add_column("Type", style="cyan", justify="center")
        table.add_column("Path", style="white")
        table.add_column("Files", justify="right")
        for entry in archives:
            count = str(entry["member_count"]) if entry["member_count"] is not None else "?"
            table.add_row(entry["type"], entry["path"], count)
        console.print(table)
        console.print(f"Found [bold]{len(archives)}[/bold] archive(s).")
        return

    extract_archives(
        args.path,
        output_dir=args.output_dir,
        passwords=passwords,
        show_progress=show_progress,
        verbose=verbose,
    )
