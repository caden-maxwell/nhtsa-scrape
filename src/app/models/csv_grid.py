import logging

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

from . import DatabaseHandler


class CSVGrid(QAbstractTableModel):
    def __init__(self, db_handler: DatabaseHandler, profile_id: int):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.db_handler = db_handler
        self._data = []

        self.profile = self.db_handler.get_profile(profile_id)
        if not self.profile:
            self.logger.error(f"Profile ID {profile_id} not found.")
            return

        self._headers = self.db_handler.get_headers("events")
        self.refresh_grid()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])

        return QVariant()

    def all_events(self):
        return self._data

    def get_headers(self):
        return self._headers
    
    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return super().headerData(section, orientation, role)

    def refresh_grid(self):
        self._data = self.db_handler.get_events(self.profile[0], include_ignored=False)
        self.layoutChanged.emit()
        self.logger.debug("Refreshed data.")
