"""Core extraction logic for archive-extractor."""

import os
import re
import zipfile
import lzma

import py7zr
from tqdm import tqdm


def sanitize_filename(filename: str) -> str:
    """Remove directories and illegal characters from a filename.

    Args:
        filename: The filename to sanitize.

    Returns:
        A safe filename with illegal characters replaced and path components removed.
    """
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    filename = filename.replace("..", "")
    return os.path.basename(filename)


def find_archive_files(root_path: str):
    """Recursively yield paths to all .zip and .7z files under root_path.

    Args:
        root_path: Directory to search, or a single archive file path.

    Yields:
        Absolute paths to archive files found.
    """
    if os.path.isfile(root_path):
        ext = os.path.splitext(root_path)[1].lower()
        if ext in ('.zip', '.7z'):
            yield root_path
        return

    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            if fname.lower().endswith('.zip') or fname.lower().endswith('.7z'):
                yield os.path.join(dirpath, fname)


def load_passwords(password_file: str) -> list[str]:
    """Load passwords from a file, one per line, stripping whitespace.

    Args:
        password_file: Path to a file containing passwords.

    Returns:
        List of password strings.
    """
    with open(password_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def extract_zip_archive(
    zip_file: str,
    output_dir: str,
    passwords: list[str] | None = None,
    show_progress: bool = True
) -> int:
    """Extract a ZIP archive to the specified directory.

    Args:
        zip_file: Path to the ZIP file.
        output_dir: Directory to extract files to.
        passwords: Optional list of passwords to try for encrypted archives.
        show_progress: Whether to show tqdm progress bar.

    Returns:
        Number of files extracted, or -1 on failure.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(zip_file, 'r') as zf:
        members = zf.infolist()
        extracted_count = 0

        def extract_members(pwd_bytes=None):
            nonlocal extracted_count
            iterator = tqdm(members, desc=f"Extracting {os.path.basename(zip_file)}", leave=False) if show_progress else members
            for member in iterator:
                if member.is_dir():
                    continue
                safe_member_path = os.path.normpath(member.filename)
                if os.path.isabs(safe_member_path) or safe_member_path.startswith(".."):
                    continue
                out_path = os.path.join(output_dir, safe_member_path)
                out_dir = os.path.dirname(out_path)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                with open(out_path, 'wb') as f:
                    f.write(zf.read(member, pwd_bytes))
                extracted_count += 1

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


def extract_7z_archive(
    archive_file: str,
    output_dir: str,
    passwords: list[str] | None = None,
    show_progress: bool = True
) -> int:
    """Extract a 7z archive to the specified directory.

    Args:
        archive_file: Path to the 7z file.
        output_dir: Directory to extract files to.
        passwords: Optional list of passwords to try for encrypted archives.
        show_progress: Whether to show tqdm progress bar (currently unused for 7z).

    Returns:
        Number of files extracted, or -1 on failure.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def try_extract(password=None):
        with py7zr.SevenZipFile(archive_file, mode='r', password=password) as archive:
            archive.extractall(path=output_dir)
            return len(archive.getnames())

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
