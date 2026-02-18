"""Tests for tar archive extraction."""

import os

import pytest

from archive_extractor.tar import extract_tar_archive


class TestTarExtraction:
    def test_basic_extraction(self, simple_tar, tmp_path):
        output = tmp_path / "out"
        count = extract_tar_archive(simple_tar, str(output), show_progress=False)
        assert count == 2
        assert (output / "hello.txt").read_text() == "hello"
        assert (output / "subdir" / "world.txt").read_text() == "world"

    def test_creates_output_dir(self, simple_tar, tmp_path):
        output = tmp_path / "does_not_exist"
        extract_tar_archive(simple_tar, str(output), show_progress=False)
        assert output.exists()

    def test_skips_symlinks(self, symlink_tar, tmp_path):
        output = tmp_path / "out"
        count = extract_tar_archive(symlink_tar, str(output), show_progress=False)
        # Only "safe.txt" should be extracted; symlink is skipped
        assert count == 1
        assert (output / "safe.txt").exists()
        assert not (output / "link_to_etc").exists()

    def test_returns_count(self, simple_tar, tmp_path):
        count = extract_tar_archive(simple_tar, str(tmp_path / "out"), show_progress=False)
        assert count == 2

    def test_verbose_mode(self, simple_tar, tmp_path):
        count = extract_tar_archive(
            simple_tar, str(tmp_path / "out"), show_progress=False, verbose=True
        )
        assert count >= 0

    def test_corrupt_tar_returns_minus_one(self, tmp_path):
        bad_tar = tmp_path / "bad.tar"
        bad_tar.write_bytes(b"not a tar file")
        count = extract_tar_archive(str(bad_tar), str(tmp_path / "out"), show_progress=False)
        assert count == -1
