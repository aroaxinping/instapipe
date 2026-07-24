"""Minimal working example for instapipe."""

from instapipe import ingest, clean, metrics, output

# 1. Load your content/posts export from Meta Business Suite
raw = ingest.load("path/to/Contenido_Posts.csv")

# 2. Clean and normalize column names, types, dates
df = clean.normalize(raw)

# 3. Compute Instagram metrics (engagement rate, save rate, etc.)
report = metrics.compute(df)

# 4. Print summary
print(report.summary())

# 5. Export to CSV
output.to_csv(report, "results.csv")

# 6. Generate charts
output.plot_engagement(report, save_to="engagement.png")
output.plot_best_hours(report, save_to="best_hours.png")
output.plot_save_rate(report, save_to="save_rate.png")
output.plot_top_reels(report, save_to="top_reels.png")
