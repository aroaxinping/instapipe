"""Command-line interface for instapipe."""

import argparse
import sys
from pathlib import Path

from instapipe import __version__, ingest, clean, metrics, output
from instapipe.classify import add_topics


def main():
    parser = argparse.ArgumentParser(
        prog="instapipe",
        description="Data pipeline for Instagram analytics.",
    )
    parser.add_argument("--version", action="version", version=f"instapipe {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # ── analyze ──────────────────────────────────────────────────────────
    analyze = subparsers.add_parser(
        "analyze", help="Run the full pipeline on an export file.")
    analyze.add_argument(
        "file", type=str,
        help="Path to Instagram export file (CSV or XLSX from Meta Business Suite).")
    analyze.add_argument(
        "--output", "-o", type=str, default="results",
        help="Output directory. Default: results/")
    analyze.add_argument(
        "--no-charts", action="store_true",
        help="Skip chart generation, only export CSV.")
    analyze.add_argument(
        "--excel", action="store_true",
        help="Also generate a styled Excel workbook.")
    analyze.add_argument(
        "--dashboard", action="store_true",
        help="Also generate an interactive HTML dashboard (requires plotly).")

    # ── daily ────────────────────────────────────────────────────────────
    daily = subparsers.add_parser(
        "daily",
        help="Combine daily metric CSVs into a single dataset.")
    daily.add_argument(
        "directory", type=str,
        help="Directory containing daily CSVs (Alcance.csv, Visualizaciones.csv, etc.).")
    daily.add_argument(
        "--output", "-o", type=str, default="results",
        help="Output directory. Default: results/")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        run_analyze(args)
    elif args.command == "daily":
        run_daily(args)


def run_analyze(args):
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.file}...")
    raw = ingest.load(args.file)
    print(f"  {len(raw)} rows loaded.")

    print("Cleaning data...")
    df = clean.normalize(raw)
    print(f"  {len(df)} rows after cleaning.")

    print("Classifying topics...")
    df = add_topics(df)
    topic_counts = df["tema"].value_counts()
    for topic, count in topic_counts.items():
        print(f"  {topic}: {count}")

    print("Computing metrics...")
    report = metrics.compute(df)
    print(report.summary())

    csv_path = out_dir / "report.csv"
    output.to_csv(report, csv_path)
    print(f"\nCSV exported to {csv_path}")

    if not args.no_charts:
        print("Generating charts...")

        output.plot_engagement(report, save_to=out_dir / "engagement.png")
        print(f"  -> {out_dir / 'engagement.png'}")

        try:
            output.plot_best_hours(report, save_to=out_dir / "best_hours.png")
            print(f"  -> {out_dir / 'best_hours.png'}")
        except ValueError:
            print("  -- Skipping best hours (no hour column found)")

        try:
            output.plot_save_rate(report, save_to=out_dir / "save_rate.png")
            print(f"  -> {out_dir / 'save_rate.png'}")
        except Exception:
            print("  -- Skipping save rate chart")

        try:
            output.plot_top_reels(report, save_to=out_dir / "top_reels.png")
            print(f"  -> {out_dir / 'top_reels.png'}")
        except Exception:
            print("  -- Skipping top reels chart")

    if args.excel:
        from instapipe.excel import build_excel
        excel_path = out_dir / "analytics.xlsx"
        build_excel(report, excel_path)
        print(f"  -> {excel_path}")

    if args.dashboard:
        from instapipe.dashboard import build_dashboard
        dash_path = out_dir / "dashboard.html"
        build_dashboard(report, dash_path)
        print(f"  -> {dash_path}")

    print("\nDone.")


def run_daily(args):
    raw_dir = Path(args.directory)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.is_dir():
        print(f"Error: {raw_dir} is not a directory.")
        sys.exit(1)

    # Map known filenames to metric names
    known_files = {
        "Visualizaciones.csv": "visualizaciones",
        "Alcance.csv": "alcance",
        "Interacciones.csv": "interacciones",
        "Visitas.csv": "visitas_perfil",
        "Seguidores.csv": "seguidores_ganados",
    }

    import pandas as pd

    dfs = []
    for filename, col_name in known_files.items():
        path = raw_dir / filename
        if path.exists():
            df = ingest.load_daily(path, col_name)
            if not df.empty:
                dfs.append(df.set_index("fecha"))
                print(f"  Loaded {filename} -> {col_name} ({len(df)} days)")

    if not dfs:
        print("No daily metric CSVs found. Expected files like Alcance.csv, Visualizaciones.csv, etc.")
        sys.exit(1)

    daily = dfs[0].join(dfs[1:], how="outer").fillna(0).astype(int)
    daily = daily.sort_index()
    daily["dia_semana"] = daily.index.day_name()

    out_path = out_dir / "daily_metrics.csv"
    daily.reset_index().to_csv(out_path, index=False)
    print(f"\nDaily metrics exported to {out_path} ({len(daily)} days)")
    print("Done.")
