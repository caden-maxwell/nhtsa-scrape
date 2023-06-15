from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from app.ui.DataView_ui import Ui_DataView

class DataViewController(QWidget):
    back_btn_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.ui.backBtn.clicked.connect(self.back_btn_clicked)

    def handle_back_btn_clicked(self):
        self.back_btn_clicked.emit()