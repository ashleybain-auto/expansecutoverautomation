"""Regression tests for ECCS SQL dependency discovery."""

from pathlib import Path

from workbook_compiler.sql_reader import (
    discover_sql_references,
)


SOURCE = Path(
    "workbooks/analyzed/"
    "ECCS_REG_EXPANSE/"
    "extracted-vba/"
    "api-test-vba-source.txt"
)


def test_sql_dependencies_are_discovered() -> None:
    """Verify SQL and ADODB dependencies are identified."""

    references = discover_sql_references(
        str(SOURCE)
    )

    types = {
        item["type"]
        for item in references
    }

    assert "ADODB_CONNECTION" in types
    assert "ADODB_COMMAND" in types
    assert "ADODB_RECORDSET" in types
    assert "SERVER_SETTING" in types
    assert "DATABASE_NAME" in types
