from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.DataView_ui import Ui_DataView


class DataViewWidget(QWidget):
    exit_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.ui.exitBtn.clicked.connect(self.exit_button_clicked.emit)
