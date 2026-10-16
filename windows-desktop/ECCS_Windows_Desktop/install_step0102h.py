from pathlib import Path
from datetime import datetime
import shutil
root=Path(__file__).resolve().parent
main=root/'app'/'main.py'
if not main.is_file(): raise SystemExit('main.py not found')
s=main.read_text(encoding='utf-8')
if 'SourceAlignedEditor(self.store)' in s:
    print('STATUS: ALREADY INSTALLED'); raise SystemExit(0)
old='from .config_editor import ConfigEditor'
anchor='page = ConfigEditor(self.store)'
if old not in s or anchor not in s: raise SystemExit('Expected editor anchors not found; no changes made')
if not (root/'app'/'source_aligned_editor.py').exists(): raise SystemExit('New editor module missing')
backup=main.with_name('main.py.backup_0102H_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
shutil.copy2(main,backup)
s=s.replace(old,'from .source_aligned_editor import SourceAlignedEditor').replace(anchor,'page = SourceAlignedEditor(self.store)')
main.write_text(s,encoding='utf-8')
print('STATUS: PATCH APPLIED; BACKUP:',backup)
