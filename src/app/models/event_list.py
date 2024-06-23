import logging

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant

from app.models import DatabaseHandler, ProfileEvent, Profile


class EventList(QAbstractListModel):
    def __init__(self, db_handler: DatabaseHandler, profile: Profile):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.db_handler = db_handler
        self._data: list[ProfileEvent] = []

        self.profile = profile
        if not self.profile:
            self.logger.error("Profile is nonexistent.")
            return
        self.refresh_data()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            profile_event = self._data[index.row()]
            case_id = profile_event.event.case_id
            vehicle_num = profile_event.event.vehicle_num
            event_num = profile_event.event.event_num
            return f"{index.row() + 1}. Case: {case_id}, Vehicle: {vehicle_num}, Event: {event_num}"
        elif role == Qt.ItemDataRole.UserRole:
            return self._data[index.row()]
        elif role == Qt.ItemDataRole.FontRole:
            return self._data[index.row()].ignored

        return QVariant()

    def setData(self, index: QModelIndex, value: QVariant, role: Qt.ItemDataRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return False

        if role == Qt.ItemDataRole.FontRole:
            profile_event = self._data[index.row()]
            if self.db_handler.set_ignored(profile_event, value):
                self.refresh_data()
                return True

        return False

    def get_scatter_data(self):
        case_ids = []
        x_data = []
        y1_data = []
        y2_data = []
        for profile_event in self._data:
            if not profile_event.ignored:
                event = profile_event.event
                case_ids.append(event.case_id)
                x_data.append(event.c_bar)
                y1_data.append(event.NASS_dv)
                y2_data.append(event.TOT_dv)
        return {
            "case_ids": case_ids,
            "x_data": x_data,
            "y1_data": y1_data,
            "y2_data": y2_data,
        }

    def index_from_vals(self, case_id, vehicle_num, event_num):
        for i, profile_event in enumerate(self._data):
            event = profile_event.event
            if (
                event.case_id == case_id
                and event.vehicle_num == vehicle_num
                and event.event_num == event_num
            ):
                return self.index(i)
        return QModelIndex()

    def delete_event(self, index: QModelIndex):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return
        profile_event = self._data[index.row()]
        self.db_handler.delete_profile_event(profile_event)
        self.refresh_data()

    def refresh_data(self):
        self._data = self.db_handler.get_profile_events(self.profile)
        # TODO: Implement sorting in ProfileEvent
        # self._data.sort()

        self.layoutChanged.emit()
        self.logger.debug("Refreshed data.")
