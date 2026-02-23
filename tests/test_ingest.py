"""Tests for instapipe.ingest module."""

import pytest
import pandas as pd
from pathlib import Path

from instapipe.ingest import load, load_daily


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load("nonexistent_file.csv")


def test_load_unsupported_extension(tmp_path):
    fake_file = tmp_path / "data.txt"
    fake_file.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported file type"):
        load(fake_file)


def test_load_csv_utf8(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        "Descripción,Visualizaciones,Alcance,Me gusta\n"
        "test reel,1000,800,50\n"
        "another reel,2000,1500,100\n",
        encoding="utf-8-sig",
    )
    df = load(csv_file)
    assert len(df) == 2
    assert "Visualizaciones" in df.columns or "visualizaciones" in df.columns


def test_load_accepts_path_object(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        "Visualizaciones,Alcance\n100,80\n",
        encoding="utf-8-sig",
    )
    df = load(Path(csv_file))
    assert isinstance(df, pd.DataFrame)


def test_load_daily_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_daily("nonexistent.csv", "views")


def test_load_daily_parses_utf16(tmp_path):
    csv_file = tmp_path / "Visualizaciones.csv"
    content = (
        'sep=,\n'
        '"Visualizaciones"\n'
        '"Fecha","Valor"\n'
        '"2026-03-01T00:00:00","1234"\n'
        '"2026-03-02T00:00:00","5678"\n'
    )
    csv_file.write_text(content, encoding="utf-16")
    df = load_daily(csv_file, "visualizaciones")
    assert len(df) == 2
    assert "visualizaciones" in df.columns
    assert df["visualizaciones"].iloc[0] == 1234
