"""Security tests: path traversal rejection across all formats."""


import py7zr

from unarch.sevenz import extract_7z_archive
from unarch.tar import extract_tar_archive
from unarch.zip import extract_zip_archive


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


class TestSevenZSymlinkTraversal:
    def test_symlink_members_are_not_passed_to_py7zr_extraction(self, monkeypatch, tmp_path):
        outside = tmp_path / "outside.txt"
        output = tmp_path / "out"

        class Member:
            def __init__(self, filename: str, *, is_symlink: bool = False) -> None:
                self.filename = filename
                self.is_directory = False
                self.is_symlink = is_symlink

        class FakeArchive:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args) -> None:
                pass

            def list(self):
                return [Member("escape-link", is_symlink=True), Member("safe.txt")]

            def extract(self, *, path, targets) -> None:
                assert targets == ["safe.txt"]
                destination = tmp_path / path / "safe.txt"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text("safe", encoding="utf-8")

        monkeypatch.setattr(py7zr, "SevenZipFile", FakeArchive)

        count = extract_7z_archive("malicious.7z", str(output), show_progress=False)

        assert count == 1
        assert (output / "safe.txt").read_text(encoding="utf-8") == "safe"
        assert not outside.exists()
