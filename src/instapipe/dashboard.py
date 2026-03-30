"""Generate an interactive HTML dashboard with Plotly."""

from pathlib import Path

import pandas as pd

from instapipe.metrics import Report


def build_dashboard(report: Report, save_to: str | Path) -> None:
    """Generate a self-contained HTML dashboard from a Report.

    Creates a single HTML file with 6 interactive Plotly charts:
    1. Engagement rate by Reel (bar)
    2. Save rate vs Engagement rate (scatter)
    3. Top Reels by views (horizontal bar)
    4. Best posting hours (bar)
    5. Performance by topic (bar) — requires 'tema' column
    6. Follower conversion rate by Reel (bar)

    Args:
        report: Report object from metrics.compute().
        save_to: Path for the output HTML file.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        raise ImportError(
            "plotly is required for dashboards. Install it with: pip install plotly"
        )

    df = report.data.copy()
    df["engagement_rate"] = report.engagement_rate
    df["save_rate"] = report.save_rate
    df["share_rate"] = report.share_rate
    df["follower_conv_rate"] = report.follower_conv_rate

    # Short labels for charts
    label_col = None
    for candidate in ["descripcion_corta", "descripcion", "description"]:
        if candidate in df.columns:
            label_col = candidate
            break
    if label_col:
        df["label"] = df[label_col].astype(str).str[:30] + "..."
    else:
        df["label"] = [f"Reel {i+1}" for i in range(len(df))]

    # Colors
    PINK = "#E1306C"
    PURPLE = "#833AB4"
    DARK = "#1a1a2e"
    CARD = "#16213e"
    LIGHT = "#e2e8f0"
    MUTED = "#94a3b8"
    ACCENT = "#f093fb"

    # Determine subplot layout
    has_topics = "tema" in df.columns and df["tema"].nunique() > 1
    rows, cols = (3, 2) if has_topics else (3, 2)

    titles = [
        "Engagement Rate by Reel (%)",
        "Save Rate vs Engagement Rate",
        "Top Reels by Views",
        "Best Posting Hours",
    ]
    if has_topics:
        titles.append("Performance by Topic")
    titles.append("Follower Conversion Rate (%)")

    # Pad titles to 6
    while len(titles) < 6:
        titles.append("")

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=titles[:6],
        vertical_spacing=0.10,
        horizontal_spacing=0.10,
    )

    # 1. Engagement rate by reel
    sorted_er = df.sort_values("engagement_rate", ascending=True)
    fig.add_trace(go.Bar(
        x=sorted_er["engagement_rate"],
        y=sorted_er["label"],
        orientation="h",
        marker=dict(color=sorted_er["engagement_rate"],
                    colorscale=[[0, ACCENT], [1, PINK]], showscale=False),
        name="ER",
    ), row=1, col=1)

    # 2. Save rate vs engagement scatter
    fig.add_trace(go.Scatter(
        x=df["save_rate"],
        y=df["engagement_rate"],
        mode="markers",
        marker=dict(
            size=10,
            color=df.get("visualizaciones", df["engagement_rate"]),
            colorscale=[[0, ACCENT], [1, PINK]],
            showscale=True,
            colorbar=dict(title="Views", x=1.01, thickness=8, len=0.25, y=0.83),
        ),
        text=df["label"],
        name="ER vs Save",
    ), row=1, col=2)

    # 3. Top reels by views
    views_col = None
    for candidate in ["visualizaciones", "views"]:
        if candidate in df.columns:
            views_col = candidate
            break
    if views_col:
        top = df.nlargest(10, views_col).sort_values(views_col)
        fig.add_trace(go.Bar(
            x=top[views_col],
            y=top["label"],
            orientation="h",
            marker=dict(color=top[views_col],
                        colorscale=[[0, ACCENT], [1, PINK]], showscale=False),
            text=[f'{v/1000:.0f}K' for v in top[views_col]],
            textposition="outside",
            name="Views",
        ), row=2, col=1)

    # 4. Best posting hours
    if "hora" in df.columns:
        hour_data = pd.DataFrame({
            "hour": df["hora"], "engagement": df["engagement_rate"],
        }).dropna()
        if not hour_data.empty:
            hourly = hour_data.groupby("hour")["engagement"].median()
            fig.add_trace(go.Bar(
                x=list(hourly.index),
                y=list(hourly.values),
                marker=dict(color=list(hourly.values),
                            colorscale=[[0, PURPLE], [1, PINK]], showscale=False),
                name="Hours",
            ), row=2, col=2)

    # 5. Performance by topic
    if has_topics:
        tema_stats = df.groupby("tema").agg(
            count=("engagement_rate", "count"),
            er_medio=("engagement_rate", "mean"),
        ).reset_index()
        tema_stats = tema_stats[tema_stats["count"] > 0].sort_values("er_medio")
        fig.add_trace(go.Bar(
            x=tema_stats["er_medio"],
            y=tema_stats["tema"],
            orientation="h",
            marker=dict(color=tema_stats["er_medio"],
                        colorscale=[[0, "#a18cd1"], [1, "#fbc2eb"]], showscale=False),
            text=[f'{v:.1f}%' for v in tema_stats["er_medio"]],
            textposition="outside",
            name="Topic ER",
        ), row=3, col=1)

    # 6. Follower conversion rate
    sorted_fc = df.sort_values("follower_conv_rate", ascending=True)
    fig.add_trace(go.Bar(
        x=sorted_fc["follower_conv_rate"],
        y=sorted_fc["label"],
        orientation="h",
        marker=dict(color=sorted_fc["follower_conv_rate"],
                    colorscale=[[0, "#4facfe"], [1, "#00f2fe"]], showscale=False),
        name="Follower Conv",
    ), row=3, col=2)

    # Layout
    total_reels = len(df)
    avg_er = df["engagement_rate"].mean()
    avg_save = df["save_rate"].mean()

    fig.update_layout(
        height=1300,
        paper_bgcolor=DARK,
        plot_bgcolor=CARD,
        font=dict(color=LIGHT, family="Inter, system-ui, sans-serif", size=11),
        title=dict(
            text=f"<b>Instagram Analytics Dashboard</b> — {total_reels} Reels | "
                 f"Avg ER: {avg_er:.1f}% | Avg Save Rate: {avg_save:.1f}%",
            font=dict(size=18, color=LIGHT),
            x=0.5,
        ),
        showlegend=False,
        margin=dict(t=80, b=40, l=20, r=20),
    )

    for i in range(1, 4):
        for j in range(1, 3):
            fig.update_xaxes(showgrid=True, gridcolor="#2d3748", gridwidth=0.5,
                             zeroline=False, linecolor="#4a5568",
                             tickfont=dict(color=MUTED, size=9), row=i, col=j)
            fig.update_yaxes(showgrid=False, zeroline=False, linecolor="#4a5568",
                             tickfont=dict(color=MUTED, size=9), row=i, col=j)

    for ann in fig.layout.annotations:
        ann.font.color = LIGHT
        ann.font.size = 12

    fig.update_xaxes(title_text="Save Rate (%)", row=1, col=2)
    fig.update_yaxes(title_text="Engagement Rate (%)", row=1, col=2)

    # Export
    save_to = Path(save_to)
    save_to.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(save_to), include_plotlyjs="cdn", full_html=True)
