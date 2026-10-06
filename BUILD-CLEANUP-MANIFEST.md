# Clean-up Manifest

## Retained as build source

- config/
- database/
- docs/checkpoints/
- generated/poc/
- generated/powerapps/UPLOAD/
- manifests/
- power-platform/ (source solution definitions only)
- scripts/
- skills/
- src/
- tests/
- workbooks/
- Expanse Cutover Configuration Suite/ (Power Pages source)

## Retained as design/reference source

- canvas/active/ECCS - Registration Cutover Config - CLEAN-RESUME.msapp
- canvas/reference/demo-shells/
- canvas/reference/registration-benchmarks/
- canvas/reference/registration-source/
- canvas/reference/ECCS-PowerPages-AppHub-Package-Corrected.zip

## Intentionally removed from the clean handoff

- `.git/`, `.venv/`, pytest caches, Python caches
- `canvas/msapp files/` full historical dump
- REPAIR/BATCHFIX/READINESS iteration loops
- `canvas/srcMatchDashboard.pa.yaml.bak`
- `ECCS - Registration Cutover Config_REPAIR11-7.zip` diagnostic pack
- `Screen5-EquivalentGallery-Search.txt` and related UI-remediation forensic dumps
- duplicate/temporary `.msapp` packages that do not define the active resume baseline
- `Accommodations_RealData.csv` business-data export
- Power Platform solution `bin/` and `obj/` build products
