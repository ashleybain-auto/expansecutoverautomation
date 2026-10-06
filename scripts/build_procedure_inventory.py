"""Generate a VBA procedure inventory for an ECCS workbook."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbook_compiler.procedure_reader import (
    write_procedure_inventory,
)


def find_vba_source(
    extraction_dir: Path,
) -> Path:
    """Find the VBA source text file in an extraction directory."""

    if not extraction_dir.exists():
        raise FileNotFoundError(
            f"Extraction directory not found: {extraction_dir}"
        )

    preferred_names = (
        "vba-source.txt",
        "api-test-vba-source.txt",
    )

    for filename in preferred_names:
        candidate = extraction_dir / filename

        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate

    candidates = sorted(
        extraction_dir.glob("*vba*source*.txt")
    )

    candidates = [
        path
        for path in candidates
        if path.is_file() and path.stat().st_size > 0
    ]

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            "No VBA source text file was found in "
            f"{extraction_dir}"
        )

    names = ", ".join(
        path.name
        for path in candidates
    )

    raise RuntimeError(
        "Multiple VBA source files were found. "
        f"Available files: {names}"
    )


def main() -> None:
    """Generate a procedure inventory from extracted VBA."""

    parser = argparse.ArgumentParser(
        description=(
            "Build an ECCS VBA procedure inventory."
        )
    )

    parser.add_argument(
        "--source",
        help=(
            "Path to extracted VBA source. "
            "When omitted, the extraction directory is searched."
        ),
    )

    parser.add_argument(
        "--extraction-dir",
        help=(
            "Directory containing extracted VBA source."
        ),
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for procedures.json.",
    )

    args = parser.parse_args()

    if args.source:
        source = Path(args.source)

        if not source.exists():
            raise FileNotFoundError(
                f"Specified VBA source file not found: {source}"
            )

    elif args.extraction_dir:
        source = find_vba_source(
            Path(args.extraction_dir)
        )

    else:
        raise ValueError(
            "Provide either --source or --extraction-dir."
        )

    output = Path(args.output)

    procedures = write_procedure_inventory(
        str(source),
        str(output),
    )

    counts: dict[str, int] = {}

    for procedure in procedures:
        classification = procedure["classification"]

        counts[classification] = (
            counts.get(classification, 0) + 1
        )

    print(f"Source: {source}")
    print(f"Procedures discovered: {len(procedures)}")

    for classification, count in sorted(
        counts.items()
    ):
        print(
            f"{classification}: {count}"
        )

    print(f"Output: {output}")

    json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )


if __name__ == "__main__":
    main()
