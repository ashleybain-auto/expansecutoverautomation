"""Clone real REG / EXPANSE XWALK READ results into local ECCS_Dev.

Authoritative source:
    XRDCWDDBSUIP06
    MTX_ACOE_Cutover_Reporting

Local target:
    localhost
    ECCS_Dev

The source connection executes only the discovered
UI_Excel_Select_Xwalk_Source_* stored procedures.

All local clone tables are created under the staging schema.
"""

from __future__ import annotations

import argparse
import datetime as dt
import decimal
import getpass
import re
import uuid
from dataclasses import dataclass
from typing import Any

import pyodbc


SOURCE_SERVER = "xrdcwddbsuip06"
SOURCE_DATABASE = "MTX_ACOE_Cutover_Reporting"

TARGET_SERVER = "localhost"
TARGET_DATABASE = "ECCS_Dev"
TARGET_SCHEMA = "staging"

ODBC_DRIVER = "ODBC Driver 18 for SQL Server"


@dataclass(frozen=True)
class XwalkContract:
    """Definition of one Registration XWALK READ operation."""

    domain: str
    procedure: str
    scope_parameter: str
    scope_kind: str


CONTRACTS = (
    XwalkContract(
        "Accommodations",
        "UI_Excel_Select_Xwalk_Source_Accommodations",
        "@facmnem_src",
        "facility",
    ),
    XwalkContract(
        "AdmitSource",
        "UI_Excel_Select_Xwalk_Source_AdmitSource",
        "@networkmnem_src",
        "network",
    ),
    XwalkContract(
        "County",
        "UI_Excel_Select_Xwalk_Source_County",
        "@networkmnem",
        "network",
    ),
    XwalkContract(
        "DischargeDisposition",
        "UI_Excel_Select_Xwalk_Source_DischargeDisposition",
        "@networkmnem",
        "network",
    ),
    XwalkContract(
        "FinancialApprover",
        "UI_Excel_Select_Xwalk_Source_Financial_Approver",
        "@orgsearch",
        "organization",
    ),
    XwalkContract(
        "FinancialClass",
        "UI_Excel_Select_Xwalk_Source_FinancialClass",
        "@networkmnem_src",
        "network",
    ),
    XwalkContract(
        "Insurance",
        "UI_Excel_Select_Xwalk_Source_Insurance",
        "@networkmnem",
        "network",
    ),
    XwalkContract(
        "InsAuthStatus",
        "UI_Excel_Select_Xwalk_Source_Insurance_Auth_Status",
        "@orgsearch",
        "organization",
    ),
    XwalkContract(
        "Locations",
        "UI_Excel_Select_Xwalk_Source_Location",
        "@facmnem_src",
        "facility",
    ),
    XwalkContract(
        "RoomBed",
        "UI_Excel_Select_Xwalk_Source_Room_and_Bed",
        "@facmnem_src",
        "facility",
    ),
    XwalkContract(
        "Services",
        "UI_Excel_Select_Xwalk_Source_Services",
        "@facmnem_src",
        "facility",
    ),
)


def connection_string(
    server: str,
    database: str,
    application_name: str,
) -> str:
    """Create a Windows-integrated SQL Server connection string."""

    return (
        f"DRIVER={{{ODBC_DRIVER}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        f"Application Name={application_name};"
    )


def quote_identifier(value: str) -> str:
    """Safely quote a SQL Server identifier."""

    return "[" + value.replace("]", "]]") + "]"


def normalize_column_names(
    columns: list[str],
) -> list[str]:
    """Create unique SQL-safe column names while retaining source meaning."""

    result: list[str] = []
    used: set[str] = set()

    for index, original in enumerate(columns, start=1):
        name = str(original or "").strip()

        if not name:
            name = f"Column_{index}"

        name = re.sub(r"[\x00-\x1f]", "", name)

        candidate = name
        suffix = 2

        while candidate.lower() in used:
            candidate = f"{name}_{suffix}"
            suffix += 1

        used.add(candidate.lower())
        result.append(candidate)

    return result


