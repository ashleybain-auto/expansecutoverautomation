# # ECCS Application Compiler Skill

## Project Identity

Suite:
Expanse Cutover Configuration Suite

Suite Code:
ECCS

Factory:
Expanse ConfigTool Factory

Publisher Prefix:
eccs

Development Environment:
DevelopmentAuto

## Pilot Applications

Registration:
ECCS - Registration

Non-Magic Registration:
ECCS - Non-Magic Registration

## Purpose

The Application Compiler converts a validated ConfigTool migration manifest
into a development-ready Power Platform application package using reusable
Expanse application patterns.

The Application Compiler consumes:

- migration-manifest.json
- Expanse UI templates
- SQL definitions
- API definitions
- connector metadata
- integration definitions
- test definitions

It must generate a consistent application without requiring developers to
manually rebuild the entire source workbook.

---

# 1. Core Principle

The Application Compiler is template-driven.

Never generate each application from scratch.

Use:

Migration Manifest
    +
Expanse Shared Template
    +
Integration Definitions
    +
SQL Definitions
    +
Test Definitions
    ->
Power Apps Source
    ->
Power Platform Solution
    ->
.msapp development artifact

The .pa.yaml/source representation is the preferred editable application
source.

The .msapp is a build artifact.

The Power Platform Solution is the deployable enterprise artifact.

---

# 2. Required Inputs

At minimum:

- migration-manifest.json

Optional:

- workbook-ir.json
- API/OpenAPI definitions
- SQL schema
- SQL stored procedures
- existing Power App templates
- Power Automate definitions
- connector definitions
- environment definition
- security-role definition

---

# 3. Supported Application Types

The compiler must support:

- Registration
- PHA
- Non-Med
- EDM
- Non-Magic Registration
- RAD
- LAB
- Diet
- Level of Care
- future ConfigTools
- future conversion applications

The application name and code come from the migration manifest.

Do not hard-code Registration into the core compiler.

---

# 4. Shared Expanse Application Shell

Every generated ConfigTool app should use the shared shell.

Required shared capabilities:

- header
- navigation
- environment selector
- application title
- domain selector
- search
- filter
- status display
- notifications
- user identity
- validation summary
- audit access
- help/instructions access

Suggested component names:

cmpHeader
cmpLeftNav
cmpEnvironmentSelector
cmpDomainSelector
cmpSearchBar
cmpFilterPanel
cmpStatusBadge
cmpValidationSummary
cmpExceptionPanel
cmpAuditTrail
cmpConfirmationDialog
cmpProgress

---

# 5. Application Navigation

Default navigation:

Home
Configuration
Mappings
Integrations
Validation
Publish
Reports
Audit History
Administration

Only display sections applicable to the generated application.

Examples:

Registration:
Configuration
Validation
Publish
Reports
Audit

API-enabled Registration:
Configuration
Mappings
Integrations
Validation
Publish
Reports
Audit

---

# 6. Subpage Generation

Do not generate a single screen per worksheet automatically.

Use the manifest's functional grouping.

Example:

Registration
    Configuration
        Accommodations
        Locations
        Services
        Insurance
        Room / Bed
        Financial Class
        Admit Source

    Validation
    Publish
    Reports
    Audit

Each domain should use reusable page templates.

---

# 7. Page Templates

Supported page types:

dashboard
mappingGrid
editableGrid
detailForm
lookup
settings
validation
exceptionReview
changeSet
publish
report
audit
apiMapping
apiTest
help
administration

The Application Compiler selects page templates based on the manifest.

---

# 8. Mapping Grid

A mapping grid must support, where defined:

- source value
- target value
- match result
- candidate mapping
- target active indicator
- DB record count
- action
- comments/reason
- updated by
- updated date

Support:

- search
- filter
- sort
- row selection
- paging
- edit
- save draft
- validation
- change-set creation

Do not load millions of rows into the Canvas App.

Use paged API/SQL operations.

---

# 9. SQL Integration

SQL Server is the primary high-volume processing layer.

Use:

EF Core
    for metadata-oriented application operations

Dapper
    for controlled query execution where appropriate

SqlBulkCopy
    for high-volume staging

Stored Procedures
    for controlled write/update operations

The Canvas App must not directly execute unrestricted SQL.

---

# 10. SQL Action Model

A mapping action should use:

Power Apps
    ->
Service/API
    ->
SQL procedure
    ->
transaction
    ->
audit
    ->
result

Do not place complex matching or bulk transformation in Power Fx.

---

# 11. Change Set Model

All publishable modifications should use a change-set workflow:

Draft
    ->
Validate
    ->
Review
    ->
Approve
    ->
Publish
    ->
Verify
    ->
Audit

The compiler should generate reusable change-set components.

Suggested components:

cmpChangeSet
cmpApprovalDialog
cmpPublishDialog
cmpPublishProgress

---

# 12. Publish Safety

No generated application may publish directly to a production target by
default.

Environment selection must be explicit.

Use:

DEV
TEST
UAT
PROD

Production publication should require the appropriate role and approval
workflow.

