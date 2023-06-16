from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSlot
from app.ui.LogsWindow_ui import Ui_LogsWindow

class LogsWindowController(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_LogsWindow()
        self.ui.setupUi(self)
        self.ui.logsEdit.setReadOnly(True)

    def handle_logger_message(self, msg):
        self.ui.logsEdit.append(msg)
