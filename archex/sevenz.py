"""7z archive extraction for archex."""

import lzma
import os

import py7zr
from rich.console import Console
from rich.status import Status

from .core import validate_member_path

console = Console()


def extract_7z_archive(
    archive_file: str,
    output_dir: str,
    passwords: list[str] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
) -> int:
    """Extract a 7z archive to the specified directory.

    Uses member-by-member path validation before extraction to prevent path traversal.

    Args:
        archive_file: Path to the 7z file.
        output_dir: Directory to extract files to.
        passwords: Optional list of passwords to try for encrypted archives.
        show_progress: Whether to show rich progress indicator.
        verbose: Whether to print each extracted file path.

    Returns:
        Number of files extracted, or -1 on failure.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def try_extract(password=None) -> int:
        # Pass 1: list members for security validation (read-only, cheap)
        with py7zr.SevenZipFile(archive_file, mode='r', password=password) as archive:
            all_members = [m for m in archive.list() if not m.is_directory]

        # Validate each member path before extraction
        safe_names = [
            m.filename for m in all_members
            if validate_member_path(m.filename, output_dir) is not None
        ]

        if not safe_names:
            return 0

        if verbose:
            for name in safe_names:
                console.print(f"  [dim]{name}[/dim]")

        # Pass 2: extract only validated members
        basename = os.path.basename(archive_file)
        if show_progress:
            with Status(f"Extracting {basename}...", console=console):
                with py7zr.SevenZipFile(archive_file, mode='r', password=password) as archive:
                    archive.extract(path=output_dir, targets=safe_names)
        else:
            with py7zr.SevenZipFile(archive_file, mode='r', password=password) as archive:
                archive.extract(path=output_dir, targets=safe_names)

        return len(safe_names)

    if not passwords:
        try:
            return try_extract()
        except (py7zr.exceptions.PasswordRequired, py7zr.exceptions.Bad7zFile, lzma.LZMAError):
            return -1
        except Exception:
            return -1
    else:
        for pwd in passwords:
            try:
                return try_extract(pwd)
            except (py7zr.exceptions.PasswordRequired, py7zr.exceptions.Bad7zFile, lzma.LZMAError):
                continue
            except Exception:
                continue
        return -1
