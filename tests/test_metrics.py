"""Tests for instapipe.metrics module."""

import pandas as pd
import pytest

from instapipe.metrics import compute


def _make_df(**kwargs):
    return pd.DataFrame(kwargs)


def test_compute_basic():
    df = _make_df(
        alcance=[1000, 2000, 500],
        visualizaciones=[1500, 3000, 800],
        me_gustas=[100, 300, 50],
        comentarios=[10, 30, 5],
        guardados=[20, 60, 10],
        compartidos=[5, 15, 2],
    )
    report = compute(df)
    assert len(report.engagement_rate) == 3
    # ER = (100+10+20+5) / 1000 * 100 = 13.5%
    assert report.engagement_rate.iloc[0] == pytest.approx(13.5)


def test_compute_save_rate():
    df = _make_df(
        alcance=[1000, 2000],
        me_gustas=[100, 200],
        comentarios=[10, 20],
        guardados=[50, 100],
        compartidos=[5, 10],
    )
    report = compute(df)
    # Save rate = 50 / 1000 * 100 = 5.0%
    assert report.save_rate.iloc[0] == pytest.approx(5.0)


def test_compute_share_rate_uses_views():
    df = _make_df(
        alcance=[1000],
        visualizaciones=[2000],
        me_gustas=[100],
        comentarios=[10],
        guardados=[20],
        compartidos=[40],
    )
    report = compute(df)
    # Share rate = 40 / 2000 * 100 = 2.0%
    assert report.share_rate.iloc[0] == pytest.approx(2.0)


def test_compute_follower_conv_rate():
    df = _make_df(
        alcance=[1000, 2000],
        me_gustas=[100, 200],
        comentarios=[10, 20],
        guardados=[20, 40],
        compartidos=[5, 10],
        seguidores_ganados=[10, 30],
    )
    report = compute(df)
    # Follower conv = 10 / 1000 * 100 = 1.0%
    assert report.follower_conv_rate.iloc[0] == pytest.approx(1.0)


def test_compute_no_reach_or_views():
    df = _make_df(something=[1, 2, 3])
    with pytest.raises(ValueError, match="Could not find a reach or views column"):
        compute(df)


def test_compute_with_hour_and_day():
    df = _make_df(
        alcance=[1000, 2000, 500],
        me_gustas=[100, 300, 50],
        comentarios=[10, 30, 5],
        guardados=[20, 60, 10],
        compartidos=[5, 15, 2],
        hora=[14, 14, 20],
        dia_semana=["Monday", "Monday", "Friday"],
    )
    report = compute(df)
    assert report.best_hour is not None
    assert report.best_day is not None


def test_top_performers():
    alcance = [100] * 9 + [10000]
    me_gustas = [5] * 9 + [5000]
    df = _make_df(
        alcance=alcance,
        me_gustas=me_gustas,
        comentarios=[0] * 10,
        guardados=[0] * 10,
        compartidos=[0] * 10,
    )
    report = compute(df)
    assert len(report.top_performers) >= 1


def test_summary_output():
    df = _make_df(
        alcance=[1000],
        me_gustas=[100],
        comentarios=[10],
        guardados=[20],
        compartidos=[5],
    )
    report = compute(df)
    summary = report.summary()
    assert "Total reels" in summary
    assert "engagement rate" in summary.lower()
    assert "save rate" in summary.lower()
