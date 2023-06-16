from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget

from app.ui.LogsWindow_ui import Ui_LogsWindow


class LogsWindowController(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_LogsWindow()
        self.ui.setupUi(self)
        self.ui.logsEdit.setReadOnly(True)
        self.ui.clearBtn.clicked.connect(self.handle_clear_btn_clicked)

    @pyqtSlot(str)
    def handle_logger_message(self, msg):
        self.ui.logsEdit.append(msg)

    @pyqtSlot()
    def handle_clear_btn_clicked(self):
        self.ui.logsEdit.clear()
