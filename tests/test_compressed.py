"""Tests for single-file compressed extraction."""

import bz2
import gzip
import lzma

from unarch import extract_archives


class TestCompressedExtraction:
    def test_extracts_gz_file(self, tmp_archives, tmp_path):
        archive_path = tmp_archives / "invoice.txt.gz"
        with gzip.open(archive_path, "wb") as handle:
            handle.write(b"hello")

        results = extract_archives(str(archive_path), show_progress=False)

        assert results[str(archive_path)] == 1
        assert (tmp_archives / "invoice.txt" / "invoice.txt").read_bytes() == b"hello"

    def test_extracts_bz2_file(self, tmp_archives):
        archive_path = tmp_archives / "invoice.txt.bz2"
        with bz2.open(archive_path, "wb") as handle:
            handle.write(b"hello")

        results = extract_archives(str(archive_path), show_progress=False)

        assert results[str(archive_path)] == 1
        assert (tmp_archives / "invoice.txt" / "invoice.txt").read_bytes() == b"hello"

    def test_extracts_xz_file(self, tmp_archives):
        archive_path = tmp_archives / "invoice.txt.xz"
        with lzma.open(archive_path, "wb") as handle:
            handle.write(b"hello")

        results = extract_archives(str(archive_path), show_progress=False)

        assert results[str(archive_path)] == 1
        assert (tmp_archives / "invoice.txt" / "invoice.txt").read_bytes() == b"hello"
