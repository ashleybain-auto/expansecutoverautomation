from app.storage import OfflineStore

def test_facility_worksheet_filters(tmp_path):
    store = OfflineStore(tmp_path / 'offline.db')
    store.db.executemany('INSERT INTO worksheet_rows (facility, worksheet, source_key) VALUES (?, ?, ?)', [
        ('REG Facility', 'Accommodation', 'A1'),
        ('REG Facility', 'REG Facility', 'R1'),
        ('Other', 'REG Facility', 'R2')])
    store.db.commit()
    assert len(store.filter_rows('REG Facility', 'REG Facility')) == 1
    assert store.filter_rows('REG Facility', 'REG Facility')[0][2] == 'R1'
    assert len(store.filter_rows('REG Facility')) == 2
    assert store.filter_rows('Missing') == []
