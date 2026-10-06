"""ECCS bulk-upload CSV reader and source-row normalization."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = (
    "Domain",
    "SourceSystem",
    "Facility_Source",
    "Mnemonic_Source",
    "Name_Source",
    "Active_Source",
    "Target_Environment",
    "Requested_Action",
    "Source_Row_Id",
)


OPTIONAL_COLUMNS = (
    "PA_Code_Source",
    "Target_Facility",
    "Target_Mnemonic",
    "Target_Name",
    "Target_PA_Code",
    "Target_Active",
)


def validate_headers(headers: list[str]) -> list[str]:
    """Return missing required upload columns."""
    header_set = set(headers)

    return [
        column
        for column in REQUIRED_COLUMNS
        if column not in header_set
    ]


def read_upload_csv(path: str | Path) -> list[dict[str, Any]]:
    """Read and normalize an ECCS bulk-upload CSV."""
    source = Path(path)

    if not source.exists():
        raise FileNotFoundError(
            f"Upload CSV not found: {source}"
        )

    with source.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []

        missing = validate_headers(headers)

        if missing:
            raise ValueError(
                "Missing required ECCS upload columns: "
                + ", ".join(missing)
            )

        rows: list[dict[str, Any]] = []

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            normalized = {
                "Domain": (row.get("Domain") or "").strip(),
                "SourceSystem": (row.get("SourceSystem") or "").strip(),
                "Facility": (row.get("Facility_Source") or "").strip(),
                "Mnemonic": (row.get("Mnemonic_Source") or "").strip(),
                "NameDescription": (
                    row.get("Name_Source") or ""
                ).strip(),
                "PASecondaryKey": (
                    row.get("PA_Code_Source") or ""
                ).strip(),
                "Active": (row.get("Active_Source") or "").strip(),
                "TargetEnvironment": (
                    row.get("Target_Environment") or ""
                ).strip(),
                "TargetFacility": (
                    row.get("Target_Facility") or ""
                ).strip(),
                "TargetMnemonic": (
                    row.get("Target_Mnemonic") or ""
                ).strip(),
                "TargetNameDescription": (
                    row.get("Target_Name") or ""
                ).strip(),
                "TargetPASecondaryKey": (
                    row.get("Target_PA_Code") or ""
                ).strip(),
                "TargetActive": (
                    row.get("Target_Active") or ""
                ).strip(),
                "RequestedAction": (
                    row.get("Requested_Action") or ""
                ).strip(),
                "SourceRowId": (
                    row.get("Source_Row_Id") or ""
                ).strip(),
                "SourceLineNumber": line_number,
            }

            rows.append(normalized)

    return rows
