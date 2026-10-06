/*
Expanse ConfigTool Factory
Expanse Cutover Configuration Suite (ECCS)

Step 60 - ECCS SQL Runtime POC
Migration 001 - Runtime Foundation

Target:
Local development SQL Server
Database: ECCS_Dev

Purpose:
Establish the shared ECCS metadata/control tables required before
implementing the EXPANSE Registration Accommodations runtime.

This migration DOES NOT:
- create enterprise target-system tables
- execute legacy VBA-era procedures
- publish configuration changes
- contain enterprise credentials
*/
SET
    NOCOUNT ON;

SET
    XACT_ABORT ON;

IF DB_NAME() <> N'ECCS_Dev' BEGIN
    RAISERROR('Migration 001 must execute against ECCS_Dev.', 16, 1);
    RETURN;
END;

------------------------------------------------------------
-- Verify required schemas.
------------------------------------------------------------
IF SCHEMA_ID(N'eccs') IS NULL BEGIN
    RAISERROR('Required schema eccs does not exist.', 16, 1);
    RETURN;
END;

IF SCHEMA_ID(N'staging') IS NULL BEGIN
    RAISERROR('Required schema staging does not exist.', 16, 1);
    RETURN;
END;

IF SCHEMA_ID(N'execution') IS NULL BEGIN
    RAISERROR('Required schema execution does not exist.', 16, 1);
    RETURN;
END;

IF SCHEMA_ID(N'audit') IS NULL BEGIN
    RAISERROR('Required schema audit does not exist.', 16, 1);
    RETURN;
END;

IF SCHEMA_ID(N'integration') IS NULL BEGIN
    RAISERROR('Required schema integration does not exist.', 16, 1);
    RETURN;
END;

------------------------------------------------------------
-- eccs.Environment
--
-- Logical ECCS environment/context.
--
-- Server/database credentials do NOT belong here.
------------------------------------------------------------
IF OBJECT_ID (N'eccs.Environment', N'U') IS NULL BEGIN
CREATE TABLE eccs.Environment (
    EnvironmentId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_eccs_Environment PRIMARY KEY CONSTRAINT DF_eccs_Environment_EnvironmentId DEFAULT NEWSEQUENTIALID (),
    EnvironmentCode NVARCHAR (30) NOT NULL,
    EnvironmentName NVARCHAR (100) NOT NULL,
    EnvironmentType NVARCHAR (30) NOT NULL,
    IsProduction BIT NOT NULL CONSTRAINT DF_eccs_Environment_IsProduction DEFAULT(0),
    IsActive BIT NOT NULL CONSTRAINT DF_eccs_Environment_IsActive DEFAULT(1),
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_Environment_CreatedAtUtc DEFAULT SYSUTCDATETIME (),
    CreatedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_Environment_CreatedBy DEFAULT SUSER_SNAME (),
    ModifiedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_Environment_ModifiedAtUtc DEFAULT SYSUTCDATETIME (),
    ModifiedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_Environment_ModifiedBy DEFAULT SUSER_SNAME (),
    RowVersion ROWVERSION NOT NULL,
    CONSTRAINT UQ_eccs_Environment_EnvironmentCode UNIQUE (EnvironmentCode),
    CONSTRAINT CK_eccs_Environment_EnvironmentType CHECK (
        EnvironmentType IN (N'LOCAL', N'DEV', N'TEST', N'UAT', N'PROD')
    )
);

END;

------------------------------------------------------------
-- eccs.ConfigTool
--
-- Registry of workbook/application families compiled into ECCS.
------------------------------------------------------------
IF OBJECT_ID (N'eccs.ConfigTool', N'U') IS NULL BEGIN
CREATE TABLE eccs.ConfigTool (
    ConfigToolId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_eccs_ConfigTool PRIMARY KEY CONSTRAINT DF_eccs_ConfigTool_ConfigToolId DEFAULT NEWSEQUENTIALID (),
    ToolCode NVARCHAR (50) NOT NULL,
    ToolName NVARCHAR (200) NOT NULL,
    VariantCode NVARCHAR (50) NOT NULL,
    SourceWorkbookName NVARCHAR (260) NULL,
    SourceWorkbookHash CHAR(64) NULL,
    CompilerVersion NVARCHAR (50) NULL,
    ManifestVersion NVARCHAR (50) NULL,
    IsActive BIT NOT NULL CONSTRAINT DF_eccs_ConfigTool_IsActive DEFAULT(1),
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_ConfigTool_CreatedAtUtc DEFAULT SYSUTCDATETIME (),
    CreatedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_ConfigTool_CreatedBy DEFAULT SUSER_SNAME (),
    ModifiedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_ConfigTool_ModifiedAtUtc DEFAULT SYSUTCDATETIME (),
    ModifiedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_ConfigTool_ModifiedBy DEFAULT SUSER_SNAME (),
    RowVersion ROWVERSION NOT NULL,
    CONSTRAINT UQ_eccs_ConfigTool_CodeVariant UNIQUE (ToolCode, VariantCode)
);

