import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QObject

from app.widgets.ExitDataViewDialog import ExitDataViewDialog
from app.widgets.DataViewWidget import DataViewWidget

class DataViewController(QObject):
    exited = pyqtSignal()

    def __init__(self, widget: DataViewWidget):
        super().__init__()
        self.widget = widget
        self.logger = logging.getLogger(__name__)

        self.widget.exit_button_clicked.connect(self.handle_exit_button_clicked)

    def handle_exit_button_clicked(self):
        self.exit_dialog_controller = ExitDialogController()
        self.exit_dialog_controller.exited.connect(self.exited.emit)
        self.exit_dialog_controller.show_dialog()


class ExitDialogController(QObject):
    exited = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.exit_widget = ExitDataViewDialog()
        self.logger = logging.getLogger(__name__)

        self.exit_widget.save.connect(self.handle_save)
        self.exit_widget.discard.connect(self.handle_discard)
        self.exit_widget.cancel.connect(self.handle_cancel)
    
    def show_dialog(self):
        self.exit_widget.exec()

    def handle_save(self):
        ### TODO: Add save logic ###
        profile_name = self.exit_widget.ui.profileNameEdit.text()
        self.logger.info(f"User saved changes to profile \'{profile_name}\' and exited data viewer.")
        self.exited.emit()

    def handle_discard(self):
        ### TODO: Add discard logic ###
        self.logger.info("User discarded changes and exited data viewer.")
        self.exited.emit()
    
    def handle_cancel(self):
        self.logger.info("User cancelled data viewer exit.")
