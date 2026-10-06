"""ECCS SQL Runtime READ adapter for REG / EXPANSE / Accommodations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

import pyodbc


EXPECTED_TOOL_CODE = "REG"
EXPECTED_VARIANT_CODE = "EXPANSE"
EXPECTED_DOMAIN_CODE = "ACCOMMODATIONS"
EXPECTED_OPERATION = "READ"
EXPECTED_SCHEMA = "dbo"
EXPECTED_OBJECT = "UI_Excel_Select_Xwalk_Source_Accommodations"

EXPECTED_PARAMETERS = [
    {
        "ordinal": 1,
        "name": "@facmnem_src",
        "sql_type": "varchar",
        "max_length": 25,
        "source_field_code": "FACILITY_MNEM_SOURCE",
    },
    {
        "ordinal": 2,
        "name": "@usersec34",
        "sql_type": "varchar",
        "max_length": 255,
        "source_field_code": None,
    },
]


@dataclass(frozen=True)
class ReadRequest:
    """Values required by the Accommodations READ contract."""

    facility_mnemonic_source: str
    user_security_value: str


@dataclass(frozen=True)
class RuntimeContract:
    """Validated ECCS metadata for the Accommodations READ operation."""

    contract_id: str
    schema_name: str
    object_name: str
    operation_code: str
    contract_source: str | None
    validation_status: str | None
    enabled: bool
    parameter_count: int


def get_odbc_driver() -> str:
    """Return an installed SQL Server ODBC driver."""

    configured = os.getenv("ECCS_SQL_DRIVER")
    if configured:
        return configured

    installed = set(pyodbc.drivers())

    for preferred in (
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
    ):
        if preferred in installed:
            return preferred

    raise RuntimeError(
        "No supported SQL Server ODBC driver is installed. "
        "Set ECCS_SQL_DRIVER or install ODBC Driver 18 for SQL Server."
    )


def build_integrated_connection_string(
    server: str,
    database: str,
    driver: str,
    trust_server_certificate: bool = False,
) -> str:
    """Build a Windows Integrated SQL Server connection string."""

    trust_value = "yes" if trust_server_certificate else "no"

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        f"TrustServerCertificate={trust_value};"
        "Application Name=ECCS-REG-Accommodations-READ;"
    )


def rows_to_dicts(cursor: pyodbc.Cursor) -> list[dict[str, Any]]:
    """Convert the current cursor result set to dictionaries."""

    if cursor.description is None:
        return []

    columns = [column[0] for column in cursor.description]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def load_runtime_contract(
    connection: pyodbc.Connection,
) -> RuntimeContract:
    """Load the single expected ECCS Accommodations READ contract."""

    sql = """
        SELECT
            contract.SqlRuntimeContractId,
            contract.ExternalSchemaName,
            contract.ExternalObjectName,
            contract.OperationCode,
            contract.ContractSource,
            contract.ValidationStatus,
            contract.IsEnabled
        FROM integration.SqlRuntimeContract AS contract
        INNER JOIN eccs.ConfigDomain AS domain
            ON domain.ConfigDomainId = contract.ConfigDomainId
        INNER JOIN eccs.ConfigTool AS tool
            ON tool.ConfigToolId = domain.ConfigToolId
        WHERE tool.ToolCode = ?
          AND tool.VariantCode = ?
          AND domain.DomainCode = ?
          AND contract.OperationCode = ?;
    """

    cursor = connection.cursor()

    cursor.execute(
        sql,
        (
            EXPECTED_TOOL_CODE,
            EXPECTED_VARIANT_CODE,
            EXPECTED_DOMAIN_CODE,
            EXPECTED_OPERATION,
        ),
    )

    rows = rows_to_dicts(cursor)

    if len(rows) != 1:
        raise RuntimeError(
            "Expected exactly one REG / EXPANSE / ACCOMMODATIONS READ "
            f"contract; found {len(rows)}."
        )

    row = rows[0]

    return RuntimeContract(
        contract_id=str(row["SqlRuntimeContractId"]),
        schema_name=str(row["ExternalSchemaName"]),
        object_name=str(row["ExternalObjectName"]),
        operation_code=str(row["OperationCode"]),
        contract_source=(
            str(row["ContractSource"])
            if row["ContractSource"] is not None
            else None
        ),
        validation_status=(
            str(row["ValidationStatus"])
            if row["ValidationStatus"] is not None
            else None
        ),
        enabled=bool(row["IsEnabled"]),
        parameter_count=0,
    )


def load_runtime_parameters(
    connection: pyodbc.Connection,
    contract_id: str,
) -> list[dict[str, Any]]:
    """Load ordered parameter metadata for a runtime contract."""

    sql = """
        SELECT
            ParameterOrdinal,
            ParameterName,
            SqlDataType,
            MaxLength,
            IsOutput,
            IsRequired,
            SourceFieldCode
        FROM integration.SqlRuntimeParameter
        WHERE SqlRuntimeContractId = ?
        ORDER BY ParameterOrdinal;
    """

    cursor = connection.cursor()
    cursor.execute(sql, (contract_id,))

    return rows_to_dicts(cursor)


def validate_contract(
    contract: RuntimeContract,
    parameters: list[dict[str, Any]],
) -> RuntimeContract:
    """Verify the stored ECCS contract matches the known VBA READ contract."""

    if contract.schema_name.lower() != EXPECTED_SCHEMA.lower():
        raise RuntimeError(
            f"Unexpected READ schema: {contract.schema_name}"
        )

    if contract.object_name.lower() != EXPECTED_OBJECT.lower():
        raise RuntimeError(
            f"Unexpected READ procedure: {contract.object_name}"
        )

    if contract.operation_code.upper() != EXPECTED_OPERATION:
        raise RuntimeError(
            f"Unexpected operation code: {contract.operation_code}"
        )

    if contract.enabled:
        raise RuntimeError(
            "The READ contract is enabled before authoritative SQL "
            "metadata validation. Runtime execution is blocked."
        )

    if len(parameters) != len(EXPECTED_PARAMETERS):
        raise RuntimeError(
            "Unexpected READ parameter count. "
            f"Expected {len(EXPECTED_PARAMETERS)}, "
            f"found {len(parameters)}."
        )

    for expected, actual in zip(EXPECTED_PARAMETERS, parameters):
        actual_name = str(actual["ParameterName"])
        actual_type = str(actual["SqlDataType"]).lower()
        actual_length = int(actual["MaxLength"])

        if int(actual["ParameterOrdinal"]) != expected["ordinal"]:
            raise RuntimeError(
                f"Unexpected parameter ordinal for {expected['name']}."
            )

        if actual_name.lower() != expected["name"].lower():
            raise RuntimeError(
                "Unexpected parameter name. "
                f"Expected {expected['name']}; "
                f"found {actual_name}."
            )

        if actual_type != expected["sql_type"]:
            raise RuntimeError(
                f"Unexpected SQL type for {actual_name}. "
                f"Expected {expected['sql_type']}; "
                f"found {actual_type}."
            )

        if actual_length != expected["max_length"]:
            raise RuntimeError(
                f"Unexpected parameter length for {actual_name}. "
                f"Expected {expected['max_length']}; "
                f"found {actual_length}."
            )

        if bool(actual["IsOutput"]):
            raise RuntimeError(
                f"READ parameter {actual_name} unexpectedly marked OUTPUT."
            )

        if not bool(actual["IsRequired"]):
            raise RuntimeError(
                f"READ parameter {actual_name} unexpectedly marked optional."
            )

    return RuntimeContract(
        contract_id=contract.contract_id,
        schema_name=contract.schema_name,
        object_name=contract.object_name,
        operation_code=contract.operation_code,
        contract_source=contract.contract_source,
        validation_status=contract.validation_status,
        enabled=contract.enabled,
        parameter_count=len(parameters),
    )


def build_procedure_call(
    request: ReadRequest,
    schema_name: str,
    object_name: str,
) -> tuple[str, tuple[str, str]]:
    """Build the controlled stored-procedure call and parameter values."""

    qualified_name = f"[{schema_name}].[{object_name}]"

    command = (
        f"EXEC {qualified_name} "
        "@facmnem_src = ?, "
        "@usersec34 = ?;"
    )

    return command, (
        request.facility_mnemonic_source,
        request.user_security_value,
    )


def execute_read(
    server: str,
    database: str,
    request: ReadRequest,
) -> list[dict[str, Any]]:
    """Execute the authoritative Accommodations READ procedure."""

    driver = get_odbc_driver()

    connection_string = build_integrated_connection_string(
        server=server,
        database=database,
        driver=driver,
        trust_server_certificate=False,
    )

    command, values = build_procedure_call(
        request=request,
        schema_name=EXPECTED_SCHEMA,
        object_name=EXPECTED_OBJECT,
    )

    with pyodbc.connect(
        connection_string,
        timeout=30,
        autocommit=True,
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(command, values)

        return rows_to_dicts(cursor)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "ECCS REG / EXPANSE / Accommodations READ adapter."
        )
    )

    parser.add_argument(
        "--facility",
        required=True,
        help="Source facility mnemonic for @facmnem_src.",
    )

    parser.add_argument(
        "--user",
        required=True,
        help="Security/user value for @usersec34.",
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Execute the authoritative target stored procedure. "
            "Without this switch the adapter performs a dry run."
        ),
    )

    parser.add_argument(
        "--contract-server",
        default=os.getenv("ECCS_SQL_SERVER", "localhost"),
        help="ECCS_Dev SQL Server used to read the runtime contract.",
    )

    parser.add_argument(
        "--contract-database",
        default=os.getenv("ECCS_SQL_DATABASE", "ECCS_Dev"),
        help="ECCS runtime database used to read the contract.",
    )

    return parser.parse_args()


def main() -> int:
    """Validate the contract and optionally execute the READ operation."""

    args = parse_args()
    driver = get_odbc_driver()

    contract_connection_string = build_integrated_connection_string(
        server=args.contract_server,
        database=args.contract_database,
        driver=driver,
        trust_server_certificate=True,
    )

    request = ReadRequest(
        facility_mnemonic_source=args.facility,
        user_security_value=args.user,
    )

    print("")
    print("ECCS REG / EXPANSE / ACCOMMODATIONS READ")
    print("----------------------------------------")
    print(f"Contract server   : {args.contract_server}")
    print(f"Contract database : {args.contract_database}")
    print(f"SQL driver        : {driver}")
    print(f"Operation         : {EXPECTED_OPERATION}")
    print(f"Procedure         : {EXPECTED_SCHEMA}.{EXPECTED_OBJECT}")
    print(f"Facility          : {request.facility_mnemonic_source}")
    print("")

    with pyodbc.connect(
        contract_connection_string,
        timeout=30,
        autocommit=True,
    ) as connection:
        contract = load_runtime_contract(connection)

        parameters = load_runtime_parameters(
            connection,
            contract.contract_id,
        )

    validated_contract = validate_contract(
        contract,
        parameters,
    )

    command, values = build_procedure_call(
        request=request,
        schema_name=validated_contract.schema_name,
        object_name=validated_contract.object_name,
    )

    print("Contract validation: PASS")
    print(f"Contract source    : {validated_contract.contract_source}")
    print(f"Validation status  : {validated_contract.validation_status}")
    print(f"Enabled            : {validated_contract.enabled}")
    print(f"Parameter count    : {validated_contract.parameter_count}")
    print("")
    print("Generated execution statement:")
    print(command)
    print("")
    print("Parameter values:")
    print(f"  @facmnem_src = {values[0]}")
    print("  @usersec34   = <provided securely at runtime>")
    print("")

    if not args.execute:
        print("DRY RUN")
        print("No authoritative SQL procedure was executed.")
        return 0

    target_server = os.getenv("ECCS_TARGET_SQL_SERVER")
    target_database = os.getenv("ECCS_TARGET_SQL_DATABASE")

    if not target_server:
        raise RuntimeError(
            "ECCS_TARGET_SQL_SERVER is required when --execute is supplied."
        )

    if not target_database:
        raise RuntimeError(
            "ECCS_TARGET_SQL_DATABASE is required when --execute is supplied."
        )

    print("LIVE EXECUTION REQUESTED")
    print(f"Target server   : {target_server}")
    print(f"Target database : {target_database}")
    print("")

    results = execute_read(
        server=target_server,
        database=target_database,
        request=request,
    )

    output = {
        "suite": EXPECTED_TOOL_CODE,
        "configTool": EXPECTED_TOOL_CODE,
        "variant": EXPECTED_VARIANT_CODE,
        "domain": EXPECTED_DOMAIN_CODE,
        "operation": EXPECTED_OPERATION,
        "procedure": f"{EXPECTED_SCHEMA}.{EXPECTED_OBJECT}",
        "facility": request.facility_mnemonic_source,
        "rowCount": len(results),
        "rows": results,
    }

    print(json.dumps(output, indent=2, default=str))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
