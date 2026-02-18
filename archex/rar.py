"""RAR archive extraction for archex."""

import os

from rich.console import Console
from rich.progress import track

from .core import validate_member_path

console = Console()


def extract_rar_archive(
    rar_file: str,
    output_dir: str,
    passwords: list[str] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
) -> int:
    """Extract a RAR archive to the specified directory.

    Requires the 'rarfile' package and the 'unrar' binary installed on the system.

    Args:
        rar_file: Path to the RAR file.
        output_dir: Directory to extract files to.
        passwords: Optional list of passwords to try for encrypted archives.
        show_progress: Whether to show rich progress bar.
        verbose: Whether to print each extracted file path.

    Returns:
        Number of files extracted, or -1 on failure.
    """
    try:
        import rarfile
    except ImportError:
        console.print(
            "[red]Error:[/red] 'rarfile' package not installed. "
            "Install it with: [bold]pip install rarfile[/bold]"
        )
        return -1

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def try_extract(password=None) -> int:
        try:
            with rarfile.RarFile(rar_file, "r") as rf:
                if password:
                    rf.setpassword(password.encode('utf-8') if isinstance(password, str) else password)
                members = [m for m in rf.infolist() if not m.is_dir()]
                extracted_count = 0
                iterator = (
                    track(members, description=f"Extracting {os.path.basename(rar_file)}", transient=True)
                    if show_progress else members
                )
                for member in iterator:
                    safe_path = validate_member_path(member.filename, output_dir)
                    if safe_path is None:
                        continue
                    out_dir = os.path.dirname(safe_path)
                    if not os.path.exists(out_dir):
                        os.makedirs(out_dir)
                    with open(safe_path, 'wb') as f:
                        f.write(rf.read(member.filename))
                    extracted_count += 1
                    if verbose:
                        console.print(f"  [dim]{member.filename}[/dim]")
                return extracted_count
        except rarfile.BadRarFile:
            return -1
        except rarfile.PasswordRequired:
            return -2  # Signal: needs password
        except rarfile.RarWrongPassword:
            return -2  # Signal: wrong password

    try:
        # Test if unrar/bsdtar is available by attempting to open the file
        import rarfile
        rarfile.RarFile(rar_file, "r").close()
    except rarfile.RarCannotExec:
        console.print(
            "[red]Error:[/red] 'unrar' binary not found. "
            "Install it with: [bold]brew install unrar[/bold] (macOS) or [bold]apt install unrar[/bold] (Linux)"
        )
        return -1
    except Exception:
        pass

    if not passwords:
        result = try_extract()
        return result if result != -2 else -1
    else:
        for pwd in passwords:
            result = try_extract(pwd)
            if result >= 0:
                return result
        return -1
