import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.LogsWindow_ui import Ui_LogsWindow


class LogsWindowController(QWidget):
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
        ### TODO: Actually save the logs somewhere ###
        self.logger.info('Saving logs to file...')
