"""Compare two periods of Instagram data side by side."""

from dataclasses import dataclass

import pandas as pd

from instapipe.metrics import Report


@dataclass
class Comparison:
    """Container for period-over-period comparison."""

    current: dict
    previous: dict
    deltas: dict
    delta_pct: dict

    def summary(self) -> str:
        lines = ["Period comparison:"]
        for key in self.current:
            cur = self.current[key]
            prev = self.previous[key]
            d = self.deltas[key]
            pct = self.delta_pct[key]
            sign = "+" if d >= 0 else ""
            lines.append(f"  {key}: {prev:.2f} -> {cur:.2f} ({sign}{d:.2f}, {sign}{pct:.1f}%)")
        return "\n".join(lines)


def compare(current: Report, previous: Report) -> Comparison:
    """Compare two Report objects and compute deltas.

    Args:
        current: Report for the current period.
        previous: Report for the previous period.

    Returns:
        Comparison with current values, previous values, absolute deltas,
        and percentage deltas for key metrics.
    """
    metrics_to_compare = {
        "avg_engagement_rate": (current.engagement_rate.mean(), previous.engagement_rate.mean()),
        "avg_save_rate": (current.save_rate.mean(), previous.save_rate.mean()),
        "avg_share_rate": (current.share_rate.mean(), previous.share_rate.mean()),
        "avg_follower_conv": (current.follower_conv_rate.mean(), previous.follower_conv_rate.mean()),
        "total_reels": (float(len(current.data)), float(len(previous.data))),
    }

    # Add total views/reach if available
    for col_name, label in [("visualizaciones", "total_views"), ("alcance", "total_reach")]:
        cur_val = current.data[col_name].sum() if col_name in current.data.columns else 0
        prev_val = previous.data[col_name].sum() if col_name in previous.data.columns else 0
        metrics_to_compare[label] = (float(cur_val), float(prev_val))

    cur_dict = {}
    prev_dict = {}
    deltas = {}
    delta_pct = {}

    for key, (cur, prev) in metrics_to_compare.items():
        cur_dict[key] = cur
        prev_dict[key] = prev
        deltas[key] = cur - prev
        delta_pct[key] = ((cur - prev) / prev * 100) if prev != 0 else 0.0

    return Comparison(
        current=cur_dict,
        previous=prev_dict,
        deltas=deltas,
        delta_pct=delta_pct,
    )
