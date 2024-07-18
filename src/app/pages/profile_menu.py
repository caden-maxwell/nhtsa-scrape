import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, Qt, QItemSelection, pyqtSlot
from PyQt6.QtWidgets import QWidget, QMessageBox, QLineEdit, QInputDialog

from app.scrape import RequestController
from app.ui import Ui_ProfileMenu
from app.models import ProfileList, DatabaseHandler, Profile
from app.pages import DataView


class ProfileMenu(QWidget):
    back = pyqtSignal()

    def __init__(
        self, req_handler: RequestController, db_handler: DatabaseHandler, data_dir: Path
    ):
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._db_handler = db_handler
        self._model = ProfileList(self._db_handler)
        self._data_dir = data_dir
        self._req_handler = req_handler

        self.ui = Ui_ProfileMenu()
        self.ui.setupUi(self)

        self.ui.listView.setModel(self._model)
        self.ui.listView.selectionModel().selectionChanged.connect(
            self.handle_selection_changed
        )
        self.ui.listView.clearSelection()

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.openBtn.clicked.connect(self.handle_open)
        self.ui.listView.doubleClicked.connect(self.handle_open)
        self.ui.deleteBtn.clicked.connect(self.handle_delete)
        self.ui.renameBtn.clicked.connect(self.handle_rename)

        self._data_viewers: list[DataView] = []

    def showEvent(self, event):
        self._model.refresh_data()
        return super().showEvent(event)

    @pyqtSlot(str)
    def data_dir_changed(self, data_dir: str):
        data_dir = Path(data_dir)
        self._data_dir = data_dir
        for viewer in self._data_viewers:
            viewer.set_data_dir(data_dir)

    def handle_open(self):
        selected = self.ui.listView.selectedIndexes()
        for idx in selected:
            profile: Profile = idx.data(role=Qt.ItemDataRole.UserRole)
            self._logger.debug(f"Opening profile {profile}")
            data_viewer = DataView(self._req_handler, self._db_handler, profile, self._data_dir)
            self._db_handler.profile_updated.connect(data_viewer.handle_profile_updated)
            self._db_handler.event_added.connect(data_viewer.handle_event_added)
            self._data_viewers.append(data_viewer)
            data_viewer.exited.connect(
                lambda viewer=data_viewer: self._data_viewers.remove(viewer)
            )
            data_viewer.show()

    def handle_delete(self):
        selected = self.ui.listView.selectedIndexes()
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

        self._model.delete_profiles(selected)
        self.ui.listView.clearSelection()

    def handle_rename(self):
        selected = self.ui.listView.selectedIndexes().pop()
        profile: Profile = selected.data(role=Qt.ItemDataRole.UserRole)
        profile_name = selected.data(role=Qt.ItemDataRole.DisplayRole)
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Profile",
            "Enter a new name for the profile:",
            QLineEdit.EchoMode.Normal,
            profile_name,
        )
        if not ok or not new_name:
            return
        self._db_handler.update_profile(profile, name=new_name)
        self._model.refresh_data()
        self.ui.listView.clearSelection()

    def handle_selection_changed(self, selected: QItemSelection, deselected):
        self.ui.openBtn.setEnabled(False)
        self.ui.deleteBtn.setEnabled(False)
        self.ui.renameBtn.setEnabled(False)
        if self.ui.listView.selectedIndexes():
            self.ui.openBtn.setEnabled(True)
            self.ui.deleteBtn.setEnabled(True)
            if len(self.ui.listView.selectedIndexes()) == 1:
                self.ui.renameBtn.setEnabled(True)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self.handle_delete()
        if event.key() == Qt.Key.Key_Return:
            self.handle_open()
        return super().keyPressEvent(event)
