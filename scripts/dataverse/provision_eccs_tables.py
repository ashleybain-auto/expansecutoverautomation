"""ECCS Dataverse table provisioning helpers."""

from __future__ import annotations

import os
from typing import Any

import requests


ENVIRONMENT_URL = "https://org77f1aacd.crm.dynamics.com"
API_URL = f"{ENVIRONMENT_URL}/api/data/v9.2"
SOLUTION_UNIQUE_NAME = "ECCSUploadMapping"


def create_label(value: str) -> dict[str, Any]:
    """Create a Dataverse localized label."""
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [
            {
                "@odata.type": (
                    "Microsoft.Dynamics.CRM.LocalizedLabel"
                ),
                "Label": value,
                "LanguageCode": 1033,
            }
        ],
    }


def create_required_level(
    value: str = "None",
) -> dict[str, Any]:
    """Create a Dataverse required-level definition."""
    return {
        "Value": value,
        "CanBeChanged": True,
    }


def create_string_column(
    schema_name: str,
    display_name: str,
    max_length: int = 200,
) -> dict[str, Any]:
    """Create Dataverse text-column metadata."""
    return {
        "@odata.type": (
            "Microsoft.Dynamics.CRM.StringAttributeMetadata"
        ),
        "AttributeType": "String",
        "AttributeTypeName": {
            "Value": "StringType",
        },
        "SchemaName": schema_name,
        "DisplayName": create_label(display_name),
        "Description": create_label(display_name),
        "RequiredLevel": create_required_level(),
        "MaxLength": max_length,
    }


def create_integer_column(
    schema_name: str,
    display_name: str,
) -> dict[str, Any]:
    """Create Dataverse whole-number metadata."""
    return {
        "@odata.type": (
            "Microsoft.Dynamics.CRM.IntegerAttributeMetadata"
        ),
        "AttributeType": "Integer",
        "AttributeTypeName": {
            "Value": "IntegerType",
        },
        "SchemaName": schema_name,
        "DisplayName": create_label(display_name),
        "Description": create_label(display_name),
        "RequiredLevel": create_required_level(),
        "MinValue": -2147483648,
        "MaxValue": 2147483647,
    }


def create_datetime_column(
    schema_name: str,
    display_name: str,
) -> dict[str, Any]:
    """Create Dataverse date/time metadata."""
    return {
        "@odata.type": (
            "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata"
        ),
        "AttributeType": "DateTime",
        "AttributeTypeName": {
            "Value": "DateTimeType",
        },
        "SchemaName": schema_name,
        "DisplayName": create_label(display_name),
        "Description": create_label(display_name),
        "RequiredLevel": create_required_level(),
        "Format": "DateAndTime",
        "DateTimeBehavior": {
            "Value": "UserLocal",
        },
    }


def create_choice_column(
    schema_name: str,
    display_name: str,
    options: list[tuple[int, str]],
) -> dict[str, Any]:
    """Create Dataverse local choice metadata."""
    return {
        "@odata.type": (
            "Microsoft.Dynamics.CRM.PicklistAttributeMetadata"
        ),
        "AttributeType": "Picklist",
        "AttributeTypeName": {
            "Value": "PicklistType",
        },
        "SchemaName": schema_name,
        "DisplayName": create_label(display_name),
        "Description": create_label(display_name),
        "RequiredLevel": create_required_level(),
        "OptionSet": {
            "@odata.type": (
                "Microsoft.Dynamics.CRM.OptionSetMetadata"
            ),
            "IsGlobal": False,
            "Options": [
                {
                    "Value": option_value,
                    "Label": create_label(option_label),
                }
                for option_value, option_label in options
            ],
        },
    }


def get_session() -> requests.Session:
    """Create an authenticated Dataverse HTTP session."""
    token = os.environ.get("DATAVERSE_ACCESS_TOKEN")

    if not token:
        raise RuntimeError(
            "DATAVERSE_ACCESS_TOKEN is not configured."
        )

    session = requests.Session()

    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": (
                "application/json; charset=utf-8"
            ),
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
    )

    return session


