import logging

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant

from app.models import DatabaseHandler


class EventList(QAbstractListModel):
    def __init__(self, db_handler: DatabaseHandler, profile_id):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.db_handler = db_handler
        self._data = []

        self.profile = self.db_handler.get_profile(profile_id)
        if not self.profile:
            self.logger.error(f"Profile ID {profile_id} not found.")
            print(f"Profile ID {profile_id} not found.")
            return
        self.refresh_data()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            data = self._data[index.row()]
            name = f"{index.row() + 1}. Case: {data[0]}, Vehicle: {data[1]}, Event: {data[2]}"
            return name
        elif role == Qt.ItemDataRole.UserRole:
            return self.event_dict(index)
        elif role == Qt.ItemDataRole.FontRole:
            return self._data[index.row()][31]

        return QVariant()

    def event_dict(self, index: QModelIndex):
        event = self._data[index.row()]
        return {
            "case_id": event[0],
            "vehicle_num": event[1],
            "event_num": event[2],
            "make": event[3],
            "model": event[4],
            "model_year": event[5],
            "curb_weight": event[6],
            "dmg_loc": event[7],
            "underride": event[8],
            "edr": event[9],
            "total_dv": event[10],
            "long_dv": event[11],
            "lat_dv": event[12],
            "smashl": event[13],
            "crush": event[14:20],
            "a_veh_num": event[20],
            "a_make": event[21],
            "a_model": event[22],
            "a_year": event[23],
            "a_curb_weight": event[24],
            "a_dmg_loc": event[25],
            "c_bar": event[26],
            "NASS_dv": event[27],
            "NASS_vc": event[28],
            "e": event[29],
            "TOT_dv": event[30],
            "ignored": event[31],
        }

    def get_scatter_data(self):
        case_ids = []
        x_data = []
        y1_data = []
        y2_data = []
        for i, event in enumerate(self._data):
            if not event[31]:
                case_ids.append(event[0])
                x_data.append(event[26])
                y1_data.append(event[27])
                y2_data.append(event[30])
        return {
            "case_ids": case_ids,
            "x_data": x_data,
            "y1_data": y1_data,
            "y2_data": y2_data,
        }

    def index_from_vals(self, case_id, vehicle_num, event_num):
        for i, event in enumerate(self._data):
            if (
                event[0] == case_id
                and event[1] == vehicle_num
                and event[2] == event_num
            ):
                return self.index(i)
        return QModelIndex()

    def delete_event(self, index: QModelIndex):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return
        event = self._data[index.row()]
        self.db_handler.delete_event(event, self.profile[0])
        self.refresh_data()

    def toggle_ignored(self, index: QModelIndex):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return
        event = self._data[index.row()]
        self.db_handler.toggle_ignored(event, self.profile[0])
        self.refresh_data()

    def refresh_data(self):
        selected = self.db_handler.get_profile_events(self.profile[0])
        selected = [(t[1], t[2], t[3], t[4]) for t in selected]
        selected.sort()

        self._data = self.db_handler.get_events(self.profile[0])
        self._data.sort()

        ignored_vals = [t[3] for t in selected]
        for i, val in enumerate(ignored_vals):
            self._data[i] += (val,)
        self.layoutChanged.emit()
        self.logger.debug("Refreshed data.")
