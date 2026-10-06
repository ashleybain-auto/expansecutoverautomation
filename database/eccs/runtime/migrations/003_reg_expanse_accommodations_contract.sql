/*
Expanse ConfigTool Factory
Expanse Cutover Configuration Suite (ECCS)

Step 60 - ECCS SQL Runtime POC
Migration 003
REG / EXPANSE / ACCOMMODATIONS

Purpose:
Register the field-level Accommodations contract and the
VBA-observed SQL procedure parameter contracts.

Source evidence:
Mapping_Expanse_REG_Domain.xlsb
workbooks\analyzed\ECCS_REG_EXPANSE\extracted-vba\api-test-vba-source.txt
workbooks\analyzed\ECCS_REG_EXPANSE\accommodations-refresh-vba.txt
workbooks\analyzed\ECCS_REG_EXPANSE\accommodations-publish-vba.txt

IMPORTANT:
The stored-procedure parameter definitions registered below are
derived from the extracted VBA caller code.

They have NOT yet been validated against the authoritative
enterprise SQL Server sys.parameters metadata.

Therefore:
- READ remains disabled.
- PUBLISH_UPDATE remains disabled.
- PUBLISH_INSERT remains disabled.
- No external SQL procedure is executed by this migration.

Target:
ECCS_Dev
*/
SET
    NOCOUNT ON;

SET
    XACT_ABORT ON;

------------------------------------------------------------
-- BATCH 1
-- Database and schema prerequisites
-- Conditional contract metadata columns
------------------------------------------------------------
IF DB_NAME () <> N'ECCS_Dev' BEGIN RAISERROR (
    'Migration 003 must execute against ECCS_Dev.',
    16,
    1
);

RETURN;

END;

IF OBJECT_ID (N'eccs.ConfigDomain', N'U') IS NULL BEGIN RAISERROR ('eccs.ConfigDomain is required.', 16, 1);

RETURN;

END;

IF OBJECT_ID (N'eccs.FieldDefinition', N'U') IS NULL BEGIN RAISERROR ('eccs.FieldDefinition is required.', 16, 1);

RETURN;

END;

IF OBJECT_ID (N'integration.SqlRuntimeContract', N'U') IS NULL BEGIN RAISERROR (
    'integration.SqlRuntimeContract is required.',
    16,
    1
);

RETURN;

END;

IF OBJECT_ID (N'integration.SqlRuntimeParameter', N'U') IS NULL BEGIN RAISERROR (
    'integration.SqlRuntimeParameter is required.',
    16,
    1
);

RETURN;

END;

------------------------------------------------------------
-- Add provenance/status columns to the SQL runtime contract
-- table if they do not already exist.
------------------------------------------------------------
IF COL_LENGTH (
    N'integration.SqlRuntimeContract',
    N'ContractSource'
) IS NULL BEGIN
ALTER TABLE integration.SqlRuntimeContract
ADD ContractSource NVARCHAR (50) NULL;

END;

IF COL_LENGTH (
    N'integration.SqlRuntimeContract',
    N'ValidationStatus'
) IS NULL BEGIN
ALTER TABLE integration.SqlRuntimeContract
ADD ValidationStatus NVARCHAR (50) NULL;

END;

IF COL_LENGTH (
    N'integration.SqlRuntimeContract',
    N'ValidationEvidence'
) IS NULL BEGIN
ALTER TABLE integration.SqlRuntimeContract
ADD ValidationEvidence NVARCHAR (1000) NULL;

END;

GO
/*
BATCH 2

The GO above is required because SQL Server compiles a batch before
execution. The columns conditionally added above therefore need to
exist before this batch references them.
*/
SET
    NOCOUNT ON;

SET
    XACT_ABORT ON;

------------------------------------------------------------
-- Verify target database again in the new batch.
------------------------------------------------------------
IF DB_NAME () <> N'ECCS_Dev' BEGIN RAISERROR (
    'Migration 003 must execute against ECCS_Dev.',
    16,
    1
);

