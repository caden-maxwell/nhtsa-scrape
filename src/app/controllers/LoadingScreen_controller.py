from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.LoadingScreen_ui import Ui_LoadingScreen

import logging


class LoadingScreenController(QWidget):
    cancel_btn_clicked = pyqtSignal()
    stop_btn_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.ui = Ui_LoadingScreen()
        self.ui.setupUi(self)

        self.ui.cancelBtn.clicked.connect(self.handle_cancel_btn_clicked)
        self.ui.stopBtn.clicked.connect(self.handle_stop_btn_clicked)

    def handle_cancel_btn_clicked(self):
        self.cancel_btn_clicked.emit()
        self.logger.info("Cancel button clicked")

    def handle_stop_btn_clicked(self):
        self.stop_btn_clicked.emit()
        self.logger.info("Stop button clicked")
