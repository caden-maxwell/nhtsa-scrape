import logging
from datetime import datetime

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QMessageBox

from app.ui.ProfileMenu_ui import Ui_ProfileMenu
from app.models.scrape_profiles import ScrapeProfiles

from .data_view import DataView


class ProfileMenu(QWidget):
    back = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.model = ScrapeProfiles()

        self.ui = Ui_ProfileMenu()
        self.ui.setupUi(self)

        self.ui.listView.setModel(self.model)
        self.ui.listView.selectionModel().selectionChanged.connect(self.handle_selection_changed)
        self.ui.listView.clearSelection()

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.openBtn.clicked.connect(self.handle_open)
        self.ui.deleteBtn.clicked.connect(self.handle_delete)

    def showEvent(self, event):
        self.model.refresh_data()
        self.ui.listView.clearSelection()
        return super().showEvent(event)

    def handle_open(self):
        selected = self.ui.listView.selectedIndexes()
        if not selected:
            return
        profile_id = selected.pop().data(role=Qt.ItemDataRole.UserRole)[0]
        self.logger.debug(f"Opening profile {profile_id}")
        self.data_viewer = DataView(profile_id)
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
        for button in [self.ui.openBtn, self.ui.deleteBtn]:
            button.setEnabled(False)
            if self.ui.listView.selectedIndexes():
                button.setEnabled(True)
