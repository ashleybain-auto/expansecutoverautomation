"""Workbook Intermediate Representation builder for ECCS."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_io import load_json, write_json


def build_workbook_ir(
    analysis_dir: str,
) -> dict[str, Any]:
    """Combine compiler artifacts into a Workbook IR."""

    directory = Path(analysis_dir)

    structure = load_json(
        directory / "workbook-structure.json"
    )

    procedures = load_json(
        directory / "procedures.json"
    )

    domain_actions = load_json(
        directory / "domain-actions.json"
    )

    sql_references = load_json(
        directory / "sql-references.json"
    )

    return {
        "compiler": {
            "name": "ECCS Workbook Compiler",
            "version": "0.1.0",
        },
        "workbook": {
            "filename": structure.get("filename"),
            "extension": structure.get("extension"),
            "sha256": structure.get("sha256"),
            "file_size_bytes": structure.get(
                "file_size_bytes"
            ),
        },
        "worksheets": structure.get(
            "worksheets",
            [],
        ),
        "procedures": procedures,
        "domains": domain_actions,
        "sql_references": sql_references,
        "api_references": [],
        "mappings": [],
        "settings": [],
        "actions": domain_actions,
        "warnings": [],
        "unsupported": [],
    }


def write_workbook_ir(
    analysis_dir: str,
    output_file: str,
) -> dict[str, Any]:
    """Build and write the Workbook IR."""

    ir = build_workbook_ir(
        analysis_dir
    )

    write_json(
        ir,
        Path(output_file),
    )

    return ir
