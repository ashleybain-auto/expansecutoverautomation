ECCS-WIN Step 01.02H - Source-aligned editor patch
Extract into existing ECCS_Windows_Desktop folder (app/ and tests/ must be merged).
Run: .\.venv\Scripts\python.exe install_step0102h.py
Run: .\.venv\Scripts\python.exe -m pytest -q
Run: .\.venv\Scripts\python.exe -m app.main
Preserves existing config_edits and config_audit tables; creates separate eccs_source_config, eccs_target_staging, eccs_target_audit tables.
No source records are invented or migrated. Empty results are expected until source fixtures are authorized/imported.
Screenshot-aligned UI only. Power Fx, actual DB schema mapping, permissions and enterprise synchronization remain pending.
