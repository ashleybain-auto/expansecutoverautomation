"""Navigation prototype only. Power Fx parity and production connections remain pending."""
import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QListWidget, QLabel, QStackedWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView)
from .storage import OfflineStore
from .source_aligned_editor import SourceAlignedEditor

SCREENS = [
    ('scrLaunchPad', 'Launch Pad'),
    ('scrRegistrationLaunchpad', 'Registration Launchpad'),
    ('scrCutoverReadinessDash', 'Cutover Readiness'),
    ('srcMatchDashboard', 'Match Dashboard'),
    ('scrWorksheetResults', 'Worksheet Results'),
    ('scrAccommodations', 'Config Tool Update/Edit'),
    ('scrProviderCrosswalks', 'Provider Crosswalks'),
]

class MainWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()
        self.store = OfflineStore(database)
        self.setWindowTitle('ECCS Windows Desktop — Offline Prototype')
        self.resize(1200, 760)
        shell = QWidget(); layout = QHBoxLayout(shell)
        self.nav = QListWidget(); self.nav.setFixedWidth(250)
        self.pages = QStackedWidget()
        for key, label in SCREENS:
            self.nav.addItem(label)
            if key == 'scrAccommodations':
                page = SourceAlignedEditor(self.store)
            elif key == 'scrWorksheetResults':
                page = self.worksheet_page()
            else:
                page = QWidget(); vertical = QVBoxLayout(page)
                vertical.addWidget(QLabel(label))
                vertical.addWidget(QLabel('Source behavior not yet reconstructed; placeholder only.'))
                vertical.addStretch()
            self.pages.addWidget(page)
        layout.addWidget(self.nav); layout.addWidget(self.pages, 1)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self.setCentralWidget(shell)
        self.setStyleSheet('''QMainWindow,QWidget{background:#ffffff;color:#54585A;font-family:"Open Sans";font-size:11pt}
          QListWidget{background:#03173E;color:white;border:0;padding:12px}
          QListWidget::item{padding:10px} QListWidget::item:selected{background:#E05929;color:white}
          QLabel{padding:8px} QComboBox{padding:6px}''')

    def worksheet_page(self):
        page = QWidget(); vertical = QVBoxLayout(page)
        vertical.addWidget(QLabel('Worksheet Results — offline filtering prototype'))
        self.facility = QComboBox(); self.worksheet = QComboBox()
        self.facility.addItems(['All facilities'] + self.store.facets('facility'))
        self.worksheet.addItems(['All worksheets'] + self.store.facets('worksheet'))
        vertical.addWidget(self.facility); vertical.addWidget(self.worksheet)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Facility','Worksheet','Source Key','Source Name','Target Key','Status'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        vertical.addWidget(self.table)
        self.facility.currentIndexChanged.connect(self.refresh_rows)
        self.worksheet.currentIndexChanged.connect(self.refresh_rows)
        self.refresh_rows()
        return page

    def refresh_rows(self):
        facility = self.facility.currentText() if self.facility.currentIndex() > 0 else None
        worksheet = self.worksheet.currentText() if self.worksheet.currentIndex() > 0 else None
        rows = self.store.filter_rows(facility, worksheet)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem('' if value is None else str(value)))

def main():
    app = QApplication(sys.argv)
    window = MainWindow(Path.home() / '.eccs-windows' / 'offline.sqlite3')
    window.show()
    return app.exec()

if __name__ == '__main__':
    raise SystemExit(main())
