/*
Expanse ConfigTool Factory
Expanse Cutover Configuration Suite (ECCS)

Step 60 - ECCS SQL Runtime POC
Migration 002 - Runtime Contract and Execution Evidence

Target:
SQL Server: localhost
Database:   ECCS_Dev

Purpose:
Establish the metadata and execution envelope used by ECCS for:

READ
->
PREVIEW
->
PUBLISH
->
RECONCILE

The contract describes external/legacy SQL operations without
duplicating or executing those procedures inside ECCS_Dev.

IMPORTANT:
- This migration does NOT execute target procedures.
- This migration does NOT publish configuration changes.
- This migration does NOT contain credentials.
- All discovered legacy operations are initially DISABLED.
- Publish operations require approval and reconciliation.
*/
SET
    NOCOUNT ON;

SET
    XACT_ABORT ON;

------------------------------------------------------------
-- DATABASE SAFETY CHECK
------------------------------------------------------------
IF DB_NAME() <> N'ECCS_Dev' BEGIN
    RAISERROR('Migration 002 must execute against ECCS_Dev.', 16, 1);
    RETURN;
END;

------------------------------------------------------------
-- REQUIRED FOUNDATION CHECKS
------------------------------------------------------------
IF SCHEMA_ID(N'eccs') IS NULL BEGIN
    RAISERROR('Required schema eccs does not exist.', 16, 1);
    RETURN;
END;

IF SCHEMA_ID(N'integration') IS NULL BEGIN
    RAISERROR('Required schema integration does not exist.', 16, 1);
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

IF OBJECT_ID(N'eccs.ConfigDomain', N'U') IS NULL BEGIN
    RAISERROR('Required table eccs.ConfigDomain does not exist.', 16, 1);
    RETURN;
END;

IF OBJECT_ID(N'eccs.ConfigTool', N'U') IS NULL BEGIN
    RAISERROR('Required table eccs.ConfigTool does not exist.', 16, 1);
    RETURN;
END;

IF OBJECT_ID(N'eccs.Environment', N'U') IS NULL BEGIN
    RAISERROR('Required table eccs.Environment does not exist.', 16, 1);
    RETURN;
END;

------------------------------------------------------------
-- integration.SqlRuntimeContract
--
-- Registry of external/legacy SQL operations known to ECCS.
--
-- Example:
--
--   REG / EXPANSE / ACCOMMODATIONS
--   READ
--   dbo.UI_Excel_Select_Xwalk_Source_Accommodations
--
-- IMPORTANT:
-- External object names are metadata only.
-- Nothing in this table executes those objects.
------------------------------------------------------------
IF OBJECT_ID (N'integration.SqlRuntimeContract', N'U') IS NULL BEGIN
CREATE TABLE integration.SqlRuntimeContract (
    SqlRuntimeContractId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_integration_SqlRuntimeContract PRIMARY KEY CONSTRAINT DF_integration_SqlRuntimeContract_Id DEFAULT NEWSEQUENTIALID (),
    ConfigDomainId UNIQUEIDENTIFIER NOT NULL,
    OperationCode NVARCHAR (50) NOT NULL,
    OperationSequence INT NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Sequence DEFAULT(100),
    ExternalSchemaName SYSNAME NOT NULL,
    ExternalObjectName SYSNAME NOT NULL,
    ExternalObjectType NVARCHAR (30) NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_ObjectType DEFAULT(N'PROCEDURE'),
    ConnectionReference NVARCHAR (500) NULL,
    ContractVersion NVARCHAR (50) NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Version DEFAULT(N'1.0.0'),
    IsReadOnly BIT NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_ReadOnly DEFAULT(1),
    RequiresApproval BIT NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Approval DEFAULT(0),
    RequiresReconciliation BIT NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Reconciliation DEFAULT(1),
    IsEnabled BIT NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Enabled DEFAULT(0),
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Created DEFAULT SYSUTCDATETIME (),
    CreatedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_CreatedBy DEFAULT SUSER_SNAME (),
    ModifiedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_Modified DEFAULT SYSUTCDATETIME (),
    ModifiedBy NVARCHAR (256) NOT NULL CONSTRAINT DF_integration_SqlRuntimeContract_ModifiedBy DEFAULT SUSER_SNAME (),
    RowVersion ROWVERSION NOT NULL,
    CONSTRAINT FK_integration_SqlRuntimeContract_ConfigDomain FOREIGN KEY (ConfigDomainId) REFERENCES eccs.ConfigDomain (ConfigDomainId),
    CONSTRAINT UQ_integration_SqlRuntimeContract_Operation UNIQUE (ConfigDomainId, OperationCode),
    CONSTRAINT CK_integration_SqlRuntimeContract_Operation CHECK (
        OperationCode IN (
            N'READ',
            N'PREVIEW',
            N'PUBLISH_UPDATE',
            N'PUBLISH_INSERT',
            N'RECONCILE'
        )
    ),
    CONSTRAINT CK_integration_SqlRuntimeContract_ObjectType CHECK (
        ExternalObjectType IN (N'PROCEDURE', N'VIEW', N'FUNCTION')
    )
);

