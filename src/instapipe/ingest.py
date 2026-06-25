"""Load Instagram export files from Meta Business Suite."""

from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".xlsx", ".csv"}

# Meta Business Suite daily CSVs use utf-16 encoding with a special header.
# The content/posts CSV uses utf-8-sig with a standard table structure.
# This module handles both transparently.


def load(path: str | Path) -> pd.DataFrame:
    """Load an Instagram analytics export file.

    Supports:
        - Content/Posts CSV (utf-8-sig, standard table with columns like
          Descripcion, Visualizaciones, Alcance, etc.)
        - Daily metric CSVs from Meta Business Suite (utf-16, two-column
          date/value format with a 3-line header)
        - XLSX files with one or more sheets

    Args:
        path: Path to the CSV or XLSX file exported from Meta Business Suite.

    Returns:
        Raw DataFrame with the original columns and data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not supported.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {ext}. Use one of: {SUPPORTED_EXTENSIONS}"
        )

    if ext == ".xlsx":
        return pd.read_excel(path, engine="openpyxl")

    # Try utf-8-sig first (content/posts CSV), fall back to utf-16 (daily metrics)
    return _load_csv(path)


def load_daily(path: str | Path, metric_name: str) -> pd.DataFrame:
    """Load a daily metric CSV exported from Meta Business Suite.

    These files use utf-16 encoding and have a 3-line header before the data.
    Each row is a date/value pair like: "2026-03-01T...","1234"

    Args:
        path: Path to the daily metric CSV (e.g. Visualizaciones.csv).
        metric_name: Name for the value column (e.g. "visualizaciones").

    Returns:
        DataFrame with columns [fecha, <metric_name>], indexed by fecha.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    rows = []
    with open(path, encoding="utf-16") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Skip the first 3 lines (sep=, title, header)
    for line in lines[3:]:
        line = line.strip('"')
        parts = line.split('","')
        if len(parts) == 2:
            try:
                date_str = parts[0].split("T")[0]
                value = int(parts[1].replace('"', "").replace(",", ""))
                rows.append({"fecha": date_str, metric_name: value})
            except ValueError:
                continue

    df = pd.DataFrame(rows)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def _load_csv(path: Path) -> pd.DataFrame:
    """Try to load a CSV with utf-8-sig first, then utf-16."""
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        if len(df.columns) > 1:
            return df
    except (UnicodeDecodeError, pd.errors.ParserError):
        pass

    # Fall back to utf-16 (daily metrics format)
    return pd.read_csv(path, encoding="utf-16")