RETURN;

END;

------------------------------------------------------------
-- Resolve REG / EXPANSE / ACCOMMODATIONS.
------------------------------------------------------------
DECLARE @AccommodationsDomainId UNIQUEIDENTIFIER;

SELECT
    @AccommodationsDomainId = domain.ConfigDomainId
FROM
    eccs.ConfigDomain AS domain
    INNER JOIN eccs.ConfigTool AS tool ON tool.ConfigToolId = domain.ConfigToolId
WHERE
    tool.ToolCode = N'REG'
    AND tool.VariantCode = N'EXPANSE'
    AND domain.DomainCode = N'ACCOMMODATIONS';

IF @AccommodationsDomainId IS NULL BEGIN RAISERROR (
    'REG / EXPANSE / ACCOMMODATIONS could not be resolved.',
    16,
    1
);

RETURN;

END;

------------------------------------------------------------
-- Mark the existing Accommodations SQL runtime contracts as
-- VBA-observed and pending authoritative SQL validation.
------------------------------------------------------------
UPDATE integration.SqlRuntimeContract
SET
    ContractSource = N'VBA_OBSERVED',
    ValidationStatus = N'PENDING_SQL_METADATA',
    ValidationEvidence = N'Extracted from Mapping_Expanse_REG_Domain.xlsb VBA source.',
    ModifiedAtUtc = SYSUTCDATETIME (),
    ModifiedBy = SUSER_SNAME ()
WHERE
    ConfigDomainId = @AccommodationsDomainId;

------------------------------------------------------------
-- FIELD DEFINITIONS
--
-- These fields are based on the actual Accommodations workbook
-- and extracted VBA references.
------------------------------------------------------------
DECLARE @FieldDefinitions
TABLE (
    FieldCode NVARCHAR (128) NOT NULL,
    FieldName NVARCHAR (200) NOT NULL,
    SourceColumnName NVARCHAR (200) NULL,
    DataType NVARCHAR (50) NOT NULL,
    FieldRole NVARCHAR (50) NOT NULL,
    DisplayOrder INT NOT NULL,
    IsRequired BIT NOT NULL,
    IsEditable BIT NOT NULL
);

INSERT INTO
    @FieldDefinitions (
        FieldCode,
        FieldName,
        SourceColumnName,
        DataType,
        FieldRole,
        DisplayOrder,
        IsRequired,
        IsEditable
    )
VALUES
    (
        N'FACILITY_MNEM_SOURCE',
        N'FacilityMnem_Source',
        N'FacilityMnem_Source',
        N'VARCHAR',
        N'SOURCE',
        10,
        1,
        0
    ),
    (
        N'FACILITY_MNEM_TARGET',
        N'FacilityMnem_Target',
        N'FacilityMnem_Target',
        N'VARCHAR',
        N'TARGET',
        20,
        1,
        1
    ),
    (
        N'ACCOMMODATION_MNEM_SOURCE',
        N'Accommodation_Mnem_Source',
        N'Accommodation_Mnem_Source',
        N'VARCHAR',
        N'SOURCE',
        30,
        1,
        0
    ),
    (
        N'ACCOMMODATION_MNEM_TARGET',
        N'Accommodation_Mnem_Target',
        N'Accommodation_Mnem_Target',
        N'VARCHAR',
        N'TARGET',
        40,
        1,
        1
    ),
    (
        N'ACCOMMODATION_NAME_TARGET',
        N'Accommodation_Name_Target',
        N'Accommodation_Name_Target',
        N'VARCHAR',
        N'TARGET',
        50,
        1,
        1
    ),
    (
        N'PA_CODE_TARGET',
        N'PA_Code_Target',
        N'PA_Code_Target',
        N'VARCHAR',
        N'TARGET',
        60,
        0,
        1
    ),
    (
        N'ACTIVE_TARGET',
        N'Active_Target',
        N'Active_Target',
        N'VARCHAR',
        N'STATUS',
        70,
        0,
        1
    ),
    (
        N'DISPLAY_CURRENT_VALUES',
        N'DisplayCurrentValues',
        N'DisplayCurrentValues',
        N'VARCHAR',
        N'STATUS',
        80,
        0,
        1
    ),
    (
        N'EXCLUDE_FROM_SHAREPOINT',
        N'ExcludeFromSharepoint',
        N'ExcludeFromSharepoint',
        N'VARCHAR',
        N'STATUS',
        90,
        0,
        1
    ),
    (
        N'ACTION_TO_TAKE',
        N'Action To Take',
        N'Action To Take',
        N'VARCHAR',
        N'ACTION',
        100,
        0,
        1
    ),
    (
        N'UPDATE_USER',
        N'Update_User',
        N'Update_User',
        N'VARCHAR',
        N'AUDIT',
        110,
        0,
        0
    ),
    (
        N'UPDATE_DATETIME',
        N'Update_Datetime',
        N'Update_Datetime',
        N'DATETIME',
        N'AUDIT',
        120,
        0,
        0
    );

