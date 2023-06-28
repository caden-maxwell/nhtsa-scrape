import logging

from PyQt6.QtWidgets import QDialog, QDialogButtonBox 

from app.ui.LoadingDialog_ui import Ui_LoadingDialog


class LoadingWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoadingDialog()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.view_button = self.ui.buttonBox.addButton("Stop and View Data", QDialogButtonBox.ButtonRole.AcceptRole)
