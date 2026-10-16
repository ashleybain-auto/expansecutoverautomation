import sqlite3
import pytest
from app.config_editor import initialize, save_record


def test_create_update_audit():
    db = sqlite3.connect(':memory:')
    initialize(db)
    record = {'facility':'REG Facility','worksheet':'Registration','source_key':'A1','source_name':'Example','target_key':'','status':'Pending'}
    rid = save_record(db, record)
    record['target_key'] = 'B1'
    save_record(db, record, rid)
    assert db.execute('SELECT target_key FROM config_edits').fetchone()[0] == 'B1'
    assert db.execute('SELECT count(*) FROM config_audit').fetchone()[0] == 2


def test_required_fields():
    db = sqlite3.connect(':memory:')
    initialize(db)
    with pytest.raises(ValueError):
        save_record(db, {'facility':'','worksheet':'X','source_key':'Y','status':'Pending'})
