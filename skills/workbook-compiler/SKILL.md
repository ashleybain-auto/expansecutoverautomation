# ECCS Workbook Compiler Skill

## Project

Suite:
Expanse Cutover Configuration Suite

Suite Code:
ECCS

Factory:
Expanse ConfigTool Factory

Publisher Prefix:
eccs

Repository:
Expanse-ConfigTool-Factory

## Purpose

The Workbook Compiler converts an existing Excel VBA ConfigTool workbook
(.xlsb or .xlsm) into a deterministic intermediate representation that can
be consumed by the Application Compiler.

The compiler is NOT an Excel-to-Power-Apps visual copier.

It must preserve and describe the workbook's existing functional behavior
before application generation occurs.

The primary pilot inputs are:

- Mapping_Expanse_REG_Domain.xlsb
- Mapping_NonMagic_Expanse_REG_Domain.xlsb

Later reference inputs include:

- Mapping_Expanse_PHA_Domain.xlsb
- Mapping_Expanse_NONMED_Domain.xlsb
- ACOE_Expanse_ConfigTool_EdmAutomation.xlsb
- additional ConfigTool and clinical-area mapping workbooks

---

# 1. Core Principle

Never translate VBA line-for-line into Power Fx.

Translate workbook behavior into a normalized functional model.

Use this pipeline:

XLSB/XLSM
    ->
Workbook Inventory
    ->
Worksheet Model
    ->
VBA Model
    ->
SQL/Integration Model
    ->
Functional Classification
    ->
Workbook Intermediate Representation
    ->
Migration Manifest
    ->
Application Compiler

The workbook is a functional source specification and regression reference.

The generated Power App is NOT the authoritative source of the original
workbook behavior until migration parity has been established.

---

# 2. Supported Workbook Types

Primary:

- .xlsb
- .xlsm

Secondary if technically supported:

- .xlsx
- .xls

Preserve the original filename, extension, file hash, file size, modified
timestamp, and ingestion timestamp.

The original source file must never be modified by the compiler.

If the workbook file fails to parse or is corrupted, halt analysis, log a PARSE_ERROR entry in warnings, and do not generate partial IR or manifest files.

---

# 3. Required Workbook Analysis

Every workbook submission must produce a complete inventory of:

## Workbook Metadata

- filename
- extension
- SHA-256 hash
- file size
- workbook properties when available
- workbook calculation mode when available
- hidden/protected state where discoverable

## Worksheets

For every worksheet capture:

- sheet name
- visible/hidden/very hidden status
- used range
- row count
- column count
- header row(s)
- data start row
- data end row
- merged cells
- formulas
- hyperlinks
- data validation
- named ranges associated with sheet
- tables associated with sheet
- likely purpose

Classify sheets as one of:

- instruction
- settings
- mapping
- lookup
- source data
- target data
- staging
- report
- export
- error
- reference
- unknown

Never silently discard a worksheet.

---

# 4. Column Analysis

For every column in worksheets classified as mapping, lookup, source data, target data, staging, or settings, capture the following attributes.

- ordinal position
- column name
- display name
- inferred data type
- observed data types
- null/blank frequency
- distinct count for columns with fewer than 100,000 rows; otherwise mark as SAMPLED_ESTIMATE
- example values
- formula presence
- formula pattern
- editable/read-only estimate
- likely key field
- likely source field
- likely target field
- likely system field
- mapping/status semantics

Recognize common ConfigTool fields such as:

- Source
- Target
- Source_Value
- Target_Value
- Match
- TargetMatchMtx
- DB_RecordCount
- Active
- Action_To_Take
- Update_User
- Update_Datetime
- Settings
- Server
- Database
- Environment

Do not assume exact column names. Use explicit mapping metadata.

---

# 5. VBA Analysis

Extract all accessible VBA source.

Analyze:

- modules
- module types
- procedures
- functions
- parameters
- return values
- calls between procedures
- worksheet references
- range references
- table references
- named range references
- SQL strings
- ADO references
- DAO references
- ADODB references
- connection creation
- stored procedure calls
- HTTP/API references
- file writes
- SharePoint references
- clipboard operations
- Excel UI automation
- form/control events
- button actions
- error handling
- retry logic
- transactions where detectable

Use `olevba` where appropriate for source extraction.

If olevba extraction fails or is unavailable, record an UNSUPPORTED entry for VBA analysis and continue with worksheet-level analysis rather than aborting the entire compilation.

Do not execute VBA during analysis.

