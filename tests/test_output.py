"""Tests for instapipe.output module."""

import pandas as pd
import pytest

from instapipe.metrics import compute
from instapipe.output import to_csv, to_json, plot_engagement, plot_best_hours, plot_save_rate, plot_top_reels

import matplotlib
matplotlib.use("Agg")


def _make_report():
    df = pd.DataFrame({
        "alcance": [1000, 2000, 500, 800, 1500],
        "visualizaciones": [1500, 3000, 800, 1200, 2200],
        "me_gustas": [100, 300, 50, 80, 200],
        "comentarios": [10, 30, 5, 8, 20],
        "guardados": [20, 60, 10, 15, 40],
        "compartidos": [5, 15, 2, 3, 10],
        "hora": [14, 18, 20, 14, 16],
        "descripcion_corta": ["reel 1", "reel 2", "reel 3", "reel 4", "reel 5"],
    })
    return compute(df)


def test_to_csv(tmp_path):
    report = _make_report()
    path = tmp_path / "report.csv"
    to_csv(report, path)
    assert path.exists()
    df = pd.read_csv(path)
    assert "engagement_rate" in df.columns
    assert "save_rate" in df.columns
    assert len(df) == 5


def test_to_json(tmp_path):
    report = _make_report()
    path = tmp_path / "report.json"
    to_json(report, path)
    assert path.exists()
    df = pd.read_json(path)
    assert len(df) == 5


def test_plot_engagement(tmp_path):
    report = _make_report()
    path = tmp_path / "engagement.png"
    plot_engagement(report, save_to=path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_plot_best_hours(tmp_path):
    report = _make_report()
    path = tmp_path / "best_hours.png"
    plot_best_hours(report, save_to=path)
    assert path.exists()


def test_plot_save_rate(tmp_path):
    report = _make_report()
    path = tmp_path / "save_rate.png"
    plot_save_rate(report, save_to=path)
    assert path.exists()


def test_plot_top_reels(tmp_path):
    report = _make_report()
    path = tmp_path / "top_reels.png"
    plot_top_reels(report, save_to=path)
    assert path.exists()
