"""Classify Instagram Reels by topic based on description and hashtags."""

import re

import pandas as pd


# Default topic rules: list of (topic_name, keywords).
# Checked in order — first match wins.
DEFAULT_RULES = [
    ("SQL",                  ["sql", "select", "query", "queries", "database"]),
    ("Python",               ["python", "pyth", "pandas", "jupyter", "numpy"]),
    ("Terminal/Bash",        ["terminal", "bash", "shell", "cli", "command line"]),
    ("Excel",                ["excel", "spreadsheet", "hoja de calculo"]),
    ("Git",                  ["git", "github", "commit", "merge", "branch"]),
    ("Linux",                ["linux", "ubuntu", "debian", "arch"]),
    ("Data Science",         ["datascience", "cienciadedatos", "machinelearning", "data science", "ml"]),
    ("Best practices",       ["readme", "clean code", "buenas practicas", "best practice"]),
    ("Personal humor",       ["chico", "novio", "pareja", "relaci", "womanin", "apodo", "crush"]),
    ("Programming general",  ["programad", "codigo", "code", "developer", "coding", "dev"]),
    ("Tech humor",           ["informatic", "techhumor", "techgirl", "tech humor"]),
]


def classify_topic(description: str, rules: list[tuple[str, list[str]]] | None = None) -> str:
    """Classify a single description into a topic.

    Args:
        description: The Reel description text (including hashtags).
        rules: Optional custom rules as [(topic, [keywords])].
               Defaults to DEFAULT_RULES.

    Returns:
        The matched topic name, or "Other" if no rule matches.
    """
    if rules is None:
        rules = DEFAULT_RULES

    text = str(description).lower()
    # Remove hashtag symbols so "#python" matches "python"
    text = text.replace("#", "")

    for topic, keywords in rules:
        if any(kw in text for kw in keywords):
            return topic

    return "Other"


def add_topics(df: pd.DataFrame, description_col: str = "descripcion",
               rules: list[tuple[str, list[str]]] | None = None) -> pd.DataFrame:
    """Add a 'tema' column to a DataFrame based on description classification.

    Args:
        df: DataFrame with a description column.
        description_col: Name of the column containing descriptions.
        rules: Optional custom classification rules.

    Returns:
        DataFrame with a new 'tema' column.
    """
    df = df.copy()
    col = description_col if description_col in df.columns else None

    # Try common alternatives
    if col is None:
        for candidate in ["descripcion", "descripcion_corta", "description"]:
            if candidate in df.columns:
                col = candidate
                break

    if col is None:
        df["tema"] = "Other"
        return df

    df["tema"] = df[col].apply(lambda x: classify_topic(x, rules))
    return df