END;

------------------------------------------------------------
-- integration.SqlRuntimeParameter
--
-- Stores the exact parameter contract discovered from an
-- authoritative external SQL object.
--
-- This table remains empty until parameter discovery has been
-- completed and reviewed.
------------------------------------------------------------
IF OBJECT_ID (N'integration.SqlRuntimeParameter', N'U') IS NULL BEGIN
CREATE TABLE integration.SqlRuntimeParameter (
    SqlRuntimeParameterId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_integration_SqlRuntimeParameter PRIMARY KEY CONSTRAINT DF_integration_SqlRuntimeParameter_Id DEFAULT NEWSEQUENTIALID (),
    SqlRuntimeContractId UNIQUEIDENTIFIER NOT NULL,
    ParameterOrdinal INT NOT NULL,
    ParameterName SYSNAME NOT NULL,
    SqlDataType SYSNAME NOT NULL,
    MaxLength INT NULL,
    NumericPrecision TINYINT NULL,
    NumericScale TINYINT NULL,
    IsOutput BIT NOT NULL CONSTRAINT DF_integration_SqlRuntimeParameter_Output DEFAULT(0),
    IsRequired BIT NOT NULL CONSTRAINT DF_integration_SqlRuntimeParameter_Required DEFAULT(1),
    SourceFieldCode NVARCHAR (128) NULL,
    CreatedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_integration_SqlRuntimeParameter_Created DEFAULT SYSUTCDATETIME (),
    CONSTRAINT FK_integration_SqlRuntimeParameter_Contract FOREIGN KEY (SqlRuntimeContractId) REFERENCES integration.SqlRuntimeContract (SqlRuntimeContractId),
    CONSTRAINT UQ_integration_SqlRuntimeParameter_Ordinal UNIQUE (SqlRuntimeContractId, ParameterOrdinal),
    CONSTRAINT UQ_integration_SqlRuntimeParameter_Name UNIQUE (SqlRuntimeContractId, ParameterName)
);

END;

