from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QTableWidgetItem, QLabel, QWidget

class Table(QWidget):
    def __init__(self, name: str, columns: list[str], rows: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel(f"<b>{name}</b>")
        self.layout.addWidget(self.title_label)

        self.last_updated_label = QLabel("Last updated: Loading...")
        self.layout.addWidget(self.last_updated_label)

        self.table = QTableWidget(rows, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)


    
    def update_cell(self, row: int, col: int, text: str):
        if row < self.rowCount() and col < self.columnCount():
            item = self.item(row, col)
            if item is None:
                item = QTableWidgetItem(text)
                self.setItem(row, col, item)
            else:
                item.setText(text)
        else:
            raise IndexError("Row or column index out of range")
    
    def clear_table(self):
        self.setRowCount(0)
        self.setColumnCount(len(self.horizontalHeaderLabels()))
        for col in range(self.columnCount()):
            self.setHorizontalHeaderItem(col, QTableWidgetItem(self.horizontalHeaderItem(col).text()))
        self.resizeColumnsToContents()
    
    def loading_indicator(self):
        ...
        