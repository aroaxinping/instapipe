# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-03-30

### Added
- **ingest** module: load CSV (utf-8-sig, utf-16) and XLSX files from Meta Business Suite
- **clean** module: normalize column names (Spanish/English), parse dates, convert types
- **metrics** module: engagement rate, save rate, share rate, follower conversion rate, best hour/day, top performers
- **output** module: CSV/JSON export, matplotlib charts (engagement distribution, best hours, save rate scatter, top reels)
- **classify** module: classify Reels by topic based on description and hashtags, with customizable rules
- **dashboard** module: interactive HTML dashboard with 6 Plotly charts (requires plotly)
- **excel** module: styled Excel workbook with native formulas (Overview, Reels Raw, Engagement Calc)
- **compare** module: period-over-period comparison with absolute and percentage deltas
- **insights** module: viral detection (outlier flagging), duration analysis, hashtag analysis
- **CLI**: `instapipe analyze` with `--excel` and `--dashboard` flags, `instapipe daily` for daily CSVs
- Sample data (`examples/sample_data.csv`) for testing without an Instagram account
- 53 tests across all modules
- GitHub Actions CI (Python 3.10-3.13)
- Issue templates (bug report, feature request)
- Pre-commit hooks (ruff)
