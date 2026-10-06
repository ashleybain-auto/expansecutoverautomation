"""Regression tests for the ECCS EXPANSE Workbook IR."""

from pathlib import Path

from workbook_compiler.ir_builder import (
    build_workbook_ir,
)


ANALYSIS_DIR = Path(
    "workbooks/analyzed/"
    "ECCS_REG_EXPANSE"
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


def test_workbook_ir_contains_required_sections() -> None:
    """Verify all required Workbook IR sections exist."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert EXPECTED_SECTIONS.issubset(
        ir.keys()
    )


def test_workbook_ir_contains_analysis_data() -> None:
    """Verify implemented analysis sections contain data."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert len(ir["worksheets"]) > 0
    assert len(ir["procedures"]) > 0
    assert len(ir["domains"]) > 0
    assert len(ir["sql_references"]) > 0
    assert len(ir["actions"]) > 0


def test_workbook_ir_identifies_expanse_source() -> None:
    """Verify the IR identifies the EXPANSE Registration workbook."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert (
        ir["workbook"]["filename"]
        == "Mapping_Expanse_REG_Domain.xlsb"
    )


def test_domains_and_actions_are_consistent() -> None:
    """Verify the current domain/action model remains consistent."""

    ir = build_workbook_ir(
        str(ANALYSIS_DIR)
    )

    assert ir["domains"] == ir["actions"]
