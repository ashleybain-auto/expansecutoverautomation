"""Extract one VBA procedure from an ECCS VBA source artifact."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_procedure(
    source_file: Path,
    procedure_name: str,
) -> str:
    """Return the complete VBA procedure matching the requested name."""

    if not source_file.exists():
        raise FileNotFoundError(
            f"VBA source file not found: {source_file}"
        )

    source = source_file.read_text(
        encoding="utf-8",
        errors="replace",
    )

    pattern = re.compile(
        rf"(?ims)"
        rf"^\s*(?:Public\s+|Private\s+|Friend\s+|Static\s+)?"
        rf"(Sub|Function)\s+{re.escape(procedure_name)}"
        rf"\b.*?"
        rf"^\s*End\s+\1\s*$"
    )

    match = pattern.search(source)

    if match is None:
        raise ValueError(
            f"Procedure not found: {procedure_name}"
        )

    return match.group(0)


def main() -> None:
    """Parse arguments and extract a VBA procedure."""

    parser = argparse.ArgumentParser(
        description="Extract one VBA procedure."
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Path to extracted VBA source.",
    )

    parser.add_argument(
        "--procedure",
        required=True,
        help="VBA procedure name.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Destination text file.",
    )

    args = parser.parse_args()

    source_file = Path(args.source)
    output_file = Path(args.output)

    procedure = extract_procedure(
        source_file,
        args.procedure,
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        procedure,
        encoding="utf-8",
    )

    print(f"Procedure: {args.procedure}")
    print(f"Source: {source_file}")
    print(f"Output: {output_file}")
    print(f"Characters: {len(procedure)}")


if __name__ == "__main__":
    main()
