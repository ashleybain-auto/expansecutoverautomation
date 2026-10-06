"""Regression tests for ECCS MEDITECH Expanse Registration."""
import json
from pathlib import Path


EXPECTED_SHEETS = {
    "Instructions",
    "ErrorCategories",
    "Accommodations",
    "Locations",
    "Services",
    "Insurance",
    "RoomBed",
    "DischargeDisposition",
    "InsAuthStatus",
    "FinancialApprover",
    "County",
    "FinancialClass",
    "AdmitSource",
    "Settings",
}


def test_registration_sheet_inventory() -> None:
    """Verify the expected Registration worksheets are discovered."""
    report = Path(
        "workbooks/analyzed/"
        "ECCS_REG_EXPANSE/"
        "workbook-structure.json"
    )

    assert report.exists()

    data = json.loads(
        report.read_text(
            encoding="utf-8"
        )
    )

    actual = {
        item["name"]
        for item in data["worksheets"]
    }

    missing = EXPECTED_SHEETS - actual

    assert not missing, (
        "Missing Registration worksheets: "
        f"{sorted(missing)}"
    )
