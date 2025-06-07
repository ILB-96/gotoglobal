from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QTableWidgetItem, QLabel, QWidget, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime as dt
from services import Log

class Table(QWidget):
    row_requested = pyqtSignal(list)

    def __init__(self, title: str, columns: list[str], rows: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName(title.lower().replace(' ', '_'))
        self.row_requested.connect(self._add_row_safe)
        self._layout = QVBoxLayout(self)
        self.title_label = QLabel(f"<b>{title}</b>")
        self._layout.addWidget(self.title_label)

        self.last_updated_label = QLabel("Last updated: Loading...")
        self._layout.addWidget(self.last_updated_label)

        self._columns = columns
        self.table = QTableWidget(rows, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.configure_table_styles()
        self._layout.addWidget(self.table)

    def configure_table_styles(self):
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
    
        if (vertical_header := self.table.verticalHeader()) is not None:
            vertical_header.setVisible(False)
        self.title_label.setStyleSheet("font-size: 16pt;")
        self.table.setStyleSheet("border-radius: 4px;")
        self.table.setStyleSheet("""
        QTableWidget {
            font-size: 13pt;
            font-family: 'Tahoma', 'Arial';
            background-color: #ffffff;
            alternate-background-color: #f9f9f9;
            gridline-color: #f0f0f0;
            selection-background-color: #cce5ff;
            selection-color: #000;
            border-radius: 4px;
            padding: 2px;
        }
        QHeaderView {
            background-color: transparent;
            border: none;
            border-radius: 4px;
        }
        QHeaderView::section {
            background-color: #e8e8e8;
            color: #333;
            font-weight: bold;
            font-size: 12pt;
            padding: 8px;
            border: none;
            border-right: 1px solid #fff;
        }
        QHeaderView::section:first {
        border-top-left-radius: 4px;
        }
        QHeaderView::section:last {
            border-top-right-radius: 4px;
            border-right: none;
        }
        QTableCornerButton::section {
            background-color: #e8e8e8;
            border: none;
            border-top-left-radius: 4px;
        }
    """)
        self.last_updated_label.setStyleSheet("color: green; font-weight: bold;")
        if (header := self.table.horizontalHeader()) is not None:
            header.setStretchLastSection(True)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
    def add_rows(self, rows_data: list[list[str]]):
        self.clear_table()
        if not all(len(row) == len(self._columns) for row in rows_data):
            raise ValueError("One or more rows do not match the number of columns")

        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        self.set_last_updated(dt.now().strftime("%H:%M"))
        start_row = self.table.rowCount()
        self.table.setRowCount(start_row + len(rows_data))

        for i, row_data in enumerate(rows_data):
            row_index = start_row + i
            for col_index, data in enumerate(row_data):
                item = QTableWidgetItem("" if data is None else str(data))
                self.table.setItem(row_index, col_index, item)

        self.table.blockSignals(False)
        self.table.setUpdatesEnabled(True)
        viewport = self.table.viewport()
        if viewport is not None:
            viewport.update()

    def _add_row_safe(self, row_data: list[str]):
        if len(row_data) != len(self._columns):
            raise ValueError("Row data length does not match number of columns")
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for col, data in enumerate(row_data):
            item = QTableWidgetItem(data)
            Log.info(f"Adding item to table: {data} at row {row_position}, column {col}")
            self.table.setItem(row_position, col, item)
            
    def clear_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(len(self._columns))
        for col in range(self.table.columnCount()):
            self.table.setHorizontalHeaderItem(col, QTableWidgetItem(self._columns[col]))
                
    def set_last_updated(self, timestamp: str):
        self.last_updated_label.setText(f"Last updated: {timestamp}")
        