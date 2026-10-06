"""Command-line interface for the ECCS Workbook Compiler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .vba_reader import extract_vba
from .workbook_reader import read_workbook


def analyze(workbook_path: str, output_dir: str) -> None:
    """Analyze a source workbook and write the initial analysis artifacts."""
    source = Path(workbook_path)
    destination = Path(output_dir)

    destination.mkdir(parents=True, exist_ok=True)

    workbook_data = read_workbook(workbook_path)

    workbook_json = destination / "workbook-structure.json"

    workbook_json.write_text(
        json.dumps(
            workbook_data,
            indent=2,
        ),
        encoding="utf-8",
    )

    vba_dir = destination / "extracted-vba"

    try:
        extract_vba(
            workbook_path,
            str(vba_dir),
        )
    except (OSError, ValueError) as exc:
        (destination / "vba-error.txt").write_text(
            str(exc),
            encoding="utf-8",
        )

    print(f"Workbook analysis complete: {source.name}")
    print(f"Output: {destination}")


def main() -> None:
    """Parse command-line arguments and execute the selected command."""
    parser = argparse.ArgumentParser(
        description="ECCS Workbook Compiler"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    analyze_parser = subparsers.add_parser("analyze")

    analyze_parser.add_argument("workbook")
    analyze_parser.add_argument("output")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze(
            args.workbook,
            args.output,
        )


if __name__ == "__main__":
    main()
