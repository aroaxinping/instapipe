"""Tests for instapipe.compare module."""

import pandas as pd
import pytest

from instapipe.metrics import compute
from instapipe.compare import compare


def _make_report(**overrides):
    base = {
        "alcance": [1000, 2000],
        "visualizaciones": [1500, 3000],
        "me_gustas": [100, 300],
        "comentarios": [10, 30],
        "guardados": [20, 60],
        "compartidos": [5, 15],
    }
    base.update(overrides)
    return compute(pd.DataFrame(base))


def test_compare_basic():
    current = _make_report(me_gustas=[200, 400])
    previous = _make_report(me_gustas=[100, 300])
    result = compare(current, previous)
    assert result.deltas["avg_engagement_rate"] > 0
    assert "avg_save_rate" in result.current


def test_compare_summary():
    current = _make_report()
    previous = _make_report()
    result = compare(current, previous)
    summary = result.summary()
    assert "Period comparison" in summary
    assert "avg_engagement_rate" in summary


def test_compare_delta_pct():
    current = _make_report(alcance=[2000, 4000])
    previous = _make_report(alcance=[1000, 2000])
    result = compare(current, previous)
    # Total reach doubled
    assert result.delta_pct["total_reach"] == pytest.approx(100.0)
