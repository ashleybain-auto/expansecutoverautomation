/*
    Expanse ConfigTool Factory
    Expanse Cutover Configuration Suite (ECCS)

    Step 60 - ECCS SQL Runtime POC
    Migration 004
    REG / EXPANSE / ACCOMMODATIONS DEMO RUNTIME

    Purpose:
        Provide a deterministic local SQL dataset for the
        Power Apps proof of concept.

    Target:
        ECCS_Dev

    This is a local ECCS POC runtime.
    It is not an enterprise target-system database.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

IF DB_NAME() <> N'ECCS_Dev'
BEGIN
    RAISERROR(
        'Migration 004 must execute against ECCS_Dev.',
        16,
        1
    );

    RETURN;
END;

IF SCHEMA_ID(N'eccs') IS NULL
BEGIN
    RAISERROR(
        'Required schema eccs does not exist.',
        16,
        1
    );

    RETURN;
END;

------------------------------------------------------------
-- DEMO TABLE
------------------------------------------------------------

IF OBJECT_ID(N'eccs.AccommodationMappingDemo', N'U') IS NULL
BEGIN
    CREATE TABLE eccs.AccommodationMappingDemo
    (
        AccommodationMappingId INT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_eccs_AccommodationMappingDemo
            PRIMARY KEY,

        FacilityMnem_Source VARCHAR(25) NOT NULL,

        FacilityMnem_Target VARCHAR(25) NOT NULL,

        Accommodation_Mnem_Source VARCHAR(25) NOT NULL,

        Accommodation_Mnem_Target VARCHAR(25) NULL,

        Accommodation_Name_Target VARCHAR(255) NULL,

        PA_Code_Target VARCHAR(25) NULL,

        Active_Target VARCHAR(25) NULL,

        DisplayCurrentValues VARCHAR(25) NULL,

        ExcludeFromSharepoint VARCHAR(25) NULL,

        Action_To_Take VARCHAR(50) NULL,

        Update_User VARCHAR(255) NULL,

        Update_Datetime DATETIME2(3) NULL,

        Created_At_Utc DATETIME2(3) NOT NULL
            CONSTRAINT DF_eccs_AccommodationMappingDemo_Created
            DEFAULT SYSUTCDATETIME(),

        Modified_At_Utc DATETIME2(3) NOT NULL
            CONSTRAINT DF_eccs_AccommodationMappingDemo_Modified
            DEFAULT SYSUTCDATETIME(),

        RowVersion ROWVERSION NOT NULL
    );
END;

------------------------------------------------------------
-- DEMO DATA
------------------------------------------------------------

IF NOT EXISTS
(
    SELECT 1
    FROM eccs.AccommodationMappingDemo
)
BEGIN
    INSERT INTO eccs.AccommodationMappingDemo
    (
        FacilityMnem_Source,
        FacilityMnem_Target,
        Accommodation_Mnem_Source,
        Accommodation_Mnem_Target,
        Accommodation_Name_Target,
        PA_Code_Target,
        Active_Target,
        DisplayCurrentValues,
        ExcludeFromSharepoint,
        Action_To_Take,
        Update_User,
        Update_Datetime
    )
    VALUES
    ('FAC001','FAC101','STD','STD','Standard','PA001','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC001','FAC101','DLX','DLX','Deluxe','PA002','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC001','FAC101','ADA','ADA','Accessible','PA003','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC001','FAC101','PED','PED','Pediatric','PA004','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC001','FAC101','ISO','ISO','Isolation','PA005','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC002','FAC102','STD','STD','Standard','PA101','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC002','FAC102','DLX','DLX','Deluxe','PA102','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC002','FAC102','ADA','ADA','Accessible','PA103','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC003','FAC103','STD','STD','Standard','PA201','Y','Y','N','None','ECCS POC',SYSUTCDATETIME()),
    ('FAC003','FAC103','OBS','OBS','Observation','PA202','Y','Y','N','None','ECCS POC',SYSUTCDATETIME());
END;

------------------------------------------------------------
-- READ VIEW
------------------------------------------------------------

IF OBJECT_ID(N'eccs.vw_AccommodationsMappingDemo', N'V') IS NULL
BEGIN
    EXEC
    (
        N'CREATE VIEW eccs.vw_AccommodationsMappingDemo
        AS
        SELECT
            AccommodationMappingId,
            FacilityMnem_Source,
            FacilityMnem_Target,
            Accommodation_Mnem_Source,
            Accommodation_Mnem_Target,
            Accommodation_Name_Target,
            PA_Code_Target,
            Active_Target,
            DisplayCurrentValues,
            ExcludeFromSharepoint,
            Action_To_Take,
            Update_User,
            Update_Datetime,
            Modified_At_Utc,
            RowVersion
        FROM eccs.AccommodationMappingDemo;'
    );
END;

------------------------------------------------------------
-- CONTROLLED POC UPDATE PROCEDURE
------------------------------------------------------------

IF OBJECT_ID(N'eccs.usp_UpdateAccommodationMappingDemo', N'P') IS NULL
BEGIN
    EXEC
    (
        N'CREATE PROCEDURE eccs.usp_UpdateAccommodationMappingDemo
            @AccommodationMappingId INT,
            @AccommodationMnemTarget VARCHAR(25),
            @AccommodationNameTarget VARCHAR(255),
            @PACodeTarget VARCHAR(25),
            @ActiveTarget VARCHAR(25),
            @DisplayCurrentValues VARCHAR(25),
            @ExcludeFromSharepoint VARCHAR(25),
            @UserName VARCHAR(255)
        AS
        BEGIN
            SET NOCOUNT ON;
            SET XACT_ABORT ON;

            UPDATE eccs.AccommodationMappingDemo
            SET
                Accommodation_Mnem_Target = @AccommodationMnemTarget,
                Accommodation_Name_Target = @AccommodationNameTarget,
                PA_Code_Target = @PACodeTarget,
                Active_Target = @ActiveTarget,
                DisplayCurrentValues = @DisplayCurrentValues,
                ExcludeFromSharepoint = @ExcludeFromSharepoint,
                Action_To_Take = ''Update'',
                Update_User = @UserName,
                Update_Datetime = SYSUTCDATETIME(),
                Modified_At_Utc = SYSUTCDATETIME()
            WHERE AccommodationMappingId = @AccommodationMappingId;

            SELECT
                AccommodationMappingId,
                FacilityMnem_Source,
                FacilityMnem_Target,
                Accommodation_Mnem_Source,
                Accommodation_Mnem_Target,
                Accommodation_Name_Target,
                PA_Code_Target,
                Active_Target,
                DisplayCurrentValues,
                ExcludeFromSharepoint,
                Action_To_Take,
                Update_User,
                Update_Datetime
            FROM eccs.AccommodationMappingDemo
            WHERE AccommodationMappingId = @AccommodationMappingId;
        END;'
    );
END;

------------------------------------------------------------
-- VERIFICATION 1
------------------------------------------------------------

SELECT
    COUNT(*) AS DemoRowCount
FROM eccs.AccommodationMappingDemo;

------------------------------------------------------------
-- VERIFICATION 2
------------------------------------------------------------

SELECT
    AccommodationMappingId,
    FacilityMnem_Source,
    FacilityMnem_Target,
    Accommodation_Mnem_Source,
    Accommodation_Mnem_Target,
    Accommodation_Name_Target,
    PA_Code_Target,
    Active_Target,
    DisplayCurrentValues,
    ExcludeFromSharepoint,
    Action_To_Take,
    Update_User,
    Update_Datetime
FROM eccs.vw_AccommodationsMappingDemo
ORDER BY AccommodationMappingId;

------------------------------------------------------------
-- VERIFICATION 3
------------------------------------------------------------

SELECT
    OBJECT_ID(
        N'eccs.AccommodationMappingDemo',
        N'U'
    ) AS DemoTableObjectId,

    OBJECT_ID(
        N'eccs.vw_AccommodationsMappingDemo',
        N'V'
    ) AS DemoViewObjectId,

    OBJECT_ID(
        N'eccs.usp_UpdateAccommodationMappingDemo',
        N'P'
    ) AS DemoUpdateProcedureObjectId;
