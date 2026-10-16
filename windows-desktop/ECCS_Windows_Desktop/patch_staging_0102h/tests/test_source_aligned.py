import sqlite3
import pytest
from app.source_aligned_editor import initialize,save_target

def test_staging_and_audit():
    db=sqlite3.connect(':memory:'); initialize(db)
    db.execute("INSERT INTO eccs_source_config(facility,worksheet,source_mnemonic) VALUES ('REG Facility','Accommodations','TEST001')")
    values=dict(target_facility='REG Facility',target_mnemonic='REG001',target_name='Demo',target_pa_code='',target_active='Y')
    save_target(db,1,values)
    values['target_mnemonic']='REG002'; save_target(db,1,values)
    assert db.execute('SELECT target_mnemonic FROM eccs_target_staging').fetchone()[0]=='REG002'
    assert db.execute('SELECT COUNT(*) FROM eccs_target_audit').fetchone()[0]==2

def test_validation():
    db=sqlite3.connect(':memory:'); initialize(db)
    with pytest.raises(ValueError): save_target(db,1,dict(target_facility='',target_mnemonic='X',target_active='Y'))
