from services.fluent.qfluentwidgets.components.widgets.label import SubtitleLabel
from ..common.style_sheet import StyleSheet
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QTableWidgetItem, QHeaderView, QWidget
from services.fluent.qfluentwidgets import  TableWidget, PushButton, BodyLabel
from datetime import datetime
class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        self.setObjectName('frame')
        StyleSheet.VIEW_INTERFACE.apply(self)

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)

class TableFrame(TableWidget):

    def __init__(self, columns,titleWidget: SubtitleLabel, parent=None):
        super().__init__(parent)
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.title = titleWidget

        self.setColumnCount(len(columns))
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(columns)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.titleText = self.title.text()
        self.title.setText(self.titleText + " (Last updated: Loading...)")

    def setRows(self, rows_data: list[list[str | tuple[str, Callable]]]):
        """ Add multiple rows to the table """
        self.setUpdatesEnabled(False)
        self.blockSignals(True)
        self.clearTable()

        self.title.setText(self.titleText + f" (Last updated: {datetime.now().strftime('%H:%M')})")


        self.setRowCount(len(rows_data))
        for i, row_data in enumerate(rows_data):
            
            
            for col_index, data in enumerate(row_data):
                if isinstance(data, tuple) and callable(data[1]):
                    button = PushButton(data[0])

                    button.clicked.connect(data[1])
                    button.setCursor(Qt.CursorShape.PointingHandCursor)
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.addWidget(button)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.setCellWidget(i, col_index, container)
                else:
                    item = QTableWidgetItem("" if data is None else str(data))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    item.setData(Qt.ItemDataRole.TextAlignmentRole, Qt.AlignmentFlag.AlignCenter)
                    self.setItem(i, col_index, item)
                self.setRowHeight(i, 64)
        # self.resizeRowsToContents()
        self.blockSignals(False)
        self.setUpdatesEnabled(True)
    
    def clearTable(self):
        """ Clear all items in the table """
        self.setRowCount(0)
        self.clearContents()
