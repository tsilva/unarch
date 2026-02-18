"""Security tests: path traversal rejection across all formats."""

import os

import pytest

from archive_extractor.zip import extract_zip_archive
from archive_extractor.tar import extract_tar_archive


class TestZipPathTraversal:
    def test_dotdot_member_not_extracted(self, traversal_zip, tmp_path):
        output = tmp_path / "out"
        count = extract_zip_archive(str(traversal_zip), str(output), show_progress=False)
        # Only "safe.txt" should be extracted
        assert count == 1
        assert (output / "safe.txt").exists()

    def test_traversal_file_not_written_outside_output(self, traversal_zip, tmp_path):
        output = tmp_path / "out"
        extract_zip_archive(str(traversal_zip), str(output), show_progress=False)
        # Ensure "evil.txt" was NOT written one level above output_dir
        evil_path = tmp_path / "evil.txt"
        assert not evil_path.exists()

    def test_nested_traversal_not_extracted(self, traversal_zip, tmp_path):
        output = tmp_path / "out"
        extract_zip_archive(str(traversal_zip), str(output), show_progress=False)
        # "subdir/../../evil2.txt" should not appear anywhere outside output
        evil2 = tmp_path / "evil2.txt"
        assert not evil2.exists()


class TestTarPathTraversal:
    def test_dotdot_member_not_extracted(self, traversal_tar, tmp_path):
        output = tmp_path / "out"
        count = extract_tar_archive(str(traversal_tar), str(output), show_progress=False)
        # Only "safe.txt" should be extracted
        assert count == 1
        assert (output / "safe.txt").exists()

    def test_traversal_file_not_written_outside_output(self, traversal_tar, tmp_path):
        output = tmp_path / "out"
        extract_tar_archive(str(traversal_tar), str(output), show_progress=False)
        evil_path = tmp_path / "evil.txt"
        assert not evil_path.exists()
