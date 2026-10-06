"""SQL dependency discovery for the ECCS Workbook Compiler."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PATTERNS = {
    "ADODB_CONNECTION": r"\bADODB\.Connection\b",
    "ADODB_COMMAND": r"\bADODB\.Command\b",
    "ADODB_RECORDSET": r"\bADODB\.Recordset\b",
    "ADODB_PARAMETER": r"\bADODB\.Parameter\b",
    "SQL_VARIABLE": r"\b(?:SQLStr|SQLString)\b",
    "SQL_OPEN": r"\b\w+\.Open\s*\(",
    "SQL_DRIVER": r"Driver=\{SQL Server\}",
    "SERVER_SETTING": (
        r'Sheets\(\s*"Settings"\s*\)'
        r'\.Range\(\s*"settingServer"\s*\)'
    ),
    "DATABASE_NAME": r"\bDatabase_Name\b",
}


def discover_sql_references(
    source_file: str,
) -> list[dict[str, Any]]:
    """Discover SQL-related references from extracted VBA."""

    source_path = Path(source_file)

    if not source_path.exists():
        raise FileNotFoundError(
            f"VBA source file not found: {source_path}"
        )

    source = source_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    references: list[dict[str, Any]] = []

    for reference_type, pattern in PATTERNS.items():
        for match in re.finditer(
            pattern,
            source,
            flags=re.IGNORECASE,
        ):
            line_number = (
                source.count(
                    "\n",
                    0,
                    match.start(),
                ) + 1
            )

            references.append(
                {
                    "type": reference_type,
                    "value": match.group(0),
                    "line_number": line_number,
                }
            )

    return references


def write_sql_inventory(
    source_file: str,
    output_file: str,
) -> list[dict[str, Any]]:
    """Write SQL dependency references to a JSON file."""

    references = discover_sql_references(
        source_file
    )

    destination = Path(output_file)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(
            references,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return references
