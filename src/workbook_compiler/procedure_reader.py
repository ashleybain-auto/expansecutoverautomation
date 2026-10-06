"""VBA procedure discovery for the ECCS Workbook Compiler."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .artifact_io import write_json
from .classifier import classify_procedure
from .source_utils import line_number_at


PROCEDURE_PATTERN = re.compile(
    r"(?im)^\s*"
    r"(?:Public\s+|Private\s+|Friend\s+|Static\s+)?"
    r"(Sub|Function|Property\s+(?:Get|Let|Set))\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)"
)


def discover_procedures(
    source_file: str,
) -> list[dict[str, Any]]:
    """Discover and classify VBA procedures from extracted source."""

    path = Path(source_file)

    if not path.exists():
        raise FileNotFoundError(
            f"VBA source file not found: {path}"
        )

    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    procedures: list[dict[str, Any]] = []

    for match in PROCEDURE_PATTERN.finditer(source):
        procedure_type = match.group(1)
        procedure_name = match.group(2)

        line_number = line_number_at(
            source,
            match.start(),
        )

        procedures.append(
            {
                "name": procedure_name,
                "procedure_type": procedure_type,
                "classification": classify_procedure(
                    procedure_name
                ),
                "line_number": line_number,
            }
        )

    return procedures


def write_procedure_inventory(
    source_file: str,
    output_file: str,
) -> list[dict[str, Any]]:
    """Discover procedures and write the inventory as JSON."""

    procedures = discover_procedures(
        source_file
    )

    write_json(
        procedures,
        Path(output_file),
    )

    return procedures
