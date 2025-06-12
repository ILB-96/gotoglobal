from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
import traceback
from src.app import start_app

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        start_app(app)
    except Exception:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Startup Error")
        msg.setText("An error occurred:")
        msg.setDetailedText(traceback.format_exc())
        msg.exec()