def create_table(
    session: requests.Session,
) -> None:
    """Create the ECCS Upload Batch table."""
    payload = {
        "@odata.type": (
            "Microsoft.Dynamics.CRM.EntityMetadata"
        ),
        "SchemaName": "eccs_UploadBatch",
        "DisplayName": create_label(
            "ECCS Upload Batch"
        ),
        "DisplayCollectionName": create_label(
            "ECCS Upload Batches"
        ),
        "Description": create_label(
            "ECCS bulk configuration upload batch."
        ),
        "OwnershipType": "UserOwned",
        "IsActivity": False,
        "HasActivities": False,
        "HasNotes": False,
        "Attributes": [
            create_string_column(
                "eccs_BatchName",
                "Batch Name",
            )
        ],
    }

    response = session.post(
        f"{API_URL}/EntityDefinitions",
        headers={
            "MSCRM.SolutionUniqueName": (
                SOLUTION_UNIQUE_NAME
            )
        },
        json=payload,
        timeout=120,
    )

    if response.status_code not in (200, 201, 204):
        raise RuntimeError(
            "Table creation failed: "
            f"HTTP {response.status_code} "
            f"{response.text}"
        )

    print("Created table: eccs_UploadBatch")


def create_column(
    session: requests.Session,
    column: dict[str, Any],
) -> None:
    """Create one column on ECCS Upload Batch."""
    response = session.post(
        (
            f"{API_URL}/EntityDefinitions"
            "(LogicalName='eccs_uploadbatch')"
            "/Attributes"
        ),
        headers={
            "MSCRM.SolutionUniqueName": (
                SOLUTION_UNIQUE_NAME
            )
        },
        json=column,
        timeout=120,
    )

    if response.status_code not in (200, 201, 204):
        raise RuntimeError(
            "Column creation failed for "
            f"{column['SchemaName']}: "
            f"HTTP {response.status_code} "
            f"{response.text}"
        )

    print(
        f"Created column: "
        f"{column['SchemaName']}"
    )


def main() -> int:
    """Provision ECCS Upload Batches."""
    session = get_session()

    create_table(session)

    columns = [
        create_string_column(
            "eccs_BatchId",
            "Batch ID",
        ),
        create_string_column(
            "eccs_SourceSystem",
            "Source System",
        ),
        create_string_column(
            "eccs_Domain",
            "Domain",
        ),
        create_string_column(
            "eccs_TargetEnvironment",
            "Target Environment",
        ),
        create_string_column(
            "eccs_FileName",
            "File Name",
        ),
        create_string_column(
            "eccs_FileType",
            "File Type",
        ),
        create_integer_column(
            "eccs_RowCount",
            "Row Count",
        ),
        create_integer_column(
            "eccs_ProcessedCount",
            "Processed Count",
        ),
        create_choice_column(
            "eccs_Status",
            "Status",
            [
                (100000000, "Uploaded"),
                (100000001, "Staged"),
                (100000002, "Processing"),
                (100000003, "Mapped"),
                (100000004, "Reviewed"),
                (100000005, "Approved"),
                (100000006, "Committed"),
                (100000007, "Completed"),
                (100000008, "Error"),
            ],
        ),
        create_string_column(
            "eccs_UploadedBy",
            "Uploaded By",
        ),
        create_datetime_column(
            "eccs_UploadDateUtc",
            "Upload Date UTC",
        ),
        create_datetime_column(
            "eccs_CompletedDateUtc",
            "Completed Date UTC",
        ),
        create_integer_column(
            "eccs_ErrorCount",
            "Error Count",
        ),
    ]

    for column in columns:
        create_column(
            session,
            column,
        )

    print("ECCS Upload Batches schema: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
