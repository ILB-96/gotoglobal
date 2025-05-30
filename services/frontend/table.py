from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QTableWidgetItem, QLabel, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie

class Table(QWidget):
    def __init__(self, title: str, columns: list[str], rows: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setObjectName(title.lower().replace(' ', '_'))  # Set the name of the widget

        self._layout = QVBoxLayout(self)
        self.title_label = QLabel(f"<b>{title}</b>")
        self._layout.addWidget(self.title_label)

        self.last_updated_label = QLabel("Last updated: Loading...")
        self._layout.addWidget(self.last_updated_label)

        self._columns = columns  # Store columns for later use
        self.table = QTableWidget(rows, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)

        self._layout.addWidget(self.table)


    
    def update_cell(self, row: int, col: int, text: str):
        if row < self.table.rowCount() and col < self.table.columnCount():
            item = self.table.item(row, col)
            if item is None:
                item = QTableWidgetItem(text)
                self.table.setItem(row, col, item)
            else:
                item.setText(text)
        else:
            raise IndexError("Row or column index out of range")
    def add_row(self, row_data: list[str]):
        if len(row_data) != len(self._columns):
            raise ValueError("Row data length does not match number of columns")
        
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for col, data in enumerate(row_data):
            item = QTableWidgetItem(data)
            self.table.setItem(row_position, col, item)
            
            
    def clear_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(len(self._columns))
        for col in range(self.table.columnCount()):
            self.table.setHorizontalHeaderItem(col, QTableWidgetItem(self._columns[col]))

    
    def start_loading_indicator(self):
        if hasattr(self, "_loading_overlay"):
            return self._loading_overlay.show()
        
        self._loading_overlay = QLabel(self)
        self._loading_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._loading_overlay.setStyleSheet("background: rgba(255,255,255,180); border-radius: 8px;")
        self._loading_overlay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._spinner_movie = QMovie("spinner.gif")
        self._spinner_movie.setScaledSize(QSize(32, 32))  # 🔹 Set desired spinner size
        self._loading_overlay.setMovie(self._spinner_movie)
        self._spinner_movie.start()

        self._loading_overlay.resize(self.table.size())
        self._loading_overlay.move(self.table.pos())
        self._loading_overlay.show()

        self.table.raise_()
        self._loading_overlay.raise_()
    
    def stop_loading_indicator(self):
        if hasattr(self, "_loading_overlay"):
            self._loading_overlay.hide()
            if hasattr(self, "_spinner_movie"):
                self._spinner_movie.stop()
                
    def set_last_updated(self, timestamp: str):
        self.last_updated_label.setText(f"Last updated: {timestamp}")
        self.last_updated_label.setStyleSheet("color: green; font-weight: bold;")