"""Shared test fixtures for archex tests."""

import io
import os
import tarfile
import zipfile

import py7zr
import pytest


@pytest.fixture
def tmp_archives(tmp_path):
    """Create a directory with test archive files and return paths."""
    archives_dir = tmp_path / "archives"
    archives_dir.mkdir()
    return archives_dir


@pytest.fixture
def simple_zip(tmp_archives):
    """Create a simple ZIP with one text file."""
    zip_path = tmp_archives / "simple.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("hello.txt", "hello")
        zf.writestr("subdir/world.txt", "world")
    return str(zip_path)


@pytest.fixture
def corrupt_zip(tmp_archives):
    """Create a corrupt ZIP file (not a valid archive)."""
    zip_path = tmp_archives / "corrupt.zip"
    zip_path.write_bytes(b"PK\x03\x04this is not a valid zip file")
    return str(zip_path)


@pytest.fixture
def traversal_zip(tmp_archives):
    """Create a ZIP with path traversal member names."""
    zip_path = tmp_archives / "traversal.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        # Safe member
        zf.writestr("safe.txt", "safe content")
        # Path traversal attempts
        info1 = zipfile.ZipInfo("../evil.txt")
        zf.writestr(info1, "evil content")
        info2 = zipfile.ZipInfo("subdir/../../evil2.txt")
        zf.writestr(info2, "evil content 2")
    return str(zip_path)


@pytest.fixture
def simple_7z(tmp_archives, tmp_path):
    """Create a simple 7z archive with one text file."""
    z7_path = tmp_archives / "simple.7z"
    src = tmp_path / "sevenz_src"
    src.mkdir()
    (src / "hello.txt").write_bytes(b"hello")
    (src / "subdir").mkdir()
    (src / "subdir" / "world.txt").write_bytes(b"world")
    with py7zr.SevenZipFile(str(z7_path), "w") as zf:
        zf.write(str(src / "hello.txt"), "hello.txt")
        zf.write(str(src / "subdir" / "world.txt"), "subdir/world.txt")
    return str(z7_path)


@pytest.fixture
def simple_tar(tmp_archives):
    """Create a simple tar.gz archive with one text file."""
    tar_path = tmp_archives / "simple.tar.gz"
    with tarfile.open(str(tar_path), "w:gz") as tf:
        _add_string_to_tar(tf, "hello.txt", "hello")
        _add_string_to_tar(tf, "subdir/world.txt", "world")
    return str(tar_path)


@pytest.fixture
def traversal_tar(tmp_archives):
    """Create a tar archive with path traversal members."""
    tar_path = tmp_archives / "traversal.tar"
    with tarfile.open(str(tar_path), "w") as tf:
        _add_string_to_tar(tf, "safe.txt", "safe content")
        _add_string_to_tar(tf, "../evil.txt", "evil content")
    return str(tar_path)


@pytest.fixture
def symlink_tar(tmp_archives):
    """Create a tar archive containing a symlink."""
    tar_path = tmp_archives / "symlink.tar"
    with tarfile.open(str(tar_path), "w") as tf:
        _add_string_to_tar(tf, "safe.txt", "safe content")
        # Add a symlink member
        sym_info = tarfile.TarInfo(name="link_to_etc")
        sym_info.type = tarfile.SYMTYPE
        sym_info.linkname = "/etc"
        tf.addfile(sym_info)
    return str(tar_path)


def _add_string_to_tar(tf: tarfile.TarFile, name: str, content: str) -> None:
    """Helper to add a string as a file to a TarFile."""
    data = content.encode("utf-8")
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    tf.addfile(info, io.BytesIO(data))
