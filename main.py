import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
import sys
import traceback
from src.app import start_app
from src.app.common.config import cfg




if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        start_app(app)
    except Exception:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Startup Error")
        msg.setFixedSize(600, 400)
        msg.setText("An error occurred:")
        msg.setDetailedText(traceback.format_exc())
        msg.exec()