END;

------------------------------------------------------------
-- eccs.ConfigDomain
--
-- Domain registry beneath a ConfigTool.
--
-- Example:
--   Tool    = REG
--   Variant = EXPANSE
--   Domain  = ACCOMMODATIONS
------------------------------------------------------------
IF OBJECT_ID (N'eccs.ConfigDomain', N'U') IS NULL BEGIN
CREATE TABLE eccs.ConfigDomain (
    ConfigDomainId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_eccs_ConfigDomain PRIMARY KEY CONSTRAINT DF_eccs_ConfigDomain_ConfigDomainId DEFAULT NEWSEQUENTIALID (),
    ConfigToolId UNIQUEIDENTIFIER NOT NULL,
    DomainCode NVARCHAR (100) NOT NULL,
    DomainName NVARCHAR (200) NOT NULL,
    SourceWorksheetName NVARCHAR (128) NULL,
    SourceTableName NVARCHAR (128) NULL,
    DisplayOrder INT NOT NULL CONSTRAINT DF_eccs_ConfigDomain_DisplayOrder DEFAULT(0),
    IsActive BIT NOT NULL CONSTRAINT DF_eccs_ConfigDomain_IsActive DEFAULT(1),
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_ConfigDomain_CreatedAtUtc DEFAULT SYSUTCDATETIME (),
    CreatedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_ConfigDomain_CreatedBy DEFAULT SUSER_SNAME (),
    ModifiedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_ConfigDomain_ModifiedAtUtc DEFAULT SYSUTCDATETIME (),
    ModifiedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_ConfigDomain_ModifiedBy DEFAULT SUSER_SNAME (),
    RowVersion ROWVERSION NOT NULL,
    CONSTRAINT FK_eccs_ConfigDomain_ConfigTool FOREIGN KEY (ConfigToolId) REFERENCES eccs.ConfigTool (ConfigToolId),
    CONSTRAINT UQ_eccs_ConfigDomain_ToolDomain UNIQUE (ConfigToolId, DomainCode)
);

END;

------------------------------------------------------------
-- eccs.FieldDefinition
--
-- Metadata describing fields exposed by a ConfigDomain.
------------------------------------------------------------
IF OBJECT_ID (N'eccs.FieldDefinition', N'U') IS NULL BEGIN
CREATE TABLE eccs.FieldDefinition (
    FieldDefinitionId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_eccs_FieldDefinition PRIMARY KEY CONSTRAINT DF_eccs_FieldDefinition_FieldDefinitionId DEFAULT NEWSEQUENTIALID (),
    ConfigDomainId UNIQUEIDENTIFIER NOT NULL,
    FieldCode NVARCHAR (128) NOT NULL,
    FieldName NVARCHAR (200) NOT NULL,
    SourceColumnName NVARCHAR (200) NULL,
    DataType NVARCHAR (50) NOT NULL,
    FieldRole NVARCHAR (50) NOT NULL,
    DisplayOrder INT NOT NULL CONSTRAINT DF_eccs_FieldDefinition_DisplayOrder DEFAULT(0),
    IsRequired BIT NOT NULL CONSTRAINT DF_eccs_FieldDefinition_IsRequired DEFAULT(0),
    IsEditable BIT NOT NULL CONSTRAINT DF_eccs_FieldDefinition_IsEditable DEFAULT(0),
    IsActive BIT NOT NULL CONSTRAINT DF_eccs_FieldDefinition_IsActive DEFAULT(1),
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_FieldDefinition_CreatedAtUtc DEFAULT SYSUTCDATETIME (),
    CreatedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_FieldDefinition_CreatedBy DEFAULT SUSER_SNAME (),
    ModifiedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_eccs_FieldDefinition_ModifiedAtUtc DEFAULT SYSUTCDATETIME (),
    ModifiedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_eccs_FieldDefinition_ModifiedBy DEFAULT SUSER_SNAME (),
    RowVersion ROWVERSION NOT NULL,
    CONSTRAINT FK_eccs_FieldDefinition_ConfigDomain FOREIGN KEY (ConfigDomainId) REFERENCES eccs.ConfigDomain (ConfigDomainId),
    CONSTRAINT UQ_eccs_FieldDefinition_DomainField UNIQUE (ConfigDomainId, FieldCode),
    CONSTRAINT CK_eccs_FieldDefinition_FieldRole CHECK (
        FieldRole IN (
            N'KEY',
            N'SOURCE',
            N'TARGET',
            N'MATCH',
            N'USAGE',
            N'STATUS',
            N'ACTION',
            N'AUDIT',
            N'SYSTEM',
            N'OTHER'
        )
    )
);

END;

