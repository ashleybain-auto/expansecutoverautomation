"""Regression tests for ECCS VBA procedure discovery."""

from pathlib import Path

from workbook_compiler.procedure_reader import (
    discover_procedures,
)


def test_nonmagic_procedure_source() -> None:
    """Verify that Non-Magic VBA procedures are discoverable."""

    source = (
        "workbooks/analyzed/"
        "ECCS_REG_NONMAGIC/"
        "extracted-vba/"
        "vba-source.txt"
    )

    procedures = discover_procedures(source)

    assert len(procedures) > 0

    source = (
        "workbooks/analyzed/"
        "ECCS_REG_NONMAGIC/"
        "extracted-vba/"
        "vba-source.txt"
    )

    procedures = discover_procedures(source)

    assert len(procedures) > 0


SOURCE = Path(
    "workbooks/analyzed/"
    "ECCS_REG_EXPANSE/"
    "extracted-vba/"
    "api-test-vba-source.txt"
)


def test_procedure_reader_finds_registration_actions() -> None:
    """Verify known Registration procedures are discovered."""

    procedures = discover_procedures(str(SOURCE))

    names = {
        item["name"]
        for item in procedures
    }

    assert "RefreshData_Accommodations" in names
    assert "PushUpdates_Accommodations" in names
    assert "RefreshData_Locations" in names
    assert "PushUpdates_Locations" in names