---

# 13. Audit Requirements

Every meaningful configuration change should capture:

- application
- domain
- entity
- entity ID
- user
- action
- before state
- after state
- correlation ID
- timestamp
- environment
- result
- error details if applicable

Audit is mandatory for:

- configuration changes
- mapping changes
- change set creation
- approval
- publish
- API calls that mutate state
- SQL updates
- failed publish attempts where supported

---

# 14. Validation

Every generated application must have a validation layer.

Support:

- required field validation
- data type validation
- uniqueness
- match status
- target active status
- source/target compatibility
- missing target
- duplicate source
- duplicate target
- exclusion
- manual review
- API contract validation
- SQL validation

NO MATCH is a screening condition and must not automatically result in
remediation.

---

# 15. Integration Architecture

Integrations must be abstracted behind a provider model.

Providers:

SQL
HCA_API
External_REST
FHIR
HL7
FILE
OTHER

The Canvas App should communicate through approved service/connector
boundaries.

Do not embed vendor-specific implementation logic into shared UI components.

---

# 16. HCA API Catalog

The HCA API Catalog is treated as the governed API catalog.

The compiler should support metadata representing:

- API
- version
- operation
- method
- path
- request schema
- response schema
- fields
- required fields
- authentication type
- environment
- owner
- approval state

The compiler must not invent undocumented API endpoints.

Only API definitions provided through approved catalog metadata/OpenAPI
definitions may be generated.

---

# 17. API Mapping Page

Provide a reusable page:

apiMapping

Required functions:

- select provider
- select API
- select operation
- select environment
- inspect request fields
- inspect response fields
- map source to API field
- configure transformation
- validate mapping
- save draft
- test

Example:

Source Field
    ->
API Field
    ->
Transformation
    ->
Validation
    ->
Approved Mapping

---

# 18. API Test Console

Generate when an API integration is present.

Required capabilities:

- API
- operation
- environment
- parameters
- request body
- response
- HTTP status
- execution time
- correlation ID
- validation result

Never display or log secrets.

---

# 19. External Vendor Providers

Support external vendor integration through an adapter contract.

Example interface:

GetSchema()
GetData()
Validate()
Transform()
Publish()
Reconcile()

For an unknown vendor, generate a provider stub and test harness rather than
inventing implementation details.

---

# 20. Power Apps Source Generation

Generate a current supported Canvas App source layout where possible.

Preferred source representation:

- App source
- screen source
- component source
- formula source
- data source definitions
- connection references
- solution metadata

Use .pa.yaml/source files when supported by the target Power Platform
tooling.

Power Apps source should be deterministic.

---

# 21. Power Apps .msapp

When requested and supported by the installed Power Platform CLI:

generate:

<ToolCode>_ConfigTool.msapp

The .msapp is a development/build artifact.

Do not make the .msapp the only source artifact.

Keep generated source in the repository.

---
## Power Platform Solutions

Core:
ExpanseCutoverConfigurationSuiteCore

Registration:
ExpanseCutoverConfigurationSuiteRegistration

Non-Magic Registration:
ExpanseCutoverConfigurationSuiteNonMagicRegistration

# 22. Power Platform Solution

Generate a solution containing applicable components:

- Canvas App
- connection references
- environment variables
- custom connectors
- flows
- required supporting components

Suggested solution naming:

Expanse_<ToolCode>_ConfigTool

Examples:

Expanse_REG_ConfigTool
Expanse_NONMAGICREG_ConfigTool
Expanse_PHA_ConfigTool

---

# 23. Environment Variables

Use environment variables for values that change by environment, such as:

- API base URL
- SQL server reference
- database name
- feature flags
- integration endpoints
- configuration identifiers

Do not hard-code environment-specific values into the Canvas App.

---

# 24. Connection References

Use connection references for:

- SQL
- custom connectors
- Power Automate integrations
- other supported Power Platform connections

Do not embed user-specific connection instances as application business
logic.

---

# 25. Custom Connectors

When an approved API has an OpenAPI specification:

1. validate definition
2. create/update custom connector
3. ensure connector belongs to the solution
4. generate connector metadata
5. create connection reference
6. generate API mapping page
7. generate API tests

Do not generate a connector from an undocumented API.

---

# 26. Power Automate

Use flows for operations that are:

- asynchronous
- long-running
- administrative
- approval-driven
- high-volume
- external
- notification-oriented

Suggested flows:

Validate_<ToolCode>
Publish_<ToolCode>
Reconcile_<ToolCode>
Export_<ToolCode>
Notify_<ToolCode>

Do not put large-data transformation into Canvas formulas.

---

# 27. Workbook Parity

Every generated application must maintain a relationship to its source
workbook.

Store:

- source workbook name
- source workbook hash
- compiler version
- manifest version
- generated application version

This enables:

Workbook
    ->
Compiler
    ->
Application

and:

Workbook
    ->
Regression
    ->
Application

comparisons.

---

# 28. Generated Test Suite

Every application must generate:

tests/unit/
tests/integration/
tests/parity/
tests/ui/