------------------------------------------------------------
-- Insert field definitions only when they do not already exist.
------------------------------------------------------------
INSERT INTO
    eccs.FieldDefinition (
        ConfigDomainId,
        FieldCode,
        FieldName,
        SourceColumnName,
        DataType,
        FieldRole,
        DisplayOrder,
        IsRequired,
        IsEditable
    )
SELECT
    @AccommodationsDomainId,
    definition.FieldCode,
    definition.FieldName,
    definition.SourceColumnName,
    definition.DataType,
    definition.FieldRole,
    definition.DisplayOrder,
    definition.IsRequired,
    definition.IsEditable
FROM
    @FieldDefinitions AS definition
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            eccs.FieldDefinition AS existing
        WHERE
            existing.ConfigDomainId = @AccommodationsDomainId
            AND existing.FieldCode = definition.FieldCode
    );

------------------------------------------------------------
-- Resolve the three runtime contracts.
------------------------------------------------------------
DECLARE @ReadContractId UNIQUEIDENTIFIER;

DECLARE @UpdateContractId UNIQUEIDENTIFIER;

DECLARE @InsertContractId UNIQUEIDENTIFIER;

SELECT
    @ReadContractId = SqlRuntimeContractId
FROM
    integration.SqlRuntimeContract
WHERE
    ConfigDomainId = @AccommodationsDomainId
    AND OperationCode = N'READ';

SELECT
    @UpdateContractId = SqlRuntimeContractId
FROM
    integration.SqlRuntimeContract
WHERE
    ConfigDomainId = @AccommodationsDomainId
    AND OperationCode = N'PUBLISH_UPDATE';

SELECT
    @InsertContractId = SqlRuntimeContractId
FROM
    integration.SqlRuntimeContract
WHERE
    ConfigDomainId = @AccommodationsDomainId
    AND OperationCode = N'PUBLISH_INSERT';

IF @ReadContractId IS NULL BEGIN RAISERROR ('READ runtime contract is missing.', 16, 1);

RETURN;

END;

IF @UpdateContractId IS NULL BEGIN RAISERROR (
    'PUBLISH_UPDATE runtime contract is missing.',
    16,
    1
);

RETURN;

END;

IF @InsertContractId IS NULL BEGIN RAISERROR (
    'PUBLISH_INSERT runtime contract is missing.',
    16,
    1
);

RETURN;

END;

------------------------------------------------------------
-- READ PARAMETER CONTRACT
--
-- Confirmed from RefreshData_Accommodations VBA:
--
-- @facmnem_src  adVarChar 25  CurFacSrc
-- @usersec34     adVarChar 255 CurUser34
------------------------------------------------------------
DECLARE @ReadParameters
TABLE (
    ParameterOrdinal INT NOT NULL,
    ParameterName SYSNAME NOT NULL,
    SqlDataType SYSNAME NOT NULL,
    MaxLength INT NULL,
    SourceFieldCode NVARCHAR (128) NULL
);