------------------------------------------------------------
-- execution.RuntimeRun
--
-- One controlled execution envelope for an ECCS runtime
-- operation.
--
-- Examples:
--   READ
--   PREVIEW
--   PUBLISH_UPDATE
--   PUBLISH_INSERT
--   RECONCILE
------------------------------------------------------------
IF OBJECT_ID (N'execution.RuntimeRun', N'U') IS NULL BEGIN
CREATE TABLE execution.RuntimeRun (
    RuntimeRunId UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_execution_RuntimeRun PRIMARY KEY CONSTRAINT DF_execution_RuntimeRun_Id DEFAULT NEWSEQUENTIALID (),
    CorrelationId UNIQUEIDENTIFIER NOT NULL,
    SqlRuntimeContractId UNIQUEIDENTIFIER NOT NULL,
    EnvironmentId UNIQUEIDENTIFIER NOT NULL,
    RunType NVARCHAR (50) NOT NULL,
    RunStatus NVARCHAR (50) NOT NULL,
    RequestedBy NVARCHAR (256) NOT NULL,
    RequestedAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_execution_RuntimeRun_Requested DEFAULT SYSUTCDATETIME (),
    StartedAtUtc DATETIME2 (3) NULL,
    CompletedAtUtc DATETIME2 (3) NULL,
    SourceRowCount BIGINT NULL,
    ResultRowCount BIGINT NULL,
    AffectedRowCount BIGINT NULL,
    ErrorCode NVARCHAR (100) NULL,
    ErrorMessage NVARCHAR (4000) NULL,
    CONSTRAINT FK_execution_RuntimeRun_Contract FOREIGN KEY (SqlRuntimeContractId) REFERENCES integration.SqlRuntimeContract (SqlRuntimeContractId),
    CONSTRAINT FK_execution_RuntimeRun_Environment FOREIGN KEY (EnvironmentId) REFERENCES eccs.Environment (EnvironmentId),
    CONSTRAINT UQ_execution_RuntimeRun_Correlation UNIQUE (CorrelationId),
    CONSTRAINT CK_execution_RuntimeRun_Type CHECK (
        RunType IN (
            N'READ',
            N'PREVIEW',
            N'PUBLISH_UPDATE',
            N'PUBLISH_INSERT',
            N'RECONCILE'
        )
    ),
    CONSTRAINT CK_execution_RuntimeRun_Status CHECK (
        RunStatus IN (
            N'QUEUED',
            N'RUNNING',
            N'SUCCEEDED',
            N'FAILED',
            N'CANCELLED',
            N'RECONCILIATION_REQUIRED',
            N'RECONCILED'
        )
    )
);

END;

------------------------------------------------------------
-- RuntimeRun indexes
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        sys.indexes
    WHERE
        object_id = OBJECT_ID (N'execution.RuntimeRun')
        AND name = N'IX_execution_RuntimeRun_ContractRequested'
) BEGIN
CREATE INDEX IX_execution_RuntimeRun_ContractRequested ON execution.RuntimeRun (SqlRuntimeContractId, RequestedAtUtc DESC);

END;

IF NOT EXISTS (
    SELECT
        1
    FROM
        sys.indexes
    WHERE
        object_id = OBJECT_ID (N'execution.RuntimeRun')
        AND name = N'IX_execution_RuntimeRun_Status'
) BEGIN
CREATE INDEX IX_execution_RuntimeRun_Status ON execution.RuntimeRun (RunStatus, RequestedAtUtc);

END;

------------------------------------------------------------
-- audit.RuntimeEvent
--
-- Append-only runtime evidence.
--
-- Normal application behavior INSERTS events.
-- Existing events should not be rewritten as part of normal
-- runtime processing.
------------------------------------------------------------
IF OBJECT_ID (N'audit.RuntimeEvent', N'U') IS NULL BEGIN
CREATE TABLE audit.RuntimeEvent (
    RuntimeEventId BIGINT IDENTITY (1, 1) NOT NULL CONSTRAINT PK_audit_RuntimeEvent PRIMARY KEY,
    RuntimeRunId UNIQUEIDENTIFIER NOT NULL,
    CorrelationId UNIQUEIDENTIFIER NOT NULL,
    EventType NVARCHAR (100) NOT NULL,
    EventStatus NVARCHAR (50) NOT NULL,
    EventAtUtc DATETIME2 (3) NOT NULL CONSTRAINT DF_audit_RuntimeEvent_EventAt DEFAULT SYSUTCDATETIME (),
    Actor NVARCHAR (256) NOT NULL,
    BeforeState NVARCHAR (MAX) NULL,
    AfterState NVARCHAR (MAX) NULL,
    Evidence NVARCHAR (MAX) NULL,
    ErrorCode NVARCHAR (100) NULL,
    ErrorMessage NVARCHAR (4000) NULL,
    CONSTRAINT FK_audit_RuntimeEvent_RuntimeRun FOREIGN KEY (RuntimeRunId) REFERENCES execution.RuntimeRun (RuntimeRunId),
    CONSTRAINT CK_audit_RuntimeEvent_BeforeStateJson CHECK (
        BeforeState IS NULL
        OR ISJSON (BeforeState) = 1
    ),
    CONSTRAINT CK_audit_RuntimeEvent_AfterStateJson CHECK (
        AfterState IS NULL
        OR ISJSON (AfterState) = 1
    ),
    CONSTRAINT CK_audit_RuntimeEvent_EvidenceJson CHECK (
        Evidence IS NULL
        OR ISJSON (Evidence) = 1
    )
);

