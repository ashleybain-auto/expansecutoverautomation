"""Regression tests for the ECCS Non-Magic Registration Workbook IR."""

from pathlib import Path

from workbook_compiler.ir_builder import (
    build_workbook_ir,
)


ANALYSIS_DIR = Path(
    "workbooks/analyzed/"
    "ECCS_REG_NONMAGIC"
)


EXPECTED_SECTIONS = {
    "compiler",
    "workbook",
    "worksheets",
    "procedures",
    "domains",
    "sql_references",
    "api_references",
    "mappings",
    "settings",
    "actions",
    "warnings",
    "unsupported",
}


def test_nonmagic_ir_contains_required_sections() -> None:
    """Verify all required IR sections exist."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert EXPECTED_SECTIONS.issubset(
        ir.keys()
    )


def test_nonmagic_ir_contains_analysis_data() -> None:
    """Verify implemented analysis sections contain data."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert len(ir["worksheets"]) > 0
    assert len(ir["procedures"]) > 0
    assert len(ir["domains"]) > 0
    assert len(ir["sql_references"]) > 0
    assert len(ir["actions"]) > 0


def test_nonmagic_ir_identifies_correct_source() -> None:
    """Verify the IR identifies the Non-Magic workbook."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert (
        ir["workbook"]["filename"]
        == "Mapping_NonMagic_Expanse_REG_Domain.xlsb"
    )
