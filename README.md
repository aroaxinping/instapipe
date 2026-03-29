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

## Requirements

### 1. Instagram Professional Account (Creator or Business)

The free personal Instagram account does not give you access to analytics. You need to switch to a **Professional** account — it's free and takes 30 seconds.

**How to switch:**
1. Open Instagram > your profile > **Settings and privacy**
2. Scroll to **Account type and tools** > **Switch to professional account**
3. Choose **Creator** (recommended for content creators) or **Business**
4. Pick a category that describes you (e.g. Digital Creator, Personal Blog, Entrepreneur)
5. Tap **Done**

Once you switch, Instagram starts collecting analytics for your account. You'll see a new **Insights** button on your profile and on each post.

> **Note:** Instagram only starts tracking metrics from the moment you switch. You won't have historical data from before the switch. If you just switched, wait at least 7 days and publish some content before exporting — otherwise you'll have an empty file.

### 2. Meta Business Suite (free)

Meta Business Suite is the web tool where you export your Instagram data as CSV files. It's free, provided by Meta, and automatically available when you have a professional Instagram account.

**How to access it:**
1. Go to [business.facebook.com](https://business.facebook.com) from a desktop browser
2. Log in with the **Facebook account linked to your Instagram** — if you don't have one linked, Instagram prompts you to create or connect a Facebook Page when you switch to a professional account
3. Once inside, click **Insights** in the left sidebar
4. Make sure your Instagram account appears at the top — if it does, you're ready to export

> **Don't have a Facebook account linked?** Go to Instagram > Settings > Accounts Center > Accounts > Add Facebook account. You need this connection for Meta Business Suite to see your Instagram data.

### 3. Export your data

instapipe works with CSV files exported from Meta Business Suite. There are two types:

#### Content/Posts CSV (the main one — required)

This is the file with one row per Reel/post and all the metrics for each one.

1. Open [Meta Business Suite](https://business.facebook.com) > **Insights** > **Content**
2. Filter by **Instagram** (top left, make sure you're not looking at Facebook)
3. Select the **date range** you want to analyze (e.g. last 28 days)
4. Click **Export** (top right corner) > choose **CSV**
5. A file like `Contenido_Posts_Feb24_Mar23.csv` downloads

This CSV includes: description, publication time, views, reach, likes, comments, saves, shares, followers gained, duration, and permalink for each Reel/post.

#### Daily metric CSVs (optional — for trend analysis)

These are individual CSVs with one data point per day for a specific metric (e.g. daily reach, daily views).

1. Open Meta Business Suite > **Insights** > **Overview**
2. For each metric you want (Reach, Views, Followers, Interactions, Profile visits), click the small **Export** icon next to it
3. Each one downloads as a separate CSV (e.g. `Alcance.csv`, `Visualizaciones.csv`, `Seguidores.csv`)

These files use **utf-16 encoding** with a 3-line header — instapipe handles this automatically, you don't need to do anything special.

### 4. Python >= 3.10

```bash
python3 --version  # Should be 3.10 or higher
```

All Python dependencies are installed automatically when you run `pip install`: pandas, openpyxl, matplotlib, seaborn.

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

### 1. Quick run (CLI)

```bash
instapipe analyze path/to/Contenido_Posts.csv --output results/
```

This runs the full pipeline (ingest -> clean -> metrics -> output) and saves a CSV report + charts to the output directory.

### 2. Python API

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

### 3. Daily metrics (optional)

For the individual daily metric CSVs exported from Meta Business Suite Overview:

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
