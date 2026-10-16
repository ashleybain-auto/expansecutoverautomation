"""Offline-only staging store; no production connector or implicit synchronization."""
import sqlite3
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS worksheet_rows (
  id INTEGER PRIMARY KEY,
  facility TEXT NOT NULL,
  worksheet TEXT NOT NULL,
  source_key TEXT NOT NULL,
  source_name TEXT NOT NULL DEFAULT '',
  target_key TEXT,
  status TEXT NOT NULL DEFAULT 'Pending',
  UNIQUE(facility, worksheet, source_key)
);
CREATE INDEX IF NOT EXISTS idx_rows_filter ON worksheet_rows(facility, worksheet);
'''

class OfflineStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path))
        self.db.executescript(SCHEMA)

    def filter_rows(self, facility=None, worksheet=None):
        clauses, args = [], []
        if facility:
            clauses.append('facility = ?')
            args.append(facility)
        if worksheet:
            clauses.append('worksheet = ?')
            args.append(worksheet)
        sql = 'SELECT facility, worksheet, source_key, source_name, target_key, status FROM worksheet_rows'
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        return self.db.execute(sql + ' ORDER BY source_key', args).fetchall()

    def facets(self, field):
        if field not in ('facility', 'worksheet'):
            raise ValueError('Invalid facet')
        return [row[0] for row in self.db.execute(f'SELECT DISTINCT {field} FROM worksheet_rows ORDER BY {field}')]
