import logging

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QDialog

from app.models import ProfileEvents
from app.ui.ExitDataViewDialog_ui import Ui_ExitDialog
from app.ui.DataView_ui import Ui_DataView

        
class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(self, profile_id):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.model = ProfileEvents(profile_id)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.ui.exitBtn.clicked.connect(self.handle_exit_button_clicked)
        self.ui.listView.setModel(self.model)
        self.ui.listView.doubleClicked.connect(self.open_item_details)

    def showEvent(self, event):
        self.model.refresh_data()
        self.ui.listView.clearSelection()
        return super().showEvent(event)

    def handle_exit_button_clicked(self):
        self.exit_dialog_controller = ExitDataViewDialog()
        self.exit_dialog_controller.exec()
        self.exited.emit()

    def open_item_details(self, index):
        print(f"Opening item details for index {index.row()}")
        
    @pyqtSlot(dict)
    def add_event(self, event): 
        self.model.add_data(event)


class ExitDataViewDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_ExitDialog()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.buttonBox.accepted.connect(self.handle_accepted)
        self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Discard).clicked.connect(self.handle_rejected)
        
    def handle_accepted(self):
        ### TODO: Add save logic ###
        profile_name = self.ui.profileNameEdit.text()
        self.logger.info(f"User saved changes to profile \'{profile_name}\' and exited data viewer.")
        self.close()

    def handle_rejected(self):
        ### TODO: Add discard logic ###
        self.logger.info("User discarded changes and exited data viewer.")
        self.close()
    