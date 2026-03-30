"""Tests for instapipe.cli module."""

import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(REPO, "examples", "sample_data.csv")


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "instapipe", *args],
        capture_output=True, text=True,
    )


def test_cli_help():
    result = _run("--help")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "instapipe" in combined


def test_cli_version():
    result = _run("--version")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "0.1.0" in combined


def test_cli_analyze_sample_data(tmp_path):
    result = _run("analyze", SAMPLE, "-o", str(tmp_path), "--no-charts")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "Done" in combined
    assert (tmp_path / "report.csv").exists()


def test_cli_analyze_with_excel(tmp_path):
    result = _run("analyze", SAMPLE, "-o", str(tmp_path), "--no-charts", "--excel")
    assert result.returncode == 0
    assert (tmp_path / "analytics.xlsx").exists()


def test_cli_analyze_file_not_found(tmp_path):
    result = _run("analyze", "nonexistent.csv", "-o", str(tmp_path))
    assert result.returncode != 0