INSERT INTO
    @ReadParameters (
        ParameterOrdinal,
        ParameterName,
        SqlDataType,
        MaxLength,
        SourceFieldCode
    )
VALUES
    (
        1,
        N'@facmnem_src',
        N'varchar',
        25,
        N'FACILITY_MNEM_SOURCE'
    ),
    (2, N'@usersec34', N'varchar', 255, NULL);

INSERT INTO
    integration.SqlRuntimeParameter (
        SqlRuntimeContractId,
        ParameterOrdinal,
        ParameterName,
        SqlDataType,
        MaxLength,
        NumericPrecision,
        NumericScale,
        IsOutput,
        IsRequired,
        SourceFieldCode
    )
SELECT
    @ReadContractId,
    parameter_info.ParameterOrdinal,
    parameter_info.ParameterName,
    parameter_info.SqlDataType,
    parameter_info.MaxLength,
    NULL,
    NULL,
    0,
    1,
    parameter_info.SourceFieldCode
FROM
    @ReadParameters AS parameter_info
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            integration.SqlRuntimeParameter AS existing
        WHERE
            existing.SqlRuntimeContractId = @ReadContractId
            AND existing.ParameterOrdinal = parameter_info.ParameterOrdinal
    );

------------------------------------------------------------
-- PUBLISH_UPDATE PARAMETER CONTRACT
--
-- Confirmed from extracted VBA:
--
-- 1  @facmnem_src
-- 2  @facmnem_tar
-- 3  @accom_mnem_src
-- 4  @usersec34
-- 5  @accom_mnem_tar
-- 6  @accom_name_tar
-- 7  @pa_tar
-- 8  @active_tar
-- 9  @vistoreadusers
-- 10 @exclreadusers
------------------------------------------------------------
DECLARE @UpdateParameters
TABLE (
    ParameterOrdinal INT NOT NULL,
    ParameterName SYSNAME NOT NULL,
    SqlDataType SYSNAME NOT NULL,
    MaxLength INT NULL,
    SourceFieldCode NVARCHAR (128) NULL
);

INSERT INTO
    @UpdateParameters (
        ParameterOrdinal,
        ParameterName,
        SqlDataType,
        MaxLength,
        SourceFieldCode
    )
VALUES
    (
        1,
        N'@facmnem_src',
        N'varchar',
        25,
        N'FACILITY_MNEM_SOURCE'
    ),
    (
        2,
        N'@facmnem_tar',
        N'varchar',
        25,
        N'FACILITY_MNEM_TARGET'
    ),
    (
        3,
        N'@accom_mnem_src',
        N'varchar',
        25,
        N'ACCOMMODATION_MNEM_SOURCE'
    ),
    (4, N'@usersec34', N'varchar', 255, NULL),
    (
        5,
        N'@accom_mnem_tar',
        N'varchar',
        25,
        N'ACCOMMODATION_MNEM_TARGET'
    ),
    (
        6,
        N'@accom_name_tar',
        N'varchar',
        255,
        N'ACCOMMODATION_NAME_TARGET'
    ),
    (7, N'@pa_tar', N'varchar', 25, N'PA_CODE_TARGET'),
    (
        8,
        N'@active_tar',
        N'varchar',
        25,
        N'ACTIVE_TARGET'
    ),
    (
        9,
        N'@vistoreadusers',
        N'varchar',
        25,
        N'DISPLAY_CURRENT_VALUES'
    ),
    (
        10,
        N'@exclreadusers',
        N'varchar',
        25,
        N'EXCLUDE_FROM_SHAREPOINT'
    );

INSERT INTO
    integration.SqlRuntimeParameter (
        SqlRuntimeContractId,
        ParameterOrdinal,
        ParameterName,
        SqlDataType,
        MaxLength,
        NumericPrecision,
        NumericScale,
        IsOutput,
        IsRequired,
        SourceFieldCode
    )
