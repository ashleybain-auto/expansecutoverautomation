"""Export the real Registration Accommodations clone for Power Apps."""

from __future__ import annotations

import csv
from pathlib import Path

import pyodbc


OUTPUT = Path(
    "generated/powerapps/REG/EXPANSE/Accommodations/"
    "Accommodations_RealData.csv"
)

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=ECCS_Dev;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Application Name=ECCS-PowerApps-RealData-Export;"
)

SQL = """
SELECT
    ECCS_Clone_RowId,
    FacilityMnem_Source,
    Accommodation_Mnem_Source,
    Accommodation_Name_Source,
    PA_Code_Source,
    Active_Source,
    TargetMatchMtx,
    DB_RecordCount,
    FacilityMnem_Target,
    Accommodation_Mnem_Target,
    Accommodation_Name_Target,
    PA_Code_Target,
    Active_Target,
    DisplayCurrentValues,
    ExcludeFromSharepoint,
    [Action To Take],
    Update_User,
    Update_Datetime,
    System_Update_User,
    System_Update_Datetime,
    ECCS_SourceServer,
    ECCS_SourceDatabase,
    ECCS_SourceProcedure,
    ECCS_ScopeKind,
    ECCS_ScopeValue,
    ECCS_SourceUser,
    ECCS_ClonedAtUtc
FROM staging.REG_EXPANSE_Xwalk_Accommodations
ORDER BY ECCS_Clone_RowId;
"""


def main() -> int:
    """Export all cloned real-data Accommodations records."""

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pyodbc.connect(
        CONNECTION_STRING,
        timeout=60,
    ) as connection:

        cursor = connection.cursor()
        cursor.execute(SQL)

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = cursor.fetchall()

    with OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as output_file:

        writer = csv.writer(
            output_file,
            quoting=csv.QUOTE_MINIMAL,
        )

        writer.writerow(columns)

        for row in rows:
            writer.writerow(row)

    print("")
    print("ECCS POWER APPS REAL-DATA EXPORT")
    print("--------------------------------")
    print(f"Rows exported : {len(rows)}")
    print(f"Columns       : {len(columns)}")
    print(f"Output        : {OUTPUT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
