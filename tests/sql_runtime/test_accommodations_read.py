"""POC tests for the ECCS REG EXPANSE Accommodations READ runtime."""

from src.eccs_sql_runtime.accommodations_read import (
    EXPECTED_OBJECT,
    EXPECTED_PARAMETERS,
    EXPECTED_SCHEMA,
    ReadRequest,
    build_procedure_call,
)


def test_accommodations_read_contract() -> None:
    """Verify the compiled Accommodations READ contract."""

    assert EXPECTED_SCHEMA == "dbo"

    assert (
        EXPECTED_OBJECT
        == "UI_Excel_Select_Xwalk_Source_Accommodations"
    )

    assert len(EXPECTED_PARAMETERS) == 2

    assert EXPECTED_PARAMETERS[0]["ordinal"] == 1
    assert EXPECTED_PARAMETERS[0]["name"] == "@facmnem_src"
    assert EXPECTED_PARAMETERS[0]["sql_type"] == "varchar"
    assert EXPECTED_PARAMETERS[0]["max_length"] == 25

    assert EXPECTED_PARAMETERS[1]["ordinal"] == 2
    assert EXPECTED_PARAMETERS[1]["name"] == "@usersec34"
    assert EXPECTED_PARAMETERS[1]["sql_type"] == "varchar"
    assert EXPECTED_PARAMETERS[1]["max_length"] == 255


def test_accommodations_read_call() -> None:
    """Verify generation of the parameterized READ invocation."""

    request = ReadRequest(
        facility_mnemonic_source="TEST",
        user_security_value="ECCS_POC_USER",
    )

    command, values = build_procedure_call(
        request=request,
        schema_name=EXPECTED_SCHEMA,
        object_name=EXPECTED_OBJECT,
    )

    assert command == (
        "EXEC "
        "[dbo].[UI_Excel_Select_Xwalk_Source_Accommodations] "
        "@facmnem_src = ?, "
        "@usersec34 = ?;"
    )

    assert values == (
        "TEST",
        "ECCS_POC_USER",
    )
