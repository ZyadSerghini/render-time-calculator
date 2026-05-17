import argparse
import re
import sys
from pathlib import Path

from render_time_calculator.benchmark import process_benchmark_file
from render_time_calculator.model_comparison import run_model_comparison

RAW_DATA_DIR = Path("data/raw")
CLEANED_DATA_PATH = Path("data/processed/cleaned_data.csv")

BENCHMARK_FILE_PATTERN = re.compile(
    r"^opendata-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}\+[0-9]{4}\.jsonl$"
)


def find_benchmark_file() -> Path:
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Missing directory: {RAW_DATA_DIR}\n"
            "Create data/raw and place the Blender benchmark JSONL file there."
        )

    matching_files = sorted(
        file
        for file in RAW_DATA_DIR.iterdir()
        if file.is_file() and BENCHMARK_FILE_PATTERN.match(file.name)
    )

    if not matching_files:
        raise FileNotFoundError(
            "No Blender benchmark JSONL file found.\n\n"
            "Download the latest Blender benchmark snapshot on:\n"
            "https://opendata.blender.org/download\n"
            f"and place it in {RAW_DATA_DIR}."
        )

    if len(matching_files) > 1:
        print(f"Multiple benchmark files found. Using: {matching_files[-1]}")

    return matching_files[-1]


def require_cleaned_data() -> None:
    if not CLEANED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing cleaned dataset: {CLEANED_DATA_PATH}\n\n"
            "Run the benchmark processing step first:\n"
            "python -m render_time_calculator.main benchmark\n\n"
            "Or run the full pipeline:\n"
            "python -m render_time_calculator.main all"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render Time Calculator project runner."
    )

    parser.add_argument(
        "command",
        choices=["benchmark", "models", "all"],
        nargs="?",
        default="all",
        help=(
            "benchmark: convert raw Blender JSONL data to cleaned CSV; "
            "models: run model comparison using cleaned CSV; "
            "all: run both steps."
        ),
    )

    args = parser.parse_args()

    try:
        if args.command in {"benchmark", "all"}:
            benchmark_file = find_benchmark_file()
            print(f"Found benchmark file: {benchmark_file}")
            process_benchmark_file(str(benchmark_file))

        if args.command in {"models", "all"}:
            require_cleaned_data()
            run_model_comparison()

    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
