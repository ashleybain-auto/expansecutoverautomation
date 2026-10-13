REG-DASH Step 01.16 - VS Code bulk patch (preview)

This patch operates on a copy of the uploaded .msapp and writes a new .msapp plus diagnostic .txt.
It makes three changes: initializes colReadinessFacilities in App.OnStart; fixes a standalone '=' line in screen OnVisible; adds four native KPI labels to cmpECCSCutoverReadinessDsh.

It does not create Dataverse rows, implement charts, or verify Power Apps formula compatibility. The new KPI labels are placeholders until snapshot grain and source data are validated. Readiness % currently displays the first snapshot's percentage and must not be treated as an aggregate across multiple rows.

In VS Code PowerShell, after saving bulk_patch.py locally:
py -3 .\bulk_patch.py --msapp "C:\path\to\ECCS - Registration Cutover Config (2).msapp" --output-dir "C:\path\to\REG-DASH\bulk-output"

Then test the generated .msapp in a non-production copy of Power Apps Studio. Do not publish or overwrite the active app. PAC CLI pack validation is not available in this runtime.
