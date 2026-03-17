"""Tar archive extraction for unarch."""

import os
import tarfile

from rich.console import Console
from rich.progress import track

from .core import validate_member_path

console = Console()


def extract_tar_archive(
    tar_file: str,
    output_dir: str,
    show_progress: bool = True,
    verbose: bool = False,
) -> int:
    """Extract a tar archive to the specified directory.

    Supports .tar, .tar.gz/.tgz, .tar.bz2/.tbz2, .tar.xz/.txz.
    Symlinks and hardlinks are skipped for security.

    Args:
        tar_file: Path to the tar archive.
        output_dir: Directory to extract files to.
        show_progress: Whether to show rich progress bar.
        verbose: Whether to print each extracted file path.

    Returns:
        Number of files extracted, or -1 on failure.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with tarfile.open(tar_file, "r:*") as tf:
            members = tf.getmembers()
            file_members = [m for m in members if m.isfile()]

            extracted_count = 0
            iterator = (
                track(file_members, description=f"Extracting {os.path.basename(tar_file)}", transient=True)
                if show_progress else file_members
            )
            for member in iterator:
                # Skip symlinks and hardlinks
                if member.issym() or member.islnk():
                    continue
                safe_path = validate_member_path(member.name, output_dir)
                if safe_path is None:
                    continue
                out_dir = os.path.dirname(safe_path)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                file_obj = tf.extractfile(member)
                if file_obj is None:
                    continue
                with open(safe_path, 'wb') as f:
                    f.write(file_obj.read())
                extracted_count += 1
                if verbose:
                    console.print(f"  [dim]{member.name}[/dim]")
            return extracted_count
    except Exception:
        return -1
