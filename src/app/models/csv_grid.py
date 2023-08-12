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
        self.data_list = []

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
        return len(self.data_list)

    def columnCount(self, parent=QModelIndex()):
        if self.rowCount():
            return len(self.data_list[0])
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.data_list)):
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            return "Hello"
            
        return super().data(index, role)

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
            self.data_list = [event for event in self.temp_list if event[IGNORED_IDX]]
            self.layoutChanged.emit()
        except sqlite3.Error as e:
            self.logger.error("Error refreshing data:", e)
            return
        self.logger.debug("Refreshed data.")
