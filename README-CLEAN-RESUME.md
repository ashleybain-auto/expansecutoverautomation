# ECCS / CutoverConfigSuite - Clean Resume Workspace

Date: 2026-10-06

This workspace is a clean build/resume baseline assembled from the mature `Expanse-ConfigTool-Factory-1` main-line workspace plus the newly supplied Power Apps `.msapp`.

## Active application artifact

`canvas/active/ECCS - Registration Cutover Config - CLEAN-RESUME.msapp`

This file is the active resume baseline. It is a direct copy of the supplied `.msapp`; its internal package was not edited or repacked so the validated Power Apps package structure is preserved.

Static package validation:

- ParserErrorCount = 0
- BindingErrorCount = 0
- 8 screens
- 19 source YAML files
- 337 controls
- OriginatingVersion = 1.349
- DevelopmentAuto Dataverse data sources are retained in the app package

## Resume functional boundary

The active app is the known-good compiled baseline. The next build task is **not** to rebuild the shell.

Current known functional boundary:

`cmpDrpdwnFiltersFacilityWksG` exposes `SelectedRecord` as a Record output and currently has a validated `Accommodations` data branch. The multi-worksheet gallery is not yet complete for the other Registration worksheet selections; that is the active remediation/build area.

Resume checkpoint: **Step 103.5CH - Screen 5 Gallery Functional Remediation**.

## Reference materials

Everything under `canvas/reference/` is intentionally retained as a design-definition-of-done/reference library, not as the active app to modify.

- `demo-shells/` contains the reference Canvas shells actually present in the three submitted workspaces (12 files, including the CNET shell).
- `registration-benchmarks/` contains selected Registration app iterations that represent useful benchmark screens and proven design states.
- `registration-source/` contains the corresponding source snapshots for representative Registration variants.
- `ECCS-PowerPages-AppHub-Package-Corrected.zip` is retained as the Power Pages reference package.

Reference artifacts should remain available for comparison while the active app evolves toward a production-ready DevOps implementation. The submitted workspaces do not contain separate PHA/MED or Non-Med/LAB shell packages, so those two reference artifacts were not fabricated or guessed into this clean baseline.

## Build architecture retained

The factory layers remain intact:

Source configuration -> workbook analysis -> manifests -> generated artifacts -> Power Platform resources -> tests

Production-specific connection details, environment bindings, and deployment instructions are intentionally **not** turned into a production build document at this stage.

## Clean-up policy used

Removed from this resume workspace:

- Git metadata and local virtual environments/caches
- historical repair/batchfix MSAPP loops
- temporary remediation workspace contents
- giant diagnostic/search artifacts
- generated real-data row dumps that are not required to compile the app
- compiled `bin`/`obj` build output

The design/reference shells were preserved deliberately because they define the intended overall ECCS experience.
