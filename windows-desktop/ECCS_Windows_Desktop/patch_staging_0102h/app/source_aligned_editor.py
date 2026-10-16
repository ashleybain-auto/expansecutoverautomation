"""Source-aligned offline editor. Screenshot parity only; Power Fx rules pending."""
import json
import sqlite3
from datetime import datetime, timezone
from PySide6.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QGridLayout,QLabel,QComboBox,
    QLineEdit,QListWidget,QPushButton,QMessageBox,QFrame,QSplitter)
from PySide6.QtCore import Qt

SOURCE_FIELDS = ('source_facility','source_mnemonic','source_name','source_pa_code','source_active')
TARGET_FIELDS = ('target_facility','target_mnemonic','target_name','target_pa_code','target_active')

def initialize(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS eccs_source_config (
      id INTEGER PRIMARY KEY, wave_subwave TEXT NOT NULL DEFAULT '',
      facility TEXT NOT NULL, worksheet TEXT NOT NULL,
      source_facility TEXT NOT NULL DEFAULT '', source_mnemonic TEXT NOT NULL DEFAULT '',
      source_name TEXT NOT NULL DEFAULT '', source_pa_code TEXT NOT NULL DEFAULT '',
      source_active TEXT NOT NULL DEFAULT '', target_match TEXT NOT NULL DEFAULT '',
      UNIQUE(facility,worksheet,source_mnemonic,source_pa_code)
    );
    CREATE TABLE IF NOT EXISTS eccs_target_staging (
      source_id INTEGER PRIMARY KEY REFERENCES eccs_source_config(id),
      target_facility TEXT NOT NULL DEFAULT '', target_mnemonic TEXT NOT NULL DEFAULT '',
      target_name TEXT NOT NULL DEFAULT '', target_pa_code TEXT NOT NULL DEFAULT '',
      target_active TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS eccs_target_audit (
      id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL,
      changed_at TEXT NOT NULL, old_json TEXT, new_json TEXT NOT NULL
    );
    ''')

def save_target(db, source_id, values):
    values = {key: str(values.get(key,'')).strip() for key in TARGET_FIELDS}
    if not values['target_facility'] or not values['target_mnemonic']:
        raise ValueError('Target Facility and Target Mnemonic are required for offline staging')
    if values['target_active'].upper() not in ('Y','N'):
        raise ValueError('Target Active must be Y or N')
    with db:
        if not db.execute('SELECT 1 FROM eccs_source_config WHERE id=?',(source_id,)).fetchone():
            raise ValueError('Source record does not exist')
        old = db.execute('SELECT '+','.join(TARGET_FIELDS)+' FROM eccs_target_staging WHERE source_id=?',(source_id,)).fetchone()
        timestamp = datetime.now(timezone.utc).isoformat()
        db.execute('INSERT INTO eccs_target_staging(source_id,'+','.join(TARGET_FIELDS)+',updated_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(source_id) DO UPDATE SET '+','.join(f'{k}=excluded.{k}' for k in TARGET_FIELDS)+',updated_at=excluded.updated_at',
            (source_id,*(values[k] for k in TARGET_FIELDS),timestamp))
        db.execute('INSERT INTO eccs_target_audit(source_id,changed_at,old_json,new_json) VALUES (?,?,?,?)',
            (source_id,timestamp,json.dumps(dict(zip(TARGET_FIELDS,old))) if old else None,json.dumps(values)))

class SourceAlignedEditor(QWidget):
    def __init__(self, store):
        super().__init__()
        self.db = store.db
        initialize(self.db)
        self.source_id = None
        root = QVBoxLayout(self)
        header = QLabel('Registration | Config Tool Update/Edit — Offline')
        header.setStyleSheet('background:#03173E;color:white;padding:12px;font-weight:bold;')
        root.addWidget(header)
        note = QLabel('Source records: read-only | Target updates: local SQLite staging only | Enterprise sync: disabled')
        root.addWidget(note)
        split = QSplitter(Qt.Orientation.Horizontal)
        left = QFrame(); left.setStyleSheet('QFrame{background:#f2f2f2;}')
        ll = QVBoxLayout(left)
        filters = QGridLayout()
        self.wave = QComboBox(); self.facility = QComboBox(); self.worksheet = QComboBox()
        for i,(name,control) in enumerate((('WAVE - SUBWAVE',self.wave),('FACILITY MNEMONIC/NAME',self.facility),('REG WORKSHEET NAME',self.worksheet))):
            filters.addWidget(QLabel(name),i,0); filters.addWidget(control,i,1)
            control.currentIndexChanged.connect(self.refresh)
        ll.addLayout(filters)
        self.search = QLineEdit(); self.search.setPlaceholderText('Search (* = wildcard)')
        self.search.textChanged.connect(self.refresh)
        ll.addWidget(self.search)
        self.count = QLabel('RESULTS: 0'); ll.addWidget(self.count)
        self.results = QListWidget(); self.results.currentRowChanged.connect(self.select_record)
        ll.addWidget(self.results)
        split.addWidget(left)
        right = QWidget(); rl = QVBoxLayout(right)
        source_title = QLabel('CURRENT CONFIGURATION'); source_title.setStyleSheet('font-weight:bold;color:#03173E;')
        rl.addWidget(source_title)
        self.source_labels = {}
        for field in SOURCE_FIELDS:
            row = QHBoxLayout(); row.addWidget(QLabel(field.replace('_',' ').title()))
            val = QLabel('—'); val.setWordWrap(True); row.addWidget(val,1)
            self.source_labels[field] = val; rl.addLayout(row)
        proposed = QLabel('PROPOSED CONFIGURATION'); proposed.setStyleSheet('font-weight:bold;color:#E05929;')
        rl.addWidget(proposed)
        self.inputs = {}
        for field in TARGET_FIELDS:
            row = QHBoxLayout(); row.addWidget(QLabel('PA Code' if field=='target_pa_code' else field.replace('_',' ').title()))
            control = QLineEdit(); control.setEnabled(False)
            self.inputs[field] = control; row.addWidget(control,1); rl.addLayout(row)
        self.match = QLabel('Target Match: —'); rl.addWidget(self.match)
        button = QPushButton('Update Target'); button.clicked.connect(self.update_target)
        button.setStyleSheet('background:#03173E;color:white;padding:9px;font-weight:bold;')
        self.update_button = button; button.setEnabled(False); rl.addWidget(button)
        rl.addWidget(QLabel('Config-Tool Connection: Offline staging | Last Refreshed: Local'))
        rl.addStretch()
        split.addWidget(right); split.setSizes([560,600]); root.addWidget(split,1)
        self.reload_facets()

    def reload_facets(self):
        for column,control in (('wave_subwave',self.wave),('facility',self.facility),('worksheet',self.worksheet)):
            control.blockSignals(True); control.clear(); control.addItem('All')
            for row in self.db.execute(f'SELECT DISTINCT {column} FROM eccs_source_config ORDER BY {column}'):
                control.addItem(row[0])
            control.blockSignals(False)
        self.refresh()

    def refresh(self,*_):
        clauses=[]; params=[]
        for column,control in (('wave_subwave',self.wave),('facility',self.facility),('worksheet',self.worksheet)):
            if control.currentIndex()>0:
                clauses.append(f'{column}=?'); params.append(control.currentText())
        q=self.search.text().strip().replace('*','%')
        if q:
            clauses.append('(source_mnemonic LIKE ? OR source_name LIKE ? OR source_pa_code LIKE ?)')
            params.extend([f'%{q}%']*3)
        sql='SELECT id,source_mnemonic,source_name,facility FROM eccs_source_config'
        if clauses: sql+=' WHERE '+' AND '.join(clauses)
        sql+=' ORDER BY source_mnemonic,source_name'
        rows=self.db.execute(sql,params).fetchall()
        self.ids=[r[0] for r in rows]
        self.results.blockSignals(True); self.results.clear()
        for r in rows: self.results.addItem(f'{r[1]}  |  {r[2]}  |  {r[3]}')
        self.results.blockSignals(False)
        self.count.setText(f'RESULTS: {len(rows)}')
        self.select_record(-1)

    def select_record(self,index):
        self.source_id = self.ids[index] if 0<=index<len(self.ids) else None
        if self.source_id is None:
            for label in self.source_labels.values(): label.setText('—')
            for control in self.inputs.values(): control.clear(); control.setEnabled(False)
            self.match.setText('Target Match: —'); self.update_button.setEnabled(False); return
        row=self.db.execute('SELECT '+','.join(SOURCE_FIELDS)+',target_match FROM eccs_source_config WHERE id=?',(self.source_id,)).fetchone()
        for field,value in zip(SOURCE_FIELDS,row[:5]): self.source_labels[field].setText(str(value or '—'))
        self.match.setText('Target Match: '+str(row[5] or '—'))
        target=self.db.execute('SELECT '+','.join(TARGET_FIELDS)+' FROM eccs_target_staging WHERE source_id=?',(self.source_id,)).fetchone()
        for i,field in enumerate(TARGET_FIELDS):
            self.inputs[field].setEnabled(True)
            self.inputs[field].setText(str(target[i] or '') if target else '')
        self.update_button.setEnabled(True)

    def update_target(self):
        if self.source_id is None: return
        try:
            save_target(self.db,self.source_id,{k:v.text() for k,v in self.inputs.items()})
            QMessageBox.information(self,'Saved','Target staged locally with audit history. No enterprise write occurred.')
        except (ValueError,sqlite3.Error) as exc:
            QMessageBox.warning(self,'Validation',str(exc))
