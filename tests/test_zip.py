"""Tests for ZIP archive extraction."""

import os

import pytest

from archex.zip import extract_zip_archive


class TestZipExtraction:
    def test_basic_extraction(self, simple_zip, tmp_path):
        output = tmp_path / "out"
        count = extract_zip_archive(simple_zip, str(output), show_progress=False)
        assert count == 2
        assert (output / "hello.txt").read_text() == "hello"
        assert (output / "subdir" / "world.txt").read_text() == "world"

    def test_creates_output_dir(self, simple_zip, tmp_path):
        output = tmp_path / "does_not_exist" / "nested"
        extract_zip_archive(simple_zip, str(output), show_progress=False)
        assert output.exists()

    def test_returns_positive_count(self, simple_zip, tmp_path):
        count = extract_zip_archive(simple_zip, str(tmp_path / "out"), show_progress=False)
        assert count >= 0

    def test_corrupt_zip_returns_minus_one(self, corrupt_zip, tmp_path):
        count = extract_zip_archive(
            corrupt_zip, str(tmp_path / "out"), show_progress=False
        )
        assert count == -1

    def test_empty_archive(self, tmp_archives, tmp_path):
        import zipfile
        empty_zip = tmp_archives / "empty.zip"
        with zipfile.ZipFile(str(empty_zip), "w"):
            pass
        count = extract_zip_archive(str(empty_zip), str(tmp_path / "out"), show_progress=False)
        assert count == 0

    def test_verbose_mode(self, simple_zip, tmp_path, capsys):
        extract_zip_archive(simple_zip, str(tmp_path / "out"), show_progress=False, verbose=True)
        # verbose just calls console.print — no exception is the passing condition
