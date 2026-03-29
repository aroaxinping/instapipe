"""Tests for instapipe.clean module."""

import pandas as pd

from instapipe.clean import normalize


def test_normalize_maps_spanish_columns():
    df = pd.DataFrame({
        "Descripción": ["test"],
        "Visualizaciones": [1000],
        "Alcance": [800],
        "Me gusta": [50],
        "Comentarios": [5],
        "Veces guardado": [10],
        "Veces que se ha compartido": [3],
        "Seguidores": [2],
        "Hora de publicación": ["03/01/2026 14:00"],
    })
    result = normalize(df)
    assert "descripcion" in result.columns
    assert "visualizaciones" in result.columns
    assert "alcance" in result.columns
    assert "me_gustas" in result.columns
    assert "guardados" in result.columns
    assert "compartidos" in result.columns


def test_normalize_maps_english_columns():
    df = pd.DataFrame({
        "Description": ["test"],
        "Views": [1000],
        "Reach": [800],
        "Likes": [50],
        "Comments": [5],
        "Saves": [10],
        "Shares": [3],
        "Followers": [2],
    })
    result = normalize(df)
    assert "descripcion" in result.columns
    assert "visualizaciones" in result.columns
    assert "alcance" in result.columns
    assert "me_gustas" in result.columns


def test_normalize_converts_numeric():
    df = pd.DataFrame({
        "Visualizaciones": ["1,000", "2,000"],
        "Alcance": ["800", "1,500"],
    })
    result = normalize(df)
    assert result["visualizaciones"].iloc[0] == 1000
    assert result["alcance"].iloc[1] == 1500


def test_normalize_parses_datetime():
    df = pd.DataFrame({
        "Hora de publicación": ["03/01/2026 14:00", "03/02/2026 18:30"],
        "Visualizaciones": [100, 200],
    })
    result = normalize(df)
    assert "fecha" in result.columns
    assert "hora" in result.columns
    assert "dia_semana" in result.columns
    assert result["hora"].iloc[0] == 14
    assert result["hora"].iloc[1] == 18


def test_normalize_fills_numeric_nulls_with_zero():
    df = pd.DataFrame({
        "Visualizaciones": [100, None, 200],
        "Alcance": [80, None, 150],
    })
    result = normalize(df)
    # NaN in numeric columns is filled with 0, not dropped
    assert len(result) == 3
    assert result["visualizaciones"].iloc[1] == 0


def test_normalize_drops_fully_empty_rows():
    df = pd.DataFrame({
        "col_a": ["hello", None, "world"],
        "col_b": ["foo", None, "bar"],
    })
    result = normalize(df)
    assert len(result) == 2
