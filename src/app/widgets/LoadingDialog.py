from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialogButtonBox, QDialog

from app.ui.LoadingDialog_ui import Ui_LoadingDialog


class LoadingWindowWidget(QDialog):
    cancel_btn_clicked = pyqtSignal()
    view_btn_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoadingDialog()
        self.ui.setupUi(self)

        cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        view_button = self.ui.buttonBox.addButton("View", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button.clicked.connect(self.cancel_btn_clicked.emit)
        view_button.clicked.connect(self.view_btn_clicked.emit)