"""Tests for instapipe.classify module."""

import pandas as pd

from instapipe.classify import classify_topic, add_topics, DEFAULT_RULES


def test_classify_sql():
    assert classify_topic("POV: explaining SQL joins #sql") == "SQL"


def test_classify_python():
    assert classify_topic("how to read a CSV in pandas #python") == "Python"


def test_classify_terminal():
    assert classify_topic("custom bash aliases for your terminal") == "Terminal/Bash"


def test_classify_personal_humor():
    assert classify_topic("mi novio me dice que paso demasiado tiempo programando") == "Personal humor"


def test_classify_tech_humor():
    assert classify_topic("POV: primer dia en informatica #techhumor") == "Tech humor"


def test_classify_other():
    assert classify_topic("random video about nothing specific") == "Other"


def test_classify_hashtag_stripped():
    assert classify_topic("#python tutorial") == "Python"


def test_classify_custom_rules():
    rules = [("Cooking", ["recipe", "cook"])]
    assert classify_topic("my best recipe ever", rules) == "Cooking"
    assert classify_topic("random text", rules) == "Other"


def test_add_topics_to_dataframe():
    df = pd.DataFrame({
        "descripcion": [
            "SQL joins explained #sql",
            "bash tips #terminal",
            "random stuff",
        ],
        "visualizaciones": [1000, 2000, 500],
    })
    result = add_topics(df)
    assert "tema" in result.columns
    assert result["tema"].iloc[0] == "SQL"
    assert result["tema"].iloc[1] == "Terminal/Bash"
    assert result["tema"].iloc[2] == "Other"


def test_add_topics_no_description_col():
    df = pd.DataFrame({"views": [100, 200]})
    result = add_topics(df)
    assert (result["tema"] == "Other").all()
