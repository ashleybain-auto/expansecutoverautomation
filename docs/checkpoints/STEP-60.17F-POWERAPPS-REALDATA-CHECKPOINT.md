# ECCS POC Checkpoint - Step 60.17F

## Resume Point

Resume at:

### Step 60.17F - Power Apps Real-Data Import / Column Mapping

Next objective:

Import the real Registration EXPANSE Accommodations dataset into the
DevelopmentAuto Power Platform environment and complete column mapping.

---

## Repository

Expanse-ConfigTool-Factory

Workspace:

C:\Users\QXA4067\Projects\Expanse-ConfigTool-Factory

---

## Local ECCS SQL Runtime

Server:

CORPQXA4067D / localhost

Database:

ECCS_Dev

Schemas:

- eccs
- staging
- execution
- audit
- integration

---

## Authoritative Registration Source

Server:

XRDCWDDBSUIP06

Database:

MTX_ACOE_Cutover_Reporting

Authentication:

Windows Integrated Authentication

Source access pattern:

READ ONLY

Workbook/runtime user:

QXA4067

Verified active security:

181 facilities

---

## Authoritative Registration XWALK Discovery

11 READ procedures were discovered:

1. UI_Excel_Select_Xwalk_Source_Accommodations
2. UI_Excel_Select_Xwalk_Source_AdmitSource
3. UI_Excel_Select_Xwalk_Source_County
4. UI_Excel_Select_Xwalk_Source_DischargeDisposition
5. UI_Excel_Select_Xwalk_Source_Financial_Approver
6. UI_Excel_Select_Xwalk_Source_FinancialClass
7. UI_Excel_Select_Xwalk_Source_Insurance
8. UI_Excel_Select_Xwalk_Source_Insurance_Auth_Status
9. UI_Excel_Select_Xwalk_Source_Location
10. UI_Excel_Select_Xwalk_Source_Room_and_Bed
11. UI_Excel_Select_Xwalk_Source_Services

The source procedure definitions support *ALL* scope semantics.

---

## Successfully Cloned Real Data

### Accommodations

Local table:

staging.REG_EXPANSE_Xwalk_Accommodations

Source procedure:

dbo.UI_Excel_Select_Xwalk_Source_Accommodations

Scope:

`*ALL*`

Real rows cloned:

3052

### AdmitSource

Local table:

staging.REG_EXPANSE_Xwalk_AdmitSource

Source procedure:

dbo.UI_Excel_Select_Xwalk_Source_AdmitSource

Scope:

`*ALL*`

Real rows cloned:

325

---

## Remaining Registration XWALK Clones

The remaining source reads were interrupted by network connectivity:

- County
- DischargeDisposition
- FinancialApprover
- FinancialClass
- Insurance
- InsAuthStatus
- Locations
- RoomBed
- Services

These can be resumed individually using:

scripts\clone_registration_xwalk_sources.py

---

## Clone Utility

File:

scripts\clone_registration_xwalk_sources.py

Compilation status:

PASS

---

## Power Apps Export Utility

File:

scripts\export_powerapps_accommodations.py

Target output:

generated\powerapps\REG\EXPANSE\Accommodations\Accommodations_RealData.csv

Expected row count:

3052

---

## Power Platform

Environment:

DevelopmentAuto

Solution:

Expanse Cutover Configuration Suite - Registration

Canvas App:

ECCS - Registration POC

---

## Power Apps Connectivity Architecture

Direct Power Apps access to the workstation SQL Server was blocked
because an on-premises data gateway was unavailable.

POC data path:

XRDCWDDBSUIP06
    ->
MTX_ACOE_Cutover_Reporting
    ->
Authoritative Registration READ procedures
    ->
CORPQXA4067D / ECCS_Dev
    ->
Real-data clone
    ->
Power Platform cloud-accessible table
    ->
ECCS - Registration POC

The Power Apps dataset must contain REAL Registration values cloned
from the authoritative SQL source.

---

## Next Step

STEP 60.17F - POWER APPS COLUMN MAPPING

Import:

generated\powerapps\REG\EXPANSE\Accommodations\Accommodations_RealData.csv

into DevelopmentAuto.

Preserve:

- FacilityMnem_Source
- Accommodation_Mnem_Source
- Accommodation_Name_Source
- PA_Code_Source
- Active_Source
- TargetMatchMtx
- DB_RecordCount
- FacilityMnem_Target
- Accommodation_Mnem_Target
- Accommodation_Name_Target
- PA_Code_Target
- Active_Target
- DisplayCurrentValues
- ExcludeFromSharepoint
- Action To Take
- Update_User
- Update_Datetime
- System_Update_User
- System_Update_Datetime
- ECCS source lineage fields

Then connect the imported table to:

ECCS - Registration POC

---

## POC Completion Target

Authoritative Registration SQL
    ->
ECCS compiler/runtime
    ->
local real-data clone
    ->
Power Apps
    ->
search/filter
    ->
select real configuration record
    ->
edit proposed target configuration
    ->
save
    ->
ECCS-controlled local publish/change path

---

## Resume Instruction

Resume ConfigTool-Refresh / Expanse-ConfigTool-Factory from
Step 60.17F - Power Apps Real-Data Import / Column Mapping.

Use the existing repository nomenclature and actual workspace paths.

Continue one operation at a time.

Explicitly identify where each command, code block, SQL operation,
or Power Apps action is performed.
