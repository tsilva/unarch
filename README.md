# 🗂️ archive-extractor

<p align="center">
  <img src="logo.png" alt="Logo" width="400"/>
</p>

🔹 Effortlessly extract all ZIP archives in a directory tree, including password-protected files.  

## 📖 Overview

Archive Extractor is a command-line tool for recursively finding and extracting all `.zip` files within a specified directory. It preserves folder structures, safely handles filenames, and can attempt multiple passwords for encrypted archives using a password list. This utility is ideal for bulk extraction tasks or forensic analysis where archives may be deeply nested or protected.

## 🚀 Installation

```bash
uv tool install .
```

## 🛠️ Usage

Extract all ZIP files under a directory:

```bash
archive-extractor /path/to/search
```

Extract ZIP files using a list of passwords (one per line in `passwords.txt`):

```bash
archive-extractor /path/to/search --passwords passwords.txt
```

- All extracted files are placed in folders named after each ZIP file (without the `.zip` extension).
- Progress is shown for each archive.
- Skips directories and prevents unsafe path traversal.

## 📄 License

This project is licensed under the [MIT License](LICENSE).