"""Offline configuration editor; no production synchronization."""
import json
import sqlite3
from datetime import datetime, timezone
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QFormLayout,
    QHeaderView)


def initialize(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS config_edits (
      id INTEGER PRIMARY KEY, facility TEXT NOT NULL, worksheet TEXT NOT NULL,
      source_key TEXT NOT NULL, source_name TEXT NOT NULL DEFAULT '',
      target_key TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Pending',
      UNIQUE(facility, worksheet, source_key)
    );
    CREATE TABLE IF NOT EXISTS config_audit (
      id INTEGER PRIMARY KEY, record_id INTEGER NOT NULL,
      changed_at TEXT NOT NULL, old_json TEXT, new_json TEXT NOT NULL
    );
    ''')

FIELDS = ('facility', 'worksheet', 'source_key', 'source_name', 'target_key', 'status')


def save_record(db, values, record_id=None):
    values = {key: str(values.get(key, '')).strip() for key in FIELDS}
    for key in ('facility', 'worksheet', 'source_key'):
        if not values[key]:
            raise ValueError(f'{key.replace("_", " ").title()} is required')
    if values['status'] not in ('Pending', 'Matched', 'Review', 'Approved'):
        raise ValueError('Status must be Pending, Matched, Review, or Approved')
    with db:
        old = None
        if record_id is not None:
            row = db.execute('SELECT ' + ','.join(FIELDS) + ' FROM config_edits WHERE id=?', (record_id,)).fetchone()
            if row is None:
                raise ValueError('Selected record no longer exists')
            old = dict(zip(FIELDS, row))
            db.execute('UPDATE config_edits SET ' + ','.join(f'{k}=?' for k in FIELDS) + ' WHERE id=?',
                       tuple(values[k] for k in FIELDS) + (record_id,))
        else:
            cur = db.execute('INSERT INTO config_edits (' + ','.join(FIELDS) + ') VALUES (?,?,?,?,?,?)',
                             tuple(values[k] for k in FIELDS))
            record_id = cur.lastrowid
        db.execute('INSERT INTO config_audit(record_id,changed_at,old_json,new_json) VALUES (?,?,?,?)',
                   (record_id, datetime.now(timezone.utc).isoformat(),
                    json.dumps(old) if old else None, json.dumps(values)))
    return record_id


class ConfigEditor(QWidget):
    def __init__(self, store):
        super().__init__()
        self.db = store.db
        initialize(self.db)
        self.record_id = None
        outer = QVBoxLayout(self)
        outer.addWidget(QLabel('Config Tool Update/Edit — Offline'))
        outer.addWidget(QLabel('Local staging only. No enterprise writes or synchronization.'))
        searchbar = QHBoxLayout()
        searchbar.addWidget(QLabel('Search'))
        self.search = QLineEdit()
        self.search.setPlaceholderText('Facility, worksheet, source key or name')
        self.search.textChanged.connect(self.refresh)
        searchbar.addWidget(self.search)
        outer.addLayout(searchbar)
        self.table = QTableWidget(0, len(FIELDS))
        self.table.setHorizontalHeaderLabels([s.replace('_', ' ').title() for s in FIELDS])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.select_record)
        outer.addWidget(self.table)
        form = QFormLayout()
        self.inputs = {}
        for field in FIELDS:
            control = QLineEdit()
            if field == 'status':
                control.setText('Pending')
                control.setPlaceholderText('Pending / Matched / Review / Approved')
            self.inputs[field] = control
            form.addRow(field.replace('_', ' ').title(), control)
        outer.addLayout(form)
        buttons = QHBoxLayout()
        new_button = QPushButton('New / Clear')
        new_button.clicked.connect(self.clear)
        save_button = QPushButton('Save to SQLite')
        save_button.clicked.connect(self.save)
        buttons.addWidget(new_button)
        buttons.addWidget(save_button)
        outer.addLayout(buttons)
        self.refresh()

    def clear(self):
        self.record_id = None
        self.table.clearSelection()
        for key, control in self.inputs.items():
            control.setText('Pending' if key == 'status' else '')

    def refresh(self, *_):
        q = '%' + self.search.text().strip() + '%'
        rows = self.db.execute('SELECT id,' + ','.join(FIELDS) + ''' FROM config_edits
            WHERE facility LIKE ? OR worksheet LIKE ? OR source_key LIKE ? OR source_name LIKE ?
            ORDER BY facility,worksheet,source_key''', (q, q, q, q)).fetchall()
        self.row_ids = [r[0] for r in rows]
        self.table.blockSignals(True)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row[1:]):
                self.table.setItem(i, j, QTableWidgetItem(str(value or '')))
        self.table.blockSignals(False)

    def select_record(self):
        i = self.table.currentRow()
        if i < 0 or i >= len(self.row_ids):
            return
        self.record_id = self.row_ids[i]
        for j, key in enumerate(FIELDS):
            self.inputs[key].setText(self.table.item(i, j).text())

    def save(self):
        try:
            values = {key: control.text() for key, control in self.inputs.items()}
            self.record_id = save_record(self.db, values, self.record_id)
            self.refresh()
            QMessageBox.information(self, 'Saved', 'Saved locally to SQLite with audit history.')
        except (ValueError, sqlite3.IntegrityError) as exc:
            QMessageBox.warning(self, 'Validation', str(exc))
