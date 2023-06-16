from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.LogsWindow_ui import Ui_LogsWindow


class LogsWindowWidget(QWidget):
    clear_logs = pyqtSignal()
    save_logs = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.ui = Ui_LogsWindow()
        self.ui.setupUi(self)
        self.ui.logsEdit.setReadOnly(True)

        self.ui.clearBtn.clicked.connect(self.clear_logs.emit)
        self.ui.saveBtn.clicked.connect(self.save_logs.emit)
