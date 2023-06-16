from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialogButtonBox, QDialog

from app.ui.ExitDataViewDialog_ui import Ui_ExitDialog


class ExitDataViewDialog(QDialog):
    save = pyqtSignal()
    discard = pyqtSignal()
    cancel = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_ExitDialog()
        self.ui.setupUi(self)

        save_button = self.ui.buttonBox.addButton("Save", QDialogButtonBox.ButtonRole.AcceptRole)
        discard_button = self.ui.buttonBox.addButton("Discard", QDialogButtonBox.ButtonRole.RejectRole)
        cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        save_button.clicked.connect(self.save.emit)
        discard_button.clicked.connect(self.discard.emit)
        cancel_button.clicked.connect(self.cancel.emit)