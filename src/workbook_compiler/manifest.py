"""Migration manifest generation for ECCS."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_io import load_json, write_json


def generate_manifest(
    ir_file: str,
    config_file: str,
) -> dict[str, Any]:
    """Generate an ECCS migration manifest from Workbook IR."""

    ir = load_json(
        Path(ir_file)
    )

    config = load_json(
        Path(config_file)
    )

    workbook = ir["workbook"]

    registration_config = (
        config["configTools"]["registration"]
    )

    workbook_name = workbook.get(
        "filename",
        "",
    )

    if "NonMagic" in workbook_name:
        variant = "NONMAGIC"
    else:
        variant = "EXPANSE"

    domains: list[dict[str, Any]] = []

    for item in ir.get("domains", []):
        domains.append(
            {
                "name": item["domain"],
                "actions": item["actions"],
            }
        )

    manifest: dict[str, Any] = {
        "suite": config["suite"],
        "factory": config["factory"],
        "configTool": {
            "code": registration_config["code"],
            "name": registration_config["name"],
            "variant": variant,
        },
        "source": {
            "workbook": workbook_name,
            "extension": workbook.get(
                "extension",
                "",
            ),
            "sha256": workbook.get(
                "sha256",
                "",
            ),
        },
        "domains": domains,
        "actions": ir.get(
            "actions",
            [],
        ),
        "integrations": {
            "sql": ir.get(
                "sql_references",
                [],
            ),
            "api": ir.get(
                "api_references",
                [],
            ),
        },
        "validation": {
            "required": True,
        },
        "audit": {
            "required": True,
        },
        "migration": {
            "status": "IN_PROGRESS",
            "generatedBy": "ECCS Workbook Compiler",
        },
    }

    return manifest


def write_manifest(
    ir_file: str,
    config_file: str,
    output_file: str,
) -> dict[str, Any]:
    """Generate and write an ECCS migration manifest."""

    manifest = generate_manifest(
        ir_file,
        config_file,
    )

    write_json(
        manifest,
        Path(output_file),
    )

    return manifest