SELECT
    @UpdateContractId,
    parameter_info.ParameterOrdinal,
    parameter_info.ParameterName,
    parameter_info.SqlDataType,
    parameter_info.MaxLength,
    NULL,
    NULL,
    0,
    1,
    parameter_info.SourceFieldCode
FROM
    @UpdateParameters AS parameter_info
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            integration.SqlRuntimeParameter AS existing
        WHERE
            existing.SqlRuntimeContractId = @UpdateContractId
            AND existing.ParameterOrdinal = parameter_info.ParameterOrdinal
    );

------------------------------------------------------------
-- PUBLISH_INSERT PARAMETER CONTRACT
--
-- Confirmed from extracted VBA:
--
-- @facmnem_src
-- @facmnem_tar
-- @srvctar
-- @usersec34
--
-- The VBA variable CurAccommodationMnemTarget is passed to
-- the SQL parameter @srvctar.
------------------------------------------------------------
DECLARE @InsertParameters
TABLE (
    ParameterOrdinal INT NOT NULL,
    ParameterName SYSNAME NOT NULL,
    SqlDataType SYSNAME NOT NULL,
    MaxLength INT NULL,
    SourceFieldCode NVARCHAR (128) NULL
);

INSERT INTO
    @InsertParameters (
        ParameterOrdinal,
        ParameterName,
        SqlDataType,
        MaxLength,
        SourceFieldCode
    )
VALUES
    (
        1,
        N'@facmnem_src',
        N'varchar',
        25,
        N'FACILITY_MNEM_SOURCE'
    ),
    (
        2,
        N'@facmnem_tar',
        N'varchar',
        25,
        N'FACILITY_MNEM_TARGET'
    ),
    (
        3,
        N'@srvctar',
        N'varchar',
        25,
        N'ACCOMMODATION_MNEM_TARGET'
    ),
    (4, N'@usersec34', N'varchar', 255, NULL);

INSERT INTO
    integration.SqlRuntimeParameter (
        SqlRuntimeContractId,
        ParameterOrdinal,
        ParameterName,
        SqlDataType,
        MaxLength,
        NumericPrecision,
        NumericScale,
        IsOutput,
        IsRequired,
        SourceFieldCode
    )
SELECT
    @InsertContractId,
    parameter_info.ParameterOrdinal,
    parameter_info.ParameterName,
    parameter_info.SqlDataType,
    parameter_info.MaxLength,
    NULL,
    NULL,
    0,
    1,
    parameter_info.SourceFieldCode
FROM
    @InsertParameters AS parameter_info
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            integration.SqlRuntimeParameter AS existing
        WHERE
            existing.SqlRuntimeContractId = @InsertContractId
            AND existing.ParameterOrdinal = parameter_info.ParameterOrdinal
    );

------------------------------------------------------------
-- SAFETY ENFORCEMENT
--
-- All Accommodations runtime contracts must remain disabled
-- until authoritative enterprise SQL metadata validation has
-- been completed.
------------------------------------------------------------
UPDATE integration.SqlRuntimeContract
SET
    IsEnabled = 0,
    ContractSource = N'VBA_OBSERVED',
    ValidationStatus = N'PENDING_SQL_METADATA',
    ValidationEvidence = N'VBA caller contract captured; authoritative SQL metadata validation pending.',
    ModifiedAtUtc = SYSUTCDATETIME (),
    ModifiedBy = SUSER_SNAME ()
WHERE
    ConfigDomainId = @AccommodationsDomainId;

------------------------------------------------------------
-- VERIFICATION 1
-- Accommodations field definitions
------------------------------------------------------------
SELECT
    field_info.FieldCode,
    field_info.FieldName,
    field_info.SourceColumnName,
    field_info.DataType,
    field_info.FieldRole,
    field_info.DisplayOrder,
    field_info.IsRequired,
    field_info.IsEditable
