"""unarch - Recursively extract ZIP, 7z, tar, and RAR archives.

CLI Usage:
    unarch /path/to/search
    unarch /path/to/search --passwords passwords.txt
    unarch --dry-run /path/to/search
    unarch -v /path/to/search

Library Usage:
    from unarch import extract_archives, list_archives

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
import tarfile
import zipfile
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version

import py7zr
from rich.console import Console
from rich.table import Table
from rich_argparse import RichHelpFormatter

from .core import find_archive_files, load_passwords
from .compressed import extract_compressed_file
from .rar import extract_rar_archive
from .sevenz import extract_7z_archive
from .tar import extract_tar_archive
from .zip import extract_zip_archive

try:
    __version__ = version("unarch")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = ["extract_archives", "list_archives", "__version__", "FORMAT_HANDLERS"]

console = Console()

FORMAT_HANDLERS: dict[str, Callable] = {
    ".zip": extract_zip_archive,
    ".7z": extract_7z_archive,
    ".tar": extract_tar_archive,
    ".tgz": extract_tar_archive,
    ".tar.gz": extract_tar_archive,
    ".tar.bz2": extract_tar_archive,
    ".tbz2": extract_tar_archive,
    ".tbz": extract_tar_archive,
    ".tar.xz": extract_tar_archive,
    ".txz": extract_tar_archive,
    ".gz": extract_compressed_file,
    ".bz2": extract_compressed_file,
    ".xz": extract_compressed_file,
    ".rar": extract_rar_archive,
}


def _get_archive_ext(archive_path: str) -> str | None:
    """Return the matched extension from FORMAT_HANDLERS, or None."""
    name_lower = archive_path.lower()
    # Check compound extensions first (longest match wins)
    for ext in sorted(FORMAT_HANDLERS.keys(), key=len, reverse=True):
        if name_lower.endswith(ext):
            return ext
    return None


def _get_archive_type_label(archive_path: str) -> str:
    """Return a human-readable archive type label."""
    ext = _get_archive_ext(archive_path)
    if ext is None:
        return "unknown"
    return ext.lstrip(".")


def _count_members(archive_path: str) -> int | None:
    """Count members in an archive without extracting. Returns None on failure."""
    ext = _get_archive_ext(archive_path)
    try:
        if ext == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zf:
                return len([m for m in zf.infolist() if not m.is_dir()])
        elif ext == ".7z":
            with py7zr.SevenZipFile(archive_path, mode="r") as zf:
                return len([m for m in zf.list() if not m.is_directory])
        elif ext in (".tar", ".tgz", ".tar.gz", ".tar.bz2", ".tbz2", ".tbz", ".tar.xz", ".txz"):
            with tarfile.open(archive_path, "r:*") as tf:
                return len([m for m in tf.getmembers() if m.isfile()])
        elif ext in (".gz", ".bz2", ".xz"):
            return 1
        elif ext == ".rar":
            try:
                import rarfile
                with rarfile.RarFile(archive_path, "r") as rf:
                    return len([m for m in rf.infolist() if not m.is_dir()])
            except Exception:
                return None
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
        type_label = _get_archive_type_label(archive_path)
        member_count = _count_members(archive_path)
        results.append({"path": archive_path, "type": type_label, "member_count": member_count})
    return results


def _base_without_archive_extension(archive_path: str) -> str:
    """Return the path without the matched archive extension."""
    ext = _get_archive_ext(archive_path)
    if ext is None:
        return archive_path
    return archive_path[: -len(ext)]


def extract_archives(
    path: str,
    output_dir: str | None = None,
    passwords: list[str] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
    output_suffix: str = "",
    skip_existing: bool = False,
) -> dict[str, int]:
    """Extract all archives found at the given path.

    Args:
        path: Single archive file or directory to search for archives.
        output_dir: Optional base directory for extraction output.
            If None, each archive extracts to a sibling directory named after the archive.
        passwords: Optional list of password strings to try for encrypted archives.
        show_progress: Whether to show progress bars during extraction.
        verbose: Whether to print each extracted file path.
        output_suffix: Optional suffix appended to each output directory name.
        skip_existing: If True, return 0 for archives whose output directory already
            exists and is non-empty.

    Returns:
        Dictionary mapping archive paths to extraction counts.
        A count of -1 indicates extraction failure.
    """
    results = {}

    for archive_path in find_archive_files(path):
        ext = _get_archive_ext(archive_path)
        if ext is None:
            continue

        base = _base_without_archive_extension(archive_path)

        if output_dir:
            archive_name = os.path.basename(base) + output_suffix
            dest_dir = os.path.join(output_dir, archive_name)
        else:
            dest_dir = base + output_suffix

        if skip_existing and os.path.isdir(dest_dir):
            try:
                has_entries = next(os.scandir(dest_dir), None) is not None
            except OSError:
                has_entries = False
            if has_entries:
                results[archive_path] = 0
                continue

        handler = FORMAT_HANDLERS[ext]

        # Tar archives don't support passwords — don't pass them
        if ext in (".tar", ".tgz", ".tar.gz", ".tar.bz2", ".tbz2", ".tbz", ".tar.xz", ".txz"):
            count = handler(archive_path, dest_dir, show_progress=show_progress, verbose=verbose)
        else:
            count = handler(archive_path, dest_dir, passwords=passwords, show_progress=show_progress, verbose=verbose)

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
    """CLI entry point for unarch."""
    supported = ", ".join(sorted(FORMAT_HANDLERS.keys()))
    parser = argparse.ArgumentParser(
        prog="unarch",
        description=f"Recursively extract archives ({supported}) under a given path.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "path",
        help=f"Root directory or file to search for archives ({supported})",
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