def infer_sql_type(values: list[Any]) -> str:
    """Infer a conservative SQL Server type for local staging."""

    populated = [
        value
        for value in values
        if value is not None
    ]

    if not populated:
        return "NVARCHAR(MAX)"

    if all(isinstance(value, bool) for value in populated):
        return "BIT"

    if all(
        isinstance(value, int)
        and not isinstance(value, bool)
        for value in populated
    ):
        return "BIGINT"

    if all(
        isinstance(value, (int, float, decimal.Decimal))
        and not isinstance(value, bool)
        for value in populated
    ):
        return "DECIMAL(38,10)"

    if all(
        isinstance(value, (dt.datetime, dt.date))
        for value in populated
    ):
        return "DATETIME2(3)"

    if all(
        isinstance(value, (bytes, bytearray))
        for value in populated
    ):
        return "VARBINARY(MAX)"

    return "NVARCHAR(MAX)"


def normalize_value(value: Any) -> Any:
    """Normalize source values for conservative local staging types."""

    if value is None:
        return None

    if isinstance(
        value,
        (bool, int, float, decimal.Decimal, dt.datetime, bytes, bytearray),
    ):
        return value

    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min)

    if isinstance(value, uuid.UUID):
        return str(value)

    return str(value)


def read_source(
    contract: XwalkContract,
    scope_value: str,
    user_security: str,
) -> tuple[list[str], list[tuple[Any, ...]]]:
    """Execute one authoritative XWALK READ procedure."""

    connection_text = connection_string(
        SOURCE_SERVER,
        SOURCE_DATABASE,
        "ECCS-REG-XWALK-READ",
    )

    with pyodbc.connect(
        connection_text,
        timeout=60,
        autocommit=True,
    ) as connection:
        cursor = connection.cursor()

        sql = (
            f"EXEC [dbo].{quote_identifier(contract.procedure)} "
            f"{contract.scope_parameter} = ?, "
            "@usersec34 = ?;"
        )

        cursor.execute(
            sql,
            scope_value,
            user_security,
        )

        while cursor.description is None:
            if not cursor.nextset():
                raise RuntimeError(
                    f"{contract.procedure} returned no result set."
                )

        source_columns = [
            str(column[0])
            for column in cursor.description
        ]

        rows = [
            tuple(row)
            for row in cursor.fetchall()
        ]

    return source_columns, rows


