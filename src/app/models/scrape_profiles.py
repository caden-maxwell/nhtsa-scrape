import logging
from pathlib import Path
import sqlite3
from sqlite3 import Error

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class ScrapeProfiles(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        try:
            db_path = Path(__file__).parent / "db_saves.sqlite3"
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
        except Error as e:
            self.logger.error(e)
            self.db = None
        
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scrape_profiles (
                profile_id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                date_created TEXT,
                date_modified TEXT
            );
            """
        )
        self.db.commit()

        self.data_list = []

    def close_database(self):
        try:
            self.cursor.close()
            self.db.close()
            self.db = None
            self.cursor = None
        except sqlite3.Error as e:
            self.logger.error(f"Error closing database: {e}")

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            data = self.data_list[index.row()]
            return f"{data[1]} - {data[2]}"
        elif role == Qt.ItemDataRole.UserRole:
            return self.data_list[index.row()]
        return None
    
    def add_data(self, data: dict):
        try:
            name = data["name"]
            description = data["description"]
            date_created = data["created"]
            date_modified = data["modified"]
            self.cursor.execute(
                """
                INSERT INTO scrape_profiles (
                    name,
                    description,
                    date_created,
                    date_modified
                )
                VALUES (?, ?, ?, ?)
                """,
                (name, description, date_created, date_modified)
            )
            self.db.commit()
            self.logger.debug(f"Added profile: {name}")
        except (KeyError, sqlite3.Error) as e:
            self.logger.error(f"Error adding profile: {e}")
            return
        self.refresh_data()
        return self.cursor.lastrowid

    def delete_data(self, index: QModelIndex):
        try:
            data = self.data_list[index.row()]
            profile_id = data[0]

            # Delete all case events that belong to this profile 
                # and are not referred to by another profile
            self.cursor.execute(
                """
                SELECT case_id, event_num, vehicle_num
                FROM scrape_profile_events
                WHERE profile_id = ?;
                """, (profile_id,))
            case_events = self.cursor.fetchall()
            for case_event in case_events:
                case_id, event_num, vehicle_num = case_event
                self.cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM scrape_profile_events
                    WHERE case_id = ?
                        AND event_num = ?
                        AND vehicle_num = ?
                        AND profile_id != ?;
                    """, (case_id, event_num, vehicle_num, profile_id))
                count = self.cursor.fetchone()[0]

                if count < 1:
                    self.cursor.execute(
                        """
                        DELETE FROM case_events
                        WHERE case_id = ?
                            AND event_num = ?
                            AND vehicle_num = ?;
                        """, (case_id, event_num, vehicle_num))

            # Delete all scrape_profile_events belonging to this profile and the profile itself
            self.cursor.execute(
                """
                DELETE FROM scrape_profile_events
                WHERE profile_id = ?;
                """, (profile_id,))
            self.cursor.execute(
                """
                DELETE FROM scrape_profiles
                WHERE profile_id = ?
                """, (profile_id,))
            self.db.commit()
            self.logger.debug(f"Deleted profile: '{data[1]}'")
        except (IndexError, sqlite3.Error) as e:
            self.logger.error(f"Error deleting profile: {e}")
            return
        self.refresh_data()

    def refresh_data(self):
        try:
            self.cursor.execute("SELECT * FROM scrape_profiles")
            self.data_list = self.cursor.fetchall()
            self.layoutChanged.emit()
        except sqlite3.Error as e:
            self.logger.error(f"Error refreshing data: {e}")
            return
        self.logger.debug("Refreshed data.")

    def __del__(self):
        self.close_database()
