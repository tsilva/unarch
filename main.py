import os
import re
import argparse
from tqdm import tqdm
import zipfile

def sanitize_filename(filename):
    # Remove directories and illegal characters
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    filename = filename.replace("..", "")  # extra safety
    return os.path.basename(filename)

def find_zip_files(root_path):
    """Recursively yield paths to all .zip files under root_path."""
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            if fname.lower().endswith('.zip'):
                yield os.path.join(dirpath, fname)

def load_passwords(password_file):
    """Load passwords from a file, one per line, stripping whitespace."""
    with open(password_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def try_extract_member(zf, member, out_path, passwords):
    """Try to extract a zip member using a list of passwords (or no password)."""
    if not passwords:
        # Try without password
        with open(out_path, 'wb') as f:
            f.write(zf.read(member))
        return True
    for pwd in passwords:
        try:
            with open(out_path, 'wb') as f:
                f.write(zf.read(member, pwd.encode('utf-8')))
            return True
        except RuntimeError as e:
            # Wrong password or not encrypted
            continue
        except zipfile.BadZipFile:
            continue
    return False

def extract_zip(zip_file, output_dir, passwords=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Starting extraction for: {zip_file}")
    with zipfile.ZipFile(zip_file, 'r') as zf:
        members = zf.infolist()
        for member in tqdm(members, desc=f"Extracting {os.path.basename(zip_file)}"):
            # Skip directories
            if member.is_dir():
                continue

            # Construct the full output path, preserving folder structure
            safe_member_path = os.path.normpath(member.filename)
            # Prevent path traversal
            if os.path.isabs(safe_member_path) or safe_member_path.startswith(".."):
                continue

            out_path = os.path.join(output_dir, safe_member_path)
            out_dir = os.path.dirname(out_path)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            # Try to extract with passwords if provided
            success = try_extract_member(zf, member, out_path, passwords)
            if not success:
                print(f"Failed to extract '{member.filename}' from '{zip_file}' (no valid password found).")

    print(f"Extracted {len(members)} items to '{output_dir}'.")

def main():
    parser = argparse.ArgumentParser(
        description="Recursively extract all files from .zip archives under a given path."
    )
    parser.add_argument(
        "path",
        help="Root directory or file to search for .zip files"
    )
    parser.add_argument(
        "--passwords",
        help="Path to a file containing passwords (one per line) to try for encrypted zip files"
    )
    args = parser.parse_args()
    root_path = args.path
    passwords = load_passwords(args.passwords) if args.passwords else None
    for zip_path in find_zip_files(root_path):
        zip_dir = os.path.splitext(zip_path)[0]
        print(f"Found zip: {zip_path} -> extracting to {zip_dir}")
        extract_zip(zip_path, zip_dir, passwords)

if __name__ == "__main__":
    main()
