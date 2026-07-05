"""Compute derived metrics from cleaned Instagram data."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class Report:
    """Container for computed metrics and the underlying data."""

    data: pd.DataFrame
    engagement_rate: pd.Series
    save_rate: pd.Series
    share_rate: pd.Series
    follower_conv_rate: pd.Series
    best_hour: int | None
    best_day: str | None
    top_performers: pd.DataFrame

    def summary(self) -> str:
        lines = [
            f"Total reels: {len(self.data)}",
            f"Avg engagement rate: {self.engagement_rate.mean():.2f}%",
            f"Avg save rate: {self.save_rate.mean():.2f}%",
            f"Avg share rate: {self.share_rate.mean():.2f}%",
            f"Avg follower conversion: {self.follower_conv_rate.mean():.2f}%",
        ]
        if self.best_hour is not None:
            lines.append(f"Best posting hour: {self.best_hour}:00")
        if self.best_day is not None:
            lines.append(f"Best posting day: {self.best_day}")
        lines.append(f"Top performers: {len(self.top_performers)} reels")
        return "\n".join(lines)


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find the first matching column name from a list of candidates.

    Checks for exact matches first, then substring matches.
    """
    # Exact match first
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    # Substring match
    for candidate in candidates:
        for col in df.columns:
            if candidate in col:
                return col
    return None


def compute(df: pd.DataFrame) -> Report:
    """Compute all Instagram metrics from a cleaned DataFrame.

    Expects columns for alcance (reach), visualizaciones (views),
    me_gustas (likes), comentarios (comments), guardados (saves),
    compartidos (shares) at minimum.

    Instagram metrics use reach (alcance) as the denominator for engagement,
    unlike TikTok which uses views. This is the standard in the industry
    because reach represents unique accounts, not repeated views.

    Args:
        df: Cleaned DataFrame from clean.normalize().

    Returns:
        Report with all computed metrics.
    """
    reach_col = _find_column(df, ["alcance", "reach"])
    views_col = _find_column(df, ["visualizaciones", "views", "reproduc"])
    likes_col = _find_column(df, ["me_gustas", "me_gusta", "likes"])
    comments_col = _find_column(df, ["comentarios", "comentario", "comments"])
    saves_col = _find_column(df, ["guardados", "guardado", "saves"])
    shares_col = _find_column(df, ["compartidos", "compartido", "shares"])
    followers_col = _find_column(
        df, ["seguidores_ganados", "seguidores_ganado", "followers"]
    )
    hour_col = _find_column(df, ["hora"])
    day_col = _find_column(df, ["dia_semana"])

    if reach_col is None and views_col is None:
        raise ValueError(
            "Could not find a reach or views column. "
            "Available columns: " + ", ".join(df.columns)
        )

    # Use reach as primary denominator, fall back to views
    denominator_col = reach_col or views_col
    denominator = df[denominator_col].fillna(0).replace(0, pd.NA)

    likes = df[likes_col].fillna(0) if likes_col else 0
    comments = df[comments_col].fillna(0) if comments_col else 0
    saves = df[saves_col].fillna(0) if saves_col else 0
    shares = df[shares_col].fillna(0) if shares_col else 0
    followers = df[followers_col].fillna(0) if followers_col else 0

    # Engagement rate: (likes + comments + saves + shares) / reach * 100
    engagement_rate = (
        (likes + comments + saves + shares) / denominator * 100
    ).fillna(0).round(2)

    # Save rate: saves / reach * 100
    save_rate = (saves / denominator * 100).fillna(0).round(2)

    # Share rate: shares / views * 100 (uses views, not reach)
    views_denom = denominator
    if views_col and views_col != denominator_col:
        views_denom = df[views_col].fillna(0).replace(0, pd.NA)
    share_rate = (shares / views_denom * 100).fillna(0).round(2)

    # Follower conversion rate: followers gained / reach * 100
    follower_conv_rate = (followers / denominator * 100).fillna(0).round(2)

    # Best posting hour
    best_hour = None
    if hour_col and hour_col in df.columns:
        hour_data = pd.DataFrame({
            "hour": df[hour_col],
            "engagement": engagement_rate,
        }).dropna()
        if not hour_data.empty:
            best_hour = int(
                hour_data.groupby("hour")["engagement"].median().idxmax()
            )

    # Best posting day
    best_day = None
    if day_col and day_col in df.columns:
        day_data = pd.DataFrame({
            "day": df[day_col],
            "engagement": engagement_rate,
        }).dropna()
        if not day_data.empty:
            best_day = str(
                day_data.groupby("day")["engagement"].median().idxmax()
            )

    # Top performers (above 90th percentile engagement)
    threshold = engagement_rate.quantile(0.9)
    top_performers = df[engagement_rate >= threshold].copy()

    return Report(
        data=df,
        engagement_rate=engagement_rate,
        save_rate=save_rate,
        share_rate=share_rate,
        follower_conv_rate=follower_conv_rate,
        best_hour=best_hour,
        best_day=best_day,
        top_performers=top_performers,
    )