At minimum test:

- launch
- navigation
- configuration load
- search
- filtering
- edit
- save
- validation
- refresh
- mapping
- change set
- publish
- audit
- failure behavior

---

# 29. SQL Tests

Generate SQL tests for:

- schema validity
- primary keys
- foreign keys
- duplicate protection
- CRUD
- stored procedures
- transactions
- rollback
- concurrency
- audit creation

---

# 30. API Tests

Generate tests for:

- contract validity
- authentication
- valid request
- invalid request
- missing required field
- invalid data type
- no result
- multiple results
- 4xx
- 5xx
- timeout
- retry
- response parsing

---

# 31. UI Tests

Use the available Power Apps UI automation strategy supported by the project.

At minimum:

- open app
- select navigation
- select domain
- search
- filter
- edit
- save
- validate
- create change set
- publish
- view audit

---

# 32. Performance Tests

Test:

1,000 rows
10,000 rows
100,000 rows
500,000 rows
1,000,000+ rows

Measure:

- initial screen load
- search
- filtering
- refresh
- mapping
- validation
- change-set creation
- publish
- reconciliation
- concurrent users

Power Apps should only retrieve the required/paged result set.

---

# 33. Concurrency

Test simultaneous editing by multiple users.

Required behavior:

- prevent silent overwrites
- detect stale version
- provide conflict message
- preserve audit
- allow safe reload/retry

Use optimistic concurrency where appropriate.

---

# 34. Security

Generated applications must support:

Reader
Editor
Reviewer/Approver
Publisher
Administrator

Never give users unrestricted database owner privileges through the app.

Prefer least-privilege SQL permissions and controlled procedures.

---

# 35. Branding

Every application must use the approved Expanse/HCA design system supplied
to the project.

Use project branding tokens rather than scattering literal colors throughout
the application.

Expected project values include:

HCA Navy: #03173E
HCA Orange: #E05929
Dark Gray: #54585A

Preferred typography:

Arial
Georgia Pro where appropriate

Use orange for standard emphasis and markup.

Use red only for genuinely critical conditions.

Use green for semantically positive/correct states.

---

# 36. Generated Application Naming

Application display name:

Expanse <Tool Name> Configuration

Examples:

Expanse Registration Configuration
Expanse Non-Magic Registration Configuration

Internal names should use stable codes.

Example:

expanse_reg_configtool
expanse_nonmagicreg_configtool

Never generate names containing unstable timestamps unless required for an
artifact filename.

---

# 37. Versioning

Every generated application must have:

ToolVersion
ManifestVersion
CompilerVersion
GeneratedAt

Use semantic versioning where practical.

Example:

1.0.0

When the source workbook changes materially, increment the migration
manifest version.

---

# 38. Compiler Output

For:

REG

generate:

generated/REG/

containing:

migration-manifest.json
REG_ConfigTool.msapp
REG_ConfigTool_Solution.zip
migration-report.html
parity-report.html
sql/
powerapps/
connectors/
flows/
tests/

For:

NONMAGICREG

generate:

generated/NONMAGICREG/

using the same shared templates.

---

# 39. Developer Review Queue

Every generated solution must include a review report:

AUTO
REVIEW
UNSUPPORTED

Example:

AUTO
    Registration Insurance mapping page

REVIEW
    Legacy custom export behavior

UNSUPPORTED
    Excel-only SendKeys workflow

The generator must never hide unresolved items.

---

# 40. One-Click Development Package

The eventual factory workflow is:

Upload Workbook
    ->
Analyze Workbook
    ->
Review Migration Report
    ->
Generate Development Solution
    ->
Run Automated Tests
    ->
Create .msapp
    ->
Create Solution ZIP
    ->
Present Artifacts

The button label should be:

Generate Development Solution

not:

Deploy to Production

---

# 41. Production Deployment

Production deployment must be separate from generation.

Development generation:

SAFE

Development import:

CONTROLLED

UAT:

CONTROLLED

Production:

APPROVED DEPLOYMENT PROCESS

The Application Compiler must not bypass enterprise ALM controls.

---

# 42. Application Compiler Exit Criteria

The compiler is ready for pilot use when:

1. It consumes the Registration migration manifest.
2. It generates the common Expanse shell.
3. It generates domain subpages.
4. It generates mapping functionality.
5. It generates validation.
6. It generates change sets.
7. It generates SQL integration metadata.
8. It generates audit behavior.
9. It generates tests.
10. It creates a development package.
11. It can generate both Registration and Non-Magic Registration from the same
shared framework.
12. It identifies unresolved migration items rather than hiding them.

---

# 43. Non-Goals

The Application Compiler must not:

- execute arbitrary VBA
- publish production SQL automatically
- invent API endpoints
- invent API credentials
- bypass Power Platform security
- silently modify business rules
- convert NO MATCH into an automatic remediation
- replace required SME approval
- treat .msapp as the only source of truth
- hard-code one ConfigTool into the shared compiler
- assume a single environment for deployment
- bypass environment-specific configuration