FROM
    eccs.FieldDefinition AS field_info
WHERE
    field_info.ConfigDomainId = @AccommodationsDomainId
ORDER BY
    field_info.DisplayOrder;

------------------------------------------------------------
-- VERIFICATION 2
-- Runtime contract metadata
------------------------------------------------------------
SELECT
    contract.OperationCode,
    CONCAT(
        contract.ExternalSchemaName,
        N'.',
        contract.ExternalObjectName
    ) AS ExternalObject,
    contract.ExternalObjectType,
    contract.ContractSource,
    contract.ValidationStatus,
    contract.IsEnabled,
    contract.RequiresApproval,
    contract.RequiresReconciliation,
    contract.ContractVersion
FROM
    integration.SqlRuntimeContract AS contract
WHERE
    contract.ConfigDomainId = @AccommodationsDomainId
ORDER BY
    contract.OperationSequence;

------------------------------------------------------------
-- VERIFICATION 3
-- Runtime parameter contract
------------------------------------------------------------
SELECT
    contract.OperationCode,
    parameter_info.ParameterOrdinal,
    parameter_info.ParameterName,
    parameter_info.SqlDataType,
    parameter_info.MaxLength,
    parameter_info.SourceFieldCode
FROM
    integration.SqlRuntimeParameter AS parameter_info
    INNER JOIN integration.SqlRuntimeContract AS contract ON contract.SqlRuntimeContractId = parameter_info.SqlRuntimeContractId
WHERE
    contract.ConfigDomainId = @AccommodationsDomainId
ORDER BY
    contract.OperationSequence,
    parameter_info.ParameterOrdinal;

------------------------------------------------------------
-- VERIFICATION 4
-- Expected parameter counts
------------------------------------------------------------
SELECT
    contract.OperationCode,
    COUNT(parameter_info.SqlRuntimeParameterId) AS ParameterCount
FROM
    integration.SqlRuntimeContract AS contract
    LEFT JOIN integration.SqlRuntimeParameter AS parameter_info ON parameter_info.SqlRuntimeContractId = contract.SqlRuntimeContractId
WHERE
    contract.ConfigDomainId = @AccommodationsDomainId
GROUP BY
    contract.OperationCode,
    contract.OperationSequence
ORDER BY
    contract.OperationSequence;

------------------------------------------------------------
-- VERIFICATION 5
-- Safety gate
------------------------------------------------------------
SELECT
    CASE
        WHEN EXISTS (
            SELECT
                1
            FROM
                integration.SqlRuntimeContract
            WHERE
                ConfigDomainId = @AccommodationsDomainId
                AND IsEnabled = 1
        ) THEN N'FAIL'
        ELSE N'PASS'
    END AS RuntimeExecutionSafetyCheck,
    (
        SELECT
            COUNT(*)
        FROM
            integration.SqlRuntimeContract
        WHERE
            ConfigDomainId = @AccommodationsDomainId
            AND IsEnabled = 1
    ) AS EnabledContractCount;

------------------------------------------------------------
-- VERIFICATION 6
-- Confirm expected contracts exist exactly once.
------------------------------------------------------------
SELECT
    OperationCode,
    COUNT(*) AS ContractCount
FROM
    integration.SqlRuntimeContract
WHERE
    ConfigDomainId = @AccommodationsDomainId
GROUP BY
    OperationCode
ORDER BY
    OperationCode;

------------------------------------------------------------
-- COMPLETION
------------------------------------------------------------
PRINT N'';

PRINT N'ECCS Migration 003 completed.';

PRINT N'REG / EXPANSE / ACCOMMODATIONS field contract registered.';

PRINT N'VBA-observed SQL parameter contracts registered.';

PRINT N'Authoritative enterprise SQL metadata validation remains pending.';

PRINT N'All Accommodations runtime operations remain disabled.';

PRINT N'No external SQL procedure was executed.';
