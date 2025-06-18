from typing import Callable
from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QTableWidgetItem, QLabel, QWidget, QHeaderView, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime as dt

class Table(QWidget):
    row_requested = pyqtSignal(list)

    def __init__(self, title: str, columns: list[str], rows: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName(title)
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
        # self.table.setWordWrap(False)
        self.table.horizontalHeader().setHighlightSections(True)
        self.table.verticalHeader().setHighlightSections(True)
        self.table.verticalHeader().setDefaultSectionSize(38)
    
        if (vertical_header := self.table.verticalHeader()) is not None:
            vertical_header.setVisible(False)
        
        self.title_label.setStyleSheet("font-size: 16pt;")
        self.table.setStyleSheet("border-radius: 4px;")
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
                font-family: 'Tahoma', 'Arial';
                background-color: #ffffff;
                alternate-background-color: #f4f6f9;
                gridline-color: #dcdcdc;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333;
                font-weight: bold;
                font-size: 11pt;
                padding: 6px;
                border: none;
                border-right: 1px solid #ddd;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
                border-right: none;
            }
            QTableCornerButton::section {
                background-color: #f0f0f0;
                border: none;
                border-top-left-radius: 8px;
            }
            QTableWidget::item:hover {
                background-color: #e3f2fd;
                color: black;
            }
            QTableWidget::item:focus {
                color: black;
            }
        """)

        self.last_updated_label.setStyleSheet("color: green; font-weight: bold;")
        if (header := self.table.horizontalHeader()) is not None:
            header.setStretchLastSection(True)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
    def add_rows(self, rows_data: list[list[str | tuple[str, Callable]]], btn_colors=("#4caf50", '#45a049', '#388e3c')):
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
                if isinstance(data, tuple) and callable(data[1]):
                    button = QPushButton(data[0])
                    button.setStyleSheet(f"""
                        QPushButton {{
                            min-height: 24px;
                            padding: 6px 14px;
                            background-color: {btn_colors[0]};
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 15px;
                            font-weight: 700;
                            font-family: 'Tahoma', 'Arial';
                        }}
                        QPushButton:hover {{
                            background-color: {btn_colors[1]};
                        }}
                        QPushButton:pressed {{
                            background-color: {btn_colors[2]};
                        }}
                    """)

                    button.clicked.connect(data[1])
                    button.setCursor(Qt.CursorShape.PointingHandCursor)
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.addWidget(button)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setCellWidget(row_index, col_index, container)
                else:
                    item = QTableWidgetItem("" if data is None else str(data))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    item.setData(Qt.ItemDataRole.TextAlignmentRole, Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_index, col_index, item)
                self.table.setRowHeight(row_index, 56)

        self.table.blockSignals(False)
        self.table.setUpdatesEnabled(True)
        viewport = self.table.viewport()
        if viewport is not None:
            viewport.update()

    def clear_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(len(self._columns))
        for col in range(self.table.columnCount()):
            self.table.setHorizontalHeaderItem(col, QTableWidgetItem(self._columns[col]))
                
    def set_last_updated(self, timestamp: str):
        self.last_updated_label.setText(f"Last updated: {timestamp}")
    

    def start_loading(self):
        if hasattr(self, "_loading_overlay") and self._loading_overlay is not None:
            self._loading_overlay.setGeometry(self.table.geometry())
            self._loading_overlay.raise_()
            self._loading_overlay.show()
            return

        # Create overlay
        self._loading_overlay = QFrame(self)
        self._loading_overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 4px;
            }
        """)
        self._loading_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._loading_overlay.setGeometry(self.table.geometry())
        self._loading_overlay.raise_()

        layout = QVBoxLayout(self._loading_overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(0, 50, 0, 0)

        self._loading_label = QLabel("Loading", self._loading_overlay)
        self._loading_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #444;")
        layout.addWidget(self._loading_label)
        self._dots = ""
        def animate():
            self._dots = "." if self._dots == "..." else self._dots + "."
            self._loading_label.setText(f"Loading{self._dots}")

        self._loading_timer = QTimer(self)
        self._loading_timer.timeout.connect(animate)
        self._loading_timer.start(500)

        self._loading_overlay.show()

        original_resize_event = self.resizeEvent
        
        def resize_event(event):
            self._loading_overlay.setGeometry(self.table.geometry())
            if original_resize_event:
                original_resize_event(event)
        self.resizeEvent = resize_event


    
    def stop_loading(self):
        if hasattr(self, "_loading_overlay"):
            self._loading_overlay.hide()
        if hasattr(self, "_loading_timer") and self._loading_timer.isActive():
            self._loading_timer.stop()


