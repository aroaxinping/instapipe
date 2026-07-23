"""
Streamlit demo for instapipe — runs the full pipeline on the bundled sample data.

Run: streamlit run streamlit_app.py
"""

import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from instapipe import ingest, clean, metrics, dashboard
from instapipe.classify import add_topics

st.set_page_config(page_title="instapipe demo", layout="wide", page_icon="📸")

_root = Path(__file__).parent
SAMPLE_PATH = _root / "examples" / "sample_data.csv"


@st.cache_data
def run_pipeline():
    raw = ingest.load(SAMPLE_PATH)
    df = clean.normalize(raw)
    df = add_topics(df)
    report = metrics.compute(df)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        dashboard.build_dashboard(report, f.name)
        html = Path(f.name).read_text()

    return report, html


report, dashboard_html = run_pipeline()

st.sidebar.title("instapipe")
st.sidebar.markdown("Data pipeline for Instagram analytics")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "This demo runs the full pipeline (ingest → clean → classify → metrics) "
    "on the sample dataset bundled with the package — no Instagram account needed."
)
st.sidebar.markdown(
    "[View on GitHub](https://github.com/aroaxinping/instapipe) · "
    "[PyPI](https://pypi.org/project/instapipe/)"
)

st.title("instapipe — sample analysis")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Reels analyzed", len(report.data))
col2.metric("Avg. engagement rate", f"{report.engagement_rate.mean():.2f}%")
col3.metric("Avg. save rate", f"{report.save_rate.mean():.2f}%")
col4.metric("Avg. follower conversion", f"{report.follower_conv_rate.mean():.2f}%")

st.markdown("### Interactive dashboard")
components.html(dashboard_html, height=1400, scrolling=True)

st.markdown("### Top performers")
st.dataframe(report.top_performers, width="stretch", hide_index=True)
