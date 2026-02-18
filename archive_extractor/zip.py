"""ZIP archive extraction for archive-extractor."""

import os
import zipfile

from rich.console import Console
from rich.progress import track

from .core import validate_member_path

console = Console()


def extract_zip_archive(
    zip_file: str,
    output_dir: str,
    passwords: list[str] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
) -> int:
    """Extract a ZIP archive to the specified directory.

    Args:
        zip_file: Path to the ZIP file.
        output_dir: Directory to extract files to.
        passwords: Optional list of passwords to try for encrypted archives.
        show_progress: Whether to show rich progress bar.
        verbose: Whether to print each extracted file path.

    Returns:
        Number of files extracted, or -1 on failure.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        zf_handle = zipfile.ZipFile(zip_file, 'r')
    except zipfile.BadZipFile:
        return -1

    with zf_handle as zf:
        members = zf.infolist()
        extracted_count = 0

        def extract_members(pwd_bytes=None):
            nonlocal extracted_count
            iterator = (
                track(members, description=f"Extracting {os.path.basename(zip_file)}", transient=True)
                if show_progress else members
            )
            for member in iterator:
                if member.is_dir():
                    continue
                safe_path = validate_member_path(member.filename, output_dir)
                if safe_path is None:
                    continue
                out_dir = os.path.dirname(safe_path)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                with open(safe_path, 'wb') as f:
                    f.write(zf.read(member, pwd_bytes))
                extracted_count += 1
                if verbose:
                    console.print(f"  [dim]{member.filename}[/dim]")

        if not passwords:
            try:
                extract_members()
                return extracted_count
            except RuntimeError:
                return -1
        else:
            for pwd in passwords:
                extracted_count = 0
                try:
                    extract_members(pwd.encode('utf-8'))
                    return extracted_count
                except RuntimeError:
                    continue
                except zipfile.BadZipFile:
                    continue
            return -1
