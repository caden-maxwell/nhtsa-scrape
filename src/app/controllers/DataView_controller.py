from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from app.ui.DataView_ui import Ui_DataView
from app.ui.ExitDataViewDialog_ui import Ui_ExitDataViewDialog
import logging

class DataViewController(QWidget):

    
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.exit_dialog_controller = ExitDialogController()

        # Data View signals
        self.ui.exitBtn.clicked.connect(self.handle_exit_btn_clicked)

        # Exit Dialog signals
        self.exit_dialog_controller.save.connect(self.handle_save_profile)
        self.exit_dialog_controller.discard.connect(self.handle_discard_data)
        
    
    def handle_exit_btn_clicked(self):
        self.exit_dialog_controller.show()
    
    def handle_save_profile(self, profile_name):
        self.logger.info(f"Save & exit: \'{profile_name}\'")

    def handle_discard_data(self):
        self.logger.info("Data Discarded")


class ExitDialogController(QWidget):
    save = pyqtSignal(str)
    discard = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_ExitDataViewDialog()
        self.ui.setupUi(self)

        self.ui.saveBtn.clicked.connect(self.handle_save_btn_clicked)
        self.ui.discardBtn.clicked.connect(self.handle_discard_btn_clicked)
    
    def handle_save_btn_clicked(self):
        profile_name = self.ui.profileNameEdit.text()
        self.close()
        self.save.emit(profile_name)

    def handle_discard_btn_clicked(self):
        self.close()
        self.discard.emit()
