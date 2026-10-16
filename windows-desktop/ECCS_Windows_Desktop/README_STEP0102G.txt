ECCS-WIN 01.02G: OFFLINE CONFIG EDITOR
Copy app/config_editor.py, tests/test_config_editor.py and apply_step0102g.py
into the existing ECCS_Windows_Desktop folder, preserving paths.
Close the running app first.
Run: .\.venv\Scripts\python.exe apply_step0102g.py
Run: .\.venv\Scripts\python.exe -m pytest -q
Run: .\.venv\Scripts\python.exe -m app.main
This editor uses a separate config_edits staging table, not source business data.
Status options are prototype defaults, not verified Power Fx parity.
No live writes, sync, import, or migrations are performed.
