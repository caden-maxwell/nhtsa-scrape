import logging
from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox

from app.ui.ProfileMenu_ui import Ui_ProfileMenu
from app.models.case_profiles import CaseProfiles

from .data_view import DataView


class ProfileMenu(QWidget):
    back = pyqtSignal()
    rescrape = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProfileMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
        self.model = CaseProfiles()
        self.ui.listView.setModel(self.model)
        self.ui.listView.selectionModel().selectionChanged.connect(self.handle_selection_changed)
        self.ui.listView.clearSelection()

        self.ui.rescrapeBtn.clicked.connect(self.handle_rescrape)
        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.openBtn.clicked.connect(self.handle_open)
        self.ui.deleteBtn.clicked.connect(self.handle_delete)

        self.profile_btns = [self.ui.openBtn, self.ui.deleteBtn, self.ui.rescrapeBtn]

    def setup(self):
        self.model.refresh_data()
        self.ui.listView.clearSelection()

        ### TODO: Remove this later ###
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        self.model.add_data(('Test', 'Some description', formatted_datetime, formatted_datetime, 'FORD', 'BRONCO-FULLSIZE', 2015, 2016, "F Front", "L Left - front or rear", 0, 159))
        ### TODO ###

    def handle_rescrape(self):
        selected = self.ui.listView.selectedIndexes()
        if not selected:
            return

        self.logger.debug("Rescraping...")
        selected = selected.pop()
        profile = self.model.data_list[selected.row()]
        data = profile[0:1] + profile[5:]
        self.rescrape.emit(data)

    def handle_open(self):
        self.data_viewer = DataView(False)
        self.data_viewer.show()
        
    def handle_delete(self):
        selected = self.ui.listView.selectedIndexes()
        if not selected:
            return

        dialog = QMessageBox(QMessageBox.Icon.Warning, "Delete Profile", "Are you sure you want to delete this profile?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        response = dialog.exec()
        if response == QMessageBox.StandardButton.No:
            return
        
        self.model.delete_data(selected.pop())
        self.ui.listView.clearSelection()
    
    def handle_selection_changed(self, selected, deselected):
        # Enable/disable buttons based on if a profile is selected
        for button in self.profile_btns:
            button.setEnabled(False)
            if self.ui.listView.selectedIndexes():
                button.setEnabled(True)
        self.logger.debug(f"Selected: {selected}, Deselected: {deselected}")
