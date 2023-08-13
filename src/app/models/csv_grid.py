import logging
from pathlib import Path
import sqlite3

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant


class CSVGrid(QAbstractTableModel):
    def __init__(self, profile_id):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.db = None
        self.cursor = None
        self.profile = None
        self.__data_list = []

        try:
            db_path = Path(__file__).parent / "db.sqlite3"
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
            self.profile = self.cursor.execute(
                """
                SELECT * FROM scrape_profiles WHERE profile_id = ?
                """,
                (profile_id,),
            ).fetchone()
            if self.profile is None:
                raise ValueError(f"Profile ID {profile_id} does not exist.")
        except (ValueError, sqlite3.Error) as e:
            self.logger.error(e)
        self.refresh_grid()

    def rowCount(self, parent=QModelIndex()):
        return len(self.__data_list)

    def columnCount(self, parent=QModelIndex()):
        if self.rowCount():
            return len(self.__data_list[0])
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.__data_list)):
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.__data_list[index.row()][index.column()])
        return QVariant()

    def all_data(self):
        return self.__data_list

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.cursor.description[section][0]
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return super().headerData(section, orientation, role)

    def refresh_grid(self):
        try:
            self.cursor.execute(
                """
                SELECT * FROM case_events
                WHERE (case_id, vehicle_num, event_num) IN (
                    SELECT case_id, vehicle_num, event_num FROM scrape_profile_events
                    WHERE profile_id = ?
                )
                """,
                (self.profile[0],),
            )
            self.temp_list = self.cursor.fetchall()
            IGNORED_IDX = 31
            self.__data_list = [
                event for event in self.temp_list if not event[IGNORED_IDX]
            ]
            self.layoutChanged.emit()
        except sqlite3.Error as e:
            self.logger.error("Error refreshing data:", e)
            return
        self.logger.debug("Refreshed data.")
