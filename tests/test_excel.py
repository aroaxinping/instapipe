"""Tests for instapipe.excel module."""

import pandas as pd
import pytest

from instapipe.metrics import compute
from instapipe.excel import build_excel


def _make_report():
    df = pd.DataFrame({
        "alcance": [1000, 2000, 500],
        "visualizaciones": [1500, 3000, 800],
        "me_gustas": [100, 300, 50],
        "comentarios": [10, 30, 5],
        "guardados": [20, 60, 10],
        "compartidos": [5, 15, 2],
        "fecha": ["2026-03-01", "2026-03-02", "2026-03-03"],
        "descripcion_corta": ["reel about sql", "bash tips", "random stuff"],
        "tema": ["SQL", "Terminal/Bash", "Other"],
    })
    return compute(df)


def test_build_excel_creates_file(tmp_path):
    report = _make_report()
    path = tmp_path / "test.xlsx"
    build_excel(report, path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_build_excel_has_sheets(tmp_path):
    report = _make_report()
    path = tmp_path / "test.xlsx"
    build_excel(report, path)
    xl = pd.ExcelFile(path)
    sheet_names = xl.sheet_names
    assert "Overview" in sheet_names
    assert "Reels Raw" in sheet_names
    assert "Engagement Calc" in sheet_names


def test_build_excel_reels_raw_data(tmp_path):
    report = _make_report()
    path = tmp_path / "test.xlsx"
    build_excel(report, path)
    df = pd.read_excel(path, sheet_name="Reels Raw")
    assert len(df) == 3
    assert "Views" in df.columns or "Likes" in df.columns