def create_clone(
    contract: XwalkContract,
    scope_value: str,
    user_security: str,
    source_columns: list[str],
    rows: list[tuple[Any, ...]],
) -> int:
    """Create a fresh local snapshot table for one XWALK domain."""

    target_table = f"REG_EXPANSE_Xwalk_{contract.domain}"
    columns = normalize_column_names(source_columns)

    column_types: list[str] = []

    for index in range(len(columns)):
        values = [
            row[index]
            for row in rows
        ]

        column_types.append(
            infer_sql_type(values)
        )

    column_definitions = [
        (
            f"{quote_identifier(column)} "
            f"{sql_type} NULL"
        )
        for column, sql_type in zip(columns, column_types)
    ]

    connection_text = connection_string(
        TARGET_SERVER,
        TARGET_DATABASE,
        "ECCS-REG-XWALK-LOCAL-CLONE",
    )

    with pyodbc.connect(
        connection_text,
        timeout=60,
        autocommit=False,
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            IF SCHEMA_ID(N'staging') IS NULL
            BEGIN
                EXEC(N'CREATE SCHEMA staging');
            END;
            """
        )

        qualified_table = (
            f"{quote_identifier(TARGET_SCHEMA)}."
            f"{quote_identifier(target_table)}"
        )

        cursor.execute(
            f"""
            IF OBJECT_ID(
                N'{TARGET_SCHEMA}.{target_table}',
                N'U'
            ) IS NOT NULL
            BEGIN
                DROP TABLE {qualified_table};
            END;
            """
        )

        metadata_columns = [
            "[ECCS_Clone_RowId] BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY",
            "[ECCS_ClonedAtUtc] DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME()",
            "[ECCS_SourceServer] NVARCHAR(128) NOT NULL",
            "[ECCS_SourceDatabase] NVARCHAR(128) NOT NULL",
            "[ECCS_SourceProcedure] NVARCHAR(256) NOT NULL",
            "[ECCS_Domain] NVARCHAR(128) NOT NULL",
            "[ECCS_ScopeKind] NVARCHAR(50) NOT NULL",
            "[ECCS_ScopeValue] NVARCHAR(255) NOT NULL",
            "[ECCS_SourceUser] NVARCHAR(255) NOT NULL",
        ]

        all_definitions = (
            metadata_columns
            + column_definitions
        )

        cursor.execute(
            f"""
            CREATE TABLE {qualified_table}
            (
                {",".join(all_definitions)}
            );
            """
        )

        if rows:
            insert_columns = [
                "ECCS_SourceServer",
                "ECCS_SourceDatabase",
                "ECCS_SourceProcedure",
                "ECCS_Domain",
                "ECCS_ScopeKind",
                "ECCS_ScopeValue",
                "ECCS_SourceUser",
                *columns,
            ]

            insert_sql = (
                f"INSERT INTO {qualified_table} "
                "("
                + ",".join(
                    quote_identifier(column)
                    for column in insert_columns
                )
                + ") VALUES ("
                + ",".join(
                    "?"
                    for _ in insert_columns
                )
                + ");"
            )

            payload = []

            for row in rows:
                payload.append(
                    (
                        SOURCE_SERVER,
                        SOURCE_DATABASE,
                        contract.procedure,
                        contract.domain,
                        contract.scope_kind,
                        scope_value,
                        user_security,
                        *[
                            normalize_value(value)
                            for value in row
                        ],
                    )
                )

            cursor.fast_executemany = True
            cursor.executemany(
                insert_sql,
                payload,
            )

        connection.commit()

    return len(rows)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--facility",
        required=True,
        help="Real source facility mnemonic.",
    )

    parser.add_argument(
        "--network",
        required=True,
        help="Real source network mnemonic.",
    )

    parser.add_argument(
        "--organization",
        required=True,
        help="Real organization search value.",
    )

    parser.add_argument(
        "--user",
        default=getpass.getuser(),
        help="Value supplied to @usersec34.",
    )

    parser.add_argument(
        "--domain",
        default="ALL",
        help="One domain name or ALL.",
    )

    return parser.parse_args()


def scope_for_contract(
    contract: XwalkContract,
    args: argparse.Namespace,
) -> str:
    """Resolve the correct scope value for a contract."""

    if contract.scope_kind == "facility":
        return args.facility

    if contract.scope_kind == "network":
        return args.network

    if contract.scope_kind == "organization":
        return args.organization

    raise RuntimeError(
        f"Unknown scope kind: {contract.scope_kind}"
    )


def main() -> int:
    """Clone selected Registration XWALK source results."""

    args = parse_args()

    requested_domain = args.domain.upper()

    selected = [
        contract
        for contract in CONTRACTS
        if (
            requested_domain == "ALL"
            or contract.domain.upper() == requested_domain
        )
    ]

    if not selected:
        raise RuntimeError(
            f"Unknown domain: {args.domain}"
        )

    print("")
    print("ECCS REGISTRATION XWALK CLONE")
    print("============================")
    print(f"Source server   : {SOURCE_SERVER}")
    print(f"Source database : {SOURCE_DATABASE}")
    print(f"Target server   : {TARGET_SERVER}")
    print(f"Target database : {TARGET_DATABASE}")
    print(f"User security   : {args.user}")
    print("")

    failures: list[str] = []

    for contract in selected:
        scope_value = scope_for_contract(
            contract,
            args,
        )

        print(
            f"[{contract.domain}] "
            f"{contract.procedure}"
        )
        print(
            f"  {contract.scope_parameter} = "
            f"{scope_value}"
        )

        try:
            source_columns, rows = read_source(
                contract=contract,
                scope_value=scope_value,
                user_security=args.user,
            )

            print(
                f"  Source columns : "
                f"{len(source_columns)}"
            )
            print(
                f"  Source rows    : "
                f"{len(rows)}"
            )

            cloned = create_clone(
                contract=contract,
                scope_value=scope_value,
                user_security=args.user,
                source_columns=source_columns,
                rows=rows,
            )

            print(
                f"  Local rows     : "
                f"{cloned}"
            )
            print("  Status         : PASS")

        except (pyodbc.Error, RuntimeError, ValueError) as exc:
            failures.append(
                f"{contract.domain}: {exc}"
            )

            print(
                f"  Status         : FAIL - {exc}"
            )

        print("")

    if failures:
        print("CLONE COMPLETED WITH FAILURES")

        for failure in failures:
            print(f"  {failure}")

        return 1

    print("ALL SELECTED XWALK CLONES COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
