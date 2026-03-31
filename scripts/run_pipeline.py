from __future__ import annotations

import argparse
from pathlib import Path

from app.config import DEFAULT_OUTPUT_STEM, RAW_SOURCES_DIR, ensure_directories
from app.pipeline import build_summary, run_pipeline, summary_to_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the multi-source extraction pipeline.")
    parser.add_argument(
        "--sources",
        nargs="*",
        help="Optional list of source files or URLs. Defaults to every file under data/raw/sources.",
    )
    parser.add_argument(
        "--output-stem",
        default=DEFAULT_OUTPUT_STEM,
        help="Base filename used for CSV/JSON/diagnostics exports.",
    )
    return parser.parse_args()


def main() -> None:
    ensure_directories()
    args = parse_args()
    sources = args.sources or [str(path) for path in sorted(RAW_SOURCES_DIR.iterdir()) if path.is_file()]
    records_df, diagnostics_df, exports = run_pipeline(sources, stem=args.output_stem)
    print(summary_to_json(build_summary(records_df, diagnostics_df)))
    for label, path in exports.items():
        print(f"{label}: {Path(path)}")


if __name__ == "__main__":
    main()
