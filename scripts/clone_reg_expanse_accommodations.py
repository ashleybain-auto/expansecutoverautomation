"""Clone real REG / EXPANSE / Accommodations data into local ECCS_Dev.

SOURCE:
    Read-only execution of:
    dbo.UI_Excel_Select_Xwalk_Source_Accommodations

TARGET:
    localhost / ECCS_Dev

The source connection is never used for INSERT, UPDATE, DELETE,
DDL, or transaction writes.
"""

from __future__ import annotations

import argparse
import getpass
from typing import Any

import pyodbc


SOURCE_PROCEDURE = (
    "[dbo].[UI_Excel_Select_Xwalk_Source_Accommodations]"
)

TARGET_SCHEMA = "staging"
TARGET_TABLE = "REG_EXPANSE_Accommodations_Clone"


def connection_string(
    server: str,
    database: str,
    trust_certificate: bool,
    application_name: str,
) -> str:
    """Build an integrated-authentication SQL Server connection."""

    trust = "yes" if trust_certificate else "no"

    return (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        f"TrustServerCertificate={trust};"
        f"Application Name={application_name};"
    )


def read_source(
    server: str,
    database: str,
    facility: str,
    user_security: str,
) -> tuple[list[str], list[tuple[Any, ...]]]:
    """Read the authoritative Accommodations recordset."""

    source_connection = connection_string(
        server=server,
        database=database,
        trust_certificate=True,
        application_name="ECCS-POC-READ-ONLY-CLONE",
    )

    with pyodbc.connect(
        source_connection,
        timeout=30,
        autocommit=True,
        readonly=True,
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            EXEC {SOURCE_PROCEDURE}
                @facmnem_src = ?,
                @usersec34 = ?;
            """,
            facility,
            user_security,
        )

        if cursor.description is None:
            raise RuntimeError(
                "Source procedure returned no result set."
            )

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = [
            tuple(row)
            for row in cursor.fetchall()
        ]

    return columns, rows


def sql_type_from_value(value: Any) -> str:
    """Infer a safe local staging SQL type."""

    if isinstance(value, bool):
        return "BIT"

    if isinstance(value, int):
        return "BIGINT"

    if isinstance(value, float):
        return "FLOAT"

    return "NVARCHAR(MAX)"


def quote_identifier(value: str) -> str:
    """Quote a SQL Server identifier."""

    return "[" + value.replace("]", "]]") + "]"


def create_local_clone(
    columns: list[str],
    rows: list[tuple[Any, ...]],
) -> None:
    """Replace the local staging clone with the current source snapshot."""

    target_connection = connection_string(
        server="localhost",
        database="ECCS_Dev",
        trust_certificate=True,
        application_name="ECCS-POC-LOCAL-CLONE",
    )

    sample_values: list[Any] = []

    for index in range(len(columns)):
        sample = None

        for row in rows:
            if row[index] is not None:
                sample = row[index]
                break

        sample_values.append(sample)

    column_definitions = []

    for name, sample in zip(columns, sample_values):
        column_definitions.append(
            f"{quote_identifier(name)} "
            f"{sql_type_from_value(sample)} NULL"
        )

    with pyodbc.connect(
        target_connection,
        timeout=30,
        autocommit=False,
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            IF SCHEMA_ID(N'{TARGET_SCHEMA}') IS NULL
                EXEC(N'CREATE SCHEMA {TARGET_SCHEMA}');
            """
        )

        cursor.execute(
            f"""
            IF OBJECT_ID(
                N'{TARGET_SCHEMA}.{TARGET_TABLE}',
                N'U'
            ) IS NOT NULL
                DROP TABLE
                    {quote_identifier(TARGET_SCHEMA)}.
                    {quote_identifier(TARGET_TABLE)};
            """
        )

        create_sql = (
            f"CREATE TABLE "
            f"{quote_identifier(TARGET_SCHEMA)}."
            f"{quote_identifier(TARGET_TABLE)} "
            "("
            "[ECCS_Clone_RowId] BIGINT IDENTITY(1,1) NOT NULL "
            "PRIMARY KEY,"
            "[ECCS_ClonedAtUtc] DATETIME2(3) NOT NULL "
            "DEFAULT SYSUTCDATETIME(),"
            + ",".join(column_definitions)
            + ");"
        )

        cursor.execute(create_sql)

        if rows:
            column_list = ",".join(
                quote_identifier(column)
                for column in columns
            )

            placeholders = ",".join(
                "?"
                for _ in columns
            )

            insert_sql = (
                f"INSERT INTO "
                f"{quote_identifier(TARGET_SCHEMA)}."
                f"{quote_identifier(TARGET_TABLE)} "
                f"({column_list}) "
                f"VALUES ({placeholders});"
            )

            cursor.fast_executemany = True
            cursor.executemany(insert_sql, rows)

        connection.commit()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source-server",
        required=True,
    )

    parser.add_argument(
        "--source-database",
        required=True,
    )

    parser.add_argument(
        "--facility",
        required=True,
    )

    parser.add_argument(
        "--user",
        default=getpass.getuser(),
    )

    return parser.parse_args()


def main() -> int:
    """Clone the authoritative READ result into ECCS_Dev."""

    args = parse_args()

    print("")
    print("ECCS REG / EXPANSE / ACCOMMODATIONS CLONE")
    print("-----------------------------------------")
    print(f"Source server   : {args.source_server}")
    print(f"Source database : {args.source_database}")
    print(f"Facility        : {args.facility}")
    print("Source mode     : READ ONLY")
    print("Target server   : localhost")
    print("Target database : ECCS_Dev")
    print("")

    columns, rows = read_source(
        server=args.source_server,
        database=args.source_database,
        facility=args.facility,
        user_security=args.user,
    )

    print(f"Source columns  : {len(columns)}")
    print(f"Source rows     : {len(rows)}")

    create_local_clone(
        columns=columns,
        rows=rows,
    )

    print("")
    print("LOCAL CLONE COMPLETE")
    print(
        "Target: "
        f"{TARGET_SCHEMA}.{TARGET_TABLE}"
    )
    print(f"Rows cloned: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
