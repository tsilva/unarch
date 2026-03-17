"""Tests for the public unarch API."""

from pathlib import Path

from unarch import extract_archives


class TestExtractArchives:
    def test_output_suffix_changes_destination_name(self, simple_zip):
        archive_path = Path(simple_zip)

        results = extract_archives(
            str(archive_path),
            show_progress=False,
            output_suffix="_archive",
        )

        assert results[str(archive_path)] == 2
        assert (archive_path.parent / "simple_archive" / "hello.txt").read_bytes() == b"hello"

    def test_skip_existing_returns_zero_without_reextracting(self, simple_zip):
        archive_path = Path(simple_zip)

        first = extract_archives(
            str(archive_path),
            show_progress=False,
            output_suffix="_archive",
            skip_existing=True,
        )
        second = extract_archives(
            str(archive_path),
            show_progress=False,
            output_suffix="_archive",
            skip_existing=True,
        )

        assert first[str(archive_path)] == 2
        assert second[str(archive_path)] == 0