END;

------------------------------------------------------------
-- RuntimeEvent indexes
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        sys.indexes
    WHERE
        object_id = OBJECT_ID (N'audit.RuntimeEvent')
        AND name = N'IX_audit_RuntimeEvent_Run'
) BEGIN
CREATE INDEX IX_audit_RuntimeEvent_Run ON audit.RuntimeEvent (RuntimeRunId, RuntimeEventId);

END;

IF NOT EXISTS (
    SELECT
        1
    FROM
        sys.indexes
    WHERE
        object_id = OBJECT_ID (N'audit.RuntimeEvent')
        AND name = N'IX_audit_RuntimeEvent_Correlation'
) BEGIN
CREATE INDEX IX_audit_RuntimeEvent_Correlation ON audit.RuntimeEvent (CorrelationId, RuntimeEventId);

END;

------------------------------------------------------------
-- Resolve REG / EXPANSE / ACCOMMODATIONS
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

IF @AccommodationsDomainId IS NULL BEGIN
    RAISERROR('REG / EXPANSE / ACCOMMODATIONS domain could not be resolved.', 16, 1);
    RETURN;
END;

------------------------------------------------------------
-- Register READ contract
--
-- DISABLED until the authoritative procedure contract has
-- been captured and reviewed.
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        integration.SqlRuntimeContract
    WHERE
        ConfigDomainId = @AccommodationsDomainId
        AND OperationCode = N'READ'
) BEGIN
INSERT INTO
    integration.SqlRuntimeContract (
        ConfigDomainId,
        OperationCode,
        OperationSequence,
        ExternalSchemaName,
        ExternalObjectName,
        ExternalObjectType,
        ConnectionReference,
        ContractVersion,
        IsReadOnly,
        RequiresApproval,
        RequiresReconciliation,
        IsEnabled
    )
VALUES
    (
        @AccommodationsDomainId,
        N'READ',
        10,
        N'dbo',
        N'UI_Excel_Select_Xwalk_Source_Accommodations',
        N'PROCEDURE',
        NULL,
        N'1.0.0',
        1,
        0,
        0,
        0
    );

END;

------------------------------------------------------------
-- Register PUBLISH_UPDATE contract
--
-- DISABLED.
-- Requires approval.
-- Requires authoritative re-read/reconciliation.
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        integration.SqlRuntimeContract
    WHERE
        ConfigDomainId = @AccommodationsDomainId
        AND OperationCode = N'PUBLISH_UPDATE'
) BEGIN
INSERT INTO
    integration.SqlRuntimeContract (
        ConfigDomainId,
        OperationCode,
        OperationSequence,
        ExternalSchemaName,
        ExternalObjectName,
        ExternalObjectType,
        ConnectionReference,
        ContractVersion,
        IsReadOnly,
        RequiresApproval,
        RequiresReconciliation,
        IsEnabled
    )
VALUES
    (
        @AccommodationsDomainId,
        N'PUBLISH_UPDATE',
        30,
        N'dbo',
        N'UI_Excel_Update_Xwalk_Source_Accommodations',
        N'PROCEDURE',
        NULL,
        N'1.0.0',
        0,
        1,
        1,
        0
    );

END;

