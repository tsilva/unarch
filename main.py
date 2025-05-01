import os
import re
import argparse
from tqdm import tqdm
import zipfile
import py7zr

def sanitize_filename(filename):
    # Remove directories and illegal characters
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    filename = filename.replace("..", "")  # extra safety
    return os.path.basename(filename)

def find_archive_files(root_path):
    """Recursively yield paths to all .zip and .7z files under root_path."""
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            if fname.lower().endswith('.zip') or fname.lower().endswith('.7z'):
                yield os.path.join(dirpath, fname)

def load_passwords(password_file):
    """Load passwords from a file, one per line, stripping whitespace."""
    with open(password_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def extract_zip(zip_file, output_dir, passwords=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(zip_file, 'r') as zf:
        members = zf.infolist()
        extracted = False
        if not passwords:
            # No passwords provided, extract directly
            for member in tqdm(members, desc=f"Extracting {os.path.basename(zip_file)}"):
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
                    f.write(zf.read(member))
            extracted = True
        else:
            # Try each password for the whole zip
            for pwd in passwords:
                try:
                    for member in tqdm(members, desc=f"Extracting {os.path.basename(zip_file)}", leave=False):
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
                            f.write(zf.read(member, pwd.encode('utf-8')))
                    extracted = True
                    break  # Stop trying passwords after success
                except RuntimeError:
                    # Wrong password, try next
                    continue
                except zipfile.BadZipFile:
                    continue
        if not extracted:
            print(f"Could not extract '{zip_file}': no valid password found.")
        else:
            print(f"Extracted {len(members)} items to '{output_dir}'.")

def extract_7z(archive_file, output_dir, passwords=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    extracted = False
    if not passwords:
        try:
            with py7zr.SevenZipFile(archive_file, mode='r') as archive:
                archive.extractall(path=output_dir)
            extracted = True
        except py7zr.exceptions.PasswordRequired:
            pass
        except py7zr.exceptions.Bad7zFile:
            pass
    else:
        for pwd in passwords:
            try:
                with py7zr.SevenZipFile(archive_file, mode='r', password=pwd) as archive:
                    archive.extractall(path=output_dir)
                extracted = True
                break
            except py7zr.exceptions.PasswordRequired:
                continue
            except py7zr.exceptions.Bad7zFile:
                continue
            except py7zr.exceptions.InvalidPassword:
                continue
    if not extracted:
        print(f"Could not extract '{archive_file}': no valid password found.")
    else:
        print(f"Extracted '{archive_file}' to '{output_dir}'.")

def main():
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
    args = parser.parse_args()
    root_path = args.path
    passwords = load_passwords(args.passwords) if args.passwords else None
    for archive_path in find_archive_files(root_path):
        archive_dir = os.path.splitext(archive_path)[0]
        ext = os.path.splitext(archive_path)[1].lower()
        if ext == ".zip":
            extract_zip(archive_path, archive_dir, passwords)
        elif ext == ".7z":
            extract_7z(archive_path, archive_dir, passwords)

if __name__ == "__main__":
    main()
