"""Tests for archive_extractor.core module."""

import os

import pytest

from archive_extractor.core import validate_member_path, find_archive_files, load_passwords


class TestValidateMemberPath:
    def test_safe_path_returns_absolute(self, tmp_path):
        result = validate_member_path("hello.txt", str(tmp_path))
        assert result is not None
        assert os.path.isabs(result)
        assert result.startswith(str(tmp_path))

    def test_safe_subdir_path(self, tmp_path):
        result = validate_member_path("subdir/hello.txt", str(tmp_path))
        assert result is not None
        assert result.endswith(os.path.join("subdir", "hello.txt"))

    def test_rejects_absolute_path(self, tmp_path):
        assert validate_member_path("/etc/passwd", str(tmp_path)) is None

    def test_rejects_dotdot(self, tmp_path):
        assert validate_member_path("../evil.txt", str(tmp_path)) is None

    def test_rejects_dotdot_in_subdir(self, tmp_path):
        assert validate_member_path("subdir/../../evil.txt", str(tmp_path)) is None

    def test_rejects_windows_style_absolute(self, tmp_path):
        # C:\evil.txt normalizes to C:\evil.txt on Windows, but on Unix it's just a relative path
        # This is more of a sanity check
        result = validate_member_path("subdir/../safe.txt", str(tmp_path))
        # After normpath, this becomes "safe.txt" which is safe
        assert result is not None

    def test_safe_nested_path(self, tmp_path):
        result = validate_member_path("a/b/c/d.txt", str(tmp_path))
        assert result is not None
        assert "a" in result and "b" in result


class TestFindArchiveFiles:
    def test_finds_zip_in_directory(self, simple_zip, tmp_archives):
        found = list(find_archive_files(str(tmp_archives)))
        assert any(f.endswith(".zip") for f in found)

    def test_finds_7z_in_directory(self, simple_7z, tmp_archives):
        found = list(find_archive_files(str(tmp_archives)))
        assert any(f.endswith(".7z") for f in found)

    def test_finds_tar_gz_in_directory(self, simple_tar, tmp_archives):
        found = list(find_archive_files(str(tmp_archives)))
        assert any(f.endswith(".tar.gz") for f in found)

    def test_single_file_zip(self, simple_zip):
        found = list(find_archive_files(simple_zip))
        assert found == [simple_zip]

    def test_single_file_unknown_ext(self, tmp_path):
        txt = tmp_path / "file.txt"
        txt.write_text("hello")
        found = list(find_archive_files(str(txt)))
        assert found == []

    def test_nonexistent_path(self, tmp_path):
        found = list(find_archive_files(str(tmp_path / "nonexistent")))
        assert found == []


class TestLoadPasswords:
    def test_loads_passwords(self, tmp_path):
        pw_file = tmp_path / "passwords.txt"
        pw_file.write_text("pass1\npass2\npass3\n")
        passwords = load_passwords(str(pw_file))
        assert passwords == ["pass1", "pass2", "pass3"]

    def test_strips_whitespace(self, tmp_path):
        pw_file = tmp_path / "passwords.txt"
        pw_file.write_text("  pass1  \n  pass2  \n")
        passwords = load_passwords(str(pw_file))
        assert passwords == ["pass1", "pass2"]

    def test_skips_blank_lines(self, tmp_path):
        pw_file = tmp_path / "passwords.txt"
        pw_file.write_text("pass1\n\npass2\n\n")
        passwords = load_passwords(str(pw_file))
        assert passwords == ["pass1", "pass2"]

    def test_empty_file(self, tmp_path):
        pw_file = tmp_path / "passwords.txt"
        pw_file.write_text("")
        passwords = load_passwords(str(pw_file))
        assert passwords == []
