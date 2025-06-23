# coding:utf-8
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QTableWidgetItem, QHeaderView, QWidget
from services.fluent.qfluentwidgets import  TableWidget, PushButton, TitleLabel
from services.fluent.qfluentwidgets.components.widgets.label import StrongBodyLabel, SubtitleLabel

from .gallery_interface import GalleryInterface
from ..common.style_sheet import StyleSheet
from ..common.config import cfg


class GotoInterface(GalleryInterface):
    """ View interface """

    def __init__(self, parent=None):
        super().__init__(
            parent=parent
        )
        self.setObjectName('viewInterface')
        late_rides_columns=[self.tr("Ride ID"), self.tr("End Time"), self.tr("Future Ride"), self.tr("Future Ride Time"), self.tr("Comment")]
        self.late_rides_table = TableFrame(columns=late_rides_columns, parent=self)
        self.late_rides_title = SubtitleLabel('Goto Late Rides', self)
        self.vBoxLayout.addWidget(self.late_rides_title)
        self.vBoxLayout.addWidget(self.late_rides_table)
        
    def _remove(self, widget):
        if widget is not None:
            self.vBoxLayout.removeWidget(widget)
            widget.setParent(None)  # Detach from the UI
            widget.deleteLater()
            
    def removeWidgets(self):
        """ Remove all widgets from the interface """
        if not cfg.get(cfg.late_rides):
            self._remove(self.late_rides_title)
            self._remove(self.late_rides_table)

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

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        # self.titleLabel = TitleLabel(title, self)
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)

        self.setColumnCount(len(columns))
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setStretchLastSection(True)

        # self.setFixedSize(625, 440)
        # self.resizeColumnsToContents()

    def setRows(self, rows_data: list[list[str | tuple[str, Callable]]], btn_colors=("#4caf50", '#45a049', '#388e3c')):
        """ Add multiple rows to the table """
        self.setUpdatesEnabled(False)
        self.blockSignals(True)
        self.clearTable()

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