The compiler must treat workbook VBA as untrusted executable content.

---

# 6. VBA Security Rule

Never execute macros automatically.

The compiler must:

1. open/read workbook content without enabling macros
2. extract VBA source statically
3. classify suspicious or external execution behavior
4. record any unsupported behavior
5. require explicit developer review for execution-dependent behavior

If the workbook or VBA project is password-protected and cannot be read statically, mark the workbook as UNSUPPORTED_ENCRYPTED and record this in warnings without attempting to bypass protection.

Never run:

- Shell
- WScript
- PowerShell
- Cmd
- external EXE
- embedded executable
- arbitrary HTTP POST
- database write
- file deletion

during workbook analysis.

---

# 7. Functional Classification

Every meaningful VBA procedure, formula region, button/action, and
worksheet behavior must be classified as one or more:

- READ
- REFRESH
- IMPORT
- COPY
- STAGE
- TRANSFORM
- NORMALIZE
- MATCH
- CROSSWALK
- VALIDATE
- EDIT
- SAVE
- APPROVE
- PUBLISH
- EXPORT
- REPORT
- AUDIT
- NAVIGATE
- CONFIGURE
- OTHER

Examples:

RefreshData_Insurance
    -> REFRESH

PushUpdates_Insurance
    -> PUBLISH

CopyData_Insurance
    -> COPY/STAGE

Generate_Export_File_For_Sharepoint
    -> EXPORT

settingServer
    -> CONFIGURE

settingDB
    -> CONFIGURE

---

# 8. ConfigTool Convention Detection

The analyzer must explicitly look for naming conventions such as:

RefreshData_*
PushUpdates_*
CopyData_*
ProcessUpdate*
Setting*
listDB
listServers
Generate_Export*
Link_To_Home
Home
Settings

Treat detected conventions as high-value evidence of intended application
behavior.

Do not require a workbook to use these names.

Support semantic detection when naming conventions differ.

---

# 9. Settings Detection

Identify settings that appear to control:

- server
- database
- environment
- source connection
- target connection
- SharePoint
- folder/path
- API endpoint
- credentials reference
- configuration mode

Never place discovered usernames, passwords, tokens, or secrets into the
generated migration manifest.

Replace secrets with secure references such as:

- CONNECTION_REFERENCE
- SECRET_REFERENCE
- ENVIRONMENT_VARIABLE
- KEY_VAULT_REFERENCE

---

# 10. SQL Detection

Detect:

- SQL Server connection strings
- database names
- server names
- SQL SELECT statements
- INSERT statements
- UPDATE statements
- DELETE statements
- stored procedure calls
- temp tables
- joins
- WHERE filters
- source/target tables
- schema references
- transaction blocks
- record counts
- active/inactive logic

Classify SQL operations:

READ
WRITE
DDL
PROCEDURE
UNKNOWN

Never execute write SQL during workbook compilation.

---

# 11. API Detection

Detect references to:

- HTTP
- HTTPS
- REST
- JSON
- XML
- FHIR
- HL7
- OpenAPI
- API endpoints
- bearer tokens
- authorization headers
- web requests
- custom connector patterns

Do not assume an API is an approved enterprise API.

Classify each integration as:

- known approved API
- candidate API
- unknown API
- external vendor API
- unsupported API

---

# 12. Mapping Model Detection

A mapping worksheet should be modeled with concepts such as:

- source value
- target value
- candidate target
- match status
- DB record count
- active flag
- exclusion
- action
- updated by
- updated date
- comments/reason
- mapping version

Recognize that NO MATCH is a screening condition.

Never translate NO MATCH directly into an automatic remediation instruction.

---

# 13. Intermediate Representation

Generate a deterministic file:

workbook-ir.json

The representation must include:

{
  "workbook": {},
  "worksheets": [],
  "columns": [],
  "vbaModules": [],
  "procedures": [],
  "sqlReferences": [],
  "apiReferences": [],
  "actions": [],
  "mappings": [],
  "settings": [],
  "warnings": [],
  "unsupported": []
}

The IR is an analysis artifact, not a Power Apps artifact.

---

# 14. Migration Manifest

Generate:

migration-manifest.json

The manifest is the contract consumed by the Application Compiler.

It should include at minimum:

- application name
- application code
- source workbook
- workbook hash
- domains
- pages
- subpages
- fields
- actions
- data sources
- SQL dependencies
- API dependencies
- validations
- audit requirements
- security requirements
- generated components
- unresolved items

Example:

