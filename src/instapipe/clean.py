"""Normalize and clean raw Instagram data."""

import pandas as pd


# Column name mapping: Meta Business Suite Spanish export -> internal names.
# Supports both Spanish and English column names.
COLUMN_MAP = {
    "descripción": "descripcion",
    "descripcion": "descripcion",
    "description": "descripcion",
    "duración (segundos)": "duracion_seg",
    "duracion (segundos)": "duracion_seg",
    "duration (seconds)": "duracion_seg",
    "hora de publicación": "hora_publicacion",
    "hora de publicacion": "hora_publicacion",
    "publish time": "hora_publicacion",
    "enlace permanente": "enlace",
    "permalink": "enlace",
    "tipo de publicación": "tipo",
    "tipo de publicacion": "tipo",
    "post type": "tipo",
    "visualizaciones": "visualizaciones",
    "views": "visualizaciones",
    "alcance": "alcance",
    "reach": "alcance",
    "me gusta": "me_gustas",
    "likes": "me_gustas",
    "veces que se ha compartido": "compartidos",
    "shares": "compartidos",
    "seguidores": "seguidores_ganados",
    "followers": "seguidores_ganados",
    "comentarios": "comentarios",
    "comments": "comentarios",
    "veces guardado": "guardados",
    "saves": "guardados",
}


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize a raw Instagram content/posts export.

    Steps:
        1. Map known column names to internal snake_case names.
        2. Parse publication datetime and extract date, hour, day of week.
        3. Convert numeric columns, fill NaN with 0.
        4. Drop rows where all values are null.

    Args:
        df: Raw DataFrame from ingest.load().

    Returns:
        Cleaned DataFrame ready for metrics computation.
    """
    df = df.copy()

    # Normalize column names: lowercase, strip whitespace
    df.columns = df.columns.str.strip().str.lower()

    # Apply known column mapping
    df = df.rename(columns=COLUMN_MAP)

    # If columns still don't match, try generic snake_case normalization
    df.columns = (
        df.columns.str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w]", "_", regex=True)
    )

    # Parse publication datetime
    if "hora_publicacion" in df.columns:
        df["fecha_dt"] = pd.to_datetime(
            df["hora_publicacion"], format="%m/%d/%Y %H:%M", errors="coerce"
        )
        # Try ISO format if the first attempt failed
        if df["fecha_dt"].isna().all():
            df["fecha_dt"] = pd.to_datetime(
                df["hora_publicacion"], errors="coerce"
            )
        df["fecha"] = df["fecha_dt"].dt.strftime("%Y-%m-%d")
        df["hora"] = df["fecha_dt"].dt.hour
        df["dia_semana"] = df["fecha_dt"].dt.day_name()

    # Convert numeric columns
    numeric_cols = [
        "visualizaciones", "alcance", "me_gustas", "compartidos",
        "seguidores_ganados", "comentarios", "guardados", "duracion_seg",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ""), errors="coerce"
            ).fillna(0).astype(int)

    # Drop completely empty rows
    df = df.dropna(how="all").reset_index(drop=True)

    return df
