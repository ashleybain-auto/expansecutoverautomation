# ECCS-WIN Step 01.02E — offline prototype

This is a **navigation and SQLite filtering prototype**, not a Power Apps conversion with verified business parity. Seven screen names from the primary source have been mapped to pages; only worksheet results have an initial offline table/filter interface. The local database starts empty by design. No live SQL Server/Dataverse/SharePoint integration is enabled, and no live records are included.

## Run on Windows in VS Code PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m app.main
```

To package, run `powershell -ExecutionPolicy Bypass -File .\build.ps1` on Windows after reviewing dependencies. Windows packaging is **not validated** in this environment.

## Next checkpoint

Step 01.02F: Extract and trace Power Fx for screen and component behavior, particularly `cmpDrpdwnFiltersFacilityWksG` and `scrWorksheetResults`; validate real REG Facility records against an authorized sanitized dataset before declaring parity.
