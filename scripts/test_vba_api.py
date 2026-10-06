"""Parameterized VBA extraction utility for the ECCS Workbook Compiler."""

from __future__ import annotations

import argparse
from pathlib import Path

from oletools.olevba import VBA_Parser


def extract_workbook(
    workbook_path: Path,
    output_dir: Path,
) -> None:
    """Extract VBA source and analysis for one workbook."""

    if not workbook_path.exists():
        raise FileNotFoundError(
            f"Workbook not found: {workbook_path}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    parser = VBA_Parser(
        str(workbook_path)
    )

    try:
        has_vba = parser.detect_vba_macros()

        print(f"Workbook: {workbook_path}")
        print(f"VBA detected: {has_vba}")

        source_parts: list[str] = []
        module_count = 0

        if has_vba:
            for (
                filename,
                stream_path,
                vba_filename,
                vba_code,
            ) in parser.extract_macros():

                module_count += 1

                source_parts.append(
                    f"===== {vba_filename} =====\n"
                    f"Source: {filename}\n"
                    f"Stream: {stream_path}\n\n"
                    f"{vba_code}"
                )

        source_file = (
            output_dir / "vba-source.txt"
        )

        source_file.write_text(
            "\n\n".join(source_parts),
            encoding="utf-8",
        )

        analysis = list(
            parser.analyze_macros() or []
        )

        analysis_file = (
            output_dir / "vba-analysis.txt"
        )

        analysis_file.write_text(
            "\n".join(
                f"{item[0]} | {item[1]} | {item[2]}"
                for item in analysis
            ),
            encoding="utf-8",
        )

        print(f"Modules found: {module_count}")
        print(f"Source output: {source_file}")
        print(f"Analysis output: {analysis_file}")

    finally:
        parser.close()


def main() -> None:
    """Parse arguments and extract VBA from the requested workbook."""

    parser = argparse.ArgumentParser(
        description=(
            "Extract VBA from an ECCS source workbook."
        )
    )

    parser.add_argument(
        "--workbook",
        required=True,
        help="Path to the source workbook.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Directory for extracted VBA artifacts.",
    )

    args = parser.parse_args()

    extract_workbook(
        Path(args.workbook),
        Path(args.output),
    )


if __name__ == "__main__":
    main()
