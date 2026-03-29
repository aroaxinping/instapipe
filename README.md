# instapipe

Data pipeline for Instagram analytics. Import your exported data from Meta Business Suite, clean it, compute real metrics, and visualize what actually works.

No APIs, no scraping, no third-party tokens. Just your Instagram export files (CSV/XLSX) and Python.

---

## Architecture

```
instapipe follows a classic ETL pipeline structure:

  Export (Meta Business Suite CSV/XLSX)
        |
        v
  +-----------+
  |  ingest   |  --> Load and validate raw export files (utf-8-sig & utf-16)
  +-----------+
        |
        v
  +-----------+
  |  clean    |  --> Normalize columns (ES/EN), fix types, parse dates
  +-----------+
        |
        v
  +-----------+
  |  metrics  |  --> Compute engagement, save rate, share rate, conversion
  +-----------+
        |
        v
  +-----------+
  |  output   |  --> Dataframes, CSV export, visualizations
  +-----------+
```

### Modules

| Module | What it does |
|---|---|
| `instapipe.ingest` | Reads Instagram export files (CSV, XLSX). Handles Meta Business Suite's utf-16 daily CSVs and utf-8-sig content CSVs transparently. |
| `instapipe.clean` | Maps column names (Spanish/English) to internal names, converts date/number types, parses publication time into date, hour, and day of week. |
| `instapipe.metrics` | Computes derived metrics: engagement rate (based on reach), save rate, share rate, follower conversion rate, best posting hour/day. |
| `instapipe.output` | Exports results to CSV/JSON. Generates matplotlib/seaborn visualizations (engagement distribution, best hours, save rate scatter, top reels). |

---

## Prerequisites

Before using instapipe, you need your own Instagram data. Here's what you need and how to get it:

### 1. Instagram Professional Account

You need a **Creator** or **Business** account on Instagram (the free personal account doesn't give you analytics).

**How to switch:**
1. Open Instagram > Settings > Account type and tools > Switch to professional account
2. Choose **Creator** (recommended for content creators) or **Business**
3. Pick a category that fits you (e.g. Digital Creator, Personal Blog)
4. Done — you now have access to Instagram Insights

### 2. Meta Business Suite access

Meta Business Suite is where you export your data as CSV files. It's free and linked to your professional Instagram account.

**How to set it up:**
1. Go to [business.facebook.com](https://business.facebook.com)
2. Log in with the Facebook account linked to your Instagram (if you don't have one linked, Instagram will prompt you to create or connect one when you switch to a professional account)
3. In the left sidebar, click **Insights**
4. Make sure your Instagram account appears — if it does, you're ready to export

### 3. Export your data

instapipe works with two types of exports from Meta Business Suite:

**Content/Posts CSV** (the main one):
1. Meta Business Suite > Insights > Content
2. Select the date range you want to analyze
3. Click **Export** (top right) > CSV
4. This gives you a file like `Contenido_Posts_Feb24_Mar23.csv` with one row per Reel/post, including views, reach, likes, comments, saves, shares, followers gained, etc.

**Daily metric CSVs** (optional, for trend analysis):
1. Meta Business Suite > Insights > Overview
2. For each metric (Reach, Views, Followers, etc.), click the **Export** button
3. Each export is a separate CSV file (e.g. `Alcance.csv`, `Visualizaciones.csv`, `Seguidores.csv`)
4. These files use utf-16 encoding — instapipe handles this automatically

### 4. Python >= 3.10

```bash
python3 --version  # Should be 3.10 or higher
```

Dependencies (installed automatically): pandas, openpyxl, matplotlib, seaborn

---

## Installation

```bash
# Clone the repo
git clone https://github.com/aroaxinping/instapipe.git
cd instapipe

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with all dependencies
pip install -e .
```

---

## Usage

### 1. Export your Instagram data

Go to **Meta Business Suite** > Insights > Content > Export. Save the CSV file.

For daily metrics (reach, views, followers, etc.), go to Insights > Overview > Export each metric individually. These are saved as utf-16 encoded CSVs.

### 2. Run the pipeline

```python
from instapipe import ingest, clean, metrics, output

# Load your content/posts export
raw = ingest.load("path/to/Contenido_Posts.csv")

# Clean and normalize
df = clean.normalize(raw)

# Compute metrics
report = metrics.compute(df)

# Print summary
print(report.summary())

# Export results
output.to_csv(report, "results.csv")

# Generate visualizations
output.plot_engagement(report, save_to="engagement.png")
output.plot_best_hours(report, save_to="best_hours.png")
output.plot_save_rate(report, save_to="save_rate.png")
output.plot_top_reels(report, save_to="top_reels.png")
```

### 3. Quick run (CLI)

```bash
instapipe analyze path/to/Contenido_Posts.csv --output results/
```

This runs the full pipeline and saves CSV + charts to the output directory.

### 4. Daily metrics (optional)

For daily metric CSVs exported individually from Meta Business Suite:

```python
from instapipe.ingest import load_daily

views = load_daily("Visualizaciones.csv", "visualizaciones")
reach = load_daily("Alcance.csv", "alcance")
followers = load_daily("Seguidores.csv", "seguidores_ganados")
```

---

## Available metrics

| Metric | Formula | Why this denominator |
|---|---|---|
| Engagement rate | (likes + comments + saves + shares) / reach x 100 | Reach = unique accounts. Industry standard for Instagram. |
| Save rate | saves / reach x 100 | Saves are the strongest quality signal on Instagram. |
| Share rate | shares / views x 100 | Shares drive distribution, measured against total impressions. |
| Follower conversion | followers gained / reach x 100 | How efficiently a Reel converts viewers into followers. |
| Best posting hour | Hour with highest median engagement | Based on your own data, not generic advice. |
| Best posting day | Day of week with highest median engagement | Same — your audience, your data. |
| Top performers | Reels above 90th percentile engagement | Focus on what actually works for you. |

---

## Instagram vs TikTok metrics

If you also use TikTok, check out [tokpipe](https://github.com/aroaxinping/tokpipe) — same philosophy, adapted for TikTok exports.

Key differences:
- **Instagram** uses **reach** (unique accounts) as the engagement denominator. **TikTok** uses **views** (total plays).
- Instagram exports come from **Meta Business Suite** (utf-16 daily CSVs + utf-8-sig content CSVs). TikTok exports come from **TikTok Studio** (XLSX/CSV).
- Instagram has **saves** as a key metric. TikTok has **watch time** and **completion rate**.

---

## Project structure

```
instapipe/
  src/
    instapipe/
      __init__.py       # Package init, version
      ingest.py         # Load Meta Business Suite exports
      clean.py          # Normalize and clean data
      metrics.py        # Compute derived metrics
      output.py         # Export and visualize
      cli.py            # Command-line interface
  tests/
    test_ingest.py
    test_clean.py
    test_metrics.py
  examples/
    basic_analysis.py   # Minimal working example
  pyproject.toml        # Package config
  LICENSE
  CONTRIBUTING.md
  README.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT. See [LICENSE](LICENSE).
