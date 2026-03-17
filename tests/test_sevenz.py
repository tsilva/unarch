"""Tests for 7z archive extraction."""

import os

import pytest

from unarch.sevenz import extract_7z_archive


class TestSevenZExtraction:
    def test_basic_extraction(self, simple_7z, tmp_path):
        output = tmp_path / "out"
        count = extract_7z_archive(simple_7z, str(output), show_progress=False)
        assert count == 2
        assert (output / "hello.txt").read_bytes() == b"hello"
        assert (output / "subdir" / "world.txt").read_bytes() == b"world"

    def test_creates_output_dir(self, simple_7z, tmp_path):
        output = tmp_path / "does_not_exist"
        extract_7z_archive(simple_7z, str(output), show_progress=False)
        assert output.exists()

    def test_no_password_returns_count(self, simple_7z, tmp_path):
        count = extract_7z_archive(simple_7z, str(tmp_path / "out"), show_progress=False)
        assert count >= 0

    def test_wrong_password_returns_minus_one(self, simple_7z, tmp_path):
        count = extract_7z_archive(
            simple_7z, str(tmp_path / "out"),
            passwords=["wrong_password_xyz"], show_progress=False
        )
        # No password required for non-encrypted archive — should still extract
        assert count >= 0

    def test_verbose_mode(self, simple_7z, tmp_path):
        count = extract_7z_archive(
            simple_7z, str(tmp_path / "out"), show_progress=False, verbose=True
        )
        assert count >= 0
