"""Export results and generate visualizations."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from instapipe.metrics import Report


sns.set_theme(style="whitegrid", palette="muted")


def to_csv(report: Report, path: str | Path) -> None:
    """Export the report data with computed metrics to CSV."""
    df = report.data.copy()
    df["engagement_rate"] = report.engagement_rate
    df["save_rate"] = report.save_rate
    df["share_rate"] = report.share_rate
    df["follower_conv_rate"] = report.follower_conv_rate
    df.to_csv(path, index=False)


def to_json(report: Report, path: str | Path) -> None:
    """Export the report data with computed metrics to JSON."""
    df = report.data.copy()
    df["engagement_rate"] = report.engagement_rate
    df["save_rate"] = report.save_rate
    df["share_rate"] = report.share_rate
    df["follower_conv_rate"] = report.follower_conv_rate
    df.to_json(path, orient="records", indent=2, date_format="iso")


def plot_engagement(report: Report, save_to: str | Path | None = None) -> None:
    """Plot engagement rate distribution."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(report.engagement_rate, bins=20, edgecolor="black", alpha=0.7,
            color="#E1306C")
    ax.set_xlabel("Engagement Rate (%)")
    ax.set_ylabel("Number of Reels")
    ax.set_title("Engagement Rate Distribution")
    ax.axvline(
        report.engagement_rate.median(),
        color="#405DE6",
        linestyle="--",
        label=f"Median: {report.engagement_rate.median():.2f}%",
    )
    ax.legend()
    fig.tight_layout()

    if save_to:
        fig.savefig(save_to, dpi=150)
        plt.close(fig)
    else:
        plt.show()


def plot_best_hours(report: Report, save_to: str | Path | None = None) -> None:
    """Plot median engagement by hour of day."""
    if "hora" not in report.data.columns:
        raise ValueError("No 'hora' column found. Cannot plot by hour.")

    hour_data = pd.DataFrame({
        "hour": report.data["hora"],
        "engagement": report.engagement_rate,
    }).dropna()
    hourly = hour_data.groupby("hour")["engagement"].median()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(hourly.index, hourly.values, edgecolor="black", alpha=0.7,
           color="#C13584")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Median Engagement Rate (%)")
    ax.set_title("Best Posting Hours")
    ax.set_xticks(range(24))
    fig.tight_layout()

    if save_to:
        fig.savefig(save_to, dpi=150)
        plt.close(fig)
    else:
        plt.show()


def plot_save_rate(report: Report, save_to: str | Path | None = None) -> None:
    """Plot save rate vs engagement rate scatter."""
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        report.save_rate,
        report.engagement_rate,
        c=report.data.get("visualizaciones", report.engagement_rate),
        cmap="RdPu",
        alpha=0.7,
        edgecolors="black",
        linewidths=0.5,
        s=80,
    )
    ax.set_xlabel("Save Rate (%)")
    ax.set_ylabel("Engagement Rate (%)")
    ax.set_title("Save Rate vs Engagement Rate")
    fig.colorbar(scatter, ax=ax, label="Views")
    fig.tight_layout()

    if save_to:
        fig.savefig(save_to, dpi=150)
        plt.close(fig)
    else:
        plt.show()


def plot_top_reels(report: Report, n: int = 10,
                   save_to: str | Path | None = None) -> None:
    """Plot top N reels by engagement rate."""
    df = report.data.copy()
    df["engagement_rate"] = report.engagement_rate

    label_col = None
    for candidate in ["descripcion_corta", "descripcion", "title"]:
        if candidate in df.columns:
            label_col = candidate
            break

    top = df.nlargest(n, "engagement_rate").sort_values("engagement_rate")

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = top[label_col].str[:30] + "..." if label_col else top.index.astype(str)
    colors = plt.cm.RdPu(top["engagement_rate"] / top["engagement_rate"].max())
    ax.barh(range(len(top)), top["engagement_rate"], color=colors,
            edgecolor="black", alpha=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Engagement Rate (%)")
    ax.set_title(f"Top {n} Reels by Engagement Rate")
    fig.tight_layout()

    if save_to:
        fig.savefig(save_to, dpi=150)
        plt.close(fig)
    else:
        plt.show()
