import logging

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

from app.models import DatabaseHandler, Event, Profile


class EventTable(QAbstractTableModel):
    def __init__(self, db_handler: DatabaseHandler, profile: Profile):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._db_handler = db_handler
        self._data: list[tuple] = []

        self._profile = profile
        if not self._profile:
            self._logger.error("Profile is nonexistent.")
            return

        self._headers = self._db_handler.get_headers(Event)
        self.refresh_data()

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

    def refresh_data(self):
        self._data: list[Event] = self._db_handler.get_events(
            self._profile, include_ignored=False
        )
        self._data = [event.to_tuple() for event in self._data]
        self.layoutChanged.emit()
        self._logger.debug("Refreshed data.")

    def set_profile(self, profile: Profile):
        self._profile = profile
        self.refresh_data()
        self._logger.debug(f"Set profile to {profile.id}.")
