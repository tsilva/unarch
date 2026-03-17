"""Tests for RAR archive extraction."""

import pytest


class TestRarExtraction:
    def test_missing_rarfile_package(self, tmp_path, monkeypatch):
        """If rarfile is not importable, extract_rar_archive returns -1."""
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "rarfile":
                raise ImportError("No module named 'rarfile'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        from unarch.rar import extract_rar_archive
        result = extract_rar_archive("fake.rar", str(tmp_path), show_progress=False)
        assert result == -1

    def test_rar_import_available(self):
        """rarfile package should be importable (it's a dependency)."""
        try:
            import rarfile
            assert rarfile is not None
        except ImportError:
            pytest.skip("rarfile not installed")
