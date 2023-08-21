import datetime
import logging
import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot
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

        self.ui.clearBtn.clicked.connect(self.handle_clear_clicked)
        self.ui.saveBtn.clicked.connect(self.handle_save_clicked)

    def showEvent(self, a0):
        self.ui.logsEdit.verticalScrollBar().setValue(
            self.ui.logsEdit.verticalScrollBar().maximum()
        )
        return super().showEvent(a0)

    @pyqtSlot(str)
    def handle_logger_message(self, msg):
        self.ui.logsEdit.append(msg)
        self.ui.saveBtn.setEnabled(True)
        self.ui.clearBtn.setEnabled(True)

    def handle_clear_clicked(self):
        self.ui.logsEdit.clear()
        self.ui.clearBtn.setEnabled(False)
        self.ui.saveBtn.setEnabled(False)
        self.logger.info("Cleared all logs.")

    def handle_save_clicked(self):
        dir_path = Path(__file__).parent.parent / "logs"
        os.makedirs(dir_path, exist_ok=True)
        log_path = (
            dir_path / f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
        )
        with open(log_path, "w") as f:
            f.write(self.ui.logsEdit.toPlainText())
        self.logger.info(f"Saved all logs to file at '{f.name}'.")
        self.ui.saveBtn.setEnabled(False)
