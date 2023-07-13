import logging

from PyQt6.QtCore import pyqtSignal, Qt, QItemSelection
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
        self.ui.listView.selectionModel().selectionChanged.connect(
            self.handle_selection_changed
        )
        self.ui.listView.clearSelection()

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.openBtn.clicked.connect(self.handle_open)
        self.ui.listView.doubleClicked.connect(self.handle_open)
        self.ui.deleteBtn.clicked.connect(self.handle_delete)

        self.data_viewers = []

    def showEvent(self, event):
        self.model.refresh_profiles()
        self.ui.listView.clearSelection()
        return super().showEvent(event)

    def handle_open(self):
        selected = self.ui.listView.selectedIndexes()
        if not selected:
            return
        for idx in selected:
            profile_id = idx.data(role=Qt.ItemDataRole.UserRole)[0]
            self.logger.debug(f"Opening profile {profile_id}")
            new_viewer = DataView(profile_id)
            self.data_viewers.append(new_viewer)
            new_viewer.exited.connect(lambda: self.data_viewers.remove(new_viewer))
            new_viewer.show()

    def handle_delete(self):
        selected = self.ui.listView.selectedIndexes()
        if not selected:
            return

        dialog = QMessageBox(
            QMessageBox.Icon.Warning,
            "Delete Profile",
            f"Are you sure you want to delete {'these' if len(selected) > 1 else 'this'} profile{'s'[:len(selected)^1]}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        response = dialog.exec()
        if response == QMessageBox.StandardButton.No:
            return

        self.model.delete_profiles(selected)
        self.ui.listView.clearSelection()

    def handle_selection_changed(self, selected: QItemSelection, deselected):
        self.ui.openBtn.setEnabled(False)
        self.ui.deleteBtn.setEnabled(False)
        if len(self.ui.listView.selectedIndexes()) < 1:
            self.ui.deleteBtn.setEnabled(False)
            self.ui.openBtn.setEnabled(False)
        else:
            self.ui.openBtn.setEnabled(True)
            self.ui.deleteBtn.setEnabled(True)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self.handle_delete()
        if event.key() == Qt.Key.Key_Return:
            self.handle_open()
        return super().keyPressEvent(event)
