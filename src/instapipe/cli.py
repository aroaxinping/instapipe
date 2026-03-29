"""Command-line interface for instapipe."""

import argparse
import sys
from pathlib import Path

from instapipe import __version__, ingest, clean, metrics, output


def main():
    parser = argparse.ArgumentParser(
        prog="instapipe",
        description="Data pipeline for Instagram analytics.",
    )
    parser.add_argument("--version", action="version", version=f"instapipe {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # analyze command
    analyze = subparsers.add_parser("analyze", help="Run the full pipeline on an export file.")
    analyze.add_argument("file", type=str, help="Path to Instagram export file (CSV or XLSX from Meta Business Suite).")
    analyze.add_argument(
        "--output", "-o",
        type=str,
        default="results",
        help="Output directory for CSV and charts. Default: results/",
    )
    analyze.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip chart generation, only export CSV.",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        run_analyze(args)


def run_analyze(args):
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.file}...")
    raw = ingest.load(args.file)
    print(f"  {len(raw)} rows loaded.")

    print("Cleaning data...")
    df = clean.normalize(raw)
    print(f"  {len(df)} rows after cleaning.")

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

    print("\nDone.")
