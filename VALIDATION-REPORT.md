# ECCS Clean Workspace - Validation Report

Date: 2026-10-06

## Decision

**Selected repository foundation:** `Expanse-ConfigTool-Factory-1` main line.

**Selected active Canvas app:** supplied `ECCS - Registration Cutover Config.msapp`.

The clean workspace intentionally keeps the factory architecture and separates active build artifacts from visual/functional reference artifacts.

## Workspace comparison

### 1. ECCS-UI-Remediation

Role: forensic remediation laboratory.

Observed characteristics:

- Large remediation backup tree with many dated/failed iterations.
- Multiple diagnostic text captures for Screen 5 and gallery repair.
- Includes `ECCS - Registration Cutover Config (9) - UI-TEST.msapp` with `BindingErrorCount=69` and an App Checker result set of 350 findings.
- Contains very large search/schema diagnostic artifacts that are not required to build or import the application.

Disposition: **not used as the clean repository foundation**. Its useful design knowledge is represented by the current resume checkpoint, while its historical repair material remains excluded from the clean handoff.

### 2. Expanse-ConfigTool-Factory

Role: richest factory workspace, but currently a remediation branch with a large working tree and accumulated historical Canvas assets.

Observed characteristics:

- `remediation` branch is ahead of main with cleanup commits, but the working tree contains substantial uncommitted changes.
- Contains local `.git`, `.venv`, pytest cache/build artifacts, many historical `.msapp` iterations, and remediation exports.
- The branch cleanup work is valuable evidence of what should be removed, but using the whole working tree as the new baseline would reintroduce ambiguity between source, generated output, and repair history.

Disposition: **used as a comparison/reference source, not as the clean root**.

### 3. Expanse-ConfigTool-Factory-1

Role: cleanest stable factory baseline.

Observed characteristics:

- Main branch at commit `dbe9643`.
- Substantially smaller and cleaner than the first Factory ZIP.
- Retains the established factory layers: manifests, generated artifacts, Power Platform solution source, scripts, skills, source runtime, tests, and workbooks.
- Independent mapping/workbook test suites pass: **25 passed**.
- Python source/scripts compile successfully with `compileall`.
- SQL-runtime tests require `pyodbc`, which is not installed in this analysis container; that remains an environment dependency and was not masked.

Disposition: **selected as the repository foundation**.

## Active MSAPP review

The supplied app was inspected as a real `.msapp` package rather than modified through an unsupported repack process.

Static package results:

- ZIP package integrity: pass.
- `ParserErrorCount`: **0**.
- `BindingErrorCount`: **0**.
- Originating Power Apps version: **1.349**.
- Canvas size: **1366 x 768**, desktop/tablet.
- Source YAML files: **19**.
- Control count: **337**.
- App Checker result records: **306**, primarily accessibility/quality-rule findings rather than parser or binding failures.
- Dataverse references include the DevelopmentAuto-backed data sources used by the existing Registration pilot.

The clean active `.msapp` is **byte-identical** to the supplied file. Its SHA-256 is:

`d54c0815741188f3a681f6cea636f9b9a113d703fce2500053e96ca357fcbf26`

It is also byte-identical in its `Src/` YAML content to Factory's `ECCS - Registration Cutover Config (11).msapp`.

## Functional resume boundary

The active app retains the known-good compiled shell and the current Screen 5 component contract.

`cmpDrpdwnFiltersFacilityWksG` exposes `SelectedRecord` as a Record output. Its validated gallery logic currently has the `Accommodations` branch. The other Registration worksheet branches are not yet implemented in the active gallery logic. This is the intended **next build/remediation boundary**, not something to “fix” by altering the clean baseline before import.

Resume checkpoint: **Step 103.5CH - Screen 5 Gallery Functional Remediation**.

## Reference artifacts preserved

The clean workspace preserves the reference/demo concept explicitly under `canvas/reference/`:

- 12 Canvas demo shell packages/files actually present in the submitted workspaces.
- 5 representative Registration benchmark app iterations.
- 5 representative Registration source snapshots.
- corrected Power Pages AppHub reference package.

Historical repair loops and giant forensic dumps are not carried into the new build workspace.

## Static import-readiness conclusion

The active `.msapp` is structurally intact, has zero parser errors and zero binding errors in its embedded package metadata, and survives ZIP integrity validation. The surrounding clean workspace also passes its applicable repository-level tests.

**Live Power Apps import was not executed in this container** because the Power Platform CLI (`pac`) is not installed and this runtime does not have an authenticated Power Apps maker session. Therefore this report does not claim a live import that was not performed.

The first operational gate after opening this clean workspace is to import the active `.msapp` into the already-established DevelopmentAuto environment. Only after that import/open test succeeds should production replication documentation be created.
