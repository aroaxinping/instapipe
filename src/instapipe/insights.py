"""Advanced insights: viral detection, duration analysis, hashtag analysis."""

import re
from collections import Counter

import pandas as pd

from instapipe.metrics import Report


def detect_virals(report: Report, threshold: float = 2.0) -> pd.DataFrame:
    """Flag reels that significantly outperformed the average.

    A reel is considered viral if its engagement rate is more than
    `threshold` standard deviations above the mean.

    Args:
        report: Report object from metrics.compute().
        threshold: Number of standard deviations above mean. Default: 2.0.

    Returns:
        DataFrame of viral reels with an 'outlier_score' column
        (how many std devs above the mean).
    """
    er = report.engagement_rate
    mean = er.mean()
    std = er.std()

    if std == 0:
        return pd.DataFrame()

    scores = (er - mean) / std
    mask = scores >= threshold

    virals = report.data[mask].copy()
    virals["outlier_score"] = scores[mask].round(2)
    virals["engagement_rate"] = er[mask]

    return virals.sort_values("outlier_score", ascending=False)


def analyze_duration(report: Report) -> pd.DataFrame | None:
    """Analyze correlation between Reel duration and engagement metrics.

    Groups reels into duration buckets and computes average engagement
    for each bucket.

    Args:
        report: Report object from metrics.compute().

    Returns:
        DataFrame with duration buckets and avg metrics, or None if
        no duration column is found.
    """
    df = report.data.copy()

    dur_col = None
    for candidate in ["duracion_seg", "duration", "duracion"]:
        if candidate in df.columns:
            dur_col = candidate
            break

    if dur_col is None:
        return None

    df["engagement_rate"] = report.engagement_rate
    df["save_rate"] = report.save_rate

    # Create duration buckets
    bins = [0, 15, 30, 60, 90, float("inf")]
    labels = ["<15s", "15-30s", "30-60s", "60-90s", "90s+"]
    df["duration_bucket"] = pd.cut(df[dur_col], bins=bins, labels=labels, right=True)

    result = df.groupby("duration_bucket", observed=True).agg(
        count=("engagement_rate", "count"),
        avg_engagement=("engagement_rate", "mean"),
        avg_save_rate=("save_rate", "mean"),
        avg_duration=(dur_col, "mean"),
    ).round(2)

    return result.reset_index()


def analyze_hashtags(report: Report, top_n: int = 20) -> pd.DataFrame | None:
    """Extract hashtags from descriptions and analyze which ones
    correlate with the best engagement.

    Args:
        report: Report object from metrics.compute().
        top_n: Number of top hashtags to return.

    Returns:
        DataFrame with hashtag, count, avg engagement rate, avg save rate.
        None if no description column is found.
    """
    df = report.data.copy()

    desc_col = None
    for candidate in ["descripcion", "descripcion_corta", "description"]:
        if candidate in df.columns:
            desc_col = candidate
            break

    if desc_col is None:
        return None

    df["engagement_rate"] = report.engagement_rate
    df["save_rate"] = report.save_rate

    # Extract hashtags from each description
    rows = []
    for idx, row in df.iterrows():
        text = str(row[desc_col])
        hashtags = re.findall(r"#(\w+)", text.lower())
        for tag in hashtags:
            rows.append({
                "hashtag": f"#{tag}",
                "engagement_rate": row["engagement_rate"],
                "save_rate": row["save_rate"],
            })

    if not rows:
        return None

    tags_df = pd.DataFrame(rows)
    result = tags_df.groupby("hashtag").agg(
        count=("engagement_rate", "count"),
        avg_engagement=("engagement_rate", "mean"),
        avg_save_rate=("save_rate", "mean"),
    ).round(2)

    result = result.sort_values("avg_engagement", ascending=False).head(top_n)
    return result.reset_index()