------------------------------------------------------------
-- Register PUBLISH_INSERT contract
--
-- DISABLED.
-- Requires approval.
-- Requires authoritative re-read/reconciliation.
------------------------------------------------------------
IF NOT EXISTS (
    SELECT
        1
    FROM
        integration.SqlRuntimeContract
    WHERE
        ConfigDomainId = @AccommodationsDomainId
        AND OperationCode = N'PUBLISH_INSERT'
) BEGIN
INSERT INTO
    integration.SqlRuntimeContract (
        ConfigDomainId,
        OperationCode,
        OperationSequence,
        ExternalSchemaName,
        ExternalObjectName,
        ExternalObjectType,
        ConnectionReference,
        ContractVersion,
        IsReadOnly,
        RequiresApproval,
        RequiresReconciliation,
        IsEnabled
    )
VALUES
    (
        @AccommodationsDomainId,
        N'PUBLISH_INSERT',
        40,
        N'dbo',
        N'UI_Excel_Insert_NewTargetAccommodation',
        N'PROCEDURE',
        NULL,
        N'1.0.0',
        0,
        1,
        1,
        0
    );

END;

------------------------------------------------------------
-- VERIFICATION 1
-- Runtime tables
------------------------------------------------------------
SELECT
    schema_info.name AS SchemaName,
    table_info.name AS TableName
FROM
    sys.tables AS table_info
    INNER JOIN sys.schemas AS schema_info ON schema_info.schema_id = table_info.schema_id
WHERE
    (
        schema_info.name = N'integration'
        AND table_info.name IN (N'SqlRuntimeContract', N'SqlRuntimeParameter')
    )
    OR (
        schema_info.name = N'execution'
        AND table_info.name = N'RuntimeRun'
    )
    OR (
        schema_info.name = N'audit'
        AND table_info.name = N'RuntimeEvent'
    )
ORDER BY
    schema_info.name,
    table_info.name;

------------------------------------------------------------
-- VERIFICATION 2
-- Accommodations SQL contracts
------------------------------------------------------------
SELECT
    tool.ToolCode,
    tool.VariantCode,
    domain.DomainCode,
    contract.OperationCode,
    CONCAT(
        contract.ExternalSchemaName,
        N'.',
        contract.ExternalObjectName
    ) AS ExternalObject,
    contract.ExternalObjectType,
    contract.IsReadOnly,
    contract.RequiresApproval,
    contract.RequiresReconciliation,
    contract.IsEnabled,
    contract.ContractVersion
FROM
    integration.SqlRuntimeContract AS contract
    INNER JOIN eccs.ConfigDomain AS domain ON domain.ConfigDomainId = contract.ConfigDomainId
    INNER JOIN eccs.ConfigTool AS tool ON tool.ConfigToolId = domain.ConfigToolId
WHERE
    tool.ToolCode = N'REG'
    AND tool.VariantCode = N'EXPANSE'
    AND domain.DomainCode = N'ACCOMMODATIONS'
ORDER BY
    contract.OperationSequence;

------------------------------------------------------------
-- VERIFICATION 3
-- Parameter table should currently contain zero rows for
-- these contracts because authoritative SQL parameter
-- discovery has not yet been loaded.
------------------------------------------------------------
SELECT
    contract.OperationCode,
    COUNT(parameter.SqlRuntimeParameterId) AS ParameterCount
FROM
    integration.SqlRuntimeContract AS contract
    LEFT JOIN integration.SqlRuntimeParameter AS parameter ON parameter.SqlRuntimeContractId = contract.SqlRuntimeContractId
WHERE
    contract.ConfigDomainId = @AccommodationsDomainId
GROUP BY
    contract.OperationCode,
    contract.OperationSequence
ORDER BY
    contract.OperationSequence;

------------------------------------------------------------
-- VERIFICATION 4
-- Confirm that none of the Accommodations contracts are
-- currently enabled for execution.
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
-- MIGRATION COMPLETE
------------------------------------------------------------
PRINT N'';

PRINT N'ECCS Migration 002 completed.';

PRINT N'REG / EXPANSE / ACCOMMODATIONS runtime contracts registered.';

PRINT N'All runtime contracts remain disabled.';

PRINT N'No external SQL procedure was executed.';

