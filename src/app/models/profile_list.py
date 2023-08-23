import logging

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant

from . import DatabaseHandler


class ProfileList(QAbstractListModel):
    def __init__(self, db_handler: DatabaseHandler):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.db_handler = db_handler
        self._data = []

        self.refresh_data()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            data = self._data[index.row()]
            return f"{data[1]}"  # TODO: Add more info in new TreeView class
        elif role == Qt.ItemDataRole.UserRole:
            return self._data[index.row()]

        return QVariant()

    def delete_profiles(self, indices: list[QModelIndex]):
        for index in indices:
            if not index.isValid() or not (0 <= index.row() < self.rowCount()):
                continue
            data = self._data[index.row()]
            self.db_handler.delete_profile(data[0])
        self.refresh_data()

    def refresh_data(self):
        self._data = self.db_handler.get_profiles()
        self.layoutChanged.emit()
        self.logger.debug("Refreshed data.")
