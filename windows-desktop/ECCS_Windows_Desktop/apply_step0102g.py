from pathlib import Path
from datetime import datetime
import shutil
root = Path(__file__).resolve().parent
app = root / 'app' / 'main.py'
if not app.exists():
    raise SystemExit('ERROR: Run from the ECCS_Windows_Desktop folder.')
s = app.read_text(encoding='utf-8')
if 'from .config_editor import ConfigEditor' in s:
    raise SystemExit('Already applied. No changes made.')
if "if key == 'scrWorksheetResults':" not in s:
    raise SystemExit('Expected navigation anchor not found. No changes made.')
if "('scrAccommodations', 'Config Tool Update/Edit')" not in s:
    raise SystemExit('Rename prerequisite not found. No changes made.')
s = s.replace('from .storage import OfflineStore', 'from .storage import OfflineStore\nfrom .config_editor import ConfigEditor')
s = s.replace("            if key == 'scrWorksheetResults':", "            if key == 'scrAccommodations':\n                page = ConfigEditor(self.store)\n            elif key == 'scrWorksheetResults':")
backup = app.with_name('main.py.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
shutil.copy2(app, backup)
app.write_text(s, encoding='utf-8')
print('STATUS: PATCH APPLIED')
print('BACKUP:', backup)
