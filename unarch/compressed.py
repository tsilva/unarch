"""Single-file compressed archive extraction for unarch."""

import bz2
import gzip
import lzma
import os
import shutil

from rich.console import Console
from rich.status import Status

console = Console()

_OPENERS = {
    ".gz": gzip.open,
    ".bz2": bz2.open,
    ".xz": lzma.open,
}


def extract_compressed_file(
    archive_file: str,
    output_dir: str,
    passwords: list[str] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
) -> int:
    """Extract a single-file compressed archive into an output directory."""
    del passwords  # Unsupported for these formats.

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    archive_name = os.path.basename(archive_file)
    opener = None
    stem = archive_name
    for ext, candidate in _OPENERS.items():
        if archive_name.lower().endswith(ext):
            opener = candidate
            stem = archive_name[: -len(ext)]
            break

    if opener is None or not stem:
        return -1

    output_path = os.path.join(output_dir, stem)

    try:
        if show_progress:
            with Status(f"Extracting {archive_name}...", console=console):
                with opener(archive_file, "rb") as src, open(output_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        else:
            with opener(archive_file, "rb") as src, open(output_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
    except Exception:
        return -1

    if verbose:
        console.print(f"  [dim]{stem}[/dim]")

    return 1
