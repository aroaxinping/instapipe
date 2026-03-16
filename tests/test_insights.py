"""Tests for instapipe.insights module."""

import pandas as pd
import pytest

from instapipe.metrics import compute
from instapipe.insights import detect_virals, analyze_duration, analyze_hashtags


def _make_report():
    df = pd.DataFrame({
        "alcance": [100] * 9 + [10000],
        "visualizaciones": [150] * 9 + [15000],
        "me_gustas": [5] * 9 + [5000],
        "comentarios": [0] * 10,
        "guardados": [0] * 10,
        "compartidos": [0] * 10,
        "duracion_seg": [10, 20, 30, 45, 60, 15, 25, 35, 50, 8],
        "descripcion": [
            "learn #sql joins",
            "tips #python #datascience",
            "#bash terminal tricks",
            "my #git workflow",
            "#python pandas tutorial",
            "random stuff",
            "#excel vs #python",
            "#linux tips for devs",
            "#techhumor moment",
            "viral #python reel #coding",
        ],
    })
    return compute(df)


def test_detect_virals():
    report = _make_report()
    virals = detect_virals(report, threshold=1.5)
    assert len(virals) >= 1
    assert "outlier_score" in virals.columns


def test_detect_virals_no_outliers():
    df = pd.DataFrame({
        "alcance": [1000, 1000, 1000],
        "me_gustas": [100, 100, 100],
        "comentarios": [10, 10, 10],
        "guardados": [20, 20, 20],
        "compartidos": [5, 5, 5],
    })
    report = compute(df)
    virals = detect_virals(report, threshold=2.0)
    assert len(virals) == 0


def test_analyze_duration():
    report = _make_report()
    result = analyze_duration(report)
    assert result is not None
    assert "duration_bucket" in result.columns
    assert "avg_engagement" in result.columns
    assert len(result) > 0


def test_analyze_duration_no_column():
    df = pd.DataFrame({
        "alcance": [1000], "me_gustas": [100],
        "comentarios": [10], "guardados": [20], "compartidos": [5],
    })
    result = analyze_duration(compute(df))
    assert result is None


def test_analyze_hashtags():
    report = _make_report()
    result = analyze_hashtags(report)
    assert result is not None
    assert "hashtag" in result.columns
    assert "avg_engagement" in result.columns
    assert len(result) > 0
    # #python should appear multiple times
    python_row = result[result["hashtag"] == "#python"]
    assert len(python_row) == 1
    assert python_row["count"].iloc[0] >= 3


def test_analyze_hashtags_no_description():
    df = pd.DataFrame({
        "alcance": [1000], "me_gustas": [100],
        "comentarios": [10], "guardados": [20], "compartidos": [5],
    })
    result = analyze_hashtags(compute(df))
    assert result is None
