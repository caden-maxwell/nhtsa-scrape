import datetime
import logging
import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.LogsWindow_ui import Ui_LogsWindow


class LogsWindow(QWidget):
    clear_logs = pyqtSignal()
    save_logs = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.ui = Ui_LogsWindow()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.clearBtn.clicked.connect(self.handle_clear_btn_clicked)
        self.ui.saveBtn.clicked.connect(self.handle_save_btn_clicked)

    def handle_logger_message(self, msg):
        self.ui.logsEdit.append(msg)

    def handle_clear_btn_clicked(self):
        self.ui.logsEdit.clear()

    def handle_save_btn_clicked(self):
        os.makedirs('logs', exist_ok=True)
        with open(f'logs/{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log', 'w') as f:
            f.write(self.ui.logsEdit.toPlainText())
        self.logger.info(f"Saved all logs to file at '{f.name}'.")