{
  "application": {
    "code": "REG",
    "name": "Registration"
  },
  "source": {
    "workbook": "Mapping_Expanse_REG_Domain.xlsb"
  },
  "domains": [],
  "actions": [],
  "integrations": [],
  "validation": {},
  "audit": {}
}

---

# 15. Page Grouping Rules

Do not automatically create one Power Apps screen for every worksheet.

Group related worksheets into business functional areas.

Example:

Registration
    Configuration
        Accommodations
        Locations
        Services
        Insurance
        Room / Bed
        Financial Class

    Validation
    Publish
    Reports
    Audit

For PHA:

PHA
    Medication Configuration
    MIS Configuration
    Administration
    Restrictions / Exclusions
    Validation
    Publish
    Audit

Grouping must be represented in the migration manifest.

---

# 16. Automatic vs Manual Migration

Each detected behavior must receive a migration status:

- AUTO
- REVIEW
- UNSUPPORTED

Examples:

Simple SQL SELECT
    -> AUTO

Standard mapping grid
    -> AUTO

RefreshData_* routine using known SQL pattern
    -> AUTO

Dynamic VBA code generation
    -> REVIEW

Excel-specific SendKeys
    -> REVIEW or UNSUPPORTED

Shell command
    -> UNSUPPORTED

Unknown external executable
    -> UNSUPPORTED

---

# 17. Migration Report

Generate:

migration-report.json
migration-report.html

Report:

- workbook inventory
- worksheet inventory
- VBA inventory
- SQL inventory
- API inventory
- functional classifications
- generated page recommendations
- automatic conversions
- developer review items
- unsupported items
- security concerns
- assumptions
- warnings

No generated application is considered complete if the report contains
unresolved critical items.

---

# 18. Regression Baseline

The original workbook is the regression reference.

Capture baseline behaviors where possible:

- row counts
- mapping results
- refresh results
- target matches
- NO MATCH results
- DB record counts
- active status
- action classifications
- export counts
- timing
- expected outputs

Save under:

tests/parity/baseline/

Never overwrite the baseline.

---

# 19. Determinism

Running the compiler against the same workbook should produce the same
functional model except for explicitly recorded timestamps or generated
IDs.

The compiler must not invent:

- API endpoints
- SQL credentials
- target databases
- business rules
- mapping decisions
- security roles

When a fact is unavailable, mark it:

"REQUIRES_REVIEW"

rather than inventing a value.

---

# 20. Compiler Output

For each workbook create:

generated/<ToolCode>/

with:

- workbook-ir.json
- migration-manifest.json
- migration-report.json
- migration-report.html
- extracted-vba/
- sql-candidates/
- api-candidates/
- tests/
- warnings/

The Workbook Compiler must not create a production Power Apps application
directly.

Its output is consumed by the Application Compiler.

---

# 21. Required Pilot Tests

## Registration Pilot

MEDITECH Expanse:

Tool Code:
REG

Variant:
EXPANSE

Display Name:
ECCS - Registration

Source Workbook:
Mapping_Expanse_REG_Domain.xlsb

Registration MEDITECH:

- worksheet discovery
- column discovery
- settings discovery
- VBA extraction
- refresh procedure discovery
- push procedure discovery
- SQL reference discovery
- mapping field discovery
- action field discovery
- audit field discovery

Non-Magic Expanse:

Tool Code:
REG

Variant:
NONMAGIC

Display Name:
ECCS - Non-Magic Registration

Source Workbook:
Mapping_NonMagic_Expanse_REG_Domain.xlsb

Registration Non-Magic:

Repeat all tests.

The second workbook is a required factory-repeatability test.

---

# 22. Exit Criteria

Workbook Compiler is considered complete for pilot use when:

1. Both Registration workbooks are analyzed without modifying them.
2. All worksheets are accounted for.
3. All accessible VBA procedures are cataloged.
4. Refresh and push actions are identified.
5. Settings/configuration references are identified.
6. SQL dependencies are identified.
7. Mapping fields are identified.
8. Functional behavior is represented in the IR.
9. A migration manifest is generated.
10. Critical unresolved items are explicitly reported.
11. Baseline regression artifacts are stored.
12. The same compiler code can process both Registration workbooks.

---

# 23. Non-Goals

The Workbook Compiler must not:

- execute VBA
- modify the input workbook
- publish SQL changes
- call production APIs
- deploy Power Apps
- invent mappings
- invent credentials
- bypass security review
- automatically approve business changes

Its purpose is analysis, normalization, classification, and generation of
a deterministic application specification.
