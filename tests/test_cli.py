"""Tests for CLI behavior."""

import subprocess
import sys

import pytest


def run_cli(*args, **kwargs):
    """Run the unarch CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "unarch", *args],
        capture_output=True,
        text=True,
        **kwargs,
    )


class TestCLI:
    def test_version_flag(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "unarch" in result.stdout or "unarch" in result.stderr

    def test_version_short_flag(self):
        result = run_cli("-V")
        assert result.returncode == 0

    def test_help_flag(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "path" in result.stdout.lower() or "path" in result.stderr.lower()

    def test_dry_run_no_archives(self, tmp_path):
        result = run_cli("--dry-run", str(tmp_path))
        assert result.returncode == 0
        assert "no archives" in result.stdout.lower() or "no archives" in result.stderr.lower()

    def test_dry_run_with_zip(self, simple_zip, tmp_archives):
        result = run_cli("--dry-run", str(tmp_archives))
        assert result.returncode == 0
        assert "zip" in result.stdout.lower() or "zip" in result.stderr.lower()

    def test_extract_zip(self, simple_zip, tmp_archives, tmp_path):
        result = run_cli("--output-dir", str(tmp_path), str(tmp_archives))
        assert result.returncode == 0

    def test_quiet_flag_suppresses_output(self, simple_zip, tmp_archives, tmp_path):
        result = run_cli("--quiet", "--output-dir", str(tmp_path), str(tmp_archives))
        assert result.returncode == 0
        # Quiet mode should produce no output
        assert result.stdout.strip() == ""

    def test_extract_with_password_file(self, simple_zip, tmp_archives, tmp_path):
        pw_file = tmp_path / "passwords.txt"
        pw_file.write_text("somepassword\n")
        result = run_cli(
            "--passwords", str(pw_file),
            "--output-dir", str(tmp_path / "out"),
            str(tmp_archives),
        )
        assert result.returncode == 0