------------------------------------------------------------
-- integration.ApiDefinition
--
-- Metadata registry only.
-- No API credentials or secrets are stored here.
------------------------------------------------------------
IF OBJECT_ID (N'integration.ApiDefinition', N'U') IS NULL BEGIN
CREATE TABLE integration.ApiDefinition (
    ApiDefinitionId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_integration_ApiDefinition PRIMARY KEY CONSTRAINT DF_integration_ApiDefinition_ApiDefinitionId DEFAULT NEWSEQUENTIALID (),
    ApiCode NVARCHAR (100) NOT NULL,
    ApiName NVARCHAR (200) NOT NULL,
    ApiType NVARCHAR (50) NOT NULL,
    ApiVersion NVARCHAR (50) NULL,
    CatalogReference NVARCHAR (1000) NULL,
    ConnectionReference NVARCHAR (500) NULL,
    IsActive BIT NOT NULL CONSTRAINT DF_integration_ApiDefinition_IsActive DEFAULT(1),
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_integration_ApiDefinition_CreatedAtUtc DEFAULT SYSUTCDATETIME (),
    CreatedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_integration_ApiDefinition_CreatedBy DEFAULT SUSER_SNAME (),
    ModifiedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_integration_ApiDefinition_ModifiedAtUtc DEFAULT SYSUTCDATETIME (),
    ModifiedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_integration_ApiDefinition_ModifiedBy DEFAULT SUSER_SNAME (),
    RowVersion ROWVERSION NOT NULL,
    CONSTRAINT UQ_integration_ApiDefinition_ApiCode UNIQUE (ApiCode),
    CONSTRAINT CK_integration_ApiDefinition_ApiType CHECK (
        ApiType IN (N'HCA_API', N'FHIR', N'REST', N'HL7', N'OTHER')
    )
);

END;

------------------------------------------------------------
-- Seed LOCAL environment.
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        eccs.Environment
    WHERE
        EnvironmentCode = N'LOCAL'
) BEGIN
INSERT INTO
    eccs.Environment (
        EnvironmentCode,
        EnvironmentName,
        EnvironmentType,
        IsProduction
    )
VALUES
    (N'LOCAL', N'ECCS Local Development', N'LOCAL', 0);

END;

------------------------------------------------------------
-- Seed Registration EXPANSE ConfigTool.
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        eccs.ConfigTool
    WHERE
        ToolCode = N'REG'
        AND VariantCode = N'EXPANSE'
) BEGIN
INSERT INTO
    eccs.ConfigTool (
        ToolCode,
        ToolName,
        VariantCode,
        SourceWorkbookName
    )
VALUES
    (
        N'REG',
        N'Registration',
        N'EXPANSE',
        N'Mapping_Expanse_REG_Domain.xlsb'
    );

END;

------------------------------------------------------------
-- Seed Registration Accommodations domain.
------------------------------------------------------------
DECLARE @RegistrationToolId UNIQUEIDENTIFIER;

SELECT
    @RegistrationToolId = ConfigToolId
FROM
    eccs.ConfigTool
WHERE
    ToolCode = N'REG'
    AND VariantCode = N'EXPANSE';

IF @RegistrationToolId IS NULL BEGIN
    RAISERROR('REG / EXPANSE ConfigTool could not be resolved.', 16, 1);
    RETURN;
END;

IF NOT EXISTS (
    SELECT
        1
    FROM
        eccs.ConfigDomain
    WHERE
        ConfigToolId = @RegistrationToolId
        AND DomainCode = N'ACCOMMODATIONS'
) BEGIN
INSERT INTO
    eccs.ConfigDomain (
        ConfigToolId,
        DomainCode,
        DomainName,
        SourceWorksheetName,
        SourceTableName,
        DisplayOrder
    )
VALUES
    (
        @RegistrationToolId,
        N'ACCOMMODATIONS',
        N'Accommodations',
        N'Accommodations',
        N'tblAccommodations',
        10
    );

END;

------------------------------------------------------------
-- Verification.
------------------------------------------------------------
SELECT
    EnvironmentCode,
    EnvironmentName,
    EnvironmentType,
    IsProduction,
    IsActive
FROM
    eccs.Environment
ORDER BY
    EnvironmentCode;

SELECT
    ToolCode,
    ToolName,
    VariantCode,
    SourceWorkbookName,
    IsActive
FROM
    eccs.ConfigTool
ORDER BY
    ToolCode,
    VariantCode;

SELECT
    tool.ToolCode,
    tool.VariantCode,
    domain.DomainCode,
    domain.DomainName,
    domain.SourceWorksheetName,
    domain.SourceTableName,
    domain.IsActive
FROM
    eccs.ConfigDomain AS domain
    INNER JOIN eccs.ConfigTool AS tool ON tool.ConfigToolId = domain.ConfigToolId
ORDER BY
    tool.ToolCode,
    tool.VariantCode,
    domain.DisplayOrder;

SELECT
    s.name AS SchemaName,
    t.name AS TableName
FROM
    sys.tables AS t
    INNER JOIN sys.schemas AS s ON s.schema_id = t.schema_id
WHERE
    s.name IN (N'eccs', N'integration')
ORDER BY
    s.name,
    t.